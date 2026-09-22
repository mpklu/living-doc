## [2026-07-22] meta | manual gate slipped TWICE in one hour — gate now installed here

The external:-matching fix commit ALSO slipped past the manual gate
(check_trailer.py → maintenance-tools.md, unfixed at commit time) —
within the hour of the log entry recording the first slip and defending
the manual choice. Two data points beat the rationale: this repo now
runs the same installed pre-commit gate it ships (`pre-commit-gate`
ported from the field repo, `--install` run). "Deliberately manual"
was the same discipline-will-suffice bet the entire tool suite exists
to retire; holding the methodology repo to a lower standard than its
adopters was exactly backwards.
