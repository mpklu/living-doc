#!/usr/bin/env python3
"""Stale-date flagger — find time-bombed prose: past dates still framed
as future.

THE FIELD INCIDENT THIS GENERALIZES: a hard vendor retirement date
(2026-06-30) sat in FUTURE tense across 4+ articles for three weeks
after it passed — "retires ITRANS 1 on 2026-06-30", "before 6/30",
"must be on ICD by then" — until a manual gap review caught it. Tense
is semantics, but *past-date-near-future-marker* is a string/date
comparison: a script's job.

Per knowledge article (code fences, inline code, frontmatter, and
claim-provenance parentheticals masked — tag dates are historical by
nature):

  * find date tokens: ISO `YYYY-MM-DD` and month-year forms
    ("Aug 2026", "August 2026", "~end Aug 2026" → resolved to month end)
  * a PAST date co-occurring on a line with a FUTURE-TENSE MARKER
    (will / expected / planned / upcoming / deadline / due / retires /
    retiring / ships / shipping / scheduled / ETA / by then / pre- /
    before …) is flagged with file:line + snippet.

Heuristic by design → WARNINGS (exit 0) unless --strict. Deliberately
NOT a commit-gate check: findings appear because *time passed*, not
because of the commit at hand — a gate that fails on unrelated commits
teaches people to bypass it. Right homes: the periodic drift sweep, and
CI as a non-blocking job.

Usage:
    check-dates                       # scan with today's date
    check-dates --today 2026-09-15    # time-travel (testing / previews:
                                      # "what becomes stale by then?")
    check-dates --strict              # findings exit 1
    check-dates --json

Known limitations: same-line co-occurrence only; non-ISO short forms
("6/30") are not parsed (ambiguous); month-only forms resolve to the
month's last day (a date is "past" only when the whole month is).

Uses validate_articles.parse_frontmatter — hence co-located.
"""

from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
from pathlib import Path

from validate_articles import parse_frontmatter

ISO_DATE_RE = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")
MONTHS = {m.lower(): i + 1 for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
     "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])}
MONTH_YEAR_RE = re.compile(
    r"\b(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
    r"Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|"
    r"Dec(?:ember)?)\.?\s+(\d{4})\b"
)
FUTURE_MARKER_RE = re.compile(
    r"(?i)\b(will|expected|expects|upcoming|planned|plans to|deadline|due|"
    r"retires|retiring|ships|shipping|scheduled|eta|forthcoming|"
    r"by then|must \w+(?: \w+){0,3} by|before|pre-|not yet|to be \w+ed)\b"
)
FENCE_RE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE_RE = re.compile(r"`[^`]*`")
PROVENANCE_RE = re.compile(
    r"\*\((?:code|bench|field|reported|inferred)[^)]*\)\*"
)
LOG_HEADING_RE = re.compile(r"^##\s+\[?\d{4}-\d{2}")


def masked_lines(text: str) -> list[str]:
    """Lines with frontmatter, fences, inline code, provenance tags, and
    dated log-style headings blanked; count preserved."""
    lines = text.splitlines()
    out: list[str] = []
    i = 0
    if lines and lines[0].strip() == "---":
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
        if in_fence or LOG_HEADING_RE.match(line):
            out.append("")
            continue
        line = INLINE_CODE_RE.sub("", line)
        line = PROVENANCE_RE.sub("", line)
        out.append(line)
    return out


def dates_in(line: str) -> list[tuple[datetime.date, str]]:
    found: list[tuple[datetime.date, str]] = []
    for m in ISO_DATE_RE.finditer(line):
        try:
            found.append(
                (datetime.date(int(m.group(1)), int(m.group(2)),
                               int(m.group(3))), m.group(0))
            )
        except ValueError:
            continue
    for m in MONTH_YEAR_RE.finditer(line):
        mon = MONTHS[m.group(1)[:3].lower()]
        year = int(m.group(2))
        # resolve to the month's LAST day: only past once the month is over
        nxt = datetime.date(year + (mon == 12), (mon % 12) + 1, 1)
        found.append((nxt - datetime.timedelta(days=1), m.group(0)))
    return found


def scan(knowledge_dir: str, today: datetime.date) -> list[dict]:
    root = Path(knowledge_dir)
    findings: list[dict] = []
    for path in sorted(root.rglob("*.md")):
        rel_parts = path.relative_to(root).parts
        if path.name in ("index.md", "log.md") or rel_parts[0] in ("log", "facts"):
            continue
        if parse_frontmatter(path) is None:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for lineno, line in enumerate(masked_lines(text), start=1):
            marker = FUTURE_MARKER_RE.search(line)
            if not marker:
                continue
            for d, token in dates_in(line):
                if d < today:
                    findings.append({
                        "file": str(path),
                        "line": lineno,
                        "date": token,
                        "marker": marker.group(1),
                        "snippet": line.strip()[:160],
                    })
    return findings


def cli_main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Flag past dates still framed in future tense."
    )
    ap.add_argument("--knowledge-dir", default="knowledge")
    ap.add_argument("--today", default=None,
                    help="override today (YYYY-MM-DD) — testing / previews")
    ap.add_argument("--strict", action="store_true",
                    help="findings exit 1 (default: warn only)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    if args.today:
        try:
            today = datetime.date.fromisoformat(args.today)
        except ValueError:
            print(f"check-dates: bad --today '{args.today}'", file=sys.stderr)
            return 1
    else:
        today = datetime.date.today()

    if not Path(args.knowledge_dir).is_dir():
        print(f"check-dates: knowledge dir not found: {args.knowledge_dir}",
              file=sys.stderr)
        return 1
    findings = scan(args.knowledge_dir, today)

    if args.json:
        print(json.dumps({"today": today.isoformat(), "findings": findings},
                         indent=2))
        return 1 if (findings and args.strict) else 0

    if not findings:
        print(f"✅ check-dates: no time-bombed prose (as of {today}).")
        return 0
    for f in findings:
        print(f"{f['file']}:{f['line']}: [{f['marker']} … {f['date']}] "
              f"{f['snippet']}")
    print(f"⚠️  check-dates: {len(findings)} past date(s) still framed as "
          f"future (as of {today}) — re-tense or update the prose.")
    return 1 if args.strict else 0


if __name__ == "__main__":
    sys.exit(cli_main())
