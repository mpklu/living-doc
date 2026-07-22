---
title: Facts register — the read-path layer between index and prose
description: "Optional per-article `## Facts` section (atomic, provenance-tagged lookup facts) concatenated per area into generated knowledge/facts/<area>.md files — so a needle query loads one ~3KB surface instead of 20–60KB of prose. Read-path economics: writing is cheap now; context tokens at read time are the scarce resource"
type: concept
area: methodology
updated: 2026-07-22
status: thin
load_bearing: false
references:
  - concepts/methodology/claim-provenance.md
  - concepts/methodology/scripts-over-reasoning.md
  - concepts/tooling/maintenance-tools.md
---

# Facts register

**The rule: an article MAY carry a compact `## Facts` section — atomic,
lookup-shaped facts, each claim-provenance-tagged — and `build-facts`
concatenates them per area into generated `knowledge/facts/<area>.md`
surfaces.** A needle query ("which port? which folder? what does error
3006 mean?") is answered by one small generated file instead of loading
20–60KB of article prose.

## Facts

- **Section marker**: a literal `## Facts` heading; body runs to the next `## ` heading
- **Generated output**: `knowledge/facts/<area>.md`, one per frontmatter `area:` that has ≥1 facts section
- **Sentinel** (first line of generated files): `<!-- build-facts:generated … -->`
- **Commands**: `scripts/build-facts` (write) · `scripts/build-facts --check` (CI gate; also flags orphans) *(code: build_facts.py)*
- **Fact shape**: `- **key**: value *(provenance tag)*` — atomic, one lookup per bullet
- **Single source**: the article's `## Facts` section; generated files are never edited by hand

## The read-path economics (why this layer exists)

An article is written once and read N times, and N grows with repo
lifetime and agent count. With AI in the loop, *writing* is no longer the
scarce resource — **context tokens at read time are**: loading 50KB of
prose to answer a one-line question costs money, crowds the context
window the task actually needs, and dilutes model attention. Field
evidence: a production adoption's most common agent reads were needle
queries against 20–60KB articles, and its hand-built mitigations
(handoff distillates, "start here" hubs, log pointers) were all artisanal
read-path optimizations *(field: knowledger-trans adoption, 2026-05→07)*.

The progressive-disclosure ladder this completes:

| Layer | Surface | Answers |
| --- | --- | --- |
| 0 | `description:` → generated index tables | *where do I look?* |
| **1** | **`## Facts` → generated `facts/<area>.md`** | ***what is the value?*** |
| 2 | article prose | *why is it this way?* |
| 3 | log + archives | *when/how did we learn it?* |

An agent descends only as far as the task requires. Layers 0 and 1 are
both **generated from the articles** — duplication without drift.

## Writing a facts section

- **Atomic and lookup-shaped**: paths, ports, error codes, defaults,
  folder names, versions, dates, invariants. One fact per bullet,
  `- **key**: value` form preferred.
- **Extracted, never invented**: a facts bullet restates a claim already
  made (and ideally provenance-tagged) in the prose — carry the tag onto
  the bullet. A fact with no home in the prose is a smell: write the
  prose claim first.
- **The facts section is the authoritative statement of the atom**; the
  prose elaborates it. When they disagree, fix both in the same task
  (the same-task rule applies inside an article too).
- **Small**: ~8–15 bullets. If a facts section wants 30 bullets, the
  article probably wants splitting (or a hub).
- **Adopt on touch**, like everything brownfield: add facts sections when
  an article is next edited, not as a sprint. The register is useful from
  the first section onward — coverage grows organically.
- **Compress the what, keep the why.** Facts sections carry the *what*
  (re-derivable, depreciating); prose keeps the *why* (constraints,
  alternatives, incidents — irreplaceable). Never move the why into
  bullets.

## Anti-patterns

- **Hand-editing `knowledge/facts/*.md`** — generated; the sentinel says
  so; `--check` will flag it as stale anyway.
- **Facts as a second article** — paragraphs in the facts section defeat
  the point; it's a cache line, not a summary.
- **Untagged facts** — a bare atom is exactly the "confident claim, no
  provenance" failure; carry the tag ([[claim-provenance]]).
- **Speculative facts sections** — don't add empty/placeholder sections
  to articles you aren't touching (same rule as speculative articles).

## Tooling

`build-facts` follows the house pattern ([[maintenance-tools]],
[[scripts-over-reasoning]]): stdlib-only, co-located with the shared
parser, `--check` for CI/pre-commit, orphan cleanup when an area loses
its last facts section. `sweep-report` skips `facts/` (generated, not
sweep-orderable), as it now also skips `log/` archives.
