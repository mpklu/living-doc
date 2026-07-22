#!/usr/bin/env python3
"""Provenance report — make claim-provenance tags actionable.

Companion to concepts/methodology/claim-provenance.md. Claims in articles
carry inline tags — *(code: path:line)* · *(bench: date)* ·
*(field: incident)* · *(reported: who)* · *(inferred)* — grading how each
claim was verified. This tool is what keeps the tags from rotting into
decoration:

  provenance-report               # per-article tag counts + coverage
  provenance-report --worklist    # every inferred/reported claim in a
                                  # load_bearing article — the input for
                                  # the next verification pass
  provenance-report --json        # machine-readable

Coverage view flags load_bearing articles with ZERO provenance tags —
their claims are ungraded, so a reader can't calibrate trust. Worklist
view lists file:line + snippet for each `inferred`/`reported` tag, i.e.
the claims worth spending verification (or adversarial-refutation)
effort on. Code fences and inline code are excluded from scanning.

Uses validate_articles.parse_frontmatter (the shared hand-parser) —
hence co-located.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from validate_articles import parse_frontmatter

TAG_RE = re.compile(r"\*\((code|bench|field|reported|inferred)([:)])")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE_RE = re.compile(r"`[^`]*`")
KINDS = ("code", "bench", "field", "reported", "inferred")
WORKLIST_KINDS = ("inferred", "reported")


def masked_lines(text: str) -> list[str]:
    """Body lines with code fences, inline code, AND the frontmatter block
    blanked (frontmatter mentions of tag syntax aren't claims); line count
    preserved so reported line numbers stay true."""
    lines = text.splitlines()
    out: list[str] = []
    i = 0
    if lines and lines[0].strip() == "---":  # skip frontmatter
        out.append("")
        i = 1
        while i < len(lines):
            out.append("")
            if lines[i].strip() == "---":
                i += 1
                break
            i += 1
    in_fence = False
    for line in lines[i:]:
        if FENCE_RE.match(line):
            in_fence = not in_fence
            out.append("")
            continue
        out.append("" if in_fence else INLINE_CODE_RE.sub("", line))
    return out


def scan(knowledge_dir: str) -> list[dict]:
    root = Path(knowledge_dir)
    articles: list[dict] = []
    for path in sorted(root.rglob("*.md")):
        if path.name in ("index.md", "log.md"):
            continue
        fm = parse_frontmatter(path)
        if fm is None:
            continue  # not an article (e.g. log archives)
        counts = {k: 0 for k in KINDS}
        hits: list[dict] = []
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for lineno, line in enumerate(masked_lines(text), start=1):
            for m in TAG_RE.finditer(line):
                kind = m.group(1)
                counts[kind] += 1
                if kind in WORKLIST_KINDS:
                    hits.append(
                        {
                            "line": lineno,
                            "kind": kind,
                            "snippet": line.strip()[:160],
                        }
                    )
        articles.append(
            {
                "path": str(path),
                "load_bearing": bool(fm.get("load_bearing", False)),
                "status": str(fm.get("status", "")),
                "counts": counts,
                "total": sum(counts.values()),
                "worklist": hits,
            }
        )
    return articles


def cli_main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Report claim-provenance tag coverage / verification worklist."
    )
    ap.add_argument("--knowledge-dir", default="knowledge")
    ap.add_argument("--worklist", action="store_true",
                    help="list inferred/reported claims in load_bearing articles")
    ap.add_argument("--all", action="store_true",
                    help="with --worklist: include non-load_bearing articles too")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    if not Path(args.knowledge_dir).is_dir():
        print(f"provenance-report: knowledge dir not found: {args.knowledge_dir}",
              file=sys.stderr)
        return 1
    articles = scan(args.knowledge_dir)

    if args.json:
        print(json.dumps({"articles": articles}, indent=2))
        return 0

    if args.worklist:
        rows = [
            (a, h)
            for a in articles
            if (a["load_bearing"] or args.all)
            for h in a["worklist"]
        ]
        if not rows:
            scope = "any article" if args.all else "load_bearing articles"
            print(f"provenance-report: no inferred/reported claims tagged in {scope}.")
            return 0
        print(f"Verification worklist — {len(rows)} claim(s) to verify or refute:")
        for a, h in rows:
            print(f"  {a['path']}:{h['line']}: ({h['kind']}) {h['snippet']}")
        return 0

    tagged = [a for a in articles if a["total"]]
    lb_untagged = [a for a in articles if a["load_bearing"] and not a["total"]]
    print(
        f"Provenance coverage — {len(tagged)}/{len(articles)} article(s) carry tags."
    )
    for a in tagged:
        parts = ", ".join(f"{k}:{v}" for k, v in a["counts"].items() if v)
        print(f"  {a['path']} — {parts}")
    if lb_untagged:
        print(f"\n⚠ load_bearing articles with NO provenance tags ({len(lb_untagged)}) —")
        print("  their claims are ungraded (readers can't calibrate trust):")
        for a in lb_untagged:
            print(f"  {a['path']} [{a['status']}]")
    return 0


if __name__ == "__main__":
    sys.exit(cli_main())
