#!/usr/bin/env python3
"""One-screen knowledge-base status for the start of an agent session.

WHY (2026-09-21): nothing from knowledge/ was loaded at session start, the
periodic drift sweep had no trigger ("per sprint or month" in prose only —
five articles untouched since April, check-dates findings up from 13 to 22),
and every session re-derived the read/write procedure from CLAUDE.md. This
prints ~25 lines — the entry points, the write gesture, and the head of each
worklist — via the SessionStart hook in .claude/settings.json. Read-only.
"""

from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

import bootstrap
import build_index
import check_dates
import check_handbook
import kb_paths
import facts_overlap
import roll_log
import sweep_report


def cli_main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="One-screen KB status (SessionStart hook).")
    ap.add_argument("--knowledge-dir", default="knowledge")
    args = ap.parse_args(argv)
    root = Path(args.knowledge_dir)
    if not root.is_dir():
        print(f"kb-status: no knowledge dir at {root}", file=sys.stderr)
        return 1
    today = dt.date.today()
    kd = str(root)

    articles = build_index.all_articles(root)
    areas = {a.relative_to(root).parts[1] if a.relative_to(root).parts[0] == "concepts" else a.relative_to(root).parts[0]
             for a in articles}
    print(f"KB status {today} — {len(articles)} articles in {len(areas)} areas.")
    print(f"  read : {root}/_index.md → follow the directory table (each dir has an _index.md) → ONE article · "
          f"needles: grep {root}/facts/ · trust by provenance tag (code: → open the code)")
    print(f"  write: article (+ ## Facts · ## Decisions · ## In plain terms), then ONE file "
          f"{root}/log/entries/{today}-<slug>.md starting `## {today} — <title>` (~150 words); "
          f"hook regenerates manifest/facts/guide")

    missing = bootstrap.check(kb_paths.knowledge_repo(), kb_paths.product_repos(), Path.home())
    if missing:
        print(f"  ⚠ enforcement: {len(missing)} piece(s) not installed — " + "; ".join(missing) + "  → scripts/bootstrap")
    else:
        parts = ["gate hook"] + (["trailer hooks", "session status"] if kb_paths.product_repos() else []) \
            + (["/kb skill"] if (kb_paths.skill_dir() / "SKILL.md").is_file() else [])
        print("  enforcement: " + " · ".join(parts) + " installed")

    rows, _ = sweep_report.collect(kd, None)
    stale = [r for r in rows if (today - dt.date.fromisoformat(r["updated"])).days > 120]
    print(f"\n  stalest ({len(stale)} older than 120 days):")
    for r in rows[:3]:
        print(f"    {r['updated']}  {Path(r['path']).relative_to(root)}")

    findings = check_dates.scan(kd, today)
    print(f"  stale dates: {len(findings)} past date(s) still framed as future  → scripts/check-dates")

    hb = check_handbook.check(Path(kd))
    hb_pages = len(check_handbook.pages(Path(kd)))
    hb_stale = sorted({f["page"] for f in hb if f["code"] == "stale"})
    hb_err = sum(1 for f in hb if f["severity"] == "error")
    print(f"  handbook: {hb_pages} page(s), {len(hb_stale)} behind their sources"
          + (f", {hb_err} with bad sources" if hb_err else "")
          + (f" — {', '.join(hb_stale[:3])}  → scripts/check-handbook" if hb_stale or hb_err else ""))

    fo = facts_overlap.collect(kd)
    th = sum(r["hi"] for r in fo); tm = sum(r["mid"] for r in fo)
    top = fo[0] if fo else None
    print(f"  facts↔prose: {th} near-verbatim / {tm} restating"
          + (f"; top {Path(top['path']).relative_to(root)} ({top['hi']}/{top['mid']})" if top else "")
          + "  → sweep-report --facts-overlap")

    size = sweep_report.size_rows(kd)
    big = [r for r in size if r["words"] > sweep_report.SIZE_WORDS]
    nofacts = [r for r in size if not r["facts"]]
    late = [r for r in size if r["facts"] and r["facts_pos"] is not None and r["facts_pos"] > sweep_report.FACTS_LATE]
    print(f"  size: {len(big)} articles over {sweep_report.SIZE_WORDS} words, {len(nofacts)} without ## Facts, "
          f"{len(late)} with Facts in the bottom half"
          + (f"; largest {Path(size[0]['path']).relative_to(root)} ({size[0]['words']}w)" if size else "")
          + "  → sweep-report --size")

    try:
        entries = roll_log.load_entries(root)
    except ValueError as exc:
        entries = []
        print(f"  ⚠ log entries: {exc}")
    cutoff = (today - dt.timedelta(days=roll_log.KEEP_DAYS)).isoformat()
    due = sum(1 for d, _, _ in entries if d < cutoff)
    long = len(roll_log.long_entries(root)) if entries else 0
    print(f"\n  log: {len(entries)} active entries" + (f", {due} past the {roll_log.KEEP_DAYS}-day window → scripts/roll-log" if due else "")
          + (f", {long} over {roll_log.LONG_WORDS} words → roll-log --long" if long else "") + ". Latest:")
    for _, name, text in entries[:3]:
        print(f"    {text.splitlines()[0][3:][:110]}")
    return 0


if __name__ == "__main__":
    sys.exit(cli_main())
