---
title: "Living Documentation Methodology — Overview"
subtitle: "Meta-document for AI-assisted codebases; pairs with the greenfield and brownfield adoption guides"
type: overview
audience: AI agent in workspace context, tech leads, contributors new to the methodology
companion-docs:
  - GREENFIELD_ADOPTION_GUIDE.md
  - BROWNFIELD_ADOPTION_GUIDE.md
---

# Living Documentation Methodology — Overview

A meta-document for AI-assisted codebases. Reading this alongside `GREENFIELD_ADOPTION_GUIDE.md` and `BROWNFIELD_ADOPTION_GUIDE.md` should give an agent enough context to reason about **how** to apply living documentation to any repo or workspace it encounters, and **which** of the two operational guides to follow.

## What this methodology is

Living documentation is a `knowledge/` directory at the project root, treated as the **source of truth** alongside the code. Articles describe behaviour, architecture, and rationale. The discipline that keeps documentation correct over time: **every code change that alters behaviour, config, or architecture updates the relevant article in the same task**. The rule is encoded in `CLAUDE.md` so an AI agent reads it on every interaction and enforces it by default.

The economic premise: writing and updating documentation used to be expensive enough that human teams skipped it under deadline pressure. With AI agents in the loop, that cost has collapsed. The discipline humans struggled to maintain is now cheap to enforce — because the agent does most of the article-writing work as part of the same change that produces the code.

## First principle — capture first, refine second

**Never miss a change in the documentation.** When the agent makes a code change that affects behaviour, config, or architecture, the corresponding article (and the rationale behind the change) gets written **in the same task** — even if the placement, naming, or scope of the article is uncertain. An imperfect article the user can review and refine is strictly better than a correctly-placed gap.

The asymmetry is what makes this rule load-bearing: a missed capture is unrecoverable (six months later, no one remembers the why), while an imperfect capture costs minutes of review time to refine. The agent should default to writing.

Three corollaries the agent should apply directly:

- **When in doubt whether to update an article: update it.** Small refactors often have invisible knock-on effects on rationale. Better a redundant paragraph than a silent gap.
- **When in doubt about placement: pick the closest fit and write.** The user can move the file on review; they cannot retroactively reconstruct reasoning that was never captured.
- **When in doubt about scope: capture the why, not just the what.** Code preserves the *what*. Documentation's unique value is the *why* — constraints, alternatives ruled out, customer incidents that drove the decision. Skew toward more rationale.

The agent ensures something exists. The user reviews and refines. Missing context is unrecoverable; refining an imperfect article costs minutes.

## Core mechanics

Three load-bearing pieces:

1. **The same-task rule.** Encoded in `CLAUDE.md`. Every behaviour-altering change updates the matching article in the same PR/task — not "later." The rule is enforced by the agent reading `CLAUDE.md` on every interaction.
2. **The article-mapping table.** A table in `CLAUDE.md` of the form: "When you change X, update article Y." The agent uses this to identify which article corresponds to which code path. Empty at the start of a brownfield retrofit; written before code in greenfield.
3. **The compile log (`log.md`).** A dated, append-only log of changes and which articles were touched. Captures architectural narrative and rationale that git commit messages don't preserve.

Two file conventions:

- **`knowledge/concepts/{area}/*.md`** — atomic articles describing *what something is and why*. Grouped by subject area (project internals, external systems, tooling, project context).
- **`knowledge/connections/*.md`** — cross-cutting articles describing *how multiple concepts interact*. These are the only articles that span beyond a single concept.

## Choosing the adoption path

Decision tree the agent should walk when asked to set up or evaluate this methodology:

### Step 1 — Greenfield or brownfield?

| Indicator | Path |
| --- | --- |
| Empty or near-empty repo; no substantial committed code; "starting a new project" framing | **Greenfield** → use `GREENFIELD_ADOPTION_GUIDE.md` |
| Established codebase with prior commits; existing wiki/README/design docs; team has established habits | **Brownfield** → use `BROWNFIELD_ADOPTION_GUIDE.md` |
| Mixed (new feature on an old codebase) | **Brownfield**, but apply the greenfield mindset to the new feature's articles |

Greenfield articles can drive design decisions (write the architecture article, then build it). Brownfield articles describe state that already exists; documentation is written reactively as code is touched, never via a sprint.

### Step 2 — Single repo or multi-repo workspace?

| Workspace shape | Knowledge layout |
| --- | --- |
| Single repo | All knowledge at the repo level: `repo/CLAUDE.md` + `repo/knowledge/`. No workspace layer. |
| Multi-repo, **loosely coupled** repos (no cross-repo articles ever needed) | All knowledge at the repo level. **Don't** add a workspace layer just because there are multiple repos. |
| Multi-repo, **tightly coupled** repos (call each other, share a deployment, consume a common contract) | Hybrid: primary `CLAUDE.md` + `knowledge/` at each repo's root; **thin** `CLAUDE.md` + `knowledge/connections/` (only) at the workspace root. See the multi-repo section of `BROWNFIELD_ADOPTION_GUIDE.md` for the full pattern. |

Indicators repos are tightly coupled: one calls the other, they share a deployment, they consume a common contract, or you'd want to write a single article that references both repos' internals in the same paragraph.

