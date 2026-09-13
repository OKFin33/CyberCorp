# Phase 2: establish the Corp with the Owner

The installer did Phase 1 — it copied files, substituted placeholders and wrote a `canon-map` skeleton. It could not do this part, because this part needs judgement and it needs the Owner.

**Both must be present for Phase 2.** Some of what a Corp needs is known only to whoever started the project: what the thing is for, which constraints are external and non-negotiable, which options were already tried and rejected and why. No amount of reading the repository recovers it. This is the one stretch where the Owner's attendance is required — **after it, running the Corp does not need them except to authorise irreversible actions.**

Phase 2 is done once. The work types under `.agents/skills/` take over from there.

## What goes into the initial Canon

Canon holds only what cannot be re-derived from something else: contracts spanning modules, architectural decisions with their reasons and revisiting conditions, options explicitly rejected with why, and external constraints. Everything else is a pointer.

**A PRD is not Canon.** Fifty pages may contain three facts that cannot be re-derived. Those three go in; the fifty pages stay where they are and Canon points at them. Copying the document in creates a second copy that drifts from its own source, and a drifted copy is worse than no copy because the next instance believes it.

**Material does not automatically enter the repository.** What enters is the extracted fact plus a reference to an available source — and that reference may be *none*, recorded as such. Whether the material itself may live here is the Owner's authorisation question, not the executor's convenience.

## How to find out what only the Owner knows

Ask, in rounds, and write down the answers with their attribution. The four things worth asking for map to the four kinds of Canon:

- **What is this for, and what would make it a failure even if it worked?** — intent and its acceptance
- **What is fixed from outside** — a platform, a contract, a deadline, a regulation — **that no engineering decision here may override?** — external constraints
- **What has already been decided, and what was the reason?** Especially where the reason is not visible in the result. — architectural decisions
- **What did you already consider and reject?** — rejected options with their reasons, which stop the next instance proposing them again

Record each answer with responder, channel, time, applicable scope and available source. **An answer without its scope is the one that gets over-applied later.**

Stop asking when the answers stop changing what you would write down. Unanswered questions are recorded as unanswered, not guessed.


## Then, in order

1. **Verify the native work surface** within your authorization: the actual repository, the delivery Milestone, its classification. Map their owners in `docs/corp/canon-map.yaml`. A route that cannot be established yet stays `unresolved` rather than guessed.

2. **Keep the unconditionally-read file lean.** Whatever the host reads on entry without being asked — `AGENTS.md` or its equivalent — is paid for by every executor on every task, and content aimed at someone else blurs which constraints apply. It carries only what any instance working here needs: local-data and authorization boundaries, plus the route to the Corp entry. Contributor guidance — layout, environment, checks, maintenance locations — belongs in a separate file, and the entry file should say plainly that an executor does not need it.

3. **Adopt only the Canon this project needs.** Material existing is not material adopted. Place it with its owners and check affected consumers, not copied files. Design will expose input gaps: resolve ordinary choices, return factual conflicts to their owners, and obtain only the decisions that change commitments or authority.

4. **Derive the route with the Owner**: overall scope and acceptance, then the near-term focus. State the first stage's closing conditions in machine-checkable form. Keep distant work coarse — Specs written far ahead of their inputs are invalidated before use.

5. **Resolve the `unresolved` routes.** The skeleton leaves `active-change-specs` and `current-delivery-focus` with no target, because the installer cannot know where this project's work lives. Point them at the actual native objects. **While either stays unresolved, the Corp is not established** — `check.py` says so, and no work Corpo should be started here yet.

6. **Hand the first batch to bounded planning.** Establishing work units is not this file's job: `.agents/skills/bounded-planning/SKILL.md` owns it, and it owns the same act every stage afterwards. Give it the route and let it produce the units.

7. **Hand off.** Phase 2 is done when a successor who does not know your process can read the scope and route, say what to deliver next and why, locate the implementation, inputs and checks, and begin — or identify a scoped stop. Record what remains missing, and what you kept — trial installs, consumer fixtures, temporary checkouts — under the rule that the work, the occupation and the execution site end separately. Received inputs, adopted Canon and verified results stay distinct.

Cover the agreed scope broadly; deepen only where the near-term work needs it. No extra planning role, document checklist or approval stage is required.

When an independent consumer is available and authorized, let it enter from the repository and native work alone, without private answers. Record its actual result and any hidden dependency it hit. If unexercised, keep that limit in any claim about readiness.
