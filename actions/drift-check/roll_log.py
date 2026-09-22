#!/usr/bin/env python3
"""The build log is files. This tool validates them and rolls old ones into month dirs.

An entry is `knowledge/log/entries/YYYY-MM-DD-<slug>.md`; its first line is
`## YYYY-MM-DD — <title>`, then bullets (~150 words unless it records a
decision). Nothing renders them: agents `ls knowledge/log/entries | tail`
for "lately" and `grep -rn <term> knowledge/log/` for history. The rendered
`log.md` (170 KB, 2026-09-21) was dropped the same day it was introduced —
logs are agent-facing, and a concatenation nobody Reads is only a gate step
and a merge surface.

roll-log moves entry files older than the keep-window (14 days) into
`knowledge/log/YYYY-MM/` (a rename, not a rewrite — no conservation risk).
Pre-2026-09-21 archives are concatenated `log/YYYY-MM.md` files, frozen;
grep treats both shapes alike. Not run by the hook (it moves files, and a
hook doing that mid-session leaves the tree half-staged); `kb-status` says
when it is due.

Usage:
    roll-log                          # move entries older than 14 days
    roll-log --keep-since 2026-09-01
    roll-log --dry-run
    roll-log --check                  # validate entry headers only (the gate)
    roll-log --long                   # entries over the word budget — a worklist, never a gate
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

ENTRIES_DIR = "log/entries"
KEEP_DAYS = 14
LONG_WORDS = 400   # budget ~150 words; `--long` lists entries above this (kb-status shows the count) — not in --check
HDR = re.compile(r"^##\s+\[?(\d{4}-\d{2}-\d{2})")
FILE_DATE = re.compile(r"^(\d{4}-\d{2}-\d{2})-")


def load_entries(knowledge_root: Path) -> list[tuple[str, str, str]]:
    """[(date, filename, text)] newest first; ValueError on a bad header."""
    d = knowledge_root / ENTRIES_DIR
    out: list[tuple[str, str, str]] = []
    bad: list[str] = []
    if d.is_dir():
        for p in sorted(d.glob("*.md")):
            text = p.read_text(encoding="utf-8")
            m = HDR.match(text.lstrip())
            if not m:
                bad.append(p.name)
                continue
            fd = FILE_DATE.match(p.name)
            if not fd or fd.group(1) != m.group(1):
                bad.append(f"{p.name} (header says {m.group(1)})")
                continue
            out.append((m.group(1), p.name, text))
    if bad:
        raise ValueError("entry file(s) must be named YYYY-MM-DD-<slug>.md and start with "
                         "`## YYYY-MM-DD — title` (same date): " + ", ".join(bad))
    out.sort(key=lambda e: (e[0], e[1]), reverse=True)
    return out


def long_entries(knowledge_root: Path) -> list[tuple[str, int]]:
    """(filename, words) for active entries over LONG_WORDS, longest first."""
    out = [(n, len(t.split())) for _, n, t in load_entries(knowledge_root) if len(t.split()) > LONG_WORDS]
    return sorted(out, key=lambda x: -x[1])


def roll(knowledge_root: Path, keep_since: str, dry_run: bool) -> int:
    entries_dir = knowledge_root / ENTRIES_DIR
    entries = load_entries(knowledge_root)
    old = [(d, n) for d, n, _ in entries if d < keep_since]
    by_month: dict[str, list[str]] = {}
    for d, n in old:
        by_month.setdefault(d[:7], []).append(n)
    print(f"roll-log: keep-since {keep_since} — {len(entries) - len(old)} kept, {len(old)} to roll"
          + (f" into log/{{{','.join(sorted(by_month))}}}/" if by_month else ""))
    if not old:
        return 0
    for month, names in sorted(by_month.items()):
        dest = knowledge_root / "log" / month
        for n in names:
            if (dest / n).exists():
                print(f"roll-log: {dest / n} already exists; refusing to overwrite", file=sys.stderr)
                return 1
        if dry_run:
            print(f"  would move {len(names)} entr{'y' if len(names) == 1 else 'ies'} -> log/{month}/")
            continue
        dest.mkdir(parents=True, exist_ok=True)
        for n in names:
            (entries_dir / n).rename(dest / n)
        print(f"  moved {len(names)} -> log/{month}/")
    return 0


def cli_main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Validate log entry files; roll old ones into log/YYYY-MM/.")
    ap.add_argument("--knowledge-dir", default="knowledge")
    ap.add_argument("--keep-since", help="keep entries dated on/after this (default: today-14d)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--check", action="store_true", help="validate entry headers only (the gate)")
    ap.add_argument("--long", action="store_true", help=f"list active entries over {LONG_WORDS} words (warn-only worklist)")
    args = ap.parse_args(argv)
    root = Path(args.knowledge_dir)
    if not root.is_dir():
        print(f"roll-log: no knowledge dir at {root}", file=sys.stderr)
        return 1
    try:
        if args.check:
            print(f"✅ roll-log --check: {len(load_entries(root))} entry file(s) well-formed.")
            return 0
        if args.long:
            long = long_entries(root)
            for n, w in long:
                print(f"  {w:>5}w  {n}")
            print(f"roll-log --long: {len(long)} entr{'y' if len(long) == 1 else 'ies'} over {LONG_WORDS} words "
                  f"(budget ~150; the decision itself belongs in the article's ## Decisions). Trim on touch.")
            return 0
        keep_since = args.keep_since or (dt.date.today() - dt.timedelta(days=KEEP_DAYS)).isoformat()
        return roll(root, keep_since, args.dry_run)
    except ValueError as exc:
        print(f"❌ roll-log: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(cli_main())
