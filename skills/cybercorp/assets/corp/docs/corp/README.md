# Corp entry

## The governing rule

> **Outside this project's irreversible-action list, no action requires Owner approval.**

This is not one rule among many. It decides whether any other rule may demand Owner involvement: a rule that does must first show that its action is on the list.

**The burden of proof sits on the side that wants to escalate.** To route something to the Owner, name the list entry it hits. If you cannot name one, act. "Might affect", "unclear whether" and "to be safe" are not entries on the list.

**Advancing the delivery outranks improving the conditions for advancing it.** Tightening a check, tidying infrastructure, completing a document or reviewing something already done is work when a delivery needs it — **if you cannot name the delivery it unblocks, it is not the next thing to do.** The rules below exist to remove guesses that would otherwise stop you; a rule that has you tending to the rules instead of to the result is being read wrongly.

### This project's site-recovery policy

State which sites this project treats as recoverable and on what evidence — for example, that a delivery branch is recovered once its tip is an ancestor of the default branch. Without a declared policy the executor falls back to recovering only what its own execution created, which leaves shared branches to accumulate.

### This project's irreversible-action list

- Merging into the default branch.

Add the entries this project actually has: deployment, external release, data migration, a public API change — anything that cannot be undone. Branch protection and permissions should enforce exactly this list. Anything absent from it is the executor's to decide.

## Read before you start

Five rules. Each is a mechanism from [mechanics.md](mechanics.md) in its operative form; nothing else is required before you begin.

1. **Before starting any action, leave a visible occupation on a native object** — a self-assignment plus a comment naming an instance ID unique within your runtime. Self-assign the Issue; add yourself to a PR's requested reviewers; if the work has no object yet — generating the next batch, reorganising priorities — create its carrier Issue first, then occupy it. On a shared account the assignment alone cannot tell another instance from your own earlier run; the ID can. One new ID per execution (`python3 -c 'import uuid; print("aid-v1-" + str(uuid.uuid4()))'`); it identifies, it does not authorise. After posting, reread and confirm the first valid occupation in server order is yours. Read existing occupation comments before adding yours.

2. **Completion means a PR exists and its checks pass.** No prose asserts completion, including your own.

3. **Only actions on the list above need the Owner.** To escalate, name the entry. Ordinary engineering judgement is yours. *(the governing rule)*

4. **Draw the unit's boundary by independent deliverability, then check the grain against one context window.** If it does not fit, split into sub-Issues before starting rather than carrying a half-state.

5. **`unknown` means either undecided or unrecorded — establish which.** *Undecided* needs a decision; *unrecorded* needs you to find the decision, not make it. And a retrieval that returns nothing establishes only that this retrieval found nothing, never that no constraint exists.

You do not need to know how stage review works in order to start work. That belongs to Milestone closing, not to your entry.

## Read for what you are doing

**Just installed, with no shared work yet?** Start from `.agents/skills/prepare-corp/SKILL.md`. The rules about taking and sizing work assume there is work to take; in a fresh install there is not yet, and establishing it is the first task. A route in [canon-map.yaml](canon-map.yaml) is `active`, `pending-relocation` or `unresolved` — the latter two mean that fact has not been established yet or has moved, not that something is broken. A project with no native work surface at all can still be prepared locally; the entry states what remains missing rather than blocking.

Rules are defined once, in [mechanics.md](mechanics.md). This table routes; it does not restate.

| What you are doing | Sections |
|---|---|
| Start or resume work on an Issue | `.agents/skills/work-corp/SKILL.md` |
| Generate the next batch of work, or reorganise priorities | `.agents/skills/work-corp/SKILL.md` |
| Review a stage candidate | `.agents/skills/review-corp/SKILL.md` |
| Communicate with the Owner, or adopt a reply | The [Owner communication card](owner-communication.md) |
| Take over work that looks stalled, or recover a damaged task | [mechanics.md](mechanics.md#occupation-is-visible-and-an-abandoned-one-can-be-taken-over) |
| End a checkout, branch or other site your execution created | [mechanics.md](mechanics.md#the-work-the-occupation-and-the-execution-site-end-separately) |
| Record a decision, a rejected option, or a cross-module contract | [mechanics.md](mechanics.md#direction-and-cross-cutting-facts-have-a-durable-home) |
| Establish or complete project preparation | `.agents/skills/prepare-corp/SKILL.md` from the repo root |

The card changes how things are expressed. It does not change facts, acceptance, or authority. Effective direct Owner instructions take precedence over it; lasting preference changes go back to the card.

## Where facts live

Read `{{PROJECT_REF}}` for what this project commits to. Git owns lasting facts; native Milestones and Issues own direction and work; comments own execution history; PRs and checks own their evidence. The routing table in [canon-map.yaml](canon-map.yaml) says which source is authoritative for which scope.

Do not create a second ledger of task state. Temporary handoff notes belong in the work itself.

{{SHARED_WORK}}

## Getting a working checkout

From an existing clone, verify the actual remote and the pinned version before working, and leave the original working tree as you found it. For resumed work, start from its verified checkpoint rather than the default branch. A checkout you create is an object of its own: the table above routes to what ending it requires, which is not the same act as finishing the work.

Installation does not establish shared work and does not start a process. `.agents/corp/install.json` records initial provenance, not later adoption.

## Supplied inputs

{{SOURCES}}

Read the inputs relevant to your task. Required material must remain accessible to the next authorised executor; received, adopted and verified are different states. A successor needs its own runtime, dependencies and repository access — not the creator, and not a launcher.
