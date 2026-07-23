---
title: The what is a cache; the why is a primary source
description: "Budget article prose by derivability: what-sections are caches of the code (falling value, recurring invalidation bill — keep them thin, pointed, tagged); why-sections are the only record of the non-derivable (rejected alternatives, constraints, negative results, field incidents — zero maintenance, appreciating). The derivability test decides which is which"
type: concept
area: methodology
updated: 2026-07-22
status: thin
load_bearing: false
references:
  - concepts/methodology/facts-register.md
  - concepts/methodology/claim-provenance.md
  - concepts/methodology/scripts-over-reasoning.md
---

# The what is a cache; the why is a primary source

**The rule: budget article prose by derivability. Mechanics restated from
code are a cache with a maintenance bill; rationale, constraints, and
observations are primary sources with none. Hoard the second; keep the
first thin, pointed, and gated.**

## Facts

- **The derivability test**: *re-derivable by a competent agent with the checkouts in minutes?* → cache (thin) · *needs a bench run, vendor call, production incident, or time machine?* → asset (rich prose)
- **What depreciates for two reasons**: re-derivation cost keeps falling AND every what-sentence carries a recurring invalidation bill (drift checks, sweeps, `updated:` hygiene)
- **Why has zero maintenance cost**: a historical fact can't drift — only be superseded, and the supersession is itself informative
- **Non-derivable content**: rejected alternatives · external constraints · negative results · field incidents and their symptom→cause mappings
- **Sanctioned cache form**: `## Facts` blocks ([[facts-register]]) + `*(code: path:line)*` pointers ([[claim-provenance]]) — atomic, tagged, staleness-gated
- **Exception**: operator-facing docs stay what-heavy (their readers don't grep source)

## The two depreciation forces on the what

A *what*-section is a cache of the code, and its value falls on two
independent axes:

1. **Re-derivation keeps getting cheaper.** An agent with the repo
   re-derives an enum's values or a function's behavior in seconds —
   often faster than it can decide whether a prose restatement is still
   current *(field: knowledger-trans, the `CDA_TRANSPORT` default was
   code-verified in one grep during a doc review, 2026-07-22)*.
2. **A cache needs invalidation.** Every what-sentence carries a
   recurring maintenance bill: drift checks, freshness sweeps, `updated:`
   hygiene. An entire day of this methodology's tooling — drift-check,
   check-links, build-index, check-affects — is cache-invalidation
   machinery *(field: LIVING_DOC log, 2026-07-22)*.

A stale what is worse than none: the code cannot be wrong about itself,
but the article can.

## Why the why appreciates

A *why*-section is not a cache of anything — it is the **only record** of
things that exist in no repo:

- **Alternatives rejected** — absent from the code by definition.
- **Constraints that shaped the design** — vendor contracts, deadlines,
  retirements; they live outside the source tree.
- **Negative results** — what was tried and failed.
- **Field incidents** and the symptom→cause mappings debugging paid for.

This content has **zero maintenance cost** — a why is a historical fact
that can't drift, only be superseded, and even the supersession is
informative. And it *appreciates*: every future decision is constrained
by past ones, so old rationale keeps gaining referents. Its replacement
cost is infinite once the context evaporates — the founding condition of
the field adoption this methodology was validated on was exactly that
evaporation (departed subject-matter owners, knowledge-transfer under
deadline) *(field: knowledger-trans, 2026-04→07)*.

## The boundary: the derivability test

The line is not literally what-vs-why. The operational test is
**derivability at read time**:

> *Could a competent agent with the checkouts re-derive this correctly
> in minutes?* → it's a **cache**. Keep it thin, pointed, and tagged.
>
> *Would it need a bench run, a vendor call, a production incident, or a
> time machine?* → it's the **asset**. Spend the prose there.

This correctly reclassifies some "what" as asset: cross-repo emergent
behavior (a keystore trap that spans two scripts *and* field state),
runtime characteristics, anything **observed rather than read** — which
is also exactly what the `bench:`/`field:` provenance kinds mark
([[claim-provenance]]).

## Structural consequence

Engineer-facing articles converge on:

1. **`## Facts`** — the sanctioned cache: atomic, provenance-tagged,
   staleness-gated ([[facts-register]]).
2. **Code-cites instead of restated mechanics** — `*(code: path:line)*`
   is a pointer that names its own invalidation target.
3. **Prose budget spent almost entirely on the why.**

Operator-facing docs are the legitimate exception: their readers won't
grep source, so what-heavy is correct there.

The methodology's "capture the why" thereby sharpens from a writing
preference into an economic rule: **caches are tolerated where
invalidation is mechanized; primary sources are hoarded; everything else
is a pointer.** It also gives the (still unspecified) refine ritual its
criterion: compressing an article means shrinking its cache sections
toward facts + pointers — never its why.
