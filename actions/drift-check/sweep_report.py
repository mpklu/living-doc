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
    sweep-report --facts-overlap     # second worklist: articles whose ## Facts bullets restate prose
    sweep-report --plain-terms       # Support candidates: articles with *(field:…)* tags but no ## In plain terms
    sweep-report --size              # third worklist: biggest articles; >4000 words = split/compress candidate, no ## Facts flagged
    sweep-report --facts-overlap --pairs knowledge/concepts/cda/cda-playbook.md   # the pairs, to compress on touch

Uses validate_articles.parse_frontmatter (the shared hand-parser) —
hence co-located. Articles without parseable frontmatter are listed
last with a warning (they can't be sweep-ordered).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import facts_overlap
from validate_articles import parse_frontmatter


def collect(knowledge_dir: str, area: str | None) -> tuple[list[dict], list[str]]:
    root = Path(knowledge_dir)
    rows: list[dict] = []
    unparsed: list[str] = []
    for path in sorted(root.rglob("*.md")):
        if path.name in ("index.md", "log.md", "manifest.md", "areas.md", "scopes.md", "_index.md"):
            continue
        rel_parts = path.relative_to(root).parts
        # Non-article surfaces: log archives (append-only narrative) and
        # generated facts files — neither is sweep-orderable.
        if rel_parts[0] in ("log", "facts", "manifest", "guide"):
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


SIZE_WORDS = 4000
FACTS_LATE = 0.5   # `## Facts` starting past this fraction of the body = a partial read misses it


def size_rows(knowledge_dir: str) -> list[dict]:
    """Every article: words (body only), has ## Facts, load_bearing — largest first.
    Why: the median article grew to 2.3k words and the top decile past 5k; the
    what-cache/why-asset rule had no lint behind it, and only a third of articles
    feed facts/. Ranked, not gated — the editor decides split vs. compress."""
    root = Path(knowledge_dir)
    rows: list[dict] = []
    for sub in ("concepts", "connections"):
        base = root / sub
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*.md")):
            fm = parse_frontmatter(path)
            if not fm:
                continue
            text = path.read_text(encoding="utf-8")
            if text.startswith("---"):
                end = text.find("\n---", 3)
                if end != -1:
                    text = text[end + 4:]
            lines = text.splitlines()
            fpos = next((i for i, l in enumerate(lines) if l.startswith("## Facts")), None)
            rows.append({
                "path": str(path),
                "words": len(text.split()),
                "facts": fpos is not None,
                "facts_pos": (fpos / max(len(lines), 1)) if fpos is not None else None,
                "load_bearing": bool(fm.get("load_bearing")),
            })
    rows.sort(key=lambda r: (-r["words"], r["path"]))
    return rows


FIELD_TAG_RE = re.compile(r"\*\(field:")


def plain_terms_rows(knowledge_dir: str) -> list[dict]:
    """Articles carrying incident-derived claims (field: tags) with no ## In plain terms
    section — what Support would need first, said in their language. Most field tags first."""
    root = Path(knowledge_dir)
    rows: list[dict] = []
    for sub in ("concepts", "connections"):
        base = root / sub
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*.md")):
            if path.name == "_index.md" or not parse_frontmatter(path):
                continue
            text = path.read_text(encoding="utf-8")
            n = len(FIELD_TAG_RE.findall(text))
            if n and "\n## In plain terms" not in text:
                rows.append({"path": str(path), "field_tags": n})
    rows.sort(key=lambda r: (-r["field_tags"], r["path"]))
    return rows


def plain_terms_report(args) -> int:
    rows = plain_terms_rows(args.knowledge_dir)
    picked = rows[: args.limit] if args.limit > 0 else rows
    if args.json:
        print(json.dumps(picked, indent=2))
        return 0
    print(f"Plain-terms candidates — {len(rows)} article(s) carry *(field:…)* claims and no ## In plain terms. Top {len(picked)}:")
    for r in picked:
        print(f"  field-tags={r['field_tags']:<3} {r['path']}")
    print("  → on touch: add `## In plain terms` (no identifiers, no tags) — build-facts renders it to guide/<area>.md.")
    return 0


def size_report(args) -> int:
    rows = size_rows(args.knowledge_dir)
    picked = rows[: args.limit] if args.limit > 0 else rows
    if args.json:
        print(json.dumps(picked, indent=2))
        return 0
    big = sum(1 for r in rows if r["words"] > SIZE_WORDS)
    nofacts = sum(1 for r in rows if not r["facts"])
    print(f"Size / Facts-coverage worklist — {len(rows)} articles: {big} over {SIZE_WORDS} words, "
          f"{nofacts} without a ## Facts section. Largest {len(picked)}:")
    for r in picked:
        flags = []
        if r["words"] > SIZE_WORDS:
            flags.append("SPLIT/COMPRESS?")
        if not r["facts"]:
            flags.append("no-Facts")
        elif r["facts_pos"] is not None and r["facts_pos"] > FACTS_LATE:
            flags.append(f"Facts-at-{int(r['facts_pos'] * 100)}%")
        if r["load_bearing"]:
            flags.append("load-bearing")
        print(f"  {r['words']:>6}w  {r['path']}  {' '.join(flags)}")
    print("  → over the line: split by seam, or shrink cache prose into ## Facts and keep the why; "
          "move ## Facts near the top so a partial read still yields the lookup facts.")
    return 0


def facts_overlap_report(args) -> int:
    if args.pairs:
        r = facts_overlap.article_overlap(Path(args.pairs))
        if r is None:
            print(f"sweep-report: {args.pairs} has no ## Facts section (or is unreadable).")
            return 1
        if args.json:
            print(json.dumps(r, indent=2))
            return 0
        print(f"Facts↔prose pairs — {args.pairs}: {r['bullets']} bullets, "
              f"{r['hi']} near-verbatim (≥{facts_overlap.HI:.0%}), {r['mid']} restating (≥{facts_overlap.MID:.0%}).")
        print("Compress the prose to its why where the bullet already holds the what; "
              "operator tables (playbook Part 1, runbooks) may keep the mirror.\n")
        for score, bullet, sent in r["pairs"]:
            print(f"[{score:.0%}] FACT : {bullet[:220]}")
            print(f"       PROSE: {sent[:220]}\n")
        return 0
    rows = facts_overlap.collect(args.knowledge_dir)
    picked = [r for r in rows if r["hi"] or r["mid"]]
    picked = picked[: args.limit] if args.limit > 0 else picked
    if args.json:
        print(json.dumps([{k: v for k, v in r.items() if k != "pairs"} for r in picked], indent=2))
        return 0
    tb = sum(r["bullets"] for r in rows); th = sum(r["hi"] for r in rows); tm = sum(r["mid"] for r in rows)
    print(f"Facts↔prose overlap worklist — {len(rows)} article(s) with ## Facts, {tb} bullets: "
          f"{th} near-verbatim, {tm} restating. Top {len(picked)}:")
    for r in picked:
        print(f"  hi={r['hi']:<2} mid={r['mid']:<2} of {r['bullets']:<3} {r['path']}")
    print("  → sweep-report --facts-overlap --pairs <article>  shows what to compress; apply on touch.")
    return 0


def cli_main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="List the oldest knowledge articles by updated: date."
    )
    ap.add_argument("--knowledge-dir", default="knowledge")
    ap.add_argument("--limit", type=int, default=5)
    ap.add_argument("--area", default=None)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--facts-overlap", action="store_true",
                    help="rank articles by ## Facts bullets that restate their own prose "
                         "(what-cache/why-asset compression worklist)")
    ap.add_argument("--plain-terms", action="store_true",
                    help="articles with *(field:…)* claims but no ## In plain terms section")
    ap.add_argument("--size", action="store_true",
                    help="rank articles by body word count; flag >%d words and missing ## Facts" % SIZE_WORDS)
    ap.add_argument("--pairs", default=None, metavar="ARTICLE",
                    help="with --facts-overlap: print that article's bullet↔sentence pairs")
    args = ap.parse_args(argv)

    if not Path(args.knowledge_dir).is_dir():
        print(f"sweep-report: knowledge dir not found: {args.knowledge_dir}",
              file=sys.stderr)
        return 1

    if args.facts_overlap:
        return facts_overlap_report(args)
    if args.size:
        return size_report(args)
    if args.plain_terms:
        return plain_terms_report(args)

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
