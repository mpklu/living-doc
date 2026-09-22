---
title: Hub knowledge base — one KB for many repos it does not contain
description: "The second adoption shape: a knowledge repo that documents several code repos. What changes — external: affects entries, the commit trailer as the cross-repo seam, bootstrap into repos the KB does not own — and what does not"
type: concept
area: methodology
updated: 2026-09-21
status: thin
affects: ['actions/drift-check/bootstrap.py', 'actions/drift-check/kb_paths.py', 'actions/drift-check/check_trailer.py', 'HUB_ADOPTION_GUIDE.md']
load_bearing: true
references:
  - concepts/methodology/affects-globs.md
  - concepts/methodology/local-vs-pr-enforcement.md
---

# Hub knowledge base

The adoption guides assume `knowledge/` sits beside one codebase. The field
repo this methodology was hardened in is the other shape: one KB, ~130
articles, documenting a desktop app, a server, five hosted services and a
data model, none of which live in the KB's repo. Everything below was
learned there *(field: knowledger-trans, 2026-04 → 2026-09)*.

## What changes

- **`affects:` needs a foreign form.** A glob only matches paths in the
  KB's own diff. `external: <host>/<group>/<repo>` names a repo instead;
  `drift-check` skips it and `check-trailer` matches it by repo name.
- **The seam moves to the product repo's commit message.** `drift-check`
  cannot see a code change made elsewhere. The `Knowledge: concepts/…`
  trailer, enforced by a commit-msg hook the KB installs into each product
  repo, is the same-task rule at the only point where both sides meet.
  Name-only trailers were satisfied without opening the article; the hook
  now verifies the named article was touched (dirty, committed within 24 h,
  or `updated:` today).
- **Installation is a first-class step.** `.git/hooks/` is per-clone, and
  a hub has three or more clones to keep honest. `bootstrap` installs the
  gate hook, the trailer hooks, a session-status hook in each product repo
  (their git-ignored `settings.local.json`) and the user-level skill;
  `kb-status` reports when any is missing. Repos are configuration
  (`.living-doc.json` / `KB_PRODUCT_REPOS`), not constants.
- **The agents who most need the write path work in the product repos**,
  where the KB's `CLAUDE.md` is not loaded. The procedure has to reach them
  as a skill and a session-start status, not as prose in a file they never
  read.

## What does not change

Articles, facts, decisions, the gate, the sweep. A hub is a KB with a
longer arm, not a different KB.

## Files

`HUB_ADOPTION_GUIDE.md` (adopter surface) · `bootstrap.py` · `kb_paths.py` ·
`check_trailer.py`.
