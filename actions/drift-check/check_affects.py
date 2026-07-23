#!/usr/bin/env python3
"""Lint every article's `affects:` entries — the mapping-hygiene checker.

Motivation (field-driven, 2026-07-22): the first commit-gate run on a mature
adoption was blocked twice by four latent `affects:` bugs that had sat
silently for months — a too-broad glob claiming another repo's file, free
text inside `affects:` (which fed drift-check's keyword fallback and matched
"data" against "datadog"), a meta-article claiming five whole
`knowledge/**` trees, and a bare filename that wasn't a glob at all. Every
one is detectable by string/path comparison — a script's job.

Checks, per entry (entries starting with `external:` are the documented
cross-repo convention — documentation-only, exempt from matching and from
these checks except basic shape):

  ERROR free-text      entry contains whitespace — not a glob; historically
                       keyword-fallback bait, now inert but still wrong
  ERROR article-tree   glob targets `knowledge/**` — articles claiming
                       article trees turns every article edit in the area
                       into a drift violation; drift-check maps CODE→article
  WARN  bare-literal   no `/` and no `*` — matches at most one root-level
                       file; usually a missing `**/` prefix
  WARN  dead-glob      matches no file in this repo nor in any
                       `--source-root` (liveness is only judged when the
                       glob COULD match locally, or when roots are given —
                       cross-repo globs are skipped otherwise)

Usage:
    check-affects                                  # structural checks
    check-affects --source-root ~/src/ProductRepo  # + liveness (repeatable)
    check-affects --strict                         # warnings also exit 1
    check-affects --json

Exit 1 on any ERROR (or any finding with --strict); 0 otherwise.

Uses validate_articles.parse_frontmatter and drift_check._glob_to_regex —
hence co-located.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from validate_articles import parse_frontmatter
from drift_check import _glob_to_regex


def _all_paths(root: Path, prefix: str = "") -> list[str]:
    out = []
    for p in root.rglob("*"):
        if p.is_file() and ".git" not in p.parts:
            rel = p.relative_to(root).as_posix()
            out.append(prefix + rel)
    return out


def lint(knowledge_dir: str, source_roots: list[str]) -> list[dict]:
    knowledge = Path(knowledge_dir)
    findings: list[dict] = []
    if not knowledge.is_dir():
        return [{"article": "", "entry": "", "kind": "fatal",
                 "detail": f"knowledge dir not found: {knowledge_dir}"}]

    # Candidate path corpora for liveness: this repo, plus each source root
    # (paths offered both bare-relative and basename-prefixed so globs like
    # "ProductRepo/**/x.yml" can match a root named ProductRepo).
    local_paths = _all_paths(Path("."))
    corpora: list[list[str]] = [local_paths]
    for sr in source_roots:
        rp = Path(sr).expanduser()
        if not rp.is_dir():
            findings.append({"article": "", "entry": sr, "kind": "fatal",
                             "detail": f"--source-root not found: {sr}"})
            continue
        paths = _all_paths(rp)
        corpora.append(paths + [f"{rp.name}/{p}" for p in paths])

    for article in sorted(knowledge.rglob("*.md")):
        rel_parts = article.relative_to(knowledge).parts
        if article.name in ("index.md", "log.md") or rel_parts[0] in ("log", "facts"):
            continue
        fm = parse_frontmatter(article)
        if not fm:
            continue
        for entry in fm.get("affects", []) or []:
            if not isinstance(entry, str):
                continue
            if entry.startswith("external:"):
                continue  # documented cross-repo convention; never matched
            e = entry.strip().strip("`").strip("'\"")
            if re.search(r"\s", e):
                findings.append({"article": str(article), "entry": entry,
                                 "kind": "free-text",
                                 "detail": "contains whitespace — not a glob; "
                                           "make it a real glob or prefix `external:`"})
                continue
            norm = e.lstrip("/")
            if norm.startswith(f"{knowledge_dir}/") or norm.startswith("knowledge/"):
                findings.append({"article": str(article), "entry": entry,
                                 "kind": "article-tree",
                                 "detail": "claims the knowledge tree — drift-check "
                                           "maps CODE paths to articles; remove or "
                                           "point at code"})
                continue
            regex = _glob_to_regex(e)
            alive = any(
                any(re.match(regex, p) for p in corpus) for corpus in corpora
            )
            if alive:
                continue
            if "/" not in e and "*" not in e:
                # A live bare literal (e.g. 'CLAUDE.md' matching the root
                # file) is intended and stays silent; a DEAD one is the bug
                # (usually a missing '**/' prefix).
                findings.append({"article": str(article), "entry": entry,
                                 "kind": "bare-literal",
                                 "detail": "bare filename matching nothing — "
                                           "likely missing '**/' prefix"})
                continue
            # Dead glob: only meaningful when roots were given, OR the glob
            # is plainly local-shaped (starts with a dir that exists here).
            first_seg = norm.split("/", 1)[0]
            local_shaped = first_seg not in ("**",) and Path(first_seg).exists()
            if source_roots or local_shaped:
                findings.append({"article": str(article), "entry": entry,
                                 "kind": "dead-glob",
                                 "detail": "matches no file in this repo"
                                           + (" or any --source-root" if source_roots else "")})
    return findings


ERROR_KINDS = {"free-text", "article-tree", "fatal"}


def cli_main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Lint articles' affects: entries (mapping hygiene)."
    )
    ap.add_argument("--knowledge-dir", default="knowledge")
    ap.add_argument("--source-root", action="append", default=[],
                    help="external code root for glob-liveness checks (repeatable)")
    ap.add_argument("--strict", action="store_true",
                    help="warnings (bare-literal, dead-glob) also fail")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    findings = lint(args.knowledge_dir, args.source_root)
    errors = [f for f in findings if f["kind"] in ERROR_KINDS]
    warnings = [f for f in findings if f["kind"] not in ERROR_KINDS]

    if args.json:
        print(json.dumps({"errors": errors, "warnings": warnings}, indent=2))
        return 1 if errors or (args.strict and warnings) else 0

    for f in errors:
        print(f"ERROR [{f['kind']}] {f['article']}: {f['entry']!r} — {f['detail']}")
    for f in warnings:
        print(f"warn  [{f['kind']}] {f['article']}: {f['entry']!r} — {f['detail']}")
    if not findings:
        print("✅ check-affects: all affects entries are hygienic.")
        return 0
    print(f"{'❌' if errors else '⚠️'} check-affects: "
          f"{len(errors)} error(s), {len(warnings)} warning(s).")
    return 1 if errors or (args.strict and warnings) else 0


if __name__ == "__main__":
    sys.exit(cli_main())
