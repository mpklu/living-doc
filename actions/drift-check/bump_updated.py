#!/usr/bin/env python3
"""Set the `updated:` frontmatter date on knowledge articles.

Motivation (field-tested): the same-task rule requires bumping
`updated:` on every meaningful article edit, and agents/humans forget —
which silently corrupts drift-sweep ordering (sweeps prioritize oldest
`updated:` first). This is a pure string edit; a script's job.

Two modes:

  bump-updated <paths…>          # set updated: today on these articles
  bump-updated --staged          # …on all staged knowledge articles
  bump-updated --staged --check  # don't write; exit 1 if any staged
                                 # article's updated: ≠ today (pre-commit)

Files without frontmatter or without an `updated:` line (log.md,
index.md, non-articles) are skipped silently. `--date YYYY-MM-DD`
overrides "today" (useful for tests and backfills).

Co-located with validate_articles.py per house convention.
"""

from __future__ import annotations

import argparse
import datetime
import re
import subprocess
import sys
from pathlib import Path

UPDATED_RE = re.compile(r"^(updated\s*:\s*)(\S+)\s*$")


def staged_files() -> list[Path]:
    try:
        out = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            capture_output=True, text=True, check=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"bump-updated: git diff failed: {exc}")
    return [Path(p) for p in out.splitlines() if p.strip()]


def find_updated_line(path: Path) -> tuple[list[str], int] | None:
    """Return (lines, index-of-updated-line) if the file is a frontmatter
    article with an `updated:` field; None otherwise."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    if not text.startswith("---"):
        return None
    lines = text.splitlines(keepends=True)
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return None  # frontmatter ended without an updated: line
        if UPDATED_RE.match(line.rstrip("\n")):
            return lines, i
    return None


def cli_main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Set updated: frontmatter to today on knowledge articles."
    )
    ap.add_argument("paths", nargs="*", help="article paths to bump")
    ap.add_argument("--staged", action="store_true",
                    help="operate on staged files (git diff --cached)")
    ap.add_argument("--knowledge-dir", default="knowledge",
                    help="only files under this dir are considered")
    ap.add_argument("--date", default=None, help="override today (YYYY-MM-DD)")
    ap.add_argument("--check", action="store_true",
                    help="don't write; exit 1 listing articles not at the date")
    args = ap.parse_args(argv)

    date = args.date or datetime.date.today().isoformat()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
        print(f"bump-updated: bad --date '{args.date}'", file=sys.stderr)
        return 1

    targets = [Path(p) for p in args.paths]
    if args.staged:
        targets += staged_files()
    if not targets:
        print("bump-updated: nothing to do (no paths; try --staged).")
        return 0

    kroot = Path(args.knowledge_dir)
    stale: list[tuple[Path, str]] = []
    bumped: list[Path] = []
    for path in targets:
        # Only knowledge articles; skip the index and the log (not articles).
        try:
            path.relative_to(kroot)
        except ValueError:
            continue
        if path.suffix != ".md" or path.name in ("index.md", "log.md"):
            continue
        found = find_updated_line(path)
        if not found:
            continue
        lines, i = found
        m = UPDATED_RE.match(lines[i].rstrip("\n"))
        current = m.group(2)
        if current == date:
            continue
        if args.check:
            stale.append((path, current))
            continue
        nl = "\n" if lines[i].endswith("\n") else ""
        lines[i] = f"{m.group(1)}{date}{nl}"
        path.write_text("".join(lines), encoding="utf-8")
        bumped.append(path)

    if args.check:
        if stale:
            for path, current in stale:
                print(f"{path}: updated: {current} → should be {date}")
            print(
                f"❌ bump-updated --check: {len(stale)} article(s) stale. "
                "Fix: scripts/bump-updated --staged   (then re-stage)"
            )
            return 1
        print(f"✅ bump-updated --check: all staged articles at {date}.")
        return 0

    for path in bumped:
        print(f"bump-updated: {path} → {date}")
    if not bumped:
        print("bump-updated: nothing needed bumping.")
    return 0


if __name__ == "__main__":
    sys.exit(cli_main())
