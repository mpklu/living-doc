## [2026-04-29] design seed | session-handoff skill

Captured the design for a planned `skills/session-handoff/` skill in
`concepts/methodology/session-handoff.md`. Triggered by an
end-of-long-session observation: the methodology answers "how does
the next session know what's true" but doesn't yet answer the
corollary "how does the current session, before ending, capture
what won't otherwise survive context loss?" Article scopes the
skill's five phases (audit activity → audit durable capture →
identify gaps → generate handoff brief → surface next-session
opener) and the anti-patterns to design around (don't generate a
giant doc; don't replace the same-task rule).

Implementation deferred — picked up in a future session by whoever
needs it. The article's `affects:` declares `skills/session-handoff/**`
so when the implementation starts, the same-task rule guides
whoever's writing it back to this design doc.

Companion artifact: a one-time handoff doc landed in the mira repo
at `docs/reports/2026-04-29-mp-catalog-session-handoff.md` —
captures cursor / open items / next-session opener for the long
session this design article emerged from. That artifact is
ephemeral; this article is durable.
