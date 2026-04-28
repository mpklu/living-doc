---
name: living-docs
description: Adopt, audit, or operate the living-documentation methodology in any project or workspace. Use when the user says "set up living docs", "adopt the methodology", "/living-docs adopt", "/living-docs audit", "/living-docs sweep", or asks to apply the living-documentation pattern.
---

# Living Docs Skill

This skill helps Claude apply the **living-documentation methodology** to any project or workspace. It encodes the methodology's first principle (capture first, refine second), the same-task rule, and the decision tree for choosing greenfield vs. brownfield adoption.

For the full methodology, see the companion repo:

- `LIVING_DOCS_OVERVIEW.md` — first principle, decision rules, anti-patterns
- `GREENFIELD_ADOPTION_GUIDE.md` — 8-step setup for new projects
- `BROWNFIELD_ADOPTION_GUIDE.md` — 12-step retrofit for existing codebases

This skill provides three modes: **adopt**, **audit**, and **sweep**.

## Mode: adopt

Triggered by: _"set up living docs"_, _"/living-docs adopt"_, _"adopt the methodology"_, _"start a knowledge base"_.

### Steps Claude should follow

1. **Survey the workspace.** Determine:
   - Is this a single repo, a workspace with multiple repos, or unclear?
   - For each repo: greenfield (empty / near-empty) or brownfield (established codebase)?
   - List any pre-existing documentation (README, wiki references, design docs, comments).

2. **Confirm with the user.** Summarize the findings and confirm the user agrees with the classification before proceeding. Especially: greenfield vs. brownfield, and (for multi-repo) whether the repos genuinely interact (tight coupling) or not (loose coupling).

3. **Walk through the appropriate adoption guide:**
   - Greenfield single repo → `GREENFIELD_ADOPTION_GUIDE.md` steps 1–8.
   - Brownfield single repo → `BROWNFIELD_ADOPTION_GUIDE.md` steps 1–12.
   - Multi-repo workspace, tightly coupled → both guides as appropriate per repo, plus the workspace-level layout from the brownfield guide's _"A note on multi-repo workspaces"_ section.
   - Multi-repo workspace, loosely coupled → per-repo only; do not add a workspace layer.

4. **Generate files** based on the templates in this repo's `templates/` directory:
   - `CLAUDE.md` at the appropriate scope (per-repo and/or workspace-level)
   - `knowledge/index.md` and `knowledge/log.md`
   - Empty `knowledge/concepts/` and `knowledge/connections/` directories with `.gitkeep`

5. **For greenfield, seed initial articles.** Ask the user to name the 5–7 load-bearing concepts that will exist in the project, and write 200-word thin drafts for each before any substantial code is written. Populate the article-mapping table accordingly.

6. **For brownfield, pick a seam.** Help the user choose ONE of: hot-spot module, upcoming feature, or a recent onboarding question. Write 3–5 thin articles for that seam only. Do **not** inventory the rest of the codebase.

7. **Confirm team buy-in.** Brownfield in particular: remind the user that without genuine team agreement on the same-task rule, the discipline won't survive a deadline-pressured sprint. Suggest naming a single person responsible for keeping the discipline alive for the first 2–3 months.

### Apply the first principle throughout

Whenever the agent generates an article — even an initial one — capture the **why**: context, constraints, alternatives ruled out. Not just the post-state. When unsure about placement, pick the closest fit and write — the user reviews and refines.

## Mode: audit

Triggered by: _"/living-docs audit"_, _"audit my knowledge base"_, _"is my living-docs setup healthy?"_.

### Steps Claude should follow

1. **Inventory.** Check for the artifacts:
   - Is `CLAUDE.md` present at the repo root? (And workspace root, if multi-repo?)
   - Is `knowledge/` present, with `concepts/`, `connections/`, `index.md`, `log.md`?
   - Does `CLAUDE.md` contain an article-mapping table? Is it populated?
   - Is the same-task rule explicitly stated?

2. **Spot-check the same-task rule's enforcement.** Pick the 3 most recent significant PRs in git history. For each, check:
   - Did the PR touch any code path listed in the article-mapping table?
   - If yes, did the PR also touch the corresponding article(s)?
   - Did the PR add an entry to `log.md`?

3. **Run a drift sweep on the 5 oldest articles.** Sort articles by their `updated:` frontmatter date, oldest first. For each, open the corresponding code path and scan for contradictions (signatures, field lists, env vars, config keys). List any drift found.

4. **Report.** Produce a short report covering:
   - **Maturity phase:** First adoption (months 1–3) or established (3+ months in)?
   - **Coverage:** What fraction of the active codebase has articles? (Active = touched in the last 90 days.) Aim for 60–80% by month three.
   - **Discipline:** Is the same-task rule being followed in PRs? Any specific drift or gaps?
   - **Suggested next move:** The single highest-leverage thing to fix or improve.

## Mode: sweep

Triggered by: _"/living-docs sweep"_, _"run a drift sweep"_, _"check my docs for drift"_.

### Steps Claude should follow

1. **Identify the oldest articles** by `updated:` frontmatter date. Take the oldest 5 (or however many fit in a ~30-minute review).

2. **For each article**, open the corresponding code path(s) referenced in the article (or implied by its topic) and compare:
   - Function signatures and field lists
   - Configuration keys, environment variables
   - Folder structure and module names
   - Any specific behaviour described

3. **Apply "real data beats the article."** When code and article disagree, fix the article to match the code — not the other way around — unless the user explicitly says otherwise.

4. **Update each fixed article's `updated:` date** and append a sweep entry to `log.md`.

5. **Stop after the agreed time budget.** Whatever's left waits for the next sweep. Don't try to inventory everything in one sitting.

## Anti-patterns to refuse

The skill should refuse or push back on these requests, even if the user asks:

- **"Document everything in the codebase right now."** Documentation sprints fail. Suggest the document-on-touch approach instead.
- **"Move all the concept articles to the workspace level."** Concept articles must live in their owning repo. Refuse and explain.
- **"Skip the article update for this PR, just this once."** The rule erodes from any single exception. Offer to write the update for the user instead.
- **"Write tutorials in `concepts/`."** Concept articles are descriptive, not procedural. Tutorials belong in code, tests, or a separate `tutorials/` location.

## Templates available in this repo

When generating files, use the templates at `templates/greenfield/`, `templates/brownfield/`, and `templates/workspace-level/`. They contain the recommended `CLAUDE.md`, `knowledge/index.md`, and `knowledge/log.md` shapes with `{{placeholder}}` markers ready to be filled in.
