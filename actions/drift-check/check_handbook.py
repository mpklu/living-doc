#!/usr/bin/env python3
"""Handbook freshness check — a current-state page must not fall behind its sources.

THE LAYER THIS GUARDS. `knowledge/concepts/` is the source of truth and the
record: decisions, dated evidence, provenance tags, corrections. A reader who
only wants *what is true now* has to read through that history. The handbook
(`knowledge/handbook/`) answers that reader: one page per subject, current state
only, prose for developers and non-developers alike. It is a SYNTHESIS — every
claim on a page also lives in a concept article, which the page lists in its
frontmatter `sources:` and links to for the why. One home per fact stays true.

A second layer goes stale quietly: nobody edits it when the code changes, only
the article the code touched. So the coupling is made checkable:

  ERROR  no-sources    a handbook page with no `sources:` list — it cannot be
                       checked, and has nothing to defer to
  ERROR  dead-source   a `sources:` entry that names no file under knowledge/
  WARN   stale         a source's `updated:` is later than the page's own
                       `updated:` — the source changed since the page was
                       last read against it

`sources:` entries are paths relative to knowledge/ (`concepts/fhir/x.md`).
Sources in another repository go in `external_sources:` (free text, not
checked) — the check cannot see them, which is why the field is separate.

Stale is a WARNING by design (exit 0) unless --strict: the fix is a read, and
often the page is still right. Unlike check-dates it IS gate-worthy — a stale
page is caused by a commit (someone updated a source), not by the calendar —
so the commit gate prints it without blocking. Bump the page's `updated:` once
it has been re-read, even if nothing on it changed.

Usage:
    check-handbook               # human report; exit 1 on errors only
    check-handbook --strict      # stale pages also exit 1
    check-handbook --json

Uses validate_articles.parse_frontmatter — hence co-located.
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path

from validate_articles import parse_frontmatter

HANDBOOK_DIR = "handbook"
INDEX_NAME = "_index.md"


def _date(value: object) -> datetime.date | None:
    if isinstance(value, datetime.date):
        return value
    try:
        return datetime.date.fromisoformat(str(value).strip())
    except ValueError:
        return None


def _as_list(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value.strip() else []
    return [str(v) for v in value if str(v).strip()]


def pages(knowledge_root: Path) -> list[Path]:
    base = knowledge_root / HANDBOOK_DIR
    if not base.is_dir():
        return []
    return sorted(p for p in base.rglob("*.md") if p.name != INDEX_NAME)


def check(knowledge_root: Path) -> list[dict]:
    """One finding per problem: {severity, code, page, source?, detail}."""
    findings: list[dict] = []
    for page in pages(knowledge_root):
        rel = page.relative_to(knowledge_root).as_posix()
        fm = parse_frontmatter(page) or {}
        sources = _as_list(fm.get("sources"))
        page_updated = _date(fm.get("updated"))
        if not sources:
            findings.append({"severity": "error", "code": "no-sources", "page": rel,
                             "detail": "no `sources:` — list the concept articles this page synthesises"})
            continue
        for src in sources:
            path = knowledge_root / src.strip().lstrip("/")
            if not path.is_file():
                findings.append({"severity": "error", "code": "dead-source", "page": rel, "source": src,
                                 "detail": f"`{src}` names no file under knowledge/"})
                continue
            src_updated = _date((parse_frontmatter(path) or {}).get("updated"))
            if page_updated and src_updated and src_updated > page_updated:
                findings.append({"severity": "warn", "code": "stale", "page": rel, "source": src,
                                 "detail": f"`{src}` updated {src_updated}, after this page ({page_updated}) — "
                                           f"re-read the page against it, then bump `updated:`"})
    return findings


def cli_main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="check-handbook", description=__doc__.split("\n\n")[0])
    ap.add_argument("--knowledge-dir", default="knowledge")
    ap.add_argument("--strict", action="store_true", help="stale pages also exit 1")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    root = Path(args.knowledge_dir)
    findings = check(root)
    errors = [f for f in findings if f["severity"] == "error"]
    stale = [f for f in findings if f["code"] == "stale"]

    if args.json:
        print(json.dumps({"pages": len(pages(root)), "findings": findings}, indent=2))
    else:
        n = len(pages(root))
        if not findings:
            print(f"✅ check-handbook: {n} page(s), all within their sources.")
        for f in findings:
            mark = "❌" if f["severity"] == "error" else "⚠"
            print(f"{mark} {f['page']}: [{f['code']}] {f['detail']}")
        if findings:
            print(f"check-handbook: {n} page(s) — {len(errors)} error(s), {len(stale)} stale")

    if errors or (args.strict and stale):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(cli_main())
