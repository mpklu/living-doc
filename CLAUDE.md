# LIVING_DOC

Methodology + tooling repo for the living-documentation pattern. Adopters
copy from `templates/`, run the Skill at `skills/living-docs/`, or wire
in the GitHub Action at `actions/drift-check/`.

This repo dogfoods the methodology it defines (brownfield retrofit since
2026-04-29 — see `knowledge/log.md`). Guides/overview prose gets articles
on touch, not speculatively. Methodology decisions →
`knowledge/concepts/methodology/`; tooling internals →
`knowledge/concepts/tooling/`; cross-cutting → `knowledge/connections/`.

### Source of truth

`knowledge/` is the source of truth for *the methodology's own decisions*.
The published methodology (`LIVING_DOCS_OVERVIEW.md`, the two adoption
guides, `GLOSSARY.md`) is the **adopter-facing surface**; articles are the
**maintainer-facing reasoning**. When they disagree: published prose wins
for adopter-facing concepts (canonical surface), articles win for *why*.

### The rule

Every code or methodology change that alters behaviour, structure, or a
documented decision updates the matching `knowledge/concepts/*.md`
article(s) in the same task and appends an entry to `knowledge/log.md`.
If the affected seam doesn't yet have an article, write the first thin
one in the same task. Don't defer.

**Capture first, refine second:** when in doubt, write. When unsure
where it belongs, pick the closest fit. Missing context is
unrecoverable; an imperfect article costs minutes.

### Before any commit

The same-task rule is a *principle*; this checklist is the *procedure*
— and the installed `pre-commit-gate` enforces it (`scripts/pre-commit-gate
--install` after a fresh clone; `.git/hooks` isn't versioned):

1. List the files in this commit's diff.
2. For each: does any article's `affects:` frontmatter glob match it?
   (Canonical mapping — `scripts/drift-check` reads it; the table below
   is the legacy secondary source.) If yes, open that article.
3. Did this change alter behaviour, configuration, models, structure,
   or a documented decision?
4. If yes: stage the article update + a `log.md` entry **in this same
   commit**.
5. If no article exists for the touched code path: write a thin one
   now (~200 words). Don't open a follow-up issue; don't defer.
6. If the change is genuinely doc-irrelevant (typo, formatting,
   refactor with identical observable behaviour): the commit body
   must say so explicitly: `no knowledge impact: <reason>`.

### Red flags

These thoughts mean STOP and audit:

- "I'll update docs after this commit lands."
- "The article is roughly correct."
- "This is too small to document."
- "Let me ship and circle back."
- "The reviewer can flag it if it matters."

Each rationalizes a skip; the stale article misleads the next session and
the drift compounds.

### Article mapping (legacy secondary — `affects:` frontmatter is canonical)

| When you change… | Update |
| --- | --- |
| `LIVING_DOCS_OVERVIEW.md`, `*ADOPTION_GUIDE.md`, `GLOSSARY.md` (methodology surface) | Article in `knowledge/concepts/methodology/` matching the decision |
| `templates/**` | Article in `knowledge/concepts/methodology/` (template content reflects methodology decisions) |
| `actions/drift-check/drift_check.py` | `knowledge/concepts/tooling/drift-check.md` (write on touch) |
| `actions/drift-check/{check_links,build_index,bump_updated,sweep_report,roll_log}.py`, `scripts/{check-links,build-index,bump-updated,sweep-report,roll-log}` | `knowledge/concepts/tooling/maintenance-tools.md` |
| `skills/living-docs/SKILL.md` | `knowledge/concepts/tooling/skill.md` (write on touch) |

### Where new articles go

- `knowledge/concepts/methodology/{topic}.md` — methodology decisions (most articles here).
- `knowledge/concepts/tooling/{topic}.md` — tool internals.
- `knowledge/connections/{topic}.md` — cross-cutting.

Frontmatter schema: `schemas/article-frontmatter.schema.json`
(design: `concepts/methodology/frontmatter-as-source-of-truth.md`):

```yaml
---
title: <human-readable>
description: "<one-line retrieval hook — fills generated index tables>"
type: concept | connection | meta
area: methodology | tooling | meta
updated: YYYY-MM-DD
status: thin | mature | deprecated
affects: ['glob/pattern/**']   # canonical code↔article mapping (drift-check)
# Optional: load_bearing: true · references: [other-article.md]
---
```

## Project structure

```text
LIVING_DOCS_OVERVIEW.md       methodology, first principle
GREENFIELD_ADOPTION_GUIDE.md  setup for new projects
BROWNFIELD_ADOPTION_GUIDE.md  retrofit for existing projects
GLOSSARY.md                   vocabulary
ROADMAP.md                    planned phases
README.md                     repo landing page
templates/                    copy-paste starters (greenfield, brownfield, workspace) + hooks/
skills/living-docs/           Claude Code Skill for adopt/audit/sweep
actions/drift-check/          GitHub Action + all maintenance-tool implementations
scripts/                      thin CLI wrappers (drift-check, validate-articles, check-links,
                              build-index, bump-updated, sweep-report, roll-log, build-facts,
                              provenance-report, check-affects, check-trailer, check-dates,
                              pre-commit-gate)
schemas/                      article-frontmatter JSON schema
knowledge/                    living docs (this repo dogfoods)
  concepts/{methodology,tooling}/ · connections/ · facts/ · index.md · log.md
```
