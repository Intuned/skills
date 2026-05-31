# Default to a faithful 1:1 port, not idiomatic re-architecture

When converting a Webwright Crafted CLI into an Intuned project, the skill's
default is a **faithful 1:1 port**: one craft function becomes exactly one
`automation` API with identical behavior, re-fitted only at Intuned's boundary
(injected `page`, typed `params`, returned result). The logic itself is not
re-architected.

We chose this over free-form idiomatic re-architecture (e.g. auto-decomposing
every crawl into `list` + `details` with `extend_payload`) because the whole
premise is that a parameterized CLI already maps cleanly onto a single
parameterized Intuned API — a 1:1 claim. A mechanical, bounded transform is
deterministic and testable; open-ended re-architecture invites coding-agent
hallucination and is hard to verify against the craft's known-good output.

Re-architecture is allowed only through a small, explicitly enumerated set of
exceptions, each decided deliberately (see ADR 0002). "No crawl fan-out by
default" is part of this decision: a crawl that returns a list is faithfully a
single `automation` returning that list, not a multi-API job.
