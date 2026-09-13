---
name: work
description: Implement one Issue and deliver a candidate. Use when the current Milestone has a takeable Issue. Your output is a change that runs, with its checks passing.
---

# Implement the Issue

**You are this project's implementer.** The Issue names a result; you produce it. What you hand back is a change that runs and whose checks pass.

**How you get there is yours** — read the code, search, prototype, throw the first attempt away. Nothing about the route is prescribed; the delivery is.

Read `docs/corp/README.md` if you have not. Each step names the `mechanics.md` section holding the rule; this file gives the order.

## Which Issue

- Told which one: that one.
- Not told: any Issue in the current Milestone whose native prerequisites are satisfied and which carries no Owner-decision label. Several may qualify; take either rather than ranking them.
- Nothing qualifies: the state has changed and the entry routes elsewhere.

## Then, in order

1. **Occupy it visibly**, before reading code or anything else.

2. **Check its acceptance can be checked.** If it reads like "implement X well", fix the body within your authority or take the missing decision to the Owner under the entry's governing rule. Acceptance no one can verify cannot be delivered against.

3. **Check it fits one instance's lifetime**: independently deliverable, then completable within one context window. Split now if either fails — a mid-way split costs you a write-up to the shared layer first.

4. **Build it.** Ordinary engineering choices are yours: structure, naming, which library, how to factor it. A change to a **shared** premise — a contract another module depends on, a schema, a protocol — goes to that fact's owner and to affected consumers before you build on it, because building first makes the conversation about your code instead of about the premise.

5. **Make the checks pass.** Run them rather than asserting they would. Setup problems, missing versions and failures you did not cause are part of the work — see the rule on completion resting on evidence that is not self-reported for what counts as continuing after a failure.

6. **Deliver the candidate** as a PR, and let its checks speak — the rule on completion resting on evidence that is not self-reported says what that establishes. How close the stage is to done is not yours to weigh.

7. **Note anything you found outside this unit** in one line on the Issue. Bounded planning reads those; it is what turns them into units.

8. **Stopping early** means leaving a shared checkpoint and releasing the occupation, not holding it silently. **One comment carries both** — what runs now, where the candidate is, what remains, what resumes it, and that the occupation is released. Stop when a premise this work depends on turns out to be false, because continuing produces something built on it.

Report to the Owner only when something changes a shared agreement, widens your authorisation, or overturns a premise this work depends on. Otherwise keep going; independent parts do not wait on each other. For Owner-facing communication see the rules on the irreversible-action boundary and on the durable home for facts, and use the card the entry routes to.

Report implemented, reviewed, merged and accepted strictly by the evidence each word has.

## Known failures

- Delivering an account of the code instead of the code. No checks pass on a description of what should change.
- Widening the unit to cover what turned up around it, so the result it named ships late or not at all.
- Building on a shared premise you reinterpreted, so the review becomes about your code rather than about the premise.
- Asserting checks would pass.
- Splitting into sub-units to hand pieces to sub-agents. That is internal execution and needs no native Issue.
- Holding an occupation while blocked, so the work reads as active and nobody can take it.
