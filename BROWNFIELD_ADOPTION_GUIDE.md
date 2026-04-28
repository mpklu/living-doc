---
title: "Living Documentation for Brownfield Projects"
subtitle: "A retrofit guide for applying the knowledge-base methodology to an existing codebase"
type: guide
audience: tech leads, senior engineers
---

# Living Documentation for Brownfield Projects

A practical guide for retrofitting the **living-knowledge-base** methodology onto a codebase that already exists. Greenfield adoption is straightforward: drop in `CLAUDE.md` on day one, write articles before the code, let the agent enforce the rule from the start. Brownfield adoption is harder — there's existing code, existing habits, existing partial documentation, and no fresh slate. This guide walks through how to do it without setting yourself up for failure.

## What the methodology is (one-paragraph recap)

A `knowledge/` directory at the project root, treated as the source of truth alongside the code. Articles in `concepts/` (atomic) and `connections/` (cross-cutting), an `index.md`, and a dated `log.md`. The discipline: **every code change that alters behaviour, config, or architecture updates the relevant article in the same task**, with the rule encoded in `CLAUDE.md` so an AI agent enforces it on every interaction. Reading the rule on every change makes the rule durable in a way human discipline alone has never been.

## Why brownfield is harder than greenfield

Three distinct frictions you don't have on a fresh project:

1. **You're documenting state, not designing it.** Greenfield articles drive design decisions ("write the architecture, then build it"). Brownfield articles describe decisions that have already calcified — you're transcribing reality, not authoring it.
2. **Existing habits resist new rules.** Developers under deadline pressure have established workflows. The same-task rule adds 10–20% to every task, and that friction lands hardest on the team that's been shipping fastest without it.
3. **Partial documentation already exists.** A wiki, README, design docs, comments. None of it is the source of truth, but pretending it doesn't exist erodes trust. You have to deal with it.

The good news: with the right ordering, all three frictions resolve naturally. The wrong ordering makes them compound.

## Two mindset shifts before any of the steps

These matter more than any specific step. (See also `LIVING_DOCS_OVERVIEW.md` for the first principle that informs both: **capture first, refine second** — when in doubt, write the article; the user reviews and overrides. Missing context is unrecoverable; an imperfect article costs minutes.)

### 1. You cannot retrofit the past, only the future

The methodology works for new changes starting the day you adopt it. Code that nobody touches stays undocumented until someone touches it. **Resist the urge to launch a "documentation sprint."** Documentation sprints almost always fail — they produce a burst of articles in two weeks that nobody updates afterward, leaving you with a stale archive that's worse than no documentation at all.

### 2. Document on touch, not on inventory

When a developer changes a module, they write or update its article in the same task. Stable code without articles is fine. Articles get created reactively, not proactively. This is the operational principle that makes the discipline sustainable on a large existing codebase — it scales coverage without requiring a separate documentation effort.

If you internalize these two, the steps below largely follow.

## The steps, in order

### 1. Get team buy-in first — or skip the rest

The same-task rule won't survive a deadline-pressured sprint without explicit team agreement. Make the case (the blog post, this guide, or your own version), get acknowledgment (Slack thumbs-up is enough), and ideally name one person responsible for keeping the discipline alive for the first 2–3 months. Without buy-in, every later step is wasted effort.

### 2. Drop in `CLAUDE.md` with the rule — empty article-mapping is fine

Even before any articles exist. The rule belongs in the agent's instruction file from day one of adoption. The article-mapping table starts empty and grows as articles are created. Don't try to populate it speculatively; the table is allowed to be a stub for weeks.

A starter `CLAUDE.md` fragment for a brownfield project:

