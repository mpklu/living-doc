## [2026-07-22] tooling | provenance-report retires corroborated claims from the worklist

Second refinement from the field repo, found by running the FIRST
adversarial verification sweep there: the sweep's sanctioned upgrade
path appends the stronger provenance inside the same parenthetical
(`*(reported: vendor; code: Foo.m:12)*`) — but the worklist counted any
`reported`/`inferred` keyword, so verified claims never left the list
(57 before sweep, 57 after). The scanner now parses parentheticals into
';'-segments: a parenthetical also carrying code/bench/field is a
corroborated (verified) claim and is suppressed from the worklist,
while all its keywords still count in the coverage view. Segment
anchoring (start-or-after-';') keeps evidence text from
false-corroborating (the word "code" inside `*(reported: error code
list)*` is not a keyword). Fixture-tested: combined and
multi-segment forms suppressed, bare and separate-parenthetical forms
kept, counts now include every segment keyword.
