#!/usr/bin/env python3
"""Generate one `_index.md` per content directory — the knowledge base's routing tree.

Rule (2026-09-21, Kun: "standardize the indexing/routing in a recursive /
hierarchical way so it allows deeper subfolders"): every directory under
knowledge/ that holds articles, directly or below, gets a generated
`_index.md` listing (a) its subdirectories — scope line, article count,
F/D coverage — and (b) its own articles, one row each. Routing is a walk:

    knowledge/_index.md → concepts/_index.md → concepts/macpractice/_index.md
                        → concepts/macpractice/dental/_index.md → the article

Each hop is small and sits next to what it indexes (`ls` shows it); a new
folder at any depth follows the same rule with no tool change. This replaced
`manifest.md` + `manifest/<area>.md`, which flattened the tree into one file
per area (a third level became a `###` inside a growing file) and kept a
second namespace that had to mirror the tree by hand.

Scope lines — the one curated input — live in `knowledge/scopes.md`, keyed
by directory path relative to knowledge/: `- **concepts/macpractice** — …`.
Every content directory except the root needs one; a missing line fails
`--check`. `_index.md` is used rather than `README.md` because
`concepts/cda/CDA_Digital_ID_Installer_Java/README.md` is an article.

Row: path (knowledge-relative, plain text — grep it, cat it) · title
(`title:` else H1) · status clipped at its first " — " · updated · F when a
`## Facts` section feeds facts/ · D<n> = bullets in `## Decisions` · up to
MANIFEST_AFFECTS_MAX `affects:` basenames.

Usage:
    build-index            # rewrite every _index.md (orphans removed)
    build-index --check    # exit 1 if any is stale/orphaned or a content dir lacks a scope line
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from validate_articles import parse_frontmatter

# handbook/ holds current-state pages synthesised from concepts/ (check_handbook.py keeps them fresh).
ARTICLE_ROOTS = ("concepts", "connections", "handbook")
SCOPES_FILE = "scopes.md"
INDEX_NAME = "_index.md"
SCOPE_LINE_RE = re.compile(r"^-\s+\*\*([^*]+)\*\*\s+[—–-]+\s+(.+?)\s*$")
MANIFEST_AFFECTS_MAX = 2
MANIFEST_STATUS_CHARS = 24
H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.M)
SENTINEL = "<!-- build-index:generated — edit article frontmatter (rows) or scopes.md (scope lines), not this file -->"


def _body(text: str) -> str:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4:]
    return text


def article_h1(article: Path) -> str | None:
    try:
        text = _body(article.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError):
        return None
    m = H1_RE.search(text)
    return m.group(1).strip() if m else None


def article_title(article: Path, fm: dict) -> str:
    return str(fm.get("title") or article_h1(article) or article.stem)


def section_body(text: str, heading: str) -> str | None:
    m = re.search(rf"^## {re.escape(heading)}\s*$(.*?)(?=^## |\Z)", _body(text), re.M | re.S)
    return m.group(1) if m else None


def has_facts_section(article: Path) -> bool:
    try:
        return section_body(article.read_text(encoding="utf-8"), "Facts") is not None
    except (OSError, UnicodeDecodeError):
        return False


def decisions_count(article: Path) -> int:
    try:
        body = section_body(article.read_text(encoding="utf-8"), "Decisions")
    except (OSError, UnicodeDecodeError):
        return 0
    return sum(1 for l in (body or "").splitlines() if l.lstrip().startswith("- "))


def all_articles(knowledge_root: Path) -> list[Path]:
    out: list[Path] = []
    for root in ARTICLE_ROOTS:
        base = knowledge_root / root
        if base.is_dir():
            out.extend(p for p in base.rglob("*.md") if p.name != INDEX_NAME and parse_frontmatter(p))
    return sorted(out)


def load_scopes(knowledge_root: Path) -> dict[str, str]:
    scopes: dict[str, str] = {}
    try:
        text = (knowledge_root / SCOPES_FILE).read_text(encoding="utf-8")
    except OSError:
        return scopes
    for line in text.splitlines():
        m = SCOPE_LINE_RE.match(line.strip())
        if m:
            scopes[m.group(1).strip().strip("/")] = m.group(2).strip()
    return scopes


def _cell(s: str) -> str:
    return s.replace("|", "\\|").replace("\n", " ")


def _short_status(status: object) -> str:
    s = str(status or "").strip().strip('"').strip("'")
    s = re.split(r"\s+[—–-]\s+|—", s, maxsplit=1)[0].strip()
    return s[:MANIFEST_STATUS_CHARS]


def _affects_summary(fm: dict) -> str:
    entries = [str(e) for e in (fm.get("affects") or []) if isinstance(e, str)]
    names: list[str] = []
    for e in entries:
        e = e.split(":", 1)[1] if e.startswith("external:") else e
        segs = [x for x in e.replace("\\", "/").split("/") if x and set(x) - set("*")]
        base = segs[-1] if segs else e
        if base and base not in names:
            names.append(base)
    shown = names[:MANIFEST_AFFECTS_MAX]
    extra = len(names) - len(shown)
    return ", ".join(shown) + (f", +{extra}" if extra > 0 else "")


ROW_HEAD = ["| Article | Title | Status | Updated | F | D | Affects |",
            "| --- | --- | --- | --- | --- | --- | --- |"]
DIR_HEAD = ["| Directory | Articles | F | D | Scope |", "| --- | --- | --- | --- | --- |"]

ROOT_INTRO = (
    "Entry point. Follow the directory table down to one `_index.md` whose rows list the articles, "
    "then open **one** article. Every content directory has an `_index.md` (generated by "
    "`scripts/build-index` from frontmatter + H1; scope lines from `scopes.md`). Needle lookups "
    "(paths, ports, defaults, ids): grep `facts/` — the agent surface; `guide/` is the same knowledge "
    "in plain terms for Support. F = feeds facts/, D<n> = dated decisions recorded. Brownfield: an "
    "untouched code path has no article yet."
)


def _row(article: Path, knowledge_root: Path) -> tuple[str, bool, int]:
    fm = parse_frontmatter(article) or {}
    rel = article.relative_to(knowledge_root).as_posix()
    title = article_title(article, fm)
    if fm.get("status") == "deprecated":
        title = f"*(deprecated)* {title}"
    facts = has_facts_section(article)
    dec = decisions_count(article)
    row = (f"| {rel} | {_cell(title)} | {_short_status(fm.get('status'))} | {fm.get('updated', '')} "
           f"| {'F' if facts else ''} | {f'D{dec}' if dec else ''} | {_cell(_affects_summary(fm))} |")
    return row, facts, dec


def generate(knowledge_root: Path) -> tuple[dict[Path, str], list[str]]:
    """{index_path: text} for every content dir (root included); content dirs missing a scope."""
    scopes = load_scopes(knowledge_root)
    articles = all_articles(knowledge_root)
    stats: dict[Path, tuple[int, int, int]] = {}          # dir -> (n, F, D) recursive
    dirs: set[Path] = {knowledge_root}
    for a in articles:
        _, f, d = _row(a, knowledge_root)
        p = a.parent
        while True:
            dirs.add(p)
            n0, f0, d0 = stats.get(p, (0, 0, 0))
            stats[p] = (n0 + 1, f0 + f, d0 + d)
            if p == knowledge_root:
                break
            p = p.parent
    files: dict[Path, str] = {}
    missing: list[str] = []
    for d in sorted(dirs):
        rel = d.relative_to(knowledge_root).as_posix() if d != knowledge_root else ""
        if rel and rel not in scopes:
            missing.append(rel)
        out = [SENTINEL, "", f"# {rel or 'knowledge'}", ""]
        out += [ROOT_INTRO, ""] if not rel else ([_cell(scopes[rel]), ""] if rel in scopes else [])
        children = sorted(x for x in dirs if x.parent == d and x != d)
        if children:
            out += DIR_HEAD
            for c in children:
                n, f, dd = stats[c]
                crel = c.relative_to(knowledge_root).as_posix()
                out.append(f"| [{c.name}/]({c.name}/{INDEX_NAME}) | {n} | {f} | {dd} "
                           f"| {_cell(scopes.get(crel, '*(no scope line in scopes.md)*'))} |")
            out.append("")
        own = [a for a in articles if a.parent == d]
        if own:
            out += ROW_HEAD + [_row(a, knowledge_root)[0] for a in own] + [""]
        files[d / INDEX_NAME] = "\n".join(out).rstrip("\n") + "\n"
    return files, missing


def cli_main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Generate _index.md in every content directory under knowledge/.")
    ap.add_argument("--knowledge-dir", default="knowledge")
    ap.add_argument("--check", action="store_true", help="don't write; exit 1 if stale")
    args = ap.parse_args(argv)
    root = Path(args.knowledge_dir)
    if not root.is_dir():
        print(f"build-index: no knowledge dir at {root}", file=sys.stderr)
        return 1
    files, missing = generate(root)
    rc = 0
    if missing:
        print(f"⚠️  build-index: {len(missing)} content dir(s) have no scope line in {root / SCOPES_FILE}: "
              f"{', '.join(missing)}\n   Fix: add `- **<dir/path>** — <one-line scope>` to {SCOPES_FILE}.")
        if args.check:
            rc = 1
    existing = {p for p in root.rglob(INDEX_NAME)}
    orphans = sorted(existing - set(files))
    stale = [p for p, want in files.items() if not p.exists() or p.read_text(encoding="utf-8") != want]
    if not stale and not orphans:
        print(f"✅ build-index: {len(files)} {INDEX_NAME} file(s) up to date.")
        return rc
    if args.check:
        for p in stale:
            print(f"❌ build-index: stale/missing: {p}")
        for p in orphans:
            print(f"❌ build-index: orphaned: {p}")
        print("Run scripts/build-index to fix.")
        return 1
    for p in stale:
        p.write_text(files[p], encoding="utf-8")
    for p in orphans:
        p.unlink()
    print(f"build-index: rewrote {len(stale)} file(s)" + (f", removed {len(orphans)} orphan(s)" if orphans else "") + ".")
    return rc


if __name__ == "__main__":
    sys.exit(cli_main())
