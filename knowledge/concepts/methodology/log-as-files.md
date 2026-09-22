---
title: The log is files — one entry per file, never rendered, rolled by renaming
description: "A prepend-to log.md reached 80 entries for one month: parsing to insert, racing between sessions, ~40k tokens to Read, and monthly rolling could not bound it. An entry is a file; nothing renders it; old files move into month directories"
type: concept
area: methodology
updated: 2026-09-21
status: thin
affects: ['actions/drift-check/roll_log.py']
load_bearing: true
---

# The log is files

## What broke

The compile log was one file, newest entry prepended. In an active repo
(~4 entries a day) it reached **80 entries / 2,248 lines for a single
month** *(field: 2026-09-21)*. Three costs followed: every writer parsed
the header to find the insertion point; two concurrent sessions could not
append safely; a naive `Read` cost ~40k tokens. Monthly rolling could not
bound it, because one month *was* the file.

## The rule

An entry is a file: `knowledge/log/entries/YYYY-MM-DD-<slug>.md`, whose
first line is the header the log always used — `## YYYY-MM-DD — <title>`
(the `## [YYYY-MM-DD] area | title` form is accepted). Writing one is a
single write with nothing parsed. Nothing renders the entries: `ls … |
tail` is "lately", `grep -rn <term> knowledge/log/` is history.

`roll-log --check` validates every header in the gate (filename date must
match the header date). `roll-log` **renames** files older than the
keep-window into `log/YYYY-MM/` — no rewrite, no conservation risk,
which retired the conservation check the concatenating version needed.
It stays out of the edit hook: a hook that moves files mid-session leaves
the tree half-staged under explicit-path staging.

## A rendered log lasted one commit

A generated `log.md` view was added and removed the same day. Logs are
agent-facing, and a 170 KB concatenation no agent reads is only a gate
step and a merge surface.

## Budget

~150 words per entry; `roll-log --long` lists entries over 400. The
decision itself belongs in the article's `## Decisions`
([[decisions-in-the-article]]), not in the entry. A gate warning at 250
words flagged 52 of 85 entries and was moved out of the gate — see
[[dogfooding]].
