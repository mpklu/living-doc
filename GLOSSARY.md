# Glossary

Vocabulary used throughout this methodology. Read this before either adoption guide if any of the terms feel unfamiliar.

## Terms

### Article-mapping table

A table inside `CLAUDE.md` of the form: _"When you change X, update article Y."_ The agent uses this to decide which article belongs to which code path. Empty at the start of a brownfield retrofit; populated from day one in greenfield. Grows as new articles are created.

### Capture first, refine second

The first principle of the methodology. When the agent makes a code change that affects behaviour, config, or architecture, the corresponding article gets written **in the same task** — even if placement, naming, or scope is uncertain. An imperfect article the user can review is strictly better than a correctly-placed gap. Missing context is unrecoverable; refining costs minutes.

### `CLAUDE.md`

The agent-instruction file at the project root. Contains the same-task rule, the article-mapping table, and any project-specific conventions. Read by the AI agent on every interaction. Lower-scope `CLAUDE.md` files (repo-level) take precedence over higher-scope ones (workspace-level).

### Compile log (`log.md`)

A dated, append-only log inside `knowledge/`. Each entry records what changed, why, and which articles were touched. Captures architectural narrative and rationale that git commit messages don't preserve. Read sequentially, it tells the story of the project's decisions.

### Concept article

A standalone reference article in `knowledge/concepts/{area}/*.md`. Describes _what something is and why it exists_ — not _how to use it_ (that's what code, tests, and READMEs are for). Atomic: one topic per article. Grouped into areas (project internals, external systems, tooling, project context).

### Connection article

A cross-cutting article in `knowledge/connections/*.md`. Describes _how multiple concepts interact_ rather than describing any one of them. The only kind of article that legitimately spans more than a single concept.

### Document on touch

The brownfield principle: write articles for code paths only when you're about to change them — not as a separate inventory effort. Stable, untouched code stays undocumented; that's fine. Articles are written reactively, never proactively, on a brownfield retrofit.

### Drift sweep

A periodic ritual (once a sprint or once a month, ~30 minutes) where someone scans recently-changed code paths against their corresponding articles for contradictions. Catches the cases where the same-task rule slipped. The drift fix is logged in `log.md`.

### First adoption phase

Months 1–3 of adoption, when team buy-in is fragile and the discipline hasn't yet become muscle memory. The agent should be conservative during this phase: don't write speculative articles, do most of the article writing automatically, defer to the user's judgement on edge cases.

### Greenfield

A new project with no substantial committed code, no established habits, and no existing partial documentation. Articles can drive design decisions; setup is straightforward. Apply `GREENFIELD_ADOPTION_GUIDE.md`.

### Brownfield

An existing project with prior commits, existing wiki / README / design docs, and a team with established habits. Articles describe state that has already calcified; documentation is written reactively as code is touched. Apply `BROWNFIELD_ADOPTION_GUIDE.md`.

### Hybrid layout (multi-repo)

The workspace-level pattern: each repo has its own `CLAUDE.md` and `knowledge/` (primary, authoritative); the workspace root has a thin `CLAUDE.md` and `knowledge/connections/` only — for cross-repo articles whose premise requires multiple repos to be co-present. Concept articles never live at the workspace level.

### Knowledge base (`knowledge/`)

The directory at the project root that holds all articles. Treated as the source of truth for the project's behaviour and rationale. Mirrors the code; updated in the same task as the code.

### Real data beats the article

The disambiguating rule for when code and an article disagree. Code wins (it's the actual behaviour) — but the article gets fixed in the same task, not "later." This rule prevents the failure mode of "fix the code to match the stale article."

### Same-task rule

The core discipline. Every code change that alters behaviour, config, or architecture updates the relevant article in the same task / same PR — never "later." Encoded in `CLAUDE.md` and enforced by the agent on every interaction.

### Source of truth

The role `knowledge/` plays in the project. When a question about behaviour arises, the article is the answer; if the article and the code disagree, the article is updated to match the code (see _real data beats the article_). The README, wiki, comments, and other docs are reference material; they are not the source of truth.
