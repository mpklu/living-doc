#!/usr/bin/env python3
"""Provenance report — make claim-provenance tags actionable.

Companion to concepts/methodology/claim-provenance.md. Claims in articles
carry inline tags — *(code: path:line)* · *(bench: date)* ·
*(field: incident)* · *(reported: who)* · *(inferred)* — grading how each
claim was verified. This tool is what keeps the tags from rotting into
decoration:

  provenance-report               # per-article tag counts + coverage
  provenance-report --worklist    # every inferred/reported claim in a
                                  # load_bearing article — the input for
                                  # the next verification pass
  provenance-report --json        # machine-readable

Coverage view flags load_bearing articles with ZERO provenance tags —
their claims are ungraded, so a reader can't calibrate trust. Worklist
view lists file:line + snippet for each `inferred`/`reported` tag that
is NOT corroborated — a parenthetical that also carries a
code/bench/field provenance (the combined form a verification sweep
produces, e.g. `*(reported: vendor; code: Foo.m:12)*`) is a verified
claim and is suppressed from the worklist (its keywords still count in
the coverage view). Code fences, inline code, and frontmatter are
excluded from scanning.

Uses validate_articles.parse_frontmatter (the shared hand-parser) —
hence co-located.
"""

from __future__ import annotations

import argparse
import os
import json
import re
import sys
from pathlib import Path

from validate_articles import parse_frontmatter

# A provenance parenthetical: *(kw: evidence)* — possibly multi-provenance,
# segments separated by ';', e.g. *(reported: vendor; code: Foo.m:12)*.
PAREN_RE = re.compile(
    r"\*\(((?:code|bench|field|reported|inferred)[^)]*)\)\*"
)
# Keywords inside a parenthetical: at the start, or right after a ';'.
# Anchoring keeps evidence text from matching (the word "code" inside
# "*(reported: error code list)*" is NOT a keyword). Evidence-bearing
# keywords (code/bench/field/reported) must be followed by ':' — that's
# the convention, and it rejects prose look-alikes such as
# "**(code × feeschedule)**" (found in the wild). Only `inferred` may be
# bare (`*(inferred)*`) or space-continued (`*(inferred from X)*`).
SEGMENT_KW_RE = re.compile(
    r"(?:^|;\s*)(?:(code|bench|field|reported)(?=\s*:)"
    r"|(inferred)(?=[:;\s)]|$))"
)
FENCE_RE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE_RE = re.compile(r"`[^`]*`")
KINDS = ("code", "bench", "field", "reported", "inferred")
WORKLIST_KINDS = ("inferred", "reported")
CORROBORATING = ("code", "bench", "field")


def masked_lines(text: str) -> list[str]:
    """Body lines with code fences, inline code, AND the frontmatter block
    blanked (frontmatter mentions of tag syntax aren't claims); line count
    preserved so reported line numbers stay true."""
    lines = text.splitlines()
    out: list[str] = []
    i = 0
    if lines and lines[0].strip() == "---":  # skip frontmatter
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
        out.append("" if in_fence else INLINE_CODE_RE.sub("", line))
    return out


CODE_CITE_RE = re.compile(r"\*\(\s*(?:[^)]*;\s*)?code\s*:\s*([^;)]*)")
FILE_TOKEN_RE = re.compile(
    r"([A-Za-z0-9_./+\- ]*?[A-Za-z0-9_+\-]+\.(?:swift|m|mm|h|rb|py|sh|js|ts|json|plist|yml|yaml|sql|go|c|cpp|xml|entitlements|txt|md))"
)


def code_cites(text: str) -> list[tuple[int, str]]:
    """(line, file-token) for every *(code: …)* segment that names a file; bare *(code)* skipped."""
    out: list[tuple[int, str]] = []
    in_fence = False
    for lineno, line in enumerate(text.splitlines(), start=1):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for m in CODE_CITE_RE.finditer(line):
            ev = m.group(1).replace("`", " ")
            for t in FILE_TOKEN_RE.findall(ev):
                out.append((lineno, t.strip().lstrip("./")))
    return out


def liveness(knowledge_dir: str, source_roots: list[str]) -> dict:
    """Which code: cites still name a file under the source roots (basename or path-suffix match).
    Line numbers are not checked — they rot by design; the file existing is the cheap signal."""
    index: dict[str, set[str]] = {}
    for root in source_roots:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules", ".build", "DerivedData")]
            for f in filenames:
                index.setdefault(f, set()).add(os.path.join(dirpath, f).replace("\\", "/"))
    total = live = 0
    dead: list[tuple[str, int, str]] = []
    root = Path(knowledge_dir)
    for path in sorted(root.rglob("*.md")):
        if path.relative_to(root).parts[0] in ("log", "facts", "manifest", "guide") or path.name == "_index.md":
            continue
        if parse_frontmatter(path) is None:
            continue
        for lineno, tok in code_cites(path.read_text(encoding="utf-8")):
            total += 1
            base = os.path.basename(tok)
            cands = index.get(base, set())
            ok = bool(cands) and ("/" not in tok or any(c.endswith("/" + tok) or c.endswith(tok) for c in cands))
            if ok:
                live += 1
            else:
                dead.append((str(path), lineno, tok))
    return {"total": total, "live": live, "dead": dead}


