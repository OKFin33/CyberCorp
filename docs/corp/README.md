# Corp entry

## What to do now

**One observation answers this.** Run `python3 .agents/corp/repo-context.py` and read the state off it; do not read the rule set end to end to decide.

| What the observation shows | Do this |
|---|---|
| The current Milestone has an open Issue not marked as needing an Owner decision | [`work`](../../.agents/skills/work/SKILL.md) — take the highest-priority one |
| It has none takeable, and its closing conditions do not hold | [`bounded-planning`](../../.agents/skills/bounded-planning/SKILL.md) — the gap is the work |
| Its declared closing conditions **hold** | [`review`](../../.agents/skills/review/SKILL.md) — this is the only way review opens |
| No Milestone is current, or the current one is closed | [`bounded-planning`](../../.agents/skills/bounded-planning/SKILL.md) — design the next stage |
| Methods are installed but there is no route and nothing to take | [`prepare`](../../.agents/skills/prepare/SKILL.md) — a fresh install starts here |
| The Owner assigned something explicitly | Honour the assignment |

Two states look alike and are not: an Issue that is **open** may be work nobody has started, or work already delivered and waiting on an Owner decision. The second is not takeable — planning around it duplicates it, and taking it repeats it. Mark delivered-and-waiting work as needing an Owner decision so this stays readable.

These four are the whole set of work types. They form one chain — an accepted outcome becomes units, units become candidates, candidates become a stage that holds — and each hands to the next by changing the state above, not by calling it.

**Review returns findings; it does not create work.** A blocker goes back to the Issue that produced it. A genuinely missing unit goes to `bounded-planning`, which creates it **and updates the stage's closing conditions**. A decision that is the Owner's goes to the Owner.

---

## The governing rule

> **Outside this project's irreversible-action list, no action requires Owner approval.**

This is not one rule among many. It decides whether any other rule may demand Owner involvement: a rule that does must first show that its action is on the list.

**The burden of proof sits on the side that wants to escalate.** To route something to the Owner, name the list entry it hits. If you cannot name one, act. "Might affect", "unclear whether" and "to be safe" are not entries on the list.

**Advancing the delivery outranks improving the conditions for advancing it.** Tightening a check, tidying infrastructure, completing a document or reviewing something already done is work when a delivery needs it — **if you cannot name the delivery it unblocks, it is not the next thing to do.** The rules below exist to remove guesses that would otherwise stop you; a rule that has you tending to the rules instead of to the result is being read wrongly.

### This project's site-recovery policy

A delivery branch is recovered once its tip is an ancestor of the default branch: the branch held nothing the default branch does not, so `main` is the recovery source. Verify ancestry against the actual remote before removing anything, and remove the exact ref rather than a pattern. Unmerged branches are not covered by this policy — they may hold the only copy of something.

### This project's irreversible-action list

- Merging into the default branch.

That is the whole list. This repository has no deployment and no external release. A project that has them declares them here; the list is project-level configuration, and branch protection and permissions enforce exactly it.

## Read before you start

Five rules. Each is a mechanism from [mechanics.md](mechanics.md) in its operative form; nothing else is required before you begin.

1. **Before starting any action, leave a visible occupation on a native object** — a self-assignment plus a comment naming an instance ID unique within your runtime. Self-assign the Issue; add yourself to a PR's requested reviewers; if the work has no object yet — generating the next batch, reorganising priorities — create its carrier Issue first, then occupy it. On a shared account the assignment alone cannot tell another instance from your own earlier run; the ID can. One new ID per execution (`python3 -c 'import uuid; print("aid-v1-" + str(uuid.uuid4()))'`); it identifies, it does not authorise. After posting, reread and confirm the first valid occupation in server order is yours. Read existing occupation comments before adding yours.

2. **Completion means a PR exists and its checks pass.** No prose asserts completion, including your own.

3. **Only actions on the list above need the Owner.** To escalate, name the entry. Ordinary engineering judgement is yours. *(the governing rule)*

4. **Draw the unit's boundary by independent deliverability, then check the grain against one context window.** If it does not fit, split into sub-Issues before starting rather than carrying a half-state.

5. **`unknown` means either undecided or unrecorded — establish which.** *Undecided* needs a decision; *unrecorded* needs you to find the decision, not make it. And a retrieval that returns nothing establishes only that this retrieval found nothing, never that no constraint exists.

You do not need to know how stage review works in order to start work. That belongs to Milestone closing, not to your entry.

## Read for what you are doing

**Just installed, with no shared work yet?** Start from `.agents/skills/prepare/SKILL.md`. The rules about taking and sizing work assume there is work to take; in a fresh install there is not yet, and establishing it is the first task. A route in [canon-map.yaml](canon-map.yaml) is `active`, `pending-relocation` or `unresolved` — the latter two mean that fact has not been established yet or has moved, not that something is broken. A project with no native work surface at all can still be prepared locally; the entry states what remains missing rather than blocking.

Rules are defined once, in [mechanics.md](mechanics.md). This table routes; it does not restate.

| What you are doing | Sections |
|---|---|
| Communicate with the Owner, or adopt a reply | The [Owner communication card](owner-communication.md) |
| Take over work that looks stalled, or recover a damaged task | [mechanics.md](mechanics.md#occupation-is-visible-and-an-abandoned-one-can-be-taken-over) |
| End a checkout, branch or other site your execution created | [mechanics.md](mechanics.md#the-work-the-occupation-and-the-execution-site-end-separately) |
| Record a decision, a rejected option, or a cross-module contract | [mechanics.md](mechanics.md#direction-and-cross-cutting-facts-have-a-durable-home) |
| Establish or complete project preparation | `.agents/skills/prepare/SKILL.md` from the repo root |

The card changes how things are expressed. It does not change facts, acceptance, or authority. Effective direct Owner instructions take precedence over it; lasting preference changes go back to the card.

## Where facts live

Git owns lasting facts. Native Milestones and Issues own direction and work; comments own execution history; PRs and checks own their evidence. The routing table in [canon-map.yaml](canon-map.yaml) says which source is authoritative for which scope.

Do not create a second ledger of task state. Temporary handoff notes belong in the work itself.

Shared repository: [OKFin33/CyberCorp](https://github.com/OKFin33/CyberCorp). Actual assignment, decisions and recovery evidence are held by native Issues and PRs.

## Getting a working checkout

From an existing clone, verify the actual remote and the pinned version before working, and leave the original working tree as you found it. For resumed work, start from its verified checkpoint rather than the default branch. A checkout you create is an object of its own: the table above routes to what ending it requires, which is not the same act as finishing the work.

Installation does not establish shared work and does not start a process. `.agents/corp/install.json` records initial provenance, not later adoption.

While a mechanism change is itself a candidate, tooling that reads the routing table from the remote default branch may report the entry as missing. That is not an absence of work: read the native Milestone and Issues directly, and treat the PR and the remote default branch as the authority on whether it has landed.

## Supplied inputs

- `docs/product.md` — what this product commits to
- `docs/specs/delivery-communication-verification.md` — the absorbed specification, holding the acceptance scenarios
- `CHANGELOG.md` — what has been delivered
- `docs/verification-status.md` — which capabilities have evidence and which do not

Read the inputs relevant to your task. Required material must remain accessible to the next authorised executor; received, adopted and verified are different states. A successor needs its own runtime, dependencies and repository access — not the creator, and not a launcher.

Scope, toolchain and the boundaries of working on *this* project specifically: [CONTRIBUTING.md](../../CONTRIBUTING.md).
