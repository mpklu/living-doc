# Hub Adoption Guide — one knowledge base for several repos

The other two guides put `knowledge/` beside one codebase. This shape puts it in a repo of its own,
documenting several code repos it does not contain: a desktop app, a server, hosted services, a data
model. Everything in the brownfield guide still applies; this guide covers only what a hub adds.
Reasoning and field evidence: `knowledge/concepts/methodology/hub-knowledge-base.md`.

## 1. Point `affects:` at other repos

A glob only matches paths in the hub's own diff. For code elsewhere, use the `external:` form:

```yaml
affects:
  - "external: gitlab.example.com/group/ProductRepo"
  - "**/Sources/Payments/**"        # still allowed: matched inside the product repo by check-trailer
```

`drift-check` skips `external:` entries; `check-trailer` matches them by repo name.

## 2. Enforce the same-task rule where the code changes

The hub's gate cannot see a commit in another repo. The seam is the product repo's commit message:

```text
Knowledge: concepts/payments/webhooks.md
```

`scripts/check-trailer`, installed as that repo's `commit-msg` hook, blocks a commit whose staged paths
match an article's `affects:` unless the message names an article that was **touched** in the hub (dirty,
committed within 24 hours, or `updated:` today) or says `no knowledge impact: <reason>`.

## 3. Tell the hub where its repos are

```json
// .living-doc.json at the hub's root
{ "product_repos": ["/path/to/ProductRepo", "/path/to/OtherRepo"], "skill_dir": ".claude/skills/kb" }
```

Or `KB_PRODUCT_REPOS=/path/a:/path/b` in the environment.

## 4. Install once per machine, and let the status screen tell you when it is gone

```bash
scripts/bootstrap           # gate hook here · trailer hook + kb-status session hook in each product repo · ~/.claude/skills/kb
scripts/bootstrap --check   # what kb-status runs at session start; exit 1 if anything is missing
```

Hooks live in `.git/hooks/`, which no clone carries. Without the check, a fresh clone loses enforcement
silently.

## 5. Reach the agents where they work

Sessions in the product repos never load the hub's `CLAUDE.md`. Ship the procedure as a skill (`/kb`:
read path and same-task write path as numbered steps) and print `kb-status` at their session start, so
the write gesture — article, `## Facts`, one log entry file — is in front of them before the commit hook
has to say no.

## What stays the same

Articles, facts, decisions, the generated `_index.md` tree, the sweep. A hub is a knowledge base with a
longer arm.
