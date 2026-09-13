---
name: bounded-planning
description: Turn an accepted outcome into work units another instance can take without asking you. Use when the current Milestone has no takeable Issue and its closing conditions do not hold, when no Milestone is current, or when the Owner asks for planning. Not for implementing, and not for deciding what the project should achieve.
---

# Produce work other instances can take without you

Read `docs/corp/README.md` if you have not. Each step names the `mechanics.md` section holding the rule; this file gives the order.

**What you are producing**: a stage another instance can walk into and advance. Not a plan document, not a status board — Issues that carry their own acceptance, wired to each other by real dependencies, under a stage whose closing conditions anyone can check. Everything below serves that.

**How you know you are done**: an instance that has never spoken to you reads the stage and the units, says what to deliver next and why, locates the inputs and checks, and begins — or identifies a scoped stop with a reason. If a unit needs you to explain it, it is not finished. This is the completion test; a PR is not, because this work does not produce one.

## Then, in order

1. **Occupy a carrier first.** Planning has no pre-existing object, so create the carrier Issue, occupy it, then begin. Before that, read existing planning carriers and converge on one rather than opening a parallel effort.

2. **Read the accepted outcome and the current state.** The outcome and its acceptance; the current Milestone with its declared closing conditions; every open Issue in it; open PRs; and the native dependency relations. One bounded observation is enough.

   **Also read what the other work types left for you**, because none of them turns findings into units: lines implementers noted on Issues about things outside their unit, review findings that named a missing unit rather than a blocker, and invalidation lists from adopted input. Those are inputs to step 4, not separate obligations — an unread one is a gap nobody else will close.

3. **Classify what already exists, before looking for gaps.** For each open Issue: takeable, delivered and awaiting an Owner decision, or blocked by a real prerequisite. **Work already delivered and waiting is not a gap** — planning around it duplicates it. A candidate gone stale against the default branch is that Issue's own remaining work, not a new unit.

4. **Find what the outcome needs and nothing covers.** Compare the accepted acceptance against what existing units deliver. Separate a missing implementation from a missing decision and from a missing input: the first is work you create, the other two are returned to whoever owns them with what they block stated plainly.

5. **Create each unit so it carries its own acceptance and fits one instance's lifetime.** Reference required inputs at a fixed version. Express real prerequisites as native dependency relations, not as prose. Set the actual Milestone — a parent link alone does not put work in a stage.

6. **Let both order and parallelism come from the dependencies.** There is no priority field to fill in — an executor takes anything whose prerequisites are met, so a real sequencing constraint has to be a real relation. It does not wait for a round to close. Do not maintain a batch list beside the relations — it becomes a second authority that goes stale the moment an Issue moves.

7. **State or update the stage's closing conditions** in machine-checkable form: named Issues closed, named PRs merged, named checks green. If you added units to a stage whose conditions were already declared, **update them** — stale conditions stay satisfiable, and review then opens on a stage that has moved.

8. **Hand off, or record that nothing is needed.** Both are real outputs. "Nothing is needed" carries the same evidence as a batch of Issues: what you read, how you classified it, why no gap remains. Record it on the carrier and release the occupation.

## Why the boundaries are where they are

Each of these exists because crossing it produces work the next instance cannot take.

**You do not implement.** A unit whose implementation is already half-done inside your planning cannot be taken by anyone else — they would have to read your work to find out what remains. If a unit is small enough to just do, it is still a unit: create it, then take it under `work/SKILL.md` as a separate act with its own occupation.

**You do not change the accepted outcome or its acceptance.** A successor who builds on an outcome you adjusted is building on something nobody authorised. Where the outcome is unclear, or two accepted facts conflict, that is a finding to return — returning it costs one exchange; a stage built on a guess costs the stage.

**You do not judge whether a stage is near done.** That judgement cannot be rechecked by anyone else, so it cannot be handed over. State the conditions instead and the question answers itself, for anyone, at any time.

## Known failures

- Planning around work that is already delivered and only waiting for an authorisation, because open was read as unstarted.
- Filling a gap in the accepted outcome by deciding it, when the gap was a finding to return.
- Writing Specs far ahead of their inputs. They are invalidated before use, and that effort is spent twice.
- Keeping a round list — a batch, a wave file, a planning board — beside the native relations. It becomes the stale authority the next instance trusts.
- Adding units to a declared stage without updating its closing conditions.
- Splitting into sub-units to hand pieces to sub-agents. That is internal execution; it needs no native Issue.
- Producing a plan that reads well and cannot be started: no fixed inputs, acceptance that requires judgement, or dependencies stated only in prose.
