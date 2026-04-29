---
title: Session handoff — bridging context boundaries
type: concept
area: methodology
updated: 2026-04-29
status: thin
affects:
  - 'skills/session-handoff/**'
load_bearing: false
references:
  - concepts/methodology/dogfooding.md
  - concepts/methodology/procedural-vs-principle.md
---

# Session handoff

The methodology answers "how does the next session know what's true?" —
articles, memory, commit history, CLAUDE.md. It does *not* yet
answer "how does the **current** session, before ending, capture
what won't otherwise survive context loss?"

This article scopes a planned skill at `skills/session-handoff/`
that fills the gap.

## What's already durable across sessions

- **CLAUDE.md** — auto-loaded by every session. Methodology rule,
  procedural checklist, article mapping, project structure.
- **Articles in `knowledge/concepts/` and `knowledge/connections/`**
  — design decisions and *why*. Touched by code changes per the
  same-task rule.
- **`knowledge/log.md`** — append-only commit log, narrative form.
- **Agent memory** (Claude Code's auto-memory system at
  `~/.claude/projects/<project>/memory/`) — user/feedback/project/
  reference scope.
- **Git history** — commits + messages.

## What's not durable

What gets lost when a session ends:

- **Cursor position in a multi-step plan.** "Phase G–K shipped, push
  pending, smoke harness deferred." Articles describe what *is*; a
  cursor describes what *was happening when we stopped*.
- **Decisions made in dialog that didn't change code.** "We picked
  Option C for enrichment because the rubric's heuristic shape made
  mechanical good enough." Sometimes lands in commit messages,
  sometimes only in chat. Articles capture the *outcome*, not always
  the *deliberation*.
- **Discovered failure modes that were resolved.** Some land in log.md;
  some are recovered from chat after the fact.
- **Open items mentioned but not tracked.** "We should also do X" said
  midway through a session can vanish.
- **Stylistic / micro-preferences accumulated through correction.**
  Some get saved as feedback memory; many don't, especially when the
  user says "this looks good" without flagging it as save-worthy.

## The skill, in scope

`/session-handoff` (or `/wrap-session`, `/end-session` — name TBD)
runs at session-end. Five phases:

### 1. Audit session activity

What changed since the session started? Heuristics:

- `git log` since session-open (if a marker is recorded, otherwise
  use a heuristic like "since last reflog push by this user").
- Files touched by the LLM (the harness can surface this).
- Tools fired and their outcomes.

Output: a summary of "this session did X, Y, Z."

### 2. Audit what's already captured durably

For each significant change identified in step 1, check:

- Is it in a commit? If yes, what does the commit message say?
- Did it touch an article? If yes, is the touch a content update or
  just an `affects:` widen?
- Did it land in memory (auto-memory or knowledge)?
- Is it in `log.md`?

Output: a coverage map. "Decision A: in commit, in article, in log.
Decision B: in commit only — gap."

### 3. Identify gaps

Per the methodology, durable capture happens via the same-task
rule. By session-end, gaps are either:

- **Article gaps** — code changed in a way an article describes but
  the article wasn't updated. Drift-check would catch this; the
  skill should flag it before the user closes the laptop.
- **Memory gaps** — a fact about the user, project, or workflow that
  wasn't saved to memory but matters for next session. Auto-memory
  rules apply.
- **Cursor gaps** — open items, deferred decisions, "next time look
  at X" notes. Don't fit articles; don't fit memory; need somewhere.

### 4. Generate a handoff brief

A short structured doc at a known path (e.g.,
`docs/reports/<date>-session-handoff.md` or
`<knowledge>/handoffs/<date>.md`). Schema:

- **Where we are** — one paragraph.
- **Top of HEAD** — last 5–10 commit lines.
- **Open items, ordered** — what to do next, why each was deferred.
- **What to read first** — which articles + memory + commits the
  next session should load.
- **Suggested next-session opener** — the prompt the user pastes to
  bootstrap.
- **Decisions made this session worth remembering** — captured for
  the inevitable "why did we…" question.
- **What's NOT in this handoff** — pointer to articles where deeper
  rationale lives, so the handoff doesn't grow indefinitely.

### 5. Surface a starting prompt for the next session

A single sentence the user can paste verbatim. The next session
reads CLAUDE.md (loaded automatically) plus the handoff doc, and
has full context.

### Discoverability — closing the loop

The handoff is useless if the next session doesn't know to read it.
Two complementary mechanisms:

1. **CLAUDE.md points at the convention.** Every adopter's CLAUDE.md
   should include a "Session continuity" paragraph telling the next
   session: "at session start, check for the most recent
   `docs/reports/*-session-handoff.md` (or whatever path the project
   chose) and read it before doing anything else." CLAUDE.md is
   auto-loaded; that pointer is what makes the handoff findable.
2. **The next-session opener prompt names the handoff explicitly.**
   E.g., "Continue from `docs/reports/2026-04-29-…-session-handoff.md`."
   Belt-and-braces — even if the user forgets to paste the opener,
   CLAUDE.md's pointer still surfaces the handoff.

The skill should ensure both mechanisms are in place: when generating
the handoff brief, also verify CLAUDE.md has the Session continuity
pointer, and add it if missing (one-time per repo).

## Why this lives in LIVING_DOC

Three reasons:

1. **Methodology completeness.** The methodology already answers
   "how does the next session know what's true." Session-handoff
   answers the corollary "how does the current session prepare to
   end." Same problem, different angle.
2. **General applicability.** Adopters of any project, not just
   this repo, hit the long-context problem. Skill lands in
   methodology where adopters can install it.
3. **Same machinery.** The skill consumes the same artifacts the
   methodology already produces (articles, memory, log.md, commits).
   No new infrastructure required.

## Anti-patterns to design around

- **Don't generate a giant doc.** The handoff is a cursor, not an
  archive. ≤200 lines. Pointer to durable artifacts for everything
  else.
- **Don't duplicate what articles already say.** Reference them.
  The handoff is "where we are"; articles are "what's true."
- **Don't expire silently.** Mark the handoff with the session-end
  date. The next session reading it knows whether it's fresh or
  stale.
- **Don't replace the same-task rule.** Session-handoff catches
  what the rule misses; it doesn't excuse skipping the rule
  mid-session.

## Files (planned)

- `skills/session-handoff/SKILL.md` — Skill manifest + steps
- `skills/session-handoff/template.md` — handoff brief shape
- `LIVING_DOCS_OVERVIEW.md` — when next touched, add a "Session
  handoff" section pointing at the skill

