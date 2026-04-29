---
title: Dogfooding the methodology
type: concept
area: methodology
updated: 2026-04-29
status: thin
affects:
  - 'CLAUDE.md'
  - 'README.md'
load_bearing: true
---

# Dogfooding the methodology

This repo applies its own methodology to itself: `knowledge/` plus a
same-task rule in CLAUDE.md, brownfield retrofit since 2026-04-29.

## Why dogfood

Three reasons, in order of value:

1. **Validation under realistic load.** The methodology either works on
   a project that ships templates + tooling + a Skill + an Action, or
   it doesn't. Easier to find the rough edges by living with them than
   by reading guides.
2. **The most credible adoption example.** A methodology repo that
   doesn't follow its own rules is a hypocrisy signal. One that does
   becomes its own working specification.
3. **Maintainer reasoning becomes durable.** Adoption guides intentionally
   compress the *why* to keep adopters' onboarding under 30 minutes. The
   articles capture what the guides leave out — alternatives ruled out,
   why a knob defaults this way, what failed in earlier drafts.

## What's different about a meta-repo

A typical adoptee's `knowledge/` covers their *product* concepts. This
repo's `knowledge/` covers *the methodology's own concepts* and the
internals of the tooling that supports it. Two practical consequences:

- **Distinguish article home from example content.** Adopters might
  copy `templates/brownfield/knowledge/concepts/example.md` literally;
  they should not copy `knowledge/concepts/methodology/dogfooding.md`.
  We separate by location: this repo's *own* articles live in
  `knowledge/concepts/{methodology,tooling}/`; example content lives
  in `templates/`. Frontmatter `area: methodology | tooling` reinforces
  the split.
- **The published methodology is the canonical adopter surface.** When
  prose in `LIVING_DOCS_OVERVIEW.md` and an article in `knowledge/`
  disagree on adopter-facing concepts, the prose wins (it's the
  documented contract). Articles win on *why* and on internal /
  tooling details (which the prose intentionally compresses).

## Brownfield, not back-fill

The repo already has overview + two adoption guides + glossary +
templates + Skill + Action. Per the brownfield rule, we don't write
articles for all of that on day one. We write articles when the seam
is touched. The retrofit start (2026-04-29) was triggered by the
upcoming next-phase bundle — that's the first seam, and articles for
it are the first batch.

## What this article protects

If a future contributor wonders "why does this repo have a
`knowledge/` if its content is already in the published guides?" —
this article is the answer. If someone proposes back-filling articles
for every methodology decision ever made, this article is the
counterargument.

## Files

- `CLAUDE.md` — same-task rule applied here
- `knowledge/log.md` — retrofit start entry (2026-04-29)
- `LIVING_DOCS_OVERVIEW.md`, `BROWNFIELD_ADOPTION_GUIDE.md` — the
  adopter surface this repo's articles complement
