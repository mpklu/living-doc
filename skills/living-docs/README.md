# living-docs Claude Code Skill

A Claude Code Skill for the living-documentation methodology defined in this repo. Lets Claude run the methodology's adoption, audit, and drift-sweep flows interactively in any workspace.

## Modes

- **`/living-docs adopt`** — set up the methodology in a new or existing project. Claude detects greenfield vs. brownfield, picks the right adoption guide, and walks through it.
- **`/living-docs audit`** — evaluate an existing setup. Claude inventories the artifacts, spot-checks PR enforcement, runs a drift sweep, and reports.
- **`/living-docs sweep`** — run a 30-minute drift sweep on the oldest articles.

## Installation (Claude Code, personal use)

```bash
mkdir -p ~/.claude/skills
cp -R skills/living-docs ~/.claude/skills/
```

Restart Claude Code (or run `/skills` to refresh) and the skill becomes available.

## Installation (Claude Code, team-wide)

Vendor this directory into your team's plugin repo or a shared `.claude/skills/` directory committed to a project. The skill is a single `SKILL.md` file with no external dependencies, so distribution is just file-copy.

## How it works

Claude reads `SKILL.md` when matching the skill to a user request. The skill's content includes the decision tree for greenfield vs. brownfield, the steps for each mode, the anti-patterns to refuse, and pointers to the templates in this repo's `templates/` directory.

The skill does not include scripts or external dependencies — it's purely instructions for Claude. The work happens in Claude's reasoning and file-editing, not in a separate process.

## What it depends on

- The three core methodology docs (`LIVING_DOCS_OVERVIEW.md`, `GREENFIELD_ADOPTION_GUIDE.md`, `BROWNFIELD_ADOPTION_GUIDE.md`) — Claude reads these when needed during adoption flows.
- The `templates/` directory — Claude copies template files when scaffolding a new repo.

If you install only the skill without the rest of the repo, the skill's adoption flow will fall back to generating the templates from scratch. Recommended: keep the whole repo cloned somewhere accessible (or referenced via URL in your project's `CLAUDE.md`).

## Updating

When the methodology evolves, update `SKILL.md` in this repo and re-copy to `~/.claude/skills/`. Major methodology changes will be flagged in the repo's `CHANGELOG.md`.
