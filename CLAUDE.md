# LIVING_DOC

Methodology + tooling repo for the living-documentation pattern. Adopters
copy from `templates/`, run the Skill at `skills/living-docs/`, or wire
in the GitHub Action at `actions/drift-check/`.

## Methodology

This repo dogfoods the methodology it defines. **Brownfield retrofit**
started 2026-04-29 — see `knowledge/log.md`. Articles cover the seam
we're actively working on (the next-phase bundle: frontmatter schema,
`affects:` globs, local enforcement, procedural compliance). Existing
prose in the adoption guides and overview stays put for now and gets
articles only when those documents are next touched.

For the why / methodology principles themselves, see
`knowledge/concepts/methodology/`. For tooling internals (drift-check,
Skill, templates) see `knowledge/concepts/tooling/`. For decisions that
span both, see `knowledge/connections/`.

### Source of truth

`knowledge/` is the source of truth for *the methodology's own decisions*
— how the rule set was chosen, why frontmatter is structured the way it
is, why local enforcement complements the PR check, and so on.

The published methodology (`LIVING_DOCS_OVERVIEW.md`, the two adoption
guides, `GLOSSARY.md`) is the **adopter-facing surface**. It's prose
optimized for someone learning the methodology in 30 minutes. Articles
in `knowledge/` are the **maintainer-facing reasoning** — what changed
when, why a decision went one way vs. another, what the alternatives
were. When the two disagree, prose in the published methodology wins
for adopter-facing concepts (it's the canonical surface) and articles
win for *why* (which the published docs intentionally compress).

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

The same-task rule is a *principle*; this checklist is the *procedure*.
Run through it before every commit:

1. List the files in this commit's diff.
2. For each: does any article's `affects:` frontmatter glob match it?
   (Until the `affects:`-based mapping ships, fall back to the
   article-mapping table below.) If yes, open that article.
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

The failure mode they all enable: the article goes stale before the
next read. The next session trusts the stale article and produces
wrong work. The drift compounds. This is not stylistic — it's
load-bearing.

### Article mapping

Hand-maintained for now; will be regenerated from `affects:`
frontmatter once the next-phase bundle ships
(see `knowledge/concepts/methodology/affects-globs.md`).

| When you change… | Update |
| --- | --- |
| `LIVING_DOCS_OVERVIEW.md`, `*ADOPTION_GUIDE.md`, `GLOSSARY.md` (methodology surface) | Article in `knowledge/concepts/methodology/` matching the decision |
| `templates/**` | Article in `knowledge/concepts/methodology/` (template content reflects methodology decisions) |
| `actions/drift-check/drift_check.py` | `knowledge/concepts/tooling/drift-check.md` (write on touch) |
| `skills/living-docs/SKILL.md` | `knowledge/concepts/tooling/skill.md` (write on touch) |

### Where new articles go

- `knowledge/concepts/methodology/{topic}.md` — methodology decisions
  and their reasoning. Most articles end up here in this repo.
- `knowledge/concepts/tooling/{topic}.md` — internals of `drift-check`,
  the Skill, the templates' generation logic.
- `knowledge/connections/{topic}.md` — cross-cutting (e.g.,
  "methodology decisions that flowed into both templates and tooling").

Frontmatter shape (proposed schema in
`concepts/methodology/frontmatter-as-source-of-truth.md`):

```yaml
---
title: <human-readable>
type: concept | connection | meta
area: methodology | tooling | meta
updated: YYYY-MM-DD
status: thin | mature | deprecated
# Optional, will be load-bearing after the next-phase bundle:
# affects: ['glob/pattern/**']
# load_bearing: true
# references: [other-article.md]
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
templates/                    copy-paste starters (greenfield, brownfield, workspace)
skills/living-docs/           Claude Code Skill for adopt/audit/sweep
actions/drift-check/          GitHub Action — PR-time enforcement
knowledge/                    living docs (this repo dogfoods)
  concepts/methodology/
  concepts/tooling/
  connections/
  index.md
  log.md
```