### Step 3 — How mature is the team's discipline?

| Phase | Agent posture |
| --- | --- |
| **First adoption** (months 1–3) | Assume team buy-in is fragile. Default to the most conservative interpretation of the same-task rule. Don't write speculative articles. The agent should do most of the article writing so the human cost stays near zero. |
| **Established** (3+ months in) | Team has internalized the rule. The agent can be more proactive: flag potential drift, suggest new connections, propose splits/merges of articles. |

## Universal anti-patterns

These apply regardless of greenfield/brownfield, single/multi-repo, or maturity:

1. **Don't run a documentation sprint.** Two weeks of writing followed by silence produces a stale archive. The methodology depends on continuous, gradual accumulation. Energy that doesn't sustain is worse than no energy.
2. **Don't put concept articles at the workspace level.** They strand when repos move to a different workspace. Repo-level is always the source of truth for repo-specific concepts.
3. **Don't skip article updates "just this once."** The rule erodes from any single exception under pressure. Make the agent do the article update so the human cost is near zero, and the temptation disappears.
4. **Don't paraphrase the article and the code separately.** When the article and the code disagree, the code wins (it's the actual behaviour) — but the article gets fixed in the same task, not "later." "Real data beats the article" is the disambiguating rule.
5. **Don't write tutorials when concept articles are needed.** A concept article describes *what something is and why*. Tutorials describe *how to use something*; that's usually demonstrated by tests and code, not by documentation. Tutorials in `knowledge/` are a smell.
6. **Don't duplicate articles between repo and workspace levels.** Pick one home per concept and link from the other if needed.
7. **Don't index speculatively.** The article-mapping table grows from real articles. Listing aspirational mappings whose articles don't exist degrades trust.

## Decision rules for the agent

### When operating within the methodology (any code change)

The first-principle rule applies throughout: **default to writing**. When uncertain, write the article update; the user reviews.

1. Check for `CLAUDE.md` at the repo level (and possibly workspace level). Follow its rules; lower-scope rules take precedence over higher-scope ones.
2. Identify whether the change touches a module that has an existing article in the article-mapping table. If yes, update the article in the same task. **When in doubt whether the change is "documentation-relevant," treat it as relevant.**
3. If the change touches code with no matching article in the mapping table, **write the first thin article in the same task** — regardless of whether the change is "non-trivial" by any narrow definition. Place it as:
   - `concepts/{project-area}/{topic-kebab-case}.md` for an internal concept of this project.
   - `concepts/{external-system}/{topic}.md` for an external integration. Create a new area subdirectory if the topic introduces a system not yet covered.
   - `connections/{topic}.md` for a cross-cutting article that describes how multiple existing concepts interact (rather than describing one of them).

   When unsure between two placements, pick the closest fit and write the article. The user can move it on review; the article existing is what matters.

   Then add a row to the article-mapping table in `CLAUDE.md` so future changes to the same code path know where to update.
4. **Capture the why, not just the what.** The article should record context, constraints, and alternatives considered — not only the post-change state of the code. The code preserves the *what*; only the article preserves the *why*.
5. Append a one-line entry to `log.md` summarizing what was touched.
6. Quick drift check: scan recently-changed code paths against their articles for contradictions; surface mismatches.

### When asked to set up or adopt the methodology

1. Determine greenfield/brownfield (Step 1 above) → choose the appropriate adoption guide.
2. Determine workspace shape (Step 2) → choose single-repo or hybrid layout.
3. Walk through the chosen guide's steps in order, checking back with the user at each major decision (especially Step 1 in either guide: team buy-in).

### When asked to evaluate an existing setup

1. Inventory: is there `CLAUDE.md`? Is there `knowledge/`? Is there an article-mapping table? Is there a compile log?
2. Check the same-task rule's enforcement: pick a recent PR, examine whether it touched articles alongside code.
3. Run a drift sweep on the 5 oldest articles by `updated:` date.
4. Report: maturity phase, gaps, suggested next move.

## Companion documents

- **`GREENFIELD_ADOPTION_GUIDE.md`** — full step-by-step for new projects, including a starter `CLAUDE.md` template and rationale for each step.
- **`BROWNFIELD_ADOPTION_GUIDE.md`** — full step-by-step for existing projects, including the "document on touch" mindset, the drift-sweep ritual, the failure-mode catalog, and the multi-repo workspace pattern with sample workspace `CLAUDE.md`, `index.md`, and `connections/` article.

Both companion guides are **operational** (they tell you how to do it, step by step). This overview is **meta** (it tells the agent *why* each rule exists, *which* guide to apply, and *what* anti-patterns to avoid in any variant).

## One-paragraph stakeholder summary

Living documentation makes the documentation as durable as the code by tying their updates together. Every code change updates the matching article in the same task; an AI agent enforces the rule from `CLAUDE.md` so the discipline survives deadline pressure. The result is documentation that actually mirrors the code — which means new hires onboard faster, departing teammates leave less unrecoverable context behind, and architectural reasoning persists in writing rather than evaporating from memory. The investment is roughly 10–20% per task during the conscious-effort phase (first 3–4 months); after that, the team stops thinking about it consciously and `knowledge/` becomes the place people actually go when they have a question.
