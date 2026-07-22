#!/usr/bin/env python3
"""Link checker for knowledge/ — verifies [[wikilinks]] and relative
markdown links actually resolve.

Motivation (field-tested): when an article or companion file is renamed
or deleted, references to it dangle silently until a human greps for
them. That's a string/path comparison — a script's job, not an AI
reasoning task. Run locally before commit or wire into CI.

Checks, per knowledge/**/*.md (code fences and inline code excluded):

  1. ``[[wikilink]]`` / ``[[wikilink|label]]`` / ``[[wikilink#anchor]]``
     — target must resolve to exactly one article under the knowledge
     dir. "name" resolves by unique filename stem; "area/name" (any
     path suffix) resolves by suffix match. Zero matches = broken;
     2+ matches = ambiguous (also an error: the link is unreliable).
  2. ``[text](relative/path.md)`` (any extension, not just .md) —
     resolved relative to the containing file; the target must exist.
     External schemes (http:, https:, mailto:, …) and pure-anchor
     links (#…) are skipped. Anchors on file links are stripped, not
     verified.

Co-located with drift_check.py / validate_articles.py per house
convention (they share repo layout assumptions and ship together).

Usage:
    check-links                          # human-readable report
    check-links --json                   # machine-readable JSON
    check-links --knowledge-dir docs/kb  # alt knowledge dir

Exits 1 if any link is broken or ambiguous; 0 otherwise.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

WIKILINK_RE = re.compile(r"\[\[([^\]\|#]+)(?:#[^\]\|]*)?(?:\|[^\]]*)?\]\]")
# [text](target) — target up to the first whitespace or ')' (titles after
# whitespace are tolerated and ignored).
MDLINK_RE = re.compile(r"\[[^\]]*\]\(\s*([^)\s]+)(?:\s+[^)]*)?\)")
SCHEME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE_RE = re.compile(r"`[^`]*`")


def masked_lines(text: str) -> list[str]:
    """Return the file's lines with fenced blocks and inline code blanked
    out (line count preserved, so reported line numbers stay true)."""
    out: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if FENCE_RE.match(line):
            in_fence = not in_fence
            out.append("")
            continue
        out.append("" if in_fence else INLINE_CODE_RE.sub("", line))
    return out


def build_article_index(knowledge_root: Path) -> dict[str, list[Path]]:
    """Map lowercase filename stem -> article paths (for wikilink resolution)."""
    index: dict[str, list[Path]] = {}
    for p in sorted(knowledge_root.rglob("*.md")):
        index.setdefault(p.stem.lower(), []).append(p)
    return index


def resolve_wikilink(
    target: str, stem_index: dict[str, list[Path]], knowledge_root: Path
) -> tuple[str, list[Path]]:
    """Return (status, matches): status in {'ok', 'missing', 'ambiguous'}."""
    target = target.strip()
    if "/" in target:
        # Path-qualified: match by path suffix (with .md appended).
        suffix = target.lower() + ".md"
        matches = [
            p
            for paths in stem_index.values()
            for p in paths
            if p.as_posix().lower().endswith(suffix)
        ]
    else:
        matches = stem_index.get(target.lower(), [])
    if not matches:
        return "missing", []
    if len(matches) > 1:
        return "ambiguous", matches
    return "ok", matches


def check_file(
    article: Path, stem_index: dict[str, list[Path]], knowledge_root: Path
) -> list[dict]:
    problems: list[dict] = []
    try:
        text = article.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return [
            {
                "file": str(article),
                "line": 0,
                "link": "",
                "kind": "read-error",
                "detail": str(exc),
            }
        ]

    for lineno, line in enumerate(masked_lines(text), start=1):
        for m in WIKILINK_RE.finditer(line):
            status, matches = resolve_wikilink(
                m.group(1), stem_index, knowledge_root
            )
            if status == "missing":
                problems.append(
                    {
                        "file": str(article),
                        "line": lineno,
                        "link": f"[[{m.group(1)}]]",
                        "kind": "wikilink-missing",
                        "detail": "no article with this name under the knowledge dir",
                    }
                )
            elif status == "ambiguous":
                problems.append(
                    {
                        "file": str(article),
                        "line": lineno,
                        "link": f"[[{m.group(1)}]]",
                        "kind": "wikilink-ambiguous",
                        "detail": "matches: "
                        + ", ".join(str(p) for p in matches),
                    }
                )
        for m in MDLINK_RE.finditer(line):
            target = m.group(1)
            if SCHEME_RE.match(target) or target.startswith("#"):
                continue
            path_part = target.split("#", 1)[0]
            if not path_part:
                continue
            resolved = (article.parent / path_part).resolve()
            if not resolved.exists():
                problems.append(
                    {
                        "file": str(article),
                        "line": lineno,
                        "link": target,
                        "kind": "relative-link-missing",
                        "detail": f"target not found: {resolved}",
                    }
                )
    return problems


def check_repo(knowledge_dir: str) -> dict:
    knowledge_root = Path(knowledge_dir)
    if not knowledge_root.is_dir():
        return {
            "files_checked": 0,
            "problems": [],
            "fatal": f"knowledge dir not found: {knowledge_dir}",
        }
    stem_index = build_article_index(knowledge_root)
    problems: list[dict] = []
    files = sorted(knowledge_root.rglob("*.md"))
    for article in files:
        problems.extend(check_file(article, stem_index, knowledge_root))
    return {
        "files_checked": len(files),
        "problems": problems,
        "fatal": None,
    }


def cli_main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Verify wikilinks and relative links in knowledge/ resolve."
    )
    ap.add_argument("--knowledge-dir", default="knowledge")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    result = check_repo(args.knowledge_dir)
    if args.json:
        print(json.dumps(result, indent=2))
        return 1 if (result["fatal"] or result["problems"]) else 0

    if result["fatal"]:
        print(f"check-links: {result['fatal']}", file=sys.stderr)
        return 1
    if not result["problems"]:
        print(
            f"✅ check-links: all links resolve "
            f"({result['files_checked']} file(s) checked)."
        )
        return 0
    for p in result["problems"]:
        print(f"{p['file']}:{p['line']}: [{p['kind']}] {p['link']} — {p['detail']}")
    print(
        f"❌ check-links: {len(result['problems'])} problem(s) across "
        f"{result['files_checked']} file(s)."
    )
    return 1


if __name__ == "__main__":
    sys.exit(cli_main())
