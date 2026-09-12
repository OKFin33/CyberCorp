---
name: work-corp
description: Implement, investigate or resume bounded Corp work from its accepted agreement and shared execution state.
---

# Advance the result

Follow these steps in order. Each step names the mechanics.md section it applies — read that section there when you need the rule itself; this file does not restate it.

## 0. Load context once

Read `docs/corp/README.md` if you have not already. From it, recover: the actual task you are taking, its required inputs, path contracts, and any existing results already produced against it. Do this once per session, not once per step.

## 1. Pick or confirm your unit of work

- **Resuming a named Issue** (you were told which one, or you are continuing your own prior session): go to step 2 with that Issue.
- **No Issue named yet, and work exists in the Milestone**: take the highest-priority open Issue in the current Milestone that is **not** labeled as requiring an Owner decision (S4). Go to step 2.
- **No open Issue qualifies — the Milestone queue is empty or everything left needs an Owner decision**: the deficit is itself the work. Before generating the next batch or reorganising priorities, check for an existing planning carrier and converge on it rather than opening a second one (S4). If none exists, create the carrier Issue now — that creation is itself the action step 2 occupies.

Do not skip this step by picking whatever looks interesting. "There's always a next thing to do" (S4) means *this* decision procedure, not free choice.

## 2. Occupy before you touch anything

Before any other action on the unit from step 1: self-assign the Issue (S2). If the unit didn't exist yet (the planning-carrier case), self-assign the Issue you just created. If what you're doing is reviewing a PR rather than implementing, add yourself to its requested reviewers instead — but review belongs to `.agents/skills/review-corp/SKILL.md`, not this file; stop here if that's your actual task.

Do this first, not after you have already started reading code.

## 3. Verify the unit actually carries its own acceptance

Before implementing, check the Issue body states: the outcome, the boundary, the observable acceptance, and how to verify directly — with required inputs referenced at a fixed version (a pinned commit, a permalink), not copied inline (S1).

- If it does, proceed to step 4.
- If it doesn't — acceptance reads like "implement X well," or an input is a floating branch/relative path instead of a fixed reference — that is a gap in the unit itself, not something you silently fill in and proceed past. Fix the Issue body if that is within your authority; if the missing piece is a decision that is not yours, take it to the Owner under the governing rule in `docs/corp/README.md` (name the list entry it hits). Do not start implementation against unverifiable acceptance.

## 4. Check the unit fits — split before you start, not mid-way

Apply S6's two criteria, in order:

1. **Independent deliverability**: is this one result that can be delivered, verified and integrated on its own?
2. **Context-window grain**: even if (1) holds, can you actually finish it within one context window?

If either fails, split into sub-Issues now and re-run steps 1–3 on the piece you're actually taking. If you only discover the misfit mid-way, split then — but you will have to write what you worked out to the shared layer first, which is the cost this step exists to avoid.

## 5. Implement

Choose a direct implementation and checks that expose relevant failure. Use the project's actual check entry (e.g. `python3 .agents/corp/check.py` and the project's test command) — not a check you invent for convenience.

Ordinary engineering choices (structure, naming, internal design, which test to write first) are yours to make within your authority. The entry's governing rule in `docs/corp/README.md` decides what actually needs the Owner — not a feeling that something "might" matter. If you hit a shared-premise change (something a Spec, a cross-module contract, or another Issue's acceptance depends on), take it to that fact's owner and to affected consumers before proceeding on top of it; don't route around it and don't unilaterally decide it yourself either.

If you hit setup problems, version/CI evidence questions, or need to continue after a failure, follow S3 — including that no single Issue-level judgment call decides whether a *stage* is "near done"; that call doesn't exist at this granularity.

## 6. Close out your own unit

Finish self-checks and applicable tests. Run them; don't assert they'd pass.

Independent review of whether the result satisfies intent happens at Milestone closing, through `.agents/skills/review-corp/SKILL.md` — not here, and not by you. Do not judge or claim "this stage is basically done." Your job ends at: implementation exists, your own checks are green, and the Issue's stated acceptance is met by evidence you can point to (S3: a PR existing with passing checks is completion; prose claiming completion is not).

## 7. Report only what changes something shared

Report a finding back to the Owner or to other consumers only when it:
- changes a shared agreement (a Spec, a cross-Issue contract),
- widens what you're authorized to do, or
- overturns a premise this work depends on.

Otherwise, keep going — independent parts of the work continue without a report loop. When you do need to report or communicate with the Owner, or adopt a reply from them, follow S5 (irreversible-action boundary) and S8 (durable facts, and distinguishing `unknown`-as-undecided from `unknown`-as-unrecorded) and use the project's current Owner communication card, per the routing in `docs/corp/README.md`.

## 8. Leave the unit in a state someone else can pick up

If you're stopping before the unit is fully closed (context exhausted, waiting on an Owner decision, waiting on another fact owner): leave a shared checkpoint — something written to the Issue or Canon, not just in your own head — and release your occupation (unassign, or let it go stale per S7) rather than sitting on it silently.

Report implemented, reviewed, merged and accepted results strictly according to the evidence each of those words actually has (S3) — don't upgrade "implemented" to "done" in your own summary.

---

**Quick index back into mechanics.md**: S1 acceptance · S2 occupation · S3 evidence-based completion · S4 always-a-next-thing · S5 irreversible-action boundary · S6 unit sizing · S7 stale-occupation takeover · S8 durable facts and `unknown`. Full definitions, rationale and known failure modes live only in `docs/corp/mechanics.md` — this file routes and sequences; it does not redefine.
