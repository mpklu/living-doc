# Workspace conventions

This workspace contains multiple related repos. **Each repo's own
`CLAUDE.md` is authoritative for that repo.** This file adds workspace-level
rules that apply across all of them.

The living-documentation methodology referenced by the per-repo `CLAUDE.md`
files is described at: https://github.com/mpklu/living-doc

## Repo-level rules take precedence

When working inside a repo's directory, that repo's `CLAUDE.md` is the
primary source. The rules below augment, never override.

## Cross-repo rules

{{Replace these examples with your team's actual rules.}}

- When changing repo-a's public API surface, check repo-b's clients
  (search for `from repo_a` in `repo-b/src/`) and raise a coordination
  issue if the change is breaking.
- Commit messages follow conventional-commits across all repos.
- Branch naming: `<repo>/<author>/<topic>` so cross-repo PRs are
  identifiable in the unified branch list.

## Cross-repo knowledge

- **Connection articles** spanning multiple repos live in
  `workspace/knowledge/connections/`. Each uses relative wiki-links to
  repo-level concept articles (e.g., `[[../../repo-a/knowledge/concepts/X]]`).
- **Concept articles** for any single repo live in that repo's own
  `knowledge/concepts/`. **Do not duplicate or migrate them upward** —
  they strand when repos move to a different workspace.
- The workspace compile log (`workspace/knowledge/log.md`) records only
  cross-repo coordination; per-repo changes go in each repo's own
  `log.md`.

## When a repo is removed from this workspace

Scan `workspace/knowledge/connections/` for references to the removed
repo. Either:

- Delete the affected connection articles (their premise no longer holds).
- Or mark them "premise no longer holds in this workspace" with a date,
  if you may add the repo back later.

Broken wiki-links are correct behaviour — they signal that the article's
premise no longer holds with the current set of repos.

## When a new repo joins this workspace

If the new repo genuinely interacts with existing repos (calls them, shares
a deployment, consumes a common contract), consider writing a connection
article describing the interaction. If it's loosely coupled (no cross-repo
articles needed), don't.
