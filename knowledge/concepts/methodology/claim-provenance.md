---
title: Claim provenance — grade claims by how they were verified
description: "Inline provenance tags — *(code: path:line)* · *(bench: date)* · *(field: incident)* · *(reported: who)* · *(inferred)* — so readers (human or agent) can calibrate trust per claim, not per article. The fix for AI-written docs' worst failure mode: confident-sounding inference read as fact later"
type: concept
area: methodology
updated: 2026-07-22
status: thin
load_bearing: true
references:
  - concepts/methodology/scripts-over-reasoning.md
  - concepts/tooling/maintenance-tools.md
---

# Claim provenance

**The rule: a load-bearing claim states how it was verified, inline, where
the claim is made.** Readers — human or agent — calibrate trust per claim,
not per article.

## The problem this fixes

AI agents write most articles under this methodology, and an agent's most
dangerous failure mode is not writing *badly* — it's writing **confident
prose around an unverified inference**. Six months later, another session
(or a human) reads that sentence with the same weight as a code-cited
fact, builds on it, and the error compounds. "Real data beats the
article" tells you what to do on *conflict*; provenance tags tell you how
much to trust a claim **before** you've paid to check it.

The convention standardizes what field practice already invented
organically: a production adoption's articles were ad-hoc writing
"code-confirmed (`PreferenceData.m:849`)", "verified on Beacon
(`cda-diag.20260721-095522`)", "not bench-tested", "per the vendor PDF" —
useful every single time, but unqueryable and inconsistent
*(field: knowledger-trans adoption, 2026-05→07)*.

## The vocabulary — five keywords

A tag is an **italicized parenthetical with a controlled leading
keyword**, placed immediately after the claim it grades:

| Tag | Means | Evidence (required part) |
| --- | --- | --- |
| `*(code: path:line)*` | Verified by reading the source | The citation itself — e.g. `*(code: PreferenceData.m:849)*` |
| `*(bench: date/ref)*` | Executed/observed on a test bench | Date, log name, or run id |
| `*(field: incident/date)*` | Observed in production or at a real site | Incident/site + date |
| `*(reported: who)*` | A third party said so; not independently checked | The source — vendor doc, support page, a person, a legacy wiki |
| `*(inferred)*` | Reasoned from code/docs, **not** executed or observed | None (optionally `*(inferred from X)*`) |

What you type (and how it reads — the tags render as light italics):

```markdown
The shipped default is `0` (iCA) *(code: PreferenceData.m:849)*. On
Apple Silicon the daemon can take minutes to bind *(field: Beacon
2026-07-16)*. The 4.2 build is expected ~end Aug *(reported: vendor)*.
A re-send should re-ingest the orphaned response *(inferred)*.
```

Machine-readable by one regex — `\*\((code|bench|field|reported|inferred)[:)]`
— which is what makes the tags *actionable* rather than decorative
(see Tooling below).

## Binding rules

1. **Tag load-bearing claims only** — behavioural statements about code,
   config values/defaults, error-code meanings, procedures that could
   break something. Tagging every sentence is noise and kills adoption.
2. **Evidence is the point.** `code:` without a citation is not a tag.
   For `bench:`/`field:`, a date or artifact reference makes the claim
   re-checkable.
3. **Default for untagged claims:** inherit the article's `status:` — in
   a `thin` article, read untagged claims as *inferred*; in a `mature`
   article, as swept-but-grandfathered. New or edited text should tag
   regardless of article status.
4. **No laundering.** An agent must never upgrade a claim's tag
   (`reported`/`inferred` → `code`) without actually performing the
   verification in the same task. Quoting someone else's `code:` tag
   keeps their tag.
5. **Trust ordering is context-dependent, not absolute** — `field` beats
   `inferred` always, but `code` vs `field` can disagree (code says X,
   the field observed Y): that disagreement is itself the finding; keep
   both tags and reconcile in the same task.

## What it enables

- **Verification worklists, generated not reasoned:** every `*(inferred)*`
  and `*(reported:)*` in a `load_bearing: true` article is a candidate
  for the next verification pass — `scripts/provenance-report --worklist`
  emits exactly that list ([[maintenance-tools]], [[scripts-over-reasoning]]).
- **Adversarial verification has targets:** a periodic sweep where an
  agent tries to *refute* claims starts from the worklist instead of
  re-reading everything.
- **Status promotion gets teeth:** promote `status: thin → mature` only
  when the article's load-bearing claims carry `code`/`bench`/`field`
  tags (or were demoted/removed). "Mature" then *means* something
  checkable rather than "someone felt good about it."
- **Honest capture stays cheap:** capture-first is unchanged — an agent
  unsure of a claim writes it *with* `*(inferred)*` instead of silently
  writing it as fact or silently dropping it.

## Anti-patterns

- **Tag-everything.** Only load-bearing claims (rule 1). A wall of tags
  is as unreadable as a wall of hedges.
- **Decorative tags.** If no tool consumes them and no ritual upgrades
  them, they rot into noise. Ship the worklist tool with the convention.
- **Stale citations.** `code:` line numbers drift like `affects:` globs.
  A drift sweep that touches an article re-checks its `code:` citations
  (cheap: the cited line moved → re-cite).
- **Provenance as blame.** Tags grade *claims*, not authors. `inferred`
  is an honest, first-class state — the failure is untagged inference,
  never the tag.

## Adoption path

Seeded as this article + the `provenance-report` tool. Deliberately **not**
yet folded into the published guides or templates — per this repo's own
phased convention, that happens after field validation in a production
adoption *(reported: ROADMAP "Candidate refinements", 2026-07-22)*. Fold-in
targets when validated: `LIVING_DOCS_OVERVIEW.md` decision rule 4 (done —
pointer only), the two adoption guides' article-writing sections, and the
`templates/*/CLAUDE.md` starter rules.
