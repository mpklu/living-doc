---
title: Two readers, one article — facts for agents, plain terms for people
description: "Facts are the agent's grep surface and lose precision if written for people; Support needs the same knowledge in its own words. One article carries both sections; build-facts renders two surfaces; a lint keeps identifiers out of the human one"
type: concept
area: methodology
updated: 2026-09-21
status: thin
affects: ['actions/drift-check/build_facts.py']
load_bearing: true
references:
  - concepts/methodology/facts-register.md
  - concepts/methodology/what-cache-why-asset.md
---

# Two readers, one article

## The tension

The facts register was designed as a read-path layer for agents: atomic
bullets with identifiers and provenance tags, grep-able. Measured in the
field repo, 88 % of bullets carried backticked identifiers and 40 % a
`*(code: path:line)*` tag *(bench: 762 bullets, 2026-09-21)*. That is what
makes a grep hit trustworthy. It is also unreadable to the Support staff
the KB's owner wanted `facts/` to serve — "avoid source code, prefer
non-tech language".

Rewriting facts in plain language would have destroyed the needle path.
Leaving them as they were served no human. Two audiences, one truth.

## The resolution

An article may carry two sections, written in the same task:

- `## Facts` — identifiers, values, provenance tags. Rendered to
  `facts/<area>.md`, the agent's grep surface.
- `## In plain terms` — what it means for the office and what to do,
  in everyday words. Rendered to `guide/<area>.md` for Support.

Neither is copied from the other; both are renderings of the article.
`build-facts` rejects a plain-terms bullet that contains a backtick or a
provenance tag — the reader it serves can use neither.

## Corollaries

- Operator runbooks follow the human rule throughout: plain language,
  literal copy-paste commands, no code tags.
- Developer plans are not runbooks. Once the work ships, the mechanism
  belongs in the concept article and the execution narrative in the log;
  the plan is deleted.
- `sweep-report --plain-terms` lists articles that carry incident-derived
  `*(field: …)*` claims but no plain-terms section — the knowledge Support
  needs first.

## Anti-pattern

Writing one section to serve both readers. It ends up too technical for
one and too vague for the other, and the grep surface pays for it.
