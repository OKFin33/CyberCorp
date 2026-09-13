---
name: review-corp
description: Independently review a fixed stage candidate. Use when a Milestone's stated closing conditions hold, or when a single-PR review was explicitly requested — not for ordinary PRs.
---

# Review the actual candidate

Read `docs/corp/README.md` if you have not. The rule on completion resting on evidence that is not self-reported defines when a review may open and what independence requires; do not restate those rules here, and do not open a review whose stated closing conditions are unmet.

You must not have implemented the object under review.

## Then, in order

1. **Occupy the review.** For a stage review, converge through the rule that there is always a next thing to do. For a requested single-PR review, occupy that PR directly and state your expiry alongside the scope; reread existing undertakings before going deeper. No child Issue is needed.
2. **Fix the object.** Take base and head from an independent checkout, and verify the agreement against them.
3. **Choose checks that expose concrete errors, omissions or needless complexity.** Add affected-consumer perspective for shared semantic changes; a reviewer per team is not required.
4. **Separate** acceptance blockers — agreement, scenario, consequence, recheck — from optional improvements and from decisions that are actually the Owner's.
5. **Record** in native PR reviews or inline comments: your instance and non-involvement, exact base and head, the Spec pin, scope, which checks you executed versus relied on, and what remains untested. If permissions prevent that, record the result and the limitation on the PR itself. Stage conclusions belong in the bounded Issue with evidence links.
6. **Return** findings, or a no-blocker conclusion with the evidence supporting it. The checkout you fixed base and head in ends under the rule that the work, the occupation and the execution site end separately — concluding the review does not end it.

A changed head or Spec needs re-evaluation by impact; a new integration base needs its own checks, not the previous combination's green result. Link every blocker to its correction, the precise new version, and an independent recheck.

Review and CI do not prove untested behaviour or user value, and do not grant merge authority. For Owner-facing expression see the rules on the irreversible-action boundary and on the durable home for facts.