def scan(knowledge_dir: str) -> list[dict]:
    root = Path(knowledge_dir)
    articles: list[dict] = []
    for path in sorted(root.rglob("*.md")):
        if path.name in ("index.md", "log.md", "manifest.md", "areas.md", "scopes.md", "_index.md"):
            continue
        if path.relative_to(root).parts[0] in ("log", "facts", "manifest", "guide"):
            continue
        fm = parse_frontmatter(path)
        if fm is None:
            continue  # not an article (e.g. log archives)
        counts = {k: 0 for k in KINDS}
        hits: list[dict] = []
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for lineno, line in enumerate(masked_lines(text), start=1):
            for pm in PAREN_RE.finditer(line):
                kws = [
                    m.group(1) or m.group(2)
                    for m in SEGMENT_KW_RE.finditer(pm.group(1))
                ]
                for kind in kws:
                    counts[kind] += 1
                # Corroborated-claim suppression: a parenthetical that ALSO
                # carries a code/bench/field provenance (the combined form,
                # e.g. *(reported: vendor; code: Foo.m:12)*) is a VERIFIED
                # claim — its reported/inferred segments don't belong on the
                # to-verify worklist. Learned on the first real sweep: the
                # sanctioned upgrade path appends code: alongside reported:,
                # and without this rule the worklist never shrinks.
                if any(k in CORROBORATING for k in kws):
                    continue
                for kind in kws:
                    if kind in WORKLIST_KINDS:
                        hits.append(
                            {
                                "line": lineno,
                                "kind": kind,
                                "snippet": line.strip()[:160],
                            }
                        )
        articles.append(
            {
                "path": str(path),
                "load_bearing": bool(fm.get("load_bearing", False)),
                "status": str(fm.get("status", "")),
                "counts": counts,
                "total": sum(counts.values()),
                "worklist": hits,
            }
        )
    return articles


def cli_main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Report claim-provenance tag coverage / verification worklist."
    )
    ap.add_argument("--knowledge-dir", default="knowledge")
    ap.add_argument("--worklist", action="store_true",
                    help="list inferred/reported claims in load_bearing articles")
    ap.add_argument("--all", action="store_true",
                    help="with --worklist: include non-load_bearing articles too")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--source-root", action="append", default=[],
                    help="with one or more roots: report *(code: path)* cites whose file no longer exists (warn-only)")
    args = ap.parse_args(argv)
    if args.source_root:
        res = liveness(args.knowledge_dir, args.source_root)
        print(f"code-cite liveness — {res['total']} file-naming code: cites, {res['live']} resolve under "
              f"{len(args.source_root)} root(s), {len(res['dead'])} do not:")
        for p, ln, tok in res["dead"][: 60]:
            print(f"  {p}:{ln}: {tok}")
        if len(res["dead"]) > 60:
            print(f"  … {len(res['dead']) - 60} more")
        print("  → on touch: re-point the cite (the file moved) or downgrade the claim; warn-only.")
        return 0

    if not Path(args.knowledge_dir).is_dir():
        print(f"provenance-report: knowledge dir not found: {args.knowledge_dir}",
              file=sys.stderr)
        return 1
    articles = scan(args.knowledge_dir)

    if args.json:
        print(json.dumps({"articles": articles}, indent=2))
        return 0

    if args.worklist:
        rows = [
            (a, h)
            for a in articles
            if (a["load_bearing"] or args.all)
            for h in a["worklist"]
        ]
        if not rows:
            scope = "any article" if args.all else "load_bearing articles"
            print(f"provenance-report: no inferred/reported claims tagged in {scope}.")
            return 0
        print(f"Verification worklist — {len(rows)} claim(s) to verify or refute:")
        for a, h in rows:
            print(f"  {a['path']}:{h['line']}: ({h['kind']}) {h['snippet']}")
        return 0

    tagged = [a for a in articles if a["total"]]
    lb_untagged = [a for a in articles if a["load_bearing"] and not a["total"]]
    print(
        f"Provenance coverage — {len(tagged)}/{len(articles)} article(s) carry tags."
    )
    for a in tagged:
        parts = ", ".join(f"{k}:{v}" for k, v in a["counts"].items() if v)
        print(f"  {a['path']} — {parts}")
    if lb_untagged:
        print(f"\n⚠ load_bearing articles with NO provenance tags ({len(lb_untagged)}) —")
        print("  their claims are ungraded (readers can't calibrate trust):")
        for a in lb_untagged:
            print(f"  {a['path']} [{a['status']}]")
    return 0


if __name__ == "__main__":
    sys.exit(cli_main())
