# Living Documentation Methodology

> _A documentation pattern for AI-assisted codebases._
> _Every code change updates the matching article in the same task. The agent enforces the rule._

This repository defines a methodology for keeping software documentation as durable as the code it describes. It exists because the cost of writing and maintaining documentation has collapsed — AI agents in the development loop can produce and update articles in the same change that produces the code, removing the historical reason teams gave up on documentation under deadline pressure.

The methodology is small (three documents you can read in 30 minutes) and disciplined (one rule, enforced by the AI agent reading `CLAUDE.md` on every interaction). It works for both new projects and existing ones, single repos and multi-repo workspaces.

## What's in this repo

| File | Read when |
| --- | --- |
| **[`LIVING_DOCS_OVERVIEW.md`](LIVING_DOCS_OVERVIEW.md)** | First. Defines the methodology, the first principle, and which adoption guide to follow. |
| **[`GREENFIELD_ADOPTION_GUIDE.md`](GREENFIELD_ADOPTION_GUIDE.md)** | Setting up a new project. 8 ordered steps, from `CLAUDE.md` to monthly drift sweep. |
| **[`BROWNFIELD_ADOPTION_GUIDE.md`](BROWNFIELD_ADOPTION_GUIDE.md)** | Adopting on an existing codebase. 12 ordered steps, with the "document on touch" mindset and multi-repo workspace patterns. |
| **[`GLOSSARY.md`](GLOSSARY.md)** | Vocabulary reference — concept article, compile log, drift sweep, etc. |
| **[`templates/`](templates/)** | Copy-paste-ready starter files: `CLAUDE.md`, `knowledge/` skeleton, PR template snippet. |
| **[`templates/hooks/`](templates/hooks/)** | Pre-commit hook configs for the pre-commit framework, husky, and lefthook. Local enforcement at commit time. |
| **[`skills/living-docs/`](skills/living-docs/)** | Claude Code Skill that walks Claude through adoption interactively. |
| **[`actions/drift-check/`](actions/drift-check/)** | GitHub Action that verifies PRs touch articles when they touch mapped code paths. |
| **[`scripts/`](scripts/)** | Local CLI shims: `drift-check` (mirrors the Action) and `validate-articles` (frontmatter sanity check). Zero-dep Python. |
| **[`schemas/article-frontmatter.schema.json`](schemas/article-frontmatter.schema.json)** | JSON Schema contract for article frontmatter (`title`, `type`, `area`, `updated`, `status`, optional `affects:` globs). |

## How to use this repo

There are three patterns, in order of leverage.

### Pattern 1 — reference by URL (cheapest)

Add one paragraph to your project's `CLAUDE.md`:

```markdown
## Methodology

This project follows the living-documentation methodology described in
https://github.com/mpklu/living-doc/blob/main/LIVING_DOCS_OVERVIEW.md.
The first principle ("capture first, refine second") and the same-task
rule from that document apply here.
```

The agent fetches and reads the methodology on each interaction. When the methodology updates, your project gets the update for free.

### Pattern 2 — copy a template (most common)

For a new project:

```bash
cp -R templates/greenfield/* /path/to/your/new-project/
```

For an existing project:

```bash
cp -R templates/brownfield/* /path/to/your/existing-project/
# Then follow BROWNFIELD_ADOPTION_GUIDE.md
```

For a multi-repo workspace:

```bash
cp -R templates/workspace-level/* /path/to/your/workspace/
```

Optionally also copy a pre-commit hook so the same-task rule fails fast at commit time, not just at PR review time:

```bash
cp templates/hooks/pre-commit-config.yaml /path/to/your/project/.pre-commit-config.yaml
# or husky-pre-commit / lefthook.yml — see templates/hooks/README.md
cp -R scripts/ /path/to/your/project/scripts/   # CLI the hook invokes
```

### Pattern 3 — install the Skill (most polished)

Install the Claude Code Skill from `skills/living-docs/` and run `/living-docs:adopt` in any workspace. The skill detects greenfield/brownfield, walks through the appropriate guide interactively, and generates the initial files. See [`skills/living-docs/SKILL.md`](skills/living-docs/SKILL.md) for installation.

