#!/usr/bin/env python3
"""Facts ↔ prose overlap: which `## Facts` bullets restate a sentence (or
table row) that already exists in the same article's body.

WHY (2026-09-21): a fact in this KB can live three times — in the prose,
in the article's `## Facts` section, and in the generated `facts/<area>.md`.
The third copy is generated and gated, so it cannot drift. The first two
are both hand-maintained, and that is the redundancy that rots: edit one,
forget the other. The methodology's answer is *what-cache / why-asset* —
the Facts bullet holds the what, the prose keeps the why — applied on
touch. This module turns that principle into a worklist so the article's
next editor sees exactly which sentences to compress, instead of
re-deriving the comparison.

Measurement notes, because the first cut was wrong:
  - the frontmatter is excluded (a long `description:` line matched 4 of 5
    "duplicates" in the first run);
  - bullets with fewer than MIN_TOKENS content tokens are skipped (short
    bullets score 100% against anything);
  - markdown emphasis, backticks and provenance tags are stripped before
    tokenising, and stop-words are dropped.
  - score = |bullet ∩ best sentence| / |bullet| — "how much of this bullet
    is already said in one place". HI (≥0.8) = near-verbatim; MID (≥0.5) =
    substantial restatement.

Not every hit is a defect: operator docs (the CDA playbook's Part 1, the
runbooks) are what-heavy by design, and a Facts bullet mirroring a row of a
reference table there is accepted. The tool ranks; the editor judges.

Used by sweep-report (--facts-overlap [--pairs ARTICLE]).
"""

from __future__ import annotations

import re
from pathlib import Path

from validate_articles import parse_frontmatter

HI = 0.8
MID = 0.5
MIN_TOKENS = 6
STOP = {
    "the", "and", "for", "with", "that", "this", "from", "not", "are", "when",
    "which", "into", "its", "but", "was", "has", "have", "one", "all", "only",
    "than", "then", "also", "can", "via", "per", "see", "code",
}
FACTS_RE = re.compile(r"^## Facts\s*$(.*?)(?=^## |\Z)", re.M | re.S)
PROVENANCE_RE = re.compile(r"\*\((code|bench|field|reported|inferred)[^)]*\)\*")


def tokens(s: str) -> set[str]:
    s = PROVENANCE_RE.sub("", s).replace("**", "").replace("`", "")
    return {w for w in re.findall(r"[a-z0-9_\.\-/<>]{3,}", s.lower()) if w not in STOP}


def _body(text: str) -> str:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4:]
    return text


def article_overlap(path: Path) -> dict | None:
    """None if the article has no `## Facts` section; else
    {path, bullets, hi, mid, pairs:[(score, bullet, sentence), …]}."""
    try:
        text = _body(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError):
        return None
    m = FACTS_RE.search(text)
    if not m:
        return None
    facts = m.group(1)
    prose = text[: m.start()] + text[m.end():]
    sentences = [s for s in re.split(r"(?<=[.!?])\s+|\n", prose) if len(s) > 20]
    stoks = [(s, tokens(s)) for s in sentences]
    bullets = [b.strip() for b in re.split(r"\n- ", "\n" + facts) if b.strip()]
    pairs: list[tuple[float, str, str]] = []
    hi = mid = 0
    for b in bullets:
        bt = tokens(b)
        if len(bt) < MIN_TOKENS or not stoks:
            continue
        sent, st = max(stoks, key=lambda x: len(bt & x[1]) / len(bt))
        score = len(bt & st) / len(bt)
        if score >= HI:
            hi += 1
        elif score >= MID:
            mid += 1
        if score >= MID:
            pairs.append((score, " ".join(b.split()), " ".join(sent.split())))
    pairs.sort(key=lambda p: -p[0])
    return {"path": str(path), "bullets": len(bullets), "hi": hi, "mid": mid, "pairs": pairs}


def collect(knowledge_dir: str) -> list[dict]:
    root = Path(knowledge_dir)
    rows = []
    for sub in ("concepts", "connections"):
        base = root / sub
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*.md")):
            if not parse_frontmatter(path):
                continue
            r = article_overlap(path)
            if r:
                rows.append(r)
    rows.sort(key=lambda r: (-r["hi"], -r["mid"], r["path"]))
    return rows
