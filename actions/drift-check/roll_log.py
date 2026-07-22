#!/usr/bin/env python3
"""Roll old compile-log entries out of knowledge/log.md into monthly archives.

Motivation (field-tested; ported from a production living-doc repo where
the active log outgrew its readable window in ~6 weeks): log.md is the
*active* log; entries older than the keep-window move into
knowledge/log/YYYY-MM.md (merged with any existing archive for that
month, deduped, sorted chronologically). The active log is rewritten as:
title/intro + a regenerated archives-index line + the kept entries.

Safety: idempotent and **conservation-checked** — after writing, the set
of entry texts across the active log + all archives must equal the set
before; otherwise the script aborts with an error. No entry is ever
silently lost.

Entry format: any `## ` heading starting with a date — both house styles
are supported: `## 2026-07-21 — title` and `## [2026-07-21] cat | title`.
The kept entries retain the active log's own ordering (newest-at-top and
oldest-first logs both work); archives are always chronological.

Usage:
    roll-log                                 # keep the last 14 days
    roll-log --keep-days 30
    roll-log --keep-since 2026-07-01         # keep entries on/after date
    roll-log --dry-run                       # report only; write nothing
    roll-log --log PATH --archive-dir PATH   # defaults: knowledge/log.md, knowledge/log
"""

from __future__ import annotations

import argparse
import datetime
import re
import sys
from pathlib import Path

HDR = re.compile(r"^##\s+\[?(\d{4}-\d{2}-\d{2})")
ARCHIVE_FN = re.compile(r"^\d{4}-\d{2}\.md$")
ARCHIVES_LINE_PREFIX = "> **Archives:**"


def split_entries(text: str) -> tuple[str, list[str]]:
    """Return (intro, [entry…]); an entry runs from its '## ' header to the next."""
    lines = text.splitlines(keepends=True)
    idx = [i for i, l in enumerate(lines) if l.startswith("## ")]
    if not idx:
        return text, []
    intro = "".join(lines[: idx[0]])
    entries = []
    for a, b in zip(idx, idx[1:] + [len(lines)]):
        entries.append("".join(lines[a:b]))
    return intro, entries


def edate(entry: str) -> str:
    m = HDR.match(entry)
    if not m:
        raise SystemExit(
            f"roll-log: entry without a parseable date header:\n{entry[:120]}"
        )
    return m.group(1)


def dedup_keep_order(entries: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for e in entries:
        k = e.strip()
        if k not in seen:
            seen.add(k)
            out.append(e)
    return out


def dedup_sorted(entries: list[str]) -> list[str]:
    return sorted(dedup_keep_order(entries), key=edate)  # stable within a date


def title_block(intro: str) -> str:
    """Intro minus any previous archives-index line and its rule."""
    keep = [
        l
        for l in intro.splitlines()
        if not l.startswith(ARCHIVES_LINE_PREFIX) and l.strip() != "---"
    ]
    return "\n".join(keep).rstrip()


def cli_main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Roll old log entries into monthly archives (conservation-checked)."
    )
    ap.add_argument("--log", default="knowledge/log.md")
    ap.add_argument("--archive-dir", default="knowledge/log")
    ap.add_argument("--keep-since", default=None,
                    help="keep entries dated on/after this YYYY-MM-DD")
    ap.add_argument("--keep-days", type=int, default=14,
                    help="keep-window in days when --keep-since is absent (default 14)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    keep_since = args.keep_since or (
        datetime.date.today() - datetime.timedelta(days=args.keep_days)
    ).isoformat()

    log_path = Path(args.log)
    archive_dir = Path(args.archive_dir)
    if not log_path.exists():
        print(f"roll-log: no log at {log_path}", file=sys.stderr)
        return 1
    intro, entries = split_entries(log_path.read_text(encoding="utf-8"))

    # Conservation snapshot: every entry text in the active log + archives.
    before = {e.strip() for e in entries}
    arch_entries: dict[str, list[str]] = {}
    if archive_dir.is_dir():
        for fn in sorted(archive_dir.iterdir()):
            if ARCHIVE_FN.match(fn.name):
                _, es = split_entries(fn.read_text(encoding="utf-8"))
                arch_entries[fn.name[:7]] = es
                before |= {e.strip() for e in es}

    keep = [e for e in entries if edate(e) >= keep_since]
    roll = [e for e in entries if edate(e) < keep_since]
    by_month: dict[str, list[str]] = {}
    for e in roll:
        by_month.setdefault(edate(e)[:7], []).append(e)

    print(
        f"roll-log: keep-since {keep_since} — {len(keep)} kept, {len(roll)} rolled"
        + (f" into {', '.join(sorted(by_month))}" if by_month else "")
    )
    if args.dry_run:
        for m in sorted(by_month):
            n = len(by_month[m])
            print(f"  would move {n} entr{'y' if n == 1 else 'ies'} -> {archive_dir}/{m}.md")
        if not roll:
            print("  (nothing to roll)")
        return 0
    if not roll:
        print("  (nothing to roll — log unchanged)")
        return 0

    archive_dir.mkdir(parents=True, exist_ok=True)
    final_arch = dict(arch_entries)
    for m, es in by_month.items():
        final_arch[m] = dedup_sorted(arch_entries.get(m, []) + es)
        (archive_dir / f"{m}.md").write_text(
            f"# Log archive — {m}\n\nArchived entries for {m}. "
            f"Active log: [../log.md](../log.md) · index: [../index.md](../index.md).\n\n"
            + "".join(final_arch[m]),
            encoding="utf-8",
        )

    months = sorted(
        {fn.name[:7] for fn in archive_dir.iterdir() if ARCHIVE_FN.match(fn.name)}
    )
    idx_line = (
        f"{ARCHIVES_LINE_PREFIX} older entries live in monthly files — "
        + " · ".join(f"[{m}]({archive_dir.name}/{m}.md)" for m in months)
        + f". Roll with scripts/roll-log when this grows.\n"
    )
    log_path.write_text(
        title_block(intro) + "\n\n" + idx_line + "\n---\n\n"
        + "".join(dedup_keep_order(keep)),
        encoding="utf-8",
    )

    # Conservation check: no entry may be lost.
    after = {e.strip() for e in split_entries(log_path.read_text(encoding="utf-8"))[1]}
    for fn in archive_dir.iterdir():
        if ARCHIVE_FN.match(fn.name):
            after |= {
                e.strip()
                for e in split_entries(fn.read_text(encoding="utf-8"))[1]
            }
    if before != after:
        lost = before - after
        first = next(iter(lost))[:120] if lost else "(none — unexpected extra)"
        print(
            f"roll-log: CONSERVATION FAILED — {len(lost)} entr(y/ies) lost; "
            f"ABORTING (files already written — restore from git). First: {first}",
            file=sys.stderr,
        )
        return 1
    print(
        f"roll-log: done — {len(after)} entries conserved across "
        f"{log_path.name} + {len(months)} archive(s)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(cli_main())
