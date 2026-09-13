---
name: intake
description: Turn an Owner's new material or changed direction into facts the project can work from. Use when input has arrived that is neither adopted nor explicitly rejected — a requirement changed, a technology was swapped, a document landed. Take this before other work: a changed premise makes everything downstream wrong.
---

# Get a new fact into the project before anything builds on the old one

Read `docs/corp/README.md` if you have not. Each step names the `mechanics.md` section holding the rule; this file gives the order.

**Why this goes first.** A stage whose premise has changed produces work that has to be redone. Discovering that after three Issues are closed costs all three. Whatever else is takeable, an unprocessed input outranks it.

**What you are producing**: facts the project can work from, in the place that owns them, with enough attribution that a successor can tell what they rest on. Not a copy of what the Owner handed you.

## Then, in order

1. **Create the carrier and occupy it, before judging anything.** The input exists only in a conversation until you write it down; an instance that evaluates first and dies loses it, and the Owner has to say it again. Transcribe the input and its attribution onto a native Issue — responder, channel, time, applicable scope, available source — then occupy it. Judgement comes after the input is safe.

2. **Separate the fact from the material.** What arrived may be fifty pages; what cannot be re-derived from anything else may be three sentences. Extract those. A requirement description, an interaction detail, an acceptance scenario — those regenerate from intent plus constraints. An external constraint, a settled trade-off, a rejected option and its reason do not.

3. **Decide where the material itself lives — and default to not here.** What enters the repository is the extracted fact plus a reference to an available source. That reference may be **none**, recorded as such. Whether the material may live in this repository is the Owner's authorisation question; a copy also drifts from its own source, and a drifted copy is worse than no copy because the next instance believes it.

4. **Adopt, or reject explicitly with the reason.** Adoption means the fact is in the location that owns that scope, and the routing table points there. **Rejection is recorded, not silent** — a rejected option with its reason is itself Canon, because without it the next instance proposes the same thing again. An input left in neither state is the one a successor rediscovers and re-asks about.

5. **Name what this invalidates.** A changed premise reaches further than the fact itself: Canon entries that are now wrong, Issues whose fixed inputs no longer describe the agreement, consumers built against the old contract, a stage whose closing conditions assumed the old direction. List them on the carrier.

6. **Do not repair the list yourself.** Single-point corrections you may make. Anything spanning several objects goes to `bounded-planning/SKILL.md` — organising a change into takeable work is what it is for, and one instance trying to update everything in one execution is how half-updated states get made.

7. **Close the carrier.** Adopted or rejected, with the invalidation list and where it went. Then release the occupation.

## Why the boundaries are where they are

**You do not decide what the project should achieve.** You get the Owner's decision recorded accurately, including its scope. An answer applied beyond the scope it was given is the failure this step exists to prevent — and the executor who over-applies it is usually the one who transcribed it.

**You do not carry out the downstream updates.** Your output is an accurate fact plus a visible invalidation list. Both are useful the moment they exist; a half-finished sweep across ten files is not.

**You do not manufacture your own input.** Attribution has a responder, and it is not you. Transcribing an Owner's answer is allowed and expected; presenting your own inference as an Owner input is not, and the attribution fields are what makes the difference readable.

## Known failures

- Evaluating the input before recording it, so a dead instance takes it with them.
- Storing the material because it was easier than extracting the fact, leaving a copy that drifts from its own source.
- Copying material into the repository that was never authorised to live there. The convenient move and the permitted move are different questions.
- Adopting an answer without its scope, then applying it to a system when it was given about one module.
- Leaving an input neither adopted nor rejected. It comes back as the same question from the next instance.
- Fixing everything the change invalidated inside this one execution, ending with some consumers updated and some not.
- Recording an inference of your own as if the Owner had said it.
