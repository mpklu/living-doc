---
title: A token budget per surface — what is read when, and how big it may be
description: "Every KB surface is read at a known moment: session start, per routed question, per lookup, per write. Name the moment, hold the size, and put the trigger for periodic work where it fires every time"
type: concept
area: methodology
updated: 2026-09-21
status: thin
affects: ['actions/drift-check/kb_status.py']
load_bearing: true
references:
  - concepts/methodology/what-cache-why-asset.md
  - concepts/methodology/facts-register.md
---

# A token budget per surface

## The accounting

Read cost is the scarce resource ([[facts-register]] made that argument
for one layer). Extending it to every surface, as measured in the field
repo *(bench: 2026-09-21)*:

| Moment | Surface | Held at |
| --- | --- | --- |
| Session start, every session | `CLAUDE.md` + `kb-status` output | ~3.6k + ~0.3k tokens |
| Per routed question | `_index.md` walk: root → area → deeper | ~0.3k + 1–2k per hop |
| Per lookup | grep `facts/` (hit lines only) | tens of tokens |
| Per article read | one article | median ~5k; the size lint flags > 4k words |
| Per write | one entry file, one article | nothing parsed |
| Never | the log, generated files as a whole | — |

Three moves came from filling the table in: the entry point split per
directory (a 40 KB single file was ~10k tokens per question), the rendered
log was deleted (nobody reads it), and `CLAUDE.md` was slimmed with rules
verbatim and connective prose cut.

## The trigger belongs at session start

"Sweep once a sprint" in prose fired zero times in four months. A
~25-line status printed by a SessionStart hook — entry points, write
gesture, three stalest articles, stale-date count, worklist heads, latest
entries, whether enforcement hooks are installed — costs ~300 tokens and
fires every session. Periodic work needs a place in the loop, not a
sentence in a guide.

## Rules of thumb

- Hold the fixed per-session cost under ~4k tokens; everything else is
  on demand.
- A surface an agent must read whole is bounded by what it lists; a
  surface an agent greps is bounded by nothing. Prefer grep surfaces for
  lookups, walks for routing.
- Size is a worklist, not a gate. Operator docs are long on purpose.
