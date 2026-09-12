---
name: review-corp
description: Independently review a fixed stage candidate. Use when a Milestone's stated closing conditions hold, or when a single-PR review was explicitly requested — not for ordinary PRs.
---

# Review the actual candidate

Read `docs/corp/README.md` if you have not. S3 defines when a review may open and what independence requires; do not restate those rules here, and do not open a review whose stated closing conditions are unmet.

You must not have implemented the object under review.

## Then, in order

1. **Occupy the review** (S2). For a stage review, converge through S4 first. For a requested single-PR review, comment on that PR with an instance ID unique within your runtime, the fixed object, scope and expiry; reread existing undertakings before going deeper. No child Issue is needed.
2. **Fix the object.** Take base and head from an independent checkout, and verify the agreement against them (S1).
3. **Choose checks that expose concrete errors, omissions or needless complexity.** Add affected-consumer perspective for shared semantic changes; a reviewer per team is not required.
4. **Separate** acceptance blockers — agreement, scenario, consequence, recheck — from optional improvements and from decisions that are actually the Owner's.
5. **Record** in native PR reviews or inline comments: your instance and non-involvement, exact base and head, the Spec pin, scope, which checks you executed versus relied on, and what remains untested. If permissions prevent that, record the result and the limitation on the PR itself. Stage conclusions belong in the bounded Issue with evidence links.
6. **Return** findings, or a no-blocker conclusion with the evidence supporting it.

A changed head or Spec needs re-evaluation by impact; a new integration base needs its own checks, not the previous combination's green result. Link every blocker to its correction, the precise new version, and an independent recheck.

Review and CI do not prove untested behaviour or user value, and do not grant merge authority. For Owner-facing expression see S5 and S8.
