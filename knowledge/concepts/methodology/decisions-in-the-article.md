---
title: Decisions live in the article; the story lives in the log
description: "A dated ## Decisions section per article — one bullet per decision, chose X over Y because Z, tagged *(decision: who)* — surfaced as a D count in the index. The log keeps the narrative; the article keeps the verbatim record"
type: concept
area: methodology
updated: 2026-11-09
status: thin
affects: ['actions/drift-check/build_index.py']
load_bearing: true
references:
  - concepts/methodology/claim-provenance.md
---

# Decisions live in the article

## The gap

The methodology records *facts* with provenance and *changes* in a dated
log. It had no home for *decisions*. In the field repo, 66 of 131
articles had a why-or-alternatives section, one carried a dated decision
tag, and the real record was 1 MB of log archives findable only by grep
*(bench: 2026-09-21)*. An agent asking "why is X shaped this way" got the
current state from the article and had to excavate the log for the history.

## The rule

An article may carry `## Decisions`: one bullet per decision, dated,
verbatim, in one line —

```markdown
- 2026-09-21 — chose per-directory generated indexes over a per-area manifest,
  because the manifest flattened the tree *(decision: Kun)*
```

The log entry keeps the story (what was tried, what it cost); the article
keeps the record; the index shows a `D<n>` count so the reader can see
which articles carry history before opening them.

Decisions stay in concept articles. A handbook page states only the
outcome, current state, and points to the article that holds the
decision ([handbook-layer](handbook-layer.md)).

## Why not ADRs

An ADR directory is a second tree to route through, a second place to
drift, and it separates the decision from the mechanism it shaped. A
decision is a claim about the article's subject with a provenance tag of
its own kind; it belongs where the subject is documented.

## Binding rules

- Add on touch. No back-fill sprint.
- One line per decision; the reasoning beyond one line goes in the log
  entry, which the bullet may cite.
- `*(decision: who)*` names who decided, as `reported:` names who said.
