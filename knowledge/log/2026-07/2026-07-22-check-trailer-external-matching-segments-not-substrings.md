## [2026-07-22] tooling | check-trailer external: matching — segments, not substrings

First real-repo run caught it before any user did: `external:` repo-name
matching used raw substring, so a repo named "MacPractice" matched the
GitLab HOST `gitlab.macpractice.net` inside every external entry — 12
bogus whole-repo mappings on one test commit (19 articles listed where
~9 were right). That noise level teaches users to bypass the hook.
Fixed: repo name must equal a PATH SEGMENT of the entry, with dotted
segments (hosts, filenames) excluded from comparison. Fixture gained the
host-trap case. Post-v0.2.0 patch; rides in [Unreleased].
