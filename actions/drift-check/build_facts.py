#!/usr/bin/env python3
"""Generate per-area facts indexes from articles' `## Facts` sections.

The facts register (see concepts/methodology/facts-register.md) is the
read-path layer between the index and full prose: each article MAY carry
a compact `## Facts` section — atomic, lookup-shaped facts (paths, ports,
codes, defaults, invariants), each ideally claim-provenance-tagged. This
tool concatenates them per `area:` into generated files:

    knowledge/facts/<area>.md

so an agent (or human) answering a needle query loads ONE small surface
instead of opening 20–60KB articles. The articles stay the single source;
the generated files carry a sentinel first line and per-article backlinks.

Usage:
    build-facts               # (re)write knowledge/facts/<area>.md files
    build-facts --check       # exit 1 if any facts file is stale/orphaned
    build-facts --knowledge-dir docs/kb

Extraction: everything between a literal `## Facts` heading and the next
`## ` heading (or EOF). Articles without the section are simply absent
from the register. Area comes from frontmatter `area:`, falling back to
the article's parent directory name.

Uses validate_articles.parse_frontmatter — hence co-located.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from validate_articles import parse_frontmatter

SENTINEL = "<!-- build-facts:generated — edit the articles' ## Facts sections, not this file -->"
FACTS_HEADING_RE = re.compile(r"^##\s+Facts\s*$")
H2_RE = re.compile(r"^##\s+")


def extract_facts(text: str) -> str | None:
    """Return the body of the `## Facts` section, or None if absent."""
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if FACTS_HEADING_RE.match(line):
            start = i + 1
            break
    if start is None:
        return None
    end = len(lines)
    for j in range(start, len(lines)):
        if H2_RE.match(lines[j]):
            end = j
            break
    body = "\n".join(lines[start:end]).strip("\n")
    return body if body.strip() else None


def collect(knowledge_root: Path) -> dict[str, list[tuple[Path, str]]]:
    """area -> [(article_path, facts_body)] sorted by filename."""
    by_area: dict[str, list[tuple[Path, str]]] = {}
    for path in sorted(knowledge_root.rglob("*.md")):
        if path.name in ("index.md", "log.md"):
            continue
        if "facts" in path.relative_to(knowledge_root).parts[:1]:
            continue  # never read our own output
        fm = parse_frontmatter(path)
        if fm is None:
            continue
        try:
            body = extract_facts(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError):
            continue
        if body is None:
            continue
        area = str(fm.get("area") or path.parent.name)
        by_area.setdefault(area, []).append((path, body))
    return by_area


def render(area: str, entries: list[tuple[Path, str]], facts_dir: Path) -> str:
    out = [
        SENTINEL,
        "",
        f"# Facts — {area}",
        "",
        f"Atomic lookup facts extracted from the `{area}` articles' `## Facts` "
        "sections by `scripts/build-facts`. One small surface for needle "
        "queries; open the linked article for the why.",
        "",
    ]
    for path, body in entries:
        rel = Path("..") / path.relative_to(facts_dir.parent)
        out.append(f"## {path.stem} — [{rel.as_posix()}]({rel.as_posix()})")
        out.append("")
        out.append(body)
        out.append("")
    return "\n".join(out).rstrip("\n") + "\n"


def cli_main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Generate knowledge/facts/<area>.md from articles' ## Facts sections."
    )
    ap.add_argument("--knowledge-dir", default="knowledge")
    ap.add_argument("--check", action="store_true",
                    help="don't write; exit 1 if any facts file is stale or orphaned")
    args = ap.parse_args(argv)

    knowledge_root = Path(args.knowledge_dir)
    if not knowledge_root.is_dir():
        print(f"build-facts: knowledge dir not found: {knowledge_root}", file=sys.stderr)
        return 1
    facts_dir = knowledge_root / "facts"

    by_area = collect(knowledge_root)
    expected: dict[Path, str] = {
        facts_dir / f"{area}.md": render(area, entries, facts_dir)
        for area, entries in sorted(by_area.items())
    }

    existing = set(facts_dir.glob("*.md")) if facts_dir.is_dir() else set()
    orphans = sorted(existing - set(expected))
    stale = [
        p for p, want in expected.items()
        if not p.exists() or p.read_text(encoding="utf-8") != want
    ]

    if args.check:
        for p in stale:
            print(f"❌ build-facts: stale/missing: {p}")
        for p in orphans:
            print(f"❌ build-facts: orphaned (no area produces it): {p}")
        if stale or orphans:
            print("Run scripts/build-facts to fix.")
            return 1
        n = len(expected)
        print(f"✅ build-facts: {n} facts file(s) up to date." if n else
              "✅ build-facts: no ## Facts sections found; nothing to generate.")
        return 0

    if not expected and not orphans:
        print("build-facts: no ## Facts sections found; nothing to generate.")
        return 0
    facts_dir.mkdir(parents=True, exist_ok=True)
    for p, want in expected.items():
        if not p.exists() or p.read_text(encoding="utf-8") != want:
            p.write_text(want, encoding="utf-8")
            print(f"build-facts: wrote {p}")
    for p in orphans:
        p.unlink()
        print(f"build-facts: removed orphaned {p}")
    if not stale and not orphans:
        print(f"build-facts: {len(expected)} facts file(s) already up to date.")
    return 0


if __name__ == "__main__":
    sys.exit(cli_main())
