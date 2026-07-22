#!/usr/bin/env python3
"""Drift-sweep worklist: the N oldest knowledge articles by `updated:`.

Motivation (field-tested): the methodology prescribes a periodic drift
sweep "oldest `updated:` first" — but generating that worklist by
having an agent scan frontmatter is wasted reasoning. This emits the
list deterministically; the AI (or human) spends effort on the actual
semantic review.

Usage:
    sweep-report                     # 5 oldest articles
    sweep-report --limit 10
    sweep-report --area cda          # filter by frontmatter area
    sweep-report --json

Uses validate_articles.parse_frontmatter (the shared hand-parser) —
hence co-located. Articles without parseable frontmatter are listed
last with a warning (they can't be sweep-ordered).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from validate_articles import parse_frontmatter


def collect(knowledge_dir: str, area: str | None) -> tuple[list[dict], list[str]]:
    root = Path(knowledge_dir)
    rows: list[dict] = []
    unparsed: list[str] = []
    for path in sorted(root.rglob("*.md")):
        if path.name in ("index.md", "log.md"):
            continue
        fm = parse_frontmatter(path)
        if not fm or "updated" not in fm:
            unparsed.append(str(path))
            continue
        if area and str(fm.get("area", "")) != area:
            continue
        rows.append(
            {
                "path": str(path),
                "updated": str(fm["updated"]),
                "status": str(fm.get("status", "")),
                "title": str(fm.get("title", path.stem)),
            }
        )
    rows.sort(key=lambda r: (r["updated"], r["path"]))
    return rows, unparsed


def cli_main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="List the oldest knowledge articles by updated: date."
    )
    ap.add_argument("--knowledge-dir", default="knowledge")
    ap.add_argument("--limit", type=int, default=5)
    ap.add_argument("--area", default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    if not Path(args.knowledge_dir).is_dir():
        print(f"sweep-report: knowledge dir not found: {args.knowledge_dir}",
              file=sys.stderr)
        return 1

    rows, unparsed = collect(args.knowledge_dir, args.area)
    picked = rows[: args.limit] if args.limit > 0 else rows

    if args.json:
        print(json.dumps({"articles": picked, "unparsed": unparsed}, indent=2))
        return 0

    if not picked:
        print("sweep-report: no articles matched.")
    else:
        w = max(len(r["updated"]) for r in picked)
        print(f"Drift-sweep worklist — {len(picked)} oldest of {len(rows)} article(s):")
        for r in picked:
            status = f" [{r['status']}]" if r["status"] else ""
            print(f"  {r['updated']:<{w}}  {r['path']}{status} — {r['title']}")
    for p in unparsed:
        print(f"  ⚠ no parseable frontmatter (can't order): {p}")
    return 0


if __name__ == "__main__":
    sys.exit(cli_main())
