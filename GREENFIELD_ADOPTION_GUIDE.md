---
title: "Living Documentation for Greenfield Projects"
subtitle: "A setup guide for applying the knowledge-base methodology to a brand-new codebase"
type: guide
audience: tech leads, senior engineers, agents setting up a new repo
companion-docs:
  - LIVING_DOCS_OVERVIEW.md
  - BROWNFIELD_ADOPTION_GUIDE.md
---

# Living Documentation for Greenfield Projects

A practical guide for adopting the **living-knowledge-base** methodology on a brand-new codebase. Greenfield is the easier of the two adoption paths — you have a clean slate, no calcified habits, and articles can drive design decisions rather than describe pre-existing ones. This guide walks through how to set it up so the discipline takes root from day one and grows naturally with the code.

For the methodology overview (decision tree, anti-patterns, agent decision rules), see `LIVING_DOCS_OVERVIEW.md`. For the harder retrofit case (existing codebase, established habits, partial documentation), see `BROWNFIELD_ADOPTION_GUIDE.md`.

## What the methodology is (one-paragraph recap)

A `knowledge/` directory at the project root, treated as the source of truth alongside the code. Articles in `concepts/` (atomic) and `connections/` (cross-cutting), an `index.md`, and a dated `log.md`. The discipline: **every code change that alters behaviour, config, or architecture updates the relevant article in the same task**, with the rule encoded in `CLAUDE.md` so an AI agent enforces it on every interaction. Reading the rule on every change makes the rule durable in a way human discipline alone has never been.

## Why greenfield is the easier path

Three things you have on a fresh project that you don't have on a retrofit:

1. **Articles can drive design, not describe state.** Writing the architecture article before the architecture exists forces you to design the architecture. The article isn't transcription; it's an artifact of decision.
2. **No calcified habits to fight.** The same-task rule is "how things have always been done here" instead of a new constraint imposed mid-project. Onboarding new contributors is teaching, not retraining.
3. **No partial documentation to reconcile.** No wiki, no orphaned README sections, no design docs that may or may not be current. The first source of truth is `knowledge/`.

The result is that greenfield adoption is conscious effort for maybe the first six weeks, and then it's just how the project works. Brownfield adoption typically takes three to four months to feel native.

## Two mindset shifts before any of the steps

These matter more than any specific step. (See also `LIVING_DOCS_OVERVIEW.md` for the first principle that informs both: **capture first, refine second** — when in doubt, write the article; the user reviews and overrides. Missing context is unrecoverable; an imperfect article costs minutes.)

### 1. Articles before code, when feasible

For each major component, write a thin article (200–500 words) describing what it will be and why **before** the code exists. The act of writing the article is the design step. By the time you sit down to implement, you've already worked out the boundaries, the data flow, and the trade-offs in prose. The implementation becomes the dual of the article.

This isn't always possible — small modules, refactors, exploratory spikes — and that's fine. But for the load-bearing components (architecture, primary workflow, data models, agent design, key external integrations), writing the article first is worth the modest discipline.

### 2. The agent does most of the writing, from day one

Don't try to write all the documentation yourself. Once `CLAUDE.md` is in place, ask the agent to draft articles from the code (or vice versa: ask the agent to draft code from an article you've sketched). Edit the result. The cost of producing and maintaining articles drops dramatically when the agent carries most of the keystrokes — and the discipline only sustains if that cost stays low.

## The steps, in order

### 1. Drop in `CLAUDE.md` before substantial code exists

This is the single most important step. The instruction file is what holds the system together. Drop a `CLAUDE.md` placeholder at the project root before the codebase is more than a few files. Sample template at the end of this guide.

If you write the code first and add the instruction file later, you'll be fighting habits — both your own and the agent's. Establishing the contract early means every code-writing session from day one already includes documentation updates.

### 2. Lay out the `knowledge/` directory skeleton

Create the structure:

```text
knowledge/
├── concepts/
│   ├── {your-project-name}/      # internal concepts
│   └── {first-external-system}/  # external integrations
├── connections/
├── index.md                       # navigation hub
└── log.md                         # dated compile log
```

The two-tier split — your project's internals as one concept group, each external system you integrate with as its own group — maps cleanly to almost any project. Add more groups as you go (`tooling/` for cross-cutting research, `project/` for stakeholder-and-roadmap material).

The structure is a forcing function. When you start writing about something, you have to decide where it goes. That decision (this is internal vs. external; this is a single concept vs. a connection) clarifies the topic in your head before the first sentence.

### 3. Pick a frontmatter convention and stick to it

Each article gets YAML frontmatter:

```yaml
---
title: "Webhook Data Models"
aliases: [models, schemas]
tags: [data, validation]
sources: []
created: 2026-04-25
updated: 2026-04-25
---
```

Don't overthink it. Pick five or six fields and use them consistently. Consistency is what lets future tooling — even just `grep` — work reliably, and it's what makes Obsidian, Logseq, or any PKM tool render the graph automatically.