## What's enforced, and where

Three layers, each catching what the others miss. All three read the same article-mapping source.

| Layer | Where it runs | Catches | How to enable |
| --- | --- | --- | --- |
| **Agent rule** | Inside the AI agent's loop, on every interaction | "I forgot to update the article" — the contributor's primary line of defense. | Ships in `templates/{greenfield,brownfield}/CLAUDE.md`. The 6-step "Before any commit" checklist + red-flag phrases. |
| **Local pre-commit hook** | Contributor's machine, at `git commit` time | Same forgetting, when the agent didn't catch it. Fails the commit before it lands. | Copy `templates/hooks/<framework>` + `scripts/drift-check`. See [`templates/hooks/README.md`](templates/hooks/README.md). |
| **PR-time GitHub Action** | CI, on every PR | Hooks bypassed (`--no-verify`), uninstalled, or never set up. Reviewer-visible safety net. | Add `actions/drift-check/` to a workflow. See [`actions/drift-check/example-usage.yml`](actions/drift-check/example-usage.yml). |

**Article-mapping source.** Each article declares the code paths it covers via an `affects:` glob list in YAML frontmatter (validated against [`schemas/article-frontmatter.schema.json`](schemas/article-frontmatter.schema.json)). Run `scripts/validate-articles` to check frontmatter integrity. The legacy `CLAUDE.md` mapping table is still supported for incremental migration; both sources are unioned.

You can adopt any subset of the layers. The agent rule alone is the cheapest start; the hook + Action close the loopholes.

## Quick start — greenfield project, single repo

1. Read `LIVING_DOCS_OVERVIEW.md` (10 minutes).
2. Read `GREENFIELD_ADOPTION_GUIDE.md` (15 minutes).
3. Copy `templates/greenfield/` into your new project root.
4. Edit the `CLAUDE.md` placeholders (`{{Project Name}}`, etc.).
5. Write your first 3–5 thin concept articles in `knowledge/concepts/{your-project}/` before writing much code.

That's it. The agent will enforce the same-task rule from the next change you make.

## Quick start — brownfield project, single repo

1. Read `LIVING_DOCS_OVERVIEW.md` (10 minutes).
2. Read `BROWNFIELD_ADOPTION_GUIDE.md` (20 minutes).
3. Get explicit team buy-in. Without it, skip everything else.
4. Copy `templates/brownfield/` into the project root.
5. Pick **one** seam (a hot-spot module, an upcoming feature, or an onboarding question) and write 3–5 thin articles for it.
6. From the next PR onward: same-task rule applies to that seam. Don't back-fill globally.

## Why this works (one paragraph)

The same-task rule used to be unworkable: humans under deadline pressure quietly skipped documentation updates, and "I'll do it next sprint" became the rotting wiki we all know. With AI agents in the loop, the cost of writing and updating articles drops to near-zero — the agent does it as part of the same change that produces the code. The discipline humans struggled to maintain is now cheap to enforce, because the agent reads `CLAUDE.md` on every interaction and updates the matching article by default. The result is documentation that actually mirrors the code, on by default, indefinitely.

## Origin

This project grew out of the blog post _[Living Knowledge Base — A Documentation Pattern for AI-Assisted Codebases](https://mpklu.github.io/posts/living-knowledge-base/)_, which sketched the original idea. The repo formalises the methodology, expands it with adoption guides for both greenfield and brownfield projects, and adds the templates / Skill / GitHub Action tooling that make it practical to apply.

If you're new to the methodology, the blog post is the friendliest entry point; this repo is the operational reference.

## License

This methodology is licensed under [CC-BY-4.0](LICENSE). Use it, adapt it, redistribute it — please credit this repo.

## Versioning and changes

See [`CHANGELOG.md`](CHANGELOG.md). The methodology evolves; if you reference this repo by URL, consider pinning to a tagged version once they exist.

## Roadmap and contributing

Templates, the Skill, the GitHub Action, the local CLI, and the frontmatter schema have all shipped. See [`ROADMAP.md`](ROADMAP.md) for what's next (drift sweep tooling, IDE integration, generated mapping table). Issues and discussions welcome.