```markdown
## Source of Truth

The knowledge base in `knowledge/` is the source of truth for this project.
It must always mirror the code. Entry point: `knowledge/index.md`.
Compile log: `knowledge/log.md`.

### The rule

Every code change that alters behaviour, config, models, or architecture
must update the relevant `knowledge/concepts/*.md` article(s) in the same
task and append an entry to `knowledge/log.md`.

If the affected area does not yet have an article, write the first thin
article in the same task. Don't batch knowledge updates for later.

### Article mapping

(Populated as articles are created — this is a brownfield retrofit, so
the table grows from empty over the first 2-3 months.)

| When you change... | Update this article |
| --- | --- |
| _(empty — populate as articles emerge)_ | |

### How to catch drift

Real data beats the article. If a field the article says is required
turns out to be absent in real payloads, update the article to match
reality, not the other way around. Add a compile entry to log.md.
```

### 3. Create the empty `knowledge/` skeleton

```text
knowledge/
├── concepts/
├── connections/
├── index.md    # one line: "knowledge base under construction — retrofit start: YYYY-MM-DD"
└── log.md      # one entry: "established knowledge base, retrofit begin"
```

Empty is fine. Existence beats content. The directory has to exist for the agent's instruction file to compile cleanly.

### 4. Pick exactly one seam — don't try to cover the whole codebase

The biggest retrofitting mistake is starting an inventory. Pick one of:

- **Hot-spot:** the 2–3 modules currently under active development.
- **Upcoming feature:** the next feature you'll build; write its article-set alongside the code as if it were greenfield.
- **Onboarding question:** the next question a teammate asks ("how does X work?"). Answering it becomes the first article.

Pick **one**. Articles created here become the seed.

### 5. Write the first 3–5 articles for the chosen seam

A first article can be 200 words. Don't aim for completeness; aim for accuracy about the seam. As each article lands, add a row to the article-mapping table in `CLAUDE.md`. The table grows from a stub to a real index over the first month.

### 6. From this point — the same-task rule applies to any change in a documented area

Now the discipline starts pulling its weight. When a developer touches a module that has an article, they update the article in the same PR — and the agent does most of that update for them.

If they touch a module that doesn't have one yet, they write the first thin article in the same PR. **Default to writing**, even when the change feels small — the first-principle rule (capture first, refine second) means an imperfect article that the user reviews is always better than a missed one. Place the new article as:

- `concepts/{project-area}/{topic-kebab-case}.md` for an internal concept.
- `concepts/{external-system}/{topic}.md` for an external integration; create a new area subdirectory if the system isn't already covered.
- `connections/{topic}.md` for a cross-cutting article describing how multiple existing concepts interact.

When unsure between placements, pick the closest fit and write. The user moves it on review. Add a row to `CLAUDE.md`'s article-mapping table at the same time, and capture the *why* in the article — context, constraints, alternatives considered — not just the post-change state of the code.

### 7. Don't back-fill globally — back-fill on touch

Module Z has no article and you want to change Z next week. **That's** the moment to write Z's first article — capturing the post-change state and the change rationale together. Not before. Articles for code nobody is touching can wait. This is what makes brownfield adoption sustainable.

### 8. Migrate existing docs lazily

If you have a wiki, README sections, design docs, or comments-as-docs:

- Don't migrate proactively.
- When someone touches a topic, fold the relevant legacy doc into the new article (often as the seed) and link out from where it lived.
- Mark the legacy doc with a "superseded by `knowledge/concepts/X.md`" note so future readers don't waste time on it.
- Old docs that nobody touches stay where they are. The methodology doesn't claim they're wrong; only that they aren't the source of truth going forward.

### 9. Add a "knowledge updated?" checkbox to the PR template

Tiny operational change with outsized effect. Even when the agent writes the article update automatically, the human author confirming it on the PR makes the rule real. Reviewers can hold the line on the same checkbox if needed.

Sample PR template addition:

```markdown
## Pre-merge checks

- [ ] Tests pass
- [ ] Linter passes
- [ ] **Knowledge updated** — did this change affect anything covered by an article in `knowledge/`? If yes, the matching article and `log.md` are updated in this PR. If the affected area is not yet covered, a first thin article has been written.
```

### 10. Establish a periodic drift sweep

Once a sprint or once a month, spend ~30 minutes scanning recently-changed files against their corresponding articles. Articles that drifted (the same-task rule slipped on a particular PR) get fixed; the fix is logged in `log.md`. This is the safety net for the cases where the rule wasn't followed perfectly.

A simple drift-sweep ritual:

1. List articles by `updated:` frontmatter date, oldest first.
2. For the oldest 5: open the article, open the corresponding code path, scan for contradictions (signatures, field names, env vars, config keys).
3. Fix any drift found, bump the `updated:` date, log the sweep in `log.md`.
4. Stop after 30 minutes. Whatever's left waits for next sweep.

### 11. Watch for three specific failure modes

- **The "documentation sprint" trap.** Two intense weeks of writing, then silence. If you see this pattern, slow the team down — that energy doesn't sustain. One article per task, forever, is healthier than 50 articles in a week and zero after.
- **The stale archaeological article.** An article written six months ago when someone last touched module X may be wrong now if X changed in the meantime via someone who hadn't yet internalized the rule. The drift sweep catches this; expect the first sweep after retrofit to find more drift than later ones.
- **The "this rule is too strict" rebellion.** Eventually someone pushes back: _"I need to ship this fix, I don't have time to update an article."_ Leadership has to absorb the friction here, or the rule erodes. The countermove: make the agent generate the article update so the human cost stays near zero. If a PR's article update takes more than two minutes of human attention, something is wrong with the workflow, not the rule.

### 12. After 2–3 months, evaluate honestly

Look at `knowledge/`:

- What fraction of the **active** codebase (the parts being changed) has articles? Aim for 60–80% by month three. The inactive parts can stay undocumented; that's the whole point of "document on touch."
- Does the drift sweep find a small number of errors (a few per month) or many?
- Is the compile log readable end-to-end as a project narrative?

If yes on all three: the methodology has taken root. Continue and let coverage grow naturally.

If no: figure out which step is breaking. It's almost always step 1 (buy-in eroded under pressure) or step 6 (the same-task rule isn't being enforced on PRs). Re-establish those before adding more articles.

## What success looks like at month four

When the methodology is working on a brownfield project, you'll notice:

- New hires read 3–5 articles and can answer architectural questions on day two, instead of crawling through a year of pull requests.
- When a developer asks "why does this work this way?", the answer is in `log.md` with a date.
- The team stops thinking about the rule consciously — it's just how PRs get reviewed.
- Active code is well-covered (60–80%); stable, untouched code is still mostly undocumented, and that's fine.
- A departing developer can hand off cleanly because the architectural reasoning lives in articles, not in their head.

If you're not seeing these by month four, look at steps 1 and 6 — those are the two that fail under pressure.

## A note on team size

This guide assumes a small-to-medium engineering team (1–10 developers). The same-task rule and the article-mapping table are easier to maintain at this scale. For larger teams (20+), the rule still works but the article-mapping table becomes a shared vocabulary that needs explicit ownership — usually a tech lead or staff engineer who reviews article changes the same way they review architectural decisions. The discipline doesn't change; the social mechanism around it does.

## A note on multi-repo workspaces

If your team works across multiple related repos — distributed systems, microservices, or any platform with multiple deployable artifacts — the question of where `CLAUDE.md` and `knowledge/` live becomes load-bearing. This is also the most common pattern when developers use a single workspace folder and add or remove repo subdirectories as their focus shifts.

The right answer is **hybrid, weighted heavily toward the repo level**.

### Layout

```text
workspace/
├── CLAUDE.md                # thin — workspace-level conventions only
├── knowledge/
│   ├── connections/         # ONLY cross-repo articles that need both repos to make sense
│   ├── index.md
│   └── log.md
├── repo-a/
│   ├── CLAUDE.md            # primary — full repo-a rules and article-mapping
│   ├── knowledge/           # all repo-a concepts
│   └── src/...
├── repo-b/
│   ├── CLAUDE.md
│   ├── knowledge/
│   └── src/...
└── repo-c/                  # may be added or removed as work shifts
    ├── CLAUDE.md
    ├── knowledge/
    └── src/...
```

### Why repo-level is primary

- **Repos travel with their docs.** When a repo is cloned standalone or moved to a different workspace, its documentation must come with it. Workspace-only knowledge orphans the moment a repo leaves.
- **Cloning is the lowest common denominator.** A teammate who clones one repo without your workspace setup must still get a coherent experience from that repo's `CLAUDE.md` and `knowledge/` alone.
- **Article-mapping is naturally repo-scoped.** "Change `src/X` → update `concepts/X.md`" only makes sense relative to one repo's tree.

### What goes at the workspace level

Only two kinds of content:

1. **Workspace `CLAUDE.md`** — thin, supplementary. Team-wide conventions and cross-repo workflow rules. Augments, never overrides repo-level rules.
2. **Workspace `knowledge/connections/`** — cross-repo articles whose premise requires multiple repos to be co-present. Use relative wiki-links to repo-level concept articles. Broken links when a repo is removed are correct behaviour — the article's premise no longer holds.

### What does NOT go at the workspace level

- Concept articles for any single repo (even when it would be "convenient")
- Duplicates of repo-level articles
- Article-mapping tables that span repos
- Per-repo compile logs

The temptation to put concept articles at the workspace level for convenience is the strongest single pitfall. It looks tidier today; it strands repos when they move tomorrow.

### Survival under drop / remove workflows

- **Add a repo:** brings its own `CLAUDE.md` and `knowledge/`. Claude reads them when working in that repo.
- **Remove a repo:** takes its docs with it. Workspace connection articles referencing it appear broken — correct signal that those articles' premise no longer holds.
- **Move a repo to a different workspace:** docs go with the repo; the new workspace builds its own connections layer.

The one ritual: when removing a repo, scan `workspace/knowledge/connections/` for references and either delete affected articles or mark them "premise no longer holds in this workspace" with a date.

### When to skip the workspace layer entirely

If your repos are loosely coupled enough that you'd never write a connection article, **don't bother with workspace-level knowledge**. Each repo stands alone; Claude reads the right CLAUDE.md based on which repo you're working in. You only need the workspace layer when:

- Multiple repos genuinely interact (one calls another; they share a deployment; they consume a common contract)
- You'd want to write an article mentioning multiple repos' internals in one paragraph
- You're doing cross-repo refactors that span PRs in two repos at once

If none apply, skip the workspace layer. You can always add it later when a real connection emerges.

### Sample: workspace `CLAUDE.md`

```markdown
# Workspace conventions

This workspace contains multiple related repos. Each repo's own
`CLAUDE.md` is authoritative for that repo. This file adds
workspace-level rules that apply across all of them.

## Repo-level rules take precedence

When working inside a repo's directory, that repo's `CLAUDE.md` is the
primary source. The rules below augment, never override.

## Cross-repo rules

- When changing repo-a's public API surface, check repo-b's clients of
  it (search for `from repo_a` in `repo-b/src/`) and raise a
  coordination issue if the change is breaking.
- Commit messages follow conventional-commits across all repos.
- Branch naming: `<repo>/<author>/<topic>` so cross-repo PRs are
  identifiable in the unified branch list.

## Cross-repo knowledge

- Connection articles spanning multiple repos live in
  `workspace/knowledge/connections/`.
- Concept articles for any single repo live in that repo's own
  `knowledge/concepts/`. Do not duplicate or migrate them upward.
- The workspace compile log (`workspace/knowledge/log.md`) records only
  cross-repo coordination; per-repo changes go in each repo's own
  `log.md`.

## When a repo is removed from this workspace

Scan `workspace/knowledge/connections/` for references to the removed
repo. Delete affected connection articles, or mark them
"premise no longer holds in this workspace" with a date.
```

### Sample: workspace `knowledge/index.md`

```markdown
# Workspace knowledge index

This index lists cross-repo connection articles only. Per-repo
knowledge lives inside each repo's own `knowledge/` directory.

## Connections

| Article | Spans | Updated |
| --- | --- | --- |
| [[connections/webhook-to-ticket-pipeline]] | repo-a, repo-b | 2026-04-25 |
| [[connections/shared-auth-model]]          | repo-a, repo-c | 2026-04-20 |

## Per-repo knowledge

For repo-specific concepts, see each repo's own index:

- `repo-a/knowledge/index.md`
- `repo-b/knowledge/index.md`
- `repo-c/knowledge/index.md`
```

### Sample: a workspace `connections/` article

```markdown
---
title: "Webhook-to-ticket pipeline (repo-a → repo-b)"
type: connection
spans: [repo-a, repo-b]
updated: 2026-04-25
---

# How repo-a's webhook flows into repo-b's ticket pipeline

Cross-repo data flow that exists only when both repo-a and repo-b are
deployed together. For each repo's internal concepts, follow the
links below.

## Flow

repo-a receives Zoom webhooks (see
[[../../repo-a/knowledge/concepts/webhook-receiver]]), normalizes
them to `InboundEvent`, and POSTs to repo-b's ingest endpoint (see
[[../../repo-b/knowledge/concepts/ingest-api]]).

repo-b classifies and routes (see
[[../../repo-b/knowledge/concepts/classification-workflow]]).

## Versioning

The contract between repo-a and repo-b is the `InboundEvent` schema.
Owned by repo-a; consumed by repo-b. Breaking changes require
coordinated PRs in both repos and a workspace `log.md` entry.

## When this article goes stale

If either repo is removed from the workspace, this article's premise
no longer holds. Mark it as such or delete it.
```

### Sample: workspace `log.md` entry

```markdown
## [2026-04-25] connection | repo-a → repo-b InboundEvent contract

- Added a new optional `correlation_id` field to InboundEvent in repo-a
- Updated repo-b's ingest to read it when present, fall back when not
- Cross-repo PRs: repo-a#142, repo-b#87 (merged together)
- Updated [[connections/webhook-to-ticket-pipeline]] versioning section
- Per-repo logs: repo-a/knowledge/log.md, repo-b/knowledge/log.md
```

## Closing thought

Brownfield retrofit is conscious work for the first three to four months. Around month four, the team stops thinking about the rule and just does it; `knowledge/` becomes the place people actually go when they have a question; new hires onboard faster; departing teammates hand off cleanly. The investment pays for itself, but only if you make it past the conscious-effort phase.

The single best predictor of success is whether the team genuinely agreed at step 1. The single best predictor of failure is trying to do a documentation sprint. Pick the right seam, write articles only when you're already touching the code, let the agent carry the discipline, and trust the slow accumulation. It works.