### 4. Write the first batch of articles before most of the code

Pick the 5–7 concepts that **will** exist when the project is real, and write the first thin draft of each before the code is fleshed out:

- Architecture: what the layers are and why
- Data models: the main shapes flowing through the system
- The first workflow: trigger → outcome
- Each external integration: the integration shape, not an API encyclopedia
- Local development: how someone else gets the thing running

A "thin draft" can be 200 words. The point is to commit to the topic and the boundaries, not to be exhaustive. You'll expand and refine as the code lands.

This step is where the methodology's biggest greenfield advantage lives: articles drive design. Treat the writing as design work, not documentation work.

### 5. Establish the index and compile log on the first commit

`index.md` is a table grouping articles by area, with one-line summaries and an "updated" date column. `log.md` starts with a single dated entry: "compile: initial knowledge base." Both files are tiny but load-bearing.

The index gives a stranger (or future-you, three months from now) a starting point. The compile log gives a chronological story of decisions, which `git log` only approximates because git tracks files, not topics.

### 6. Populate the article-mapping table in `CLAUDE.md`

Inside `CLAUDE.md`, write a table:

| When you change... | Update this article |
| --- | --- |
| The webhook routing logic | `concepts/{project}/classification-workflow.md` |
| A Pydantic model | `concepts/{project}/webhook-data-models.md` |
| The LLM prompt or agent config | `concepts/{project}/classification-agent.md` |
| {External system} webhook handling | `concepts/{system}/{system}-webhooks.md` |
| ... | ... |

This table is the heart of the agent's day-to-day behaviour. When the agent is editing your code and asks itself "did anything I just changed need to update an article?", this table tells it the answer.

Greenfield advantage: you can populate the table from day one. Each row corresponds to an article you've already written (step 4) and a code path you're about to write. Brownfield retrofits start with an empty table; greenfield starts with a real one.

### 7. Use the agent for both code and docs from now on

Once the contract is in place, lean into it. When you ask the agent to add a feature, it should automatically:

- Write the code change.
- Update the matching article(s) per the mapping table.
- Append an entry to `log.md` summarizing what was touched.
- Optionally run the drift check (step 8).

You can be lazy with prompts — _"add caching to the customer search"_ — and get correct documentation as a side effect, because the rule says so.

The cost asymmetry inverts here. Writing docs is now cheap because the agent does it as part of the same task. Skipping is no longer the easier path. The economics finally favour good docs.

**When the agent encounters code without a matching article.** Even on a greenfield project, the article set won't stay in sync with the code forever — new modules, new external integrations, and new cross-cutting concerns will emerge after the initial batch. When the agent makes a change to a code path that has no entry in the article-mapping table, the agent should:

1. Determine where the article belongs:
   - `concepts/{project-area}/{topic-kebab-case}.md` for an internal concept.
   - `concepts/{external-system}/{topic}.md` for an external integration; create the area subdirectory if it's a new system.
   - `connections/{topic}.md` for a cross-cutting article describing how multiple concepts interact.

   When unsure between placements, pick the closest fit and write the article. The user moves it on review.
2. Write a first thin article (200–500 words) in the same task — capturing the *why* (context, constraints, alternatives ruled out), not only the post-change state of the code.
3. Add a row to the article-mapping table.
4. Note the addition in `log.md`.

This is the same behaviour as brownfield's "document on touch" — it just happens less often on greenfield because the article set was complete at the start. The first principle still holds: never miss a change; the user can always review and override.

### 8. Do the drift check at the end of every substantive task

Add this to your `CLAUDE.md`:

> After finishing implementation, ask: "does anything in `knowledge/` now contradict what I just built?" Check signatures, field lists, config tables, folder structure, and env var names. **Real data beats the article** — if a field the article says is required turns out to be absent in real payloads, update the article to match reality, not the other way around.

The same-task rule (step 7) catches direct effects. The drift check catches indirect ones — a refactor touches files the mapping table doesn't list, or an external API turns out to behave differently than the article assumed. Without it, the system is 90% reliable, which sounds good until you realize the 10% accumulates over a year.

## Sample `CLAUDE.md` for a greenfield project

Drop this in as a starter, replacing the `{{...}}` placeholders. The article-mapping table is populated from day one based on the articles you wrote in step 4.

