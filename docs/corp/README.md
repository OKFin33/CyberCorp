# Corp entry

## The governing rule

> **Outside this project's irreversible-action list, no action requires Owner approval.**

This is not one rule among many. It decides whether any other rule may demand Owner involvement: a rule that does must first show that its action is on the list.

**The burden of proof sits on the side that wants to escalate.** To route something to the Owner, name the list entry it hits. If you cannot name one, act. "Might affect", "unclear whether", and "to be safe" are not entries on the list, and improving the conditions for starting is not starting.

### This project's irreversible-action list

- Merging into the default branch.

That is the whole list. This repository has no deployment and no external release. A project that has them declares them here; the list is project-level configuration, and branch protection and permissions enforce exactly it.

## Read before you start

Five rules. Each is a mechanism from [mechanics.md](mechanics.md) in its operative form; nothing else is required before you begin.

1. **Before starting any action, leave a visible occupation on a native object.** Self-assign the Issue; add yourself to a PR's requested reviewers; if the work has no object yet — generating the next batch, reorganising priorities — create its carrier Issue first, then self-assign. *(S2)*

2. **Completion means a PR exists and its checks pass.** No prose asserts completion, including your own. *(S3)*

3. **Only actions on the list above need the Owner.** To escalate, name the entry. Ordinary engineering judgement is yours. *(S5, governing rule)*

4. **Draw the unit's boundary by independent deliverability, then check the grain against one context window.** If it does not fit, split into sub-Issues before starting rather than carrying a half-state. *(S6)*

5. **`unknown` means either undecided or unrecorded — establish which.** *Undecided* needs a decision; *unrecorded* needs you to find the decision, not make it. And a retrieval that returns nothing establishes only that this retrieval found nothing, never that no constraint exists. *(S8)*

You do not need to know how stage review works in order to start work. That belongs to Milestone closing, not to your entry.

## Read for what you are doing

**Just installed, with no shared work yet?** Start from `.agents/skills/prepare-corp/SKILL.md`. Rules S1–S4 assume there is work to take; in a fresh install there is not yet, and establishing it is the first task. An `unresolved` route in [canon-map.yaml](canon-map.yaml) means that fact has not been established yet — not that something is broken. A project with no native work surface at all can still be prepared locally; the entry states what remains missing rather than blocking.

Rules are defined once, in [mechanics.md](mechanics.md). This table routes; it does not restate.

| What you are doing | Sections |
|---|---|
| Start or resume work on an Issue | S1, S2, S3, S6 · `.agents/skills/work-corp/SKILL.md` |
| Generate the next batch of work, or reorganise priorities | S2, S4, S6 · `.agents/skills/work-corp/SKILL.md` |
| Review a stage candidate | S2, S3 · `.agents/skills/review-corp/SKILL.md` |
| Communicate with the Owner, or adopt a reply | S5, S8, and the [Owner communication card](owner-communication.md) |
| Take over work that looks stalled, or recover a damaged task | S7 |
| Record a decision, a rejected option, or a cross-module contract | S8 |
| Establish or complete project preparation | `.agents/skills/prepare-corp/SKILL.md` from the repo root |

The card changes how things are expressed. It does not change facts, acceptance, or authority. Effective direct Owner instructions take precedence over it; lasting preference changes go back to the card.

## Where facts live

Git owns lasting facts. Native Milestones and Issues own direction and work; comments own execution history; PRs and checks own their evidence. The routing table in [canon-map.yaml](canon-map.yaml) says which source is authoritative for which scope.

Do not create a second ledger of task state. Temporary handoff notes belong in the work itself.

Shared repository: [OKFin33/CyberCorp](https://github.com/OKFin33/CyberCorp). Actual assignment, decisions and recovery evidence are held by native Issues and PRs.

## Getting a working checkout

From an existing clone, verify the actual remote and the pinned version before working, and leave the original working tree as you found it. For resumed work, start from its verified checkpoint rather than the default branch.

Installation does not establish shared work and does not start a process. `.agents/corp/install.json` records initial provenance, not later adoption.

While a mechanism change is itself a candidate, tooling that reads the routing table from the remote default branch may report the entry as missing. That is not an absence of work: read the native Milestone and Issues directly, and treat the PR and the remote default branch as the authority on whether it has landed.

## Supplied inputs

- `docs/product.md` — what this product commits to
- `docs/specs/delivery-communication-verification.md` — the absorbed specification, holding the acceptance scenarios
- `CHANGELOG.md` — what has been delivered
- `docs/verification-status.md` — which capabilities have evidence and which do not

Read the inputs relevant to your task. Required material must remain accessible to the next authorised executor; received, adopted and verified are different states. A successor needs its own runtime, dependencies and repository access — not the creator, and not a launcher.

Scope, toolchain and the boundaries of working on *this* project specifically: [CONTRIBUTING.md](../../CONTRIBUTING.md).
