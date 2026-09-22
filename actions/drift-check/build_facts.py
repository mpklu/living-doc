#!/usr/bin/env python3
"""Generate per-area facts indexes from articles' `## Facts` sections.

The facts register (see concepts/methodology/facts-register.md) is the
read-path layer between the index and full prose: each article MAY carry
a compact `## Facts` section — atomic, lookup-shaped facts (paths, ports,
codes, defaults, invariants), each ideally claim-provenance-tagged. This
tool concatenates them per `area:` into generated files:

    knowledge/facts/<area>.md

so an agent (or human) answering a needle query loads ONE small surface
instead of opening 20–60KB articles. The articles stay the single source;
the generated files carry a sentinel first line and per-article backlinks.

Usage:
    build-facts               # (re)write knowledge/facts/<area>.md files
    build-facts --check       # exit 1 if any facts file is stale/orphaned
    build-facts --knowledge-dir docs/kb

Extraction: everything between a literal `## Facts` heading and the next
`## ` heading (or EOF). Articles without the section are simply absent
from the register. Area comes from frontmatter `area:`, falling back to
the article's parent directory name.

TWO READERS, ONE SOURCE (2026-09-21, Kun: "facts/ are human-faced, avoid
source code, prefer non-tech language"): as built, facts/ is the AGENT surface —
88 % of bullets carry identifiers, 40 % are code-tagged — and that is what
makes it a precise grep target. Support needs the same knowledge said
differently. So an article may also carry `## In plain terms`: operator
language, no identifiers, no provenance tags, rendered per area into

    knowledge/guide/<area>.md

The two sections are two renderings of one article, written in the same
task; neither is copied from the other. LINT: a plain-terms bullet containing
a backtick or a `*(code:…)*` tag fails (both modes) — the reader it serves
cannot use either.

Uses validate_articles.parse_frontmatter — hence co-located.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from validate_articles import parse_frontmatter

SENTINEL = "<!-- build-facts:generated — edit the articles' ## Facts sections, not this file -->"
GUIDE_SENTINEL = "<!-- build-facts:generated — edit the articles' ## In plain terms sections, not this file -->"
FACTS_HEADING_RE = re.compile(r"^##\s+Facts\s*$")
PLAIN_HEADING_RE = re.compile(r"^##\s+In plain terms\s*$")
H2_RE = re.compile(r"^##\s+")
PLAIN_FORBIDDEN_RE = re.compile(r"`|\*\((code|bench|field|reported|inferred|decision)[^)]*\)\*")
SKIP_DIRS = ("facts", "guide", "log")


def extract_section(text: str, heading_re: re.Pattern) -> str | None:
    """Return the body of the first `## <heading>` section, or None if absent."""
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if heading_re.match(line):
            start = i + 1
            break
    if start is None:
        return None
    end = len(lines)
    for j in range(start, len(lines)):
        if H2_RE.match(lines[j]):
            end = j
            break
    body = "\n".join(lines[start:end]).strip("\n")
    return body if body.strip() else None


def extract_facts(text: str) -> str | None:
    return extract_section(text, FACTS_HEADING_RE)


def extract_plain(text: str) -> str | None:
    return extract_section(text, PLAIN_HEADING_RE)


def plain_terms_violations(path: Path, body: str) -> list[str]:
    """Bullets a Support reader cannot use: identifiers in backticks, provenance tags."""
    return [f"{path}: plain-terms bullet has code/identifier: {l.strip()[:90]}"
            for l in body.splitlines() if l.lstrip().startswith("- ") and PLAIN_FORBIDDEN_RE.search(l)]


def collect(knowledge_root: Path, heading_re: re.Pattern = FACTS_HEADING_RE
            ) -> dict[str, list[tuple[Path, str]]]:
    """area -> [(article_path, section_body)] sorted by filename."""
    by_area: dict[str, list[tuple[Path, str]]] = {}
    for path in sorted(knowledge_root.rglob("*.md")):
        if path.name in ("index.md", "log.md", "manifest.md", "areas.md", "scopes.md", "_index.md"):
            continue
        if path.relative_to(knowledge_root).parts[0] in SKIP_DIRS:
            continue  # never read our own output
        fm = parse_frontmatter(path)
        if fm is None:
            continue
        try:
            body = extract_section(path.read_text(encoding="utf-8"), heading_re)
        except (OSError, UnicodeDecodeError):
            continue
        if body is None:
            continue
        area = str(fm.get("area") or path.parent.name)
        by_area.setdefault(area, []).append((path, body))
    return by_area


def render(area: str, entries: list[tuple[Path, str]], out_dir: Path, guide: bool = False) -> str:
    if guide:
        out = [GUIDE_SENTINEL, "", f"# {area} — in plain terms", "",
               f"What the `{area}` articles mean for Support and office staff, in everyday language, "
               "collected from each article's `## In plain terms` section by `scripts/build-facts`. "
               "No code, no file names. The linked article has the technical detail.", ""]
    else:
        out = [SENTINEL, "", f"# Facts — {area}", "",
               f"Atomic lookup facts extracted from the `{area}` articles' `## Facts` sections by "
               "`scripts/build-facts` — the agent's grep surface: paths, ports, codes, defaults, each "
               "provenance-tagged. Open the linked article for the why; `guide/` has the same knowledge "
               "in plain terms.", ""]
    for path, body in entries:
        rel = Path("..") / path.relative_to(out_dir.parent)
        out.append(f"## {path.stem} — [{rel.as_posix()}]({rel.as_posix()})")
        out.append("")
        out.append(body)
        out.append("")
    return "\n".join(out).rstrip("\n") + "\n"


def cli_main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Generate knowledge/facts/<area>.md from articles' ## Facts sections."
    )
    ap.add_argument("--knowledge-dir", default="knowledge")
    ap.add_argument("--check", action="store_true",
                    help="don't write; exit 1 if any facts file is stale or orphaned")
    args = ap.parse_args(argv)

    knowledge_root = Path(args.knowledge_dir)
    if not knowledge_root.is_dir():
        print(f"build-facts: knowledge dir not found: {knowledge_root}", file=sys.stderr)
        return 1
    facts_dir = knowledge_root / "facts"
    guide_dir = knowledge_root / "guide"

    by_area = collect(knowledge_root)
    expected: dict[Path, str] = {
        facts_dir / f"{area}.md": render(area, entries, facts_dir)
        for area, entries in sorted(by_area.items())
    }
    plain = collect(knowledge_root, PLAIN_HEADING_RE)
    violations = [v for entries in plain.values() for path, body in entries
                  for v in plain_terms_violations(path, body)]
    if violations:
        for v in violations:
            print(f"❌ build-facts: {v}")
        print("   `## In plain terms` is for Support: say it without identifiers or provenance tags "
              "(they belong in ## Facts).")
        return 1
    for area, entries in sorted(plain.items()):
        expected[guide_dir / f"{area}.md"] = render(area, entries, guide_dir, guide=True)

    existing = set(facts_dir.glob("*.md")) if facts_dir.is_dir() else set()
    existing |= set(guide_dir.glob("*.md")) if guide_dir.is_dir() else set()
    orphans = sorted(existing - set(expected))
    stale = [
        p for p, want in expected.items()
        if not p.exists() or p.read_text(encoding="utf-8") != want
    ]

    if args.check:
        for p in stale:
            print(f"❌ build-facts: stale/missing: {p}")
        for p in orphans:
            print(f"❌ build-facts: orphaned (no area produces it): {p}")
        if stale or orphans:
            print("Run scripts/build-facts to fix.")
            return 1
        n = len(expected)
        print(f"✅ build-facts: {n} facts/guide file(s) up to date." if n else
              "✅ build-facts: no ## Facts sections found; nothing to generate.")
        return 0

    if not expected and not orphans:
        print("build-facts: no ## Facts sections found; nothing to generate.")
        return 0
    for p, want in expected.items():
        if not p.exists() or p.read_text(encoding="utf-8") != want:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(want, encoding="utf-8")
            print(f"build-facts: wrote {p}")
    for p in orphans:
        p.unlink()
        print(f"build-facts: removed orphaned {p}")
    if not stale and not orphans:
        print(f"build-facts: {len(expected)} facts file(s) already up to date.")
    return 0


if __name__ == "__main__":
    sys.exit(cli_main())