```markdown
# {{Project Name}}

{{One-paragraph project description.}}

## Source of Truth

The knowledge base in `knowledge/` is the source of truth for this project.
It must always mirror the code. Entry point: `knowledge/index.md`.
Compile log: `knowledge/log.md`.

### The rule

Every code change that alters behaviour, config, models, or architecture
must update the relevant `knowledge/concepts/*.md` article(s) in the same
task and append an entry to `knowledge/log.md`. Don't batch knowledge
updates for later.

### What lives where

| Location | Contains | Authority |
| --- | --- | --- |
| `knowledge/concepts/` | Standalone reference articles, grouped by area | How each thing works and why |
| `knowledge/connections/` | Cross-concept articles | How the pieces fit together |
| `src/{{your-package}}/` | Implementation | What the system does |
| `tests/` | Tests with sanitized fixtures | Testable behaviour |
| `.env` | Real credentials (gitignored) | Local config |

### Article mapping — update these when the matching code changes

| When you change... | Update this article |
| --- | --- |
| Folder structure or layer boundaries | `concepts/{{project}}/platform-architecture.md` |
| A data model (field added/removed/required-flipped) | `concepts/{{project}}/data-models.md` |
| The main workflow logic | `concepts/{{project}}/{{workflow-name}}-workflow.md` |
| The LLM agent or its tools | `concepts/{{project}}/{{agent-name}}-agent.md` |
| Webhook handling for {{external-system}} | `concepts/{{external-system}}/{{system}}-integration.md` |
| Env vars, per-environment config | `concepts/{{project}}/configuration.md` |
| Local dev setup, sandbox, replay tools | `concepts/{{project}}/local-development.md` |
| Test conventions, fakes, fixtures | `concepts/{{project}}/testing-strategy.md` |

### How to catch drift

After finishing implementation, ask: "does anything in `knowledge/` now
contradict what I just built?" Check signatures, field lists, config
tables, folder structure, and env var names. Real data beats the article
— if a field the article says is required turns out to be absent in
real payloads, update the article to match reality, not the other way
around. Add a compile entry to `knowledge/log.md` listing the articles
touched.

## Project Structure

```
{{outline of src/, tests/, config/, etc.}}
```

## Key Commands

```bash
{{your-package-manager}} install
{{your-test-runner}}
```
```

Add more sections — production-safety rules, deployment notes, key business invariants — as the project develops. The article-mapping table is the load-bearing piece; keep it accurate.

## Anti-patterns specific to greenfield

The universal anti-patterns in `LIVING_DOCS_OVERVIEW.md` apply. Two are worth specifically calling out for greenfield:

- **Don't over-architect the article structure before there's content.** A directory tree with twelve subdirectories and zero articles is procrastination. Start with two or three groups; split when you actually have enough material to justify the split.
- **Don't write tutorials disguised as concept articles.** When the codebase is fresh and small, the temptation to write "how to use X" is strong. Resist it. Concept articles describe *what something is and why*; "how to use" is what code, tests, and the README are for.

## What success looks like at month two

Greenfield adoption is faster than brownfield because there's nothing to undo. By month two you should observe:

- New contributors read 3–5 articles and can answer architectural questions without reading much source.
- The article-mapping table is broadly populated; new articles are added rarely (most code paths already have one).
- The agent's code changes routinely include article updates with no prompting.
- The compile log reads as a coherent project narrative end-to-end.
- Architectural questions get asked once; the answer ends up in an article instead of a Slack thread.

If any of these aren't happening by month two, look at step 1 (was `CLAUDE.md` actually in place from day one?) and step 7 (is the agent actually being used to maintain the docs, or is the team writing them by hand and tiring of it?).

## A note on team size

This guide assumes a small-to-medium engineering team (1–10 developers). The same-task rule and the article-mapping table are easier to maintain at this scale. For larger teams (20+), the rule still works but the article-mapping table becomes a shared vocabulary that needs explicit ownership — usually a tech lead or staff engineer who reviews article changes the same way they review architectural decisions. The discipline doesn't change; the social mechanism around it does.

## A note on multi-repo workspaces

If your greenfield work spans multiple repos that interact (e.g., a service plus a separate client library, or a monorepo split into deployable artifacts), the right shape is **hybrid**:

- Each repo gets its own `CLAUDE.md` and `knowledge/` (primary).
- The workspace root gets a thin `CLAUDE.md` and `knowledge/connections/` (only if the repos genuinely interact).

This applies the same way for greenfield as for brownfield. For the full pattern — including sample workspace-level `CLAUDE.md`, `index.md`, and `connections/` article templates — see the "A note on multi-repo workspaces" section in `BROWNFIELD_ADOPTION_GUIDE.md`. The guidance is identical regardless of whether the repos are new or existing.

If your repos are loosely coupled (no cross-repo articles ever needed), skip the workspace layer entirely. Each repo stands alone.

## Closing thought

Greenfield adoption is the easiest version of this methodology because every advantage compounds: articles drive design instead of describing it, no habits need unlearning, the article-mapping table is correct from day one, and the agent carries the discipline before any human gets tired of it. Six weeks of conscious work usually buys you a project that feels documented natively for the rest of its life.

The single best predictor of success is whether `CLAUDE.md` was in place from the first significant commit. The single best predictor of failure is treating the first batch of articles as documentation work rather than design work. Write articles to figure out what you're building, not to record what you've already built — and let the agent handle the keystrokes.
