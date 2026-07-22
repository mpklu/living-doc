#!/usr/bin/env python3
"""Regenerate knowledge/index.md article tables from article frontmatter.

Motivation (field-tested): a hand-maintained index duplicates each
article's summary and `updated:` date, and the copies drift — after any
sweep that touches several articles, someone (usually an AI agent,
burning reasoning on a mechanical task) must hand-sync the index rows.
Everything the index table needs already lives in the articles'
frontmatter; generating the table makes drift structurally impossible.

The index file stays hand-written prose EXCEPT for marked blocks:

    <!-- build-index:begin dir=concepts/methodology -->
    …generated table…
    <!-- build-index:end -->

Each block regenerates as a table of every article under that dir
(relative to the knowledge dir), sorted by filename:

    | Article | Covers | Updated |

'Covers' prefers the article's `description:` frontmatter, falling back
to `title:`. Deprecated articles (status: deprecated) are annotated.

Uses validate_articles.parse_frontmatter — the shared hand-parser —
hence co-located with it.

Usage:
    build-index                     # rewrite marked blocks in place
    build-index --check             # exit 1 if any block is stale (CI)
    build-index --knowledge-dir docs/kb
    build-index --index PATH        # default: <knowledge-dir>/index.md

Exits: 0 = up to date / rewritten; 1 = --check found staleness or error.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from validate_articles import parse_frontmatter

BEGIN_RE = re.compile(
    r"^<!--\s*build-index:begin\s+dir=([^\s>]+)\s*-->\s*$"
)
END_MARK = "<!-- build-index:end -->"


def article_row(article: Path, index_dir: Path) -> str | None:
    """One table row for an article, or None if it has no frontmatter."""
    fm = parse_frontmatter(article)
    if not fm:
        return None
    covers = str(fm.get("description") or fm.get("title") or article.stem)
    updated = str(fm.get("updated", ""))
    if fm.get("status") == "deprecated":
        covers = f"*(deprecated)* {covers}"
    try:
        rel = article.relative_to(index_dir)
    except ValueError:
        rel = article
    # Pipes inside covers would break the table.
    covers = covers.replace("|", "\\|")
    return f"| [{article.stem}]({rel.as_posix()}) | {covers} | {updated} |"


def generate_table(target_dir: Path, index_dir: Path) -> str:
    rows = []
    for article in sorted(target_dir.glob("*.md")):
        row = article_row(article, index_dir)
        if row:
            rows.append(row)
    if not rows:
        return "_(no articles yet)_"
    return "\n".join(
        ["| Article | Covers | Updated |", "| --- | --- | --- |"] + rows
    )


def rebuild(index_path: Path, knowledge_root: Path) -> tuple[str, list[str]]:
    """Return (new_index_text, [dirs regenerated])."""
    text = index_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    out: list[str] = []
    regenerated: list[str] = []
    i = 0
    while i < len(lines):
        m = BEGIN_RE.match(lines[i])
        if not m:
            out.append(lines[i])
            i += 1
            continue
        rel_dir = m.group(1)
        target_dir = knowledge_root / rel_dir
        # Find the matching end marker; everything between is replaced.
        j = i + 1
        while j < len(lines) and lines[j].strip() != END_MARK:
            j += 1
        if j >= len(lines):
            raise ValueError(
                f"{index_path}: 'build-index:begin dir={rel_dir}' has no "
                f"matching '{END_MARK}'"
            )
        out.append(lines[i])
        out.append(generate_table(target_dir, index_path.parent))
        out.append(END_MARK)
        regenerated.append(rel_dir)
        i = j + 1
    new_text = "\n".join(out)
    if text.endswith("\n"):
        new_text += "\n"
    return new_text, regenerated


def cli_main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Regenerate index.md article tables from frontmatter."
    )
    ap.add_argument("--knowledge-dir", default="knowledge")
    ap.add_argument("--index", default=None,
                    help="index file (default: <knowledge-dir>/index.md)")
    ap.add_argument("--check", action="store_true",
                    help="don't write; exit 1 if any block is stale")
    args = ap.parse_args(argv)

    knowledge_root = Path(args.knowledge_dir)
    index_path = Path(args.index) if args.index else knowledge_root / "index.md"
    if not index_path.is_file():
        print(f"build-index: no index at {index_path}", file=sys.stderr)
        return 1

    try:
        new_text, regenerated = rebuild(index_path, knowledge_root)
    except ValueError as exc:
        print(f"build-index: {exc}", file=sys.stderr)
        return 1

    if not regenerated:
        print(
            "build-index: no '<!-- build-index:begin dir=… -->' blocks in "
            f"{index_path} — nothing to generate. Add markers around each "
            "article table to adopt (see the module docstring)."
        )
        return 0

    current = index_path.read_text(encoding="utf-8")
    if current == new_text:
        print(
            f"✅ build-index: {index_path} up to date "
            f"({len(regenerated)} generated block(s))."
        )
        return 0
    if args.check:
        print(
            f"❌ build-index: {index_path} is stale for block(s): "
            f"{', '.join(regenerated)}. Run scripts/build-index to fix."
        )
        return 1
    index_path.write_text(new_text, encoding="utf-8")
    print(
        f"build-index: rewrote {index_path} "
        f"({len(regenerated)} block(s): {', '.join(regenerated)})."
    )
    return 0


if __name__ == "__main__":
    sys.exit(cli_main())
