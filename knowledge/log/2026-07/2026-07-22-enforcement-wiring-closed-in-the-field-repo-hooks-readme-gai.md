## [2026-07-22] methodology | enforcement wiring closed in the field repo (hooks README gains build-facts + the single-gate pattern)

The field repo asked the obvious question — "do these tools run
automatically?" — and the honest answer was no: CLAUDE.md is an
instruction to the agent (probabilistic), and the --check gates existed
but nothing installed them. Now wired there end-to-end: a versioned
`scripts/pre-commit-gate` (validate + check-links + build-index/facts
--check + drift-check) exec'd from a plain `.git/hooks/pre-commit`
(zero framework deps, `--install` mode), the pre-commit-framework
config updated to the same gate, GitLab CI running the identical
checks as the `--no-verify` safety net, and a Claude Code PostToolUse
hook auto-regenerating index+facts after knowledge-article edits
(pipe-tested + live-fire proven). Upstream: hooks README gains
`build-facts --check` (was missing since the facts register shipped a
few hours before it) and documents the framework-free single-gate
pattern. The enforcement ladder is now: agent instruction →
in-session auto-regen → commit gate → CI.
