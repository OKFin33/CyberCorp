# Corp entry

## What to do now

One observation answers this: `python3 .agents/corp/repo-context.py`. Read the state off it — do not read the rule set end to end to decide.

| What the observation shows | Do this |
|---|---|
| Input arrived that is neither adopted nor rejected — changed direction, new material | [`intake`](../../.agents/skills/intake/SKILL.md) **first**: a changed premise makes downstream work wrong |
| The current Milestone has an Issue whose prerequisites are met, not marked as needing an Owner decision | [`work`](../../.agents/skills/work/SKILL.md) — take any of them |
| Nothing there is takeable, and its closing conditions do not hold | [`bounded-planning`](../../.agents/skills/bounded-planning/SKILL.md) — the gap is the work |
| Its declared closing conditions **hold** | [`review`](../../.agents/skills/review/SKILL.md) — the only way review opens |
| No Milestone is current, or the current one is closed | [`bounded-planning`](../../.agents/skills/bounded-planning/SKILL.md) — design the next stage |
| The Owner assigned something explicitly | Honour the assignment |

**Two states look alike and are not.** An open Issue may be work nobody started, or work already delivered and waiting — the second is not takeable, and both taking it and planning around it repeat what exists. Two things make the difference readable, and you need both: the observation reports `open_candidates` for each Issue, so **an Issue with an unmerged candidate is not new work** whoever forgot to label it; and delivered-and-waiting work carries the Owner-decision label, which is the only signal that survives its candidate being closed or merged. **If neither is present but the Issue's own comments say it was delivered, believe the comments and fix the label** — you have just found the case where the readable signals were not maintained.

These four are the whole set. They form one chain — input becomes fact, fact becomes units, units become candidates, candidates become a stage that holds — and each hands to the next by changing the state above, not by calling it.

**Review returns findings; it does not create work.** A blocker goes back to the Issue that produced it. A genuinely missing unit goes to `bounded-planning`, which creates it **and updates the stage's closing conditions**. A decision that is the Owner's goes to the Owner.

If the routing table still has an `unresolved` required route, this Corp is not established yet: see `establish.md` in the creation package, and do not start work Corpos here.

## Before you start

**Leave a visible occupation before reading code or anything else** — a self-assignment plus a comment naming an instance ID unique within your runtime. Self-assign the Issue; add yourself to a PR's requested reviewers; if the work has no object yet, create its carrier Issue first, then occupy it. On a shared account the assignment alone cannot tell another instance from your own earlier run; the ID can. One new ID per execution (`python3 -c 'import uuid; print("aid-v1-" + str(uuid.uuid4()))'`); it identifies, it does not authorise. Read existing occupation comments before adding yours, and after posting confirm the first valid occupation in server order is yours.

## The governing rule

> **Outside this project's irreversible-action list, no action requires Owner approval.**

It decides whether any other rule may demand Owner involvement: a rule that does must first show that its action is on the list.

**The burden of proof sits on the side that wants to escalate.** To route something to the Owner, name the list entry it hits. If you cannot name one, act. "Might affect", "unclear whether" and "to be safe" are not entries on the list.

**Advancing the delivery outranks improving the conditions for advancing it.** Tightening a check, tidying infrastructure, completing a document or reviewing something already done is work when a delivery needs it — **if you cannot name the delivery it unblocks, it is not the next thing to do.**

### This project's irreversible-action list

- Merging into the default branch.

Add the entries this project actually has: deployment, external release, data migration, a public API change — anything that cannot be undone. Branch protection and permissions should enforce exactly this list. Anything absent from it is the executor's to decide.

Then read the one method file the table sent you to. Everything below is read when you hit it, not before.

---

## Read for what you are doing

**Just installed, with no shared work yet?** Start from `establish.md` in the creation package. The rules about taking and sizing work assume there is work to take; in a fresh install there is not yet, and establishing it is the first task. A route in [canon-map.yaml](canon-map.yaml) is `active`, `pending-relocation` or `unresolved` — the latter two mean that fact has not been established yet or has moved, not that something is broken. A project with no native work surface at all can still be prepared locally; the entry states what remains missing rather than blocking.

Rules are defined once, in [mechanics.md](mechanics.md). This table routes; it does not restate.

| What you are doing | Sections |
|---|---|
| Communicate with the Owner, or adopt a reply | The [Owner communication card](owner-communication.md) |
| Take over work that looks stalled, or recover a damaged task | [mechanics.md](mechanics.md#occupation-is-visible-and-an-abandoned-one-can-be-taken-over) |
| End a checkout, branch or other site your execution created | [mechanics.md](mechanics.md#the-work-the-occupation-and-the-execution-site-end-separately) |
| Record a decision, a rejected option, or a cross-module contract | [mechanics.md](mechanics.md#direction-and-cross-cutting-facts-have-a-durable-home) |

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

### This project's site-recovery policy

State which sites this project treats as recoverable and on what evidence — for example, that a delivery branch is recovered once its tip is an ancestor of the default branch. Without a declared policy the executor falls back to recovering only what its own execution created, which leaves shared branches to accumulate.
