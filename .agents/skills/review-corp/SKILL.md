---
name: review-corp
description: Independently review a fixed Corp candidate against its agreement, implementation and evidence; for an instance that did not implement it.
---

# Review the actual candidate

Read `docs/corp/README.md`. Section S3 of `docs/corp/mechanics.md` defines when a stage review may open and what independence requires; do not restate those rules here, and do not open a review whose machine-checkable closing conditions are unmet. An ordinary PR without review is not a task by itself.

Read the required Canon, the actual base/head and the implementation from an independent checkout. Verify the agreement per section S1. Occupy the review per section S2 — for a stage review, converge through section S4 first; for an explicitly requested single-PR review, comment on that PR with a runtime-unique instance ID, the fixed object, scope and expiry, and reread existing undertakings before deeper work. No artificial child Issue is needed. Update the undertaking when you finish, exit, or change to implementation.

Add affected-consumer perspective for shared semantic changes, without requiring a reviewer per team.

Choose checks exposing concrete errors, omissions or needless complexity and retain applicable evidence. Distinguish acceptance blockers (agreement, scenario, consequence, recheck), optional improvements, and actual decisions. Return findings or a supported no-blocker conclusion. Record instance and non-involvement, exact base/head, the Spec pin, scope, executed versus relied-on checks, and untested behavior in native PR Reviews or inline comments. If permissions prevent that, record the result and the limitation on the PR. Stage conclusions belong in the bounded Issue with evidence links. Use sections S5 and S8 for Owner-facing expression or decisions.

Head or relevant Spec changes need impact-based re-evaluation; a new integration base needs its own compatibility and applicable checks, not the old combination's green result. Link blockers to actual corrections, precise new versions and independent rechecks. Review and CI do not prove untested behavior or user value, and do not grant merge authority. Follow the specific one-attempt PR/head/checks/method authorization.
