# Mechanics

Every rule in the Corp is defined here, once. Other files may reference a rule; none may restate it.

Each section is one sub-problem: something that must be solved or delivery stops. A rule earns its place only by naming the sub-problem it serves and the guess it removes. A statement that forbids something without removing a guess is not a rule; it belongs in that section's **Known failures**, which you read when something breaks, not before you start.

The governing rule lives in [README.md](README.md). It decides which rules may demand Owner involvement. Nothing here overrides it.

| # | Sub-problem | The guess it removes |
|---|---|---|
| S1 | A work unit carries its own acceptance | how far to take this |
| S2 | Occupation is visible before work starts | whether someone is already on it |
| S3 | Completion rests on evidence that is not self-reported | whether this "done" can be relied on |
| S4 | There is always a next thing to do | whether to stop and wait |
| S5 | Irreversible actions have a small, explicit boundary | whether I may decide this myself |
| S6 | A work unit fits inside one instance's lifetime | whether I can finish this in one go |
| S7 | Abandoned occupation is discoverable and releasable | whether this work is dead |
| S8 | Direction and cross-cutting facts have a durable home | what is true, and where to look |

---

## S1 · A work unit carries its own acceptance

**Stops delivery when missing**: context is compressed, the next instance picks up the Issue, cannot read the previous instance's unstated understanding, and guesses what "done" means. A wrong guess produces waste that nobody detects.

**Derives from**: executors are unreliable.

**Mechanism**. An Issue is the only unit of work. Its body states the outcome, the boundary, the observable acceptance, and how to verify directly. Required inputs are referenced at a fixed version, not copied. Native carrier: Issue body.

Pin the shared `baseline_commit`. Generate the acceptance line from the body's unique nonempty region and publish it as an ordinary comment; keep its permalink. A shareable HTTPS source — a decision permalink, a goal Milestone, or a fixed-commit blob — pins an input. Relative paths and floating branches do not.

Editing a Spec invalidates its old pin. Stop affected writes, resolve the inputs, accept the new content, and update the pins that consumers depend on before they continue. Preserve superseded code and checks as evidence of the inputs they were built against. Navigation, progress and relationship edits do not change the hash and do not waive acceptance.

**Guess removed**: how far to take this, and against which version of the inputs.

**Known failures**
- An Issue whose acceptance reads "implement X well" cannot be verified by anyone, including its author.
- Copying Canon text into the body creates a second copy that drifts. Reference it.
- A Spec edited without re-accepting leaves consumers building against a pin that no longer describes the agreement.

---

## S2 · Occupation is visible before work starts

**Stops delivery when missing**: two instances — or one instance and its own restarted successor — take the same work, produce duplicate or conflicting output, and someone has to decide afterwards whose work to discard.

**Derives from**: executors are unreliable.

**Mechanism**. Before starting any action, leave a visible occupation on a native object.

- Work on an Issue: self-assign it.
- Review of a change: add yourself to the PR's requested reviewers.
- Work whose object does not exist yet — generating the next batch of work, reorganising priorities, any planning that will create Issues: **create the carrier Issue first, self-assign it, then begin.** Occupation cannot be expressed on an object that has not been created, so create it.

Native carriers: `assignee`, `requested_reviewers`.

**Guess removed**: whether someone is already doing the thing I am about to do.

**Known failures**
- Two instances independently notice "not enough upcoming work" and each start planning the next batch. Neither is visible to the other, because the planning had no carrier. This is why planning creates its carrier first.
- Three instances each independently review the same PR to completion before discovering the duplication. Reviewing is an action; it needs occupation like any other.
- A non-atomic read-then-write claim does not prove exclusivity. Visible occupation reduces collisions; it does not eliminate them.

---

## S3 · Completion rests on evidence that is not self-reported

**Stops delivery when missing**: with nobody checking, an instance reports completion that did not happen, downstream work builds on it, and the waste spreads along the dependency chain until it surfaces late and expensively.

**Derives from**: executors are unreliable.

**Mechanism**. Completion means a PR exists and its checks pass. No prose asserts completion.

Evidence has two parts. The automatable part is CI. The non-automatable part — whether the implementation satisfies the intent — cannot be produced by checks. At Issue granularity the cost of judging intent exceeds its return; at Milestone granularity it is both necessary and affordable. **Independent review is therefore this section's mechanism at Milestone granularity, not a separate quality process.**

The Plan that designs a stage states the stage's closing conditions **in machine-checkable form**: which Issues closed, which PRs merged, which checks green. When those conditions hold, review may open. No instance judges whether the stage is "near done" — that judgement does not exist in this design. The reviewer then judges only substance: does the result satisfy the intent.

A reviewer must not have implemented the object under review and must not modify it during review. Sharing a model or an account with the implementer is not the disqualifier; having implemented it is. After ending review, the same instance may take on a repair, but the repair's recheck needs an instance that did not perform it.

Native carriers: Pull Request, Checks, Milestone.

**Guess removed**: whether this claim of completion can be relied on.

**Known failures**
- Closed is not accepted. Cancelled, duplicate and not-planned are not completed.
- All checks green does not establish that a stage was achieved; it establishes that the checks passed.
- One successful run is not a lasting capability.
- A recorded request, a successful send, and a received reply are three different facts.
- Self-review, internal critique and adversarial passes are implementation methods. They do not open a stage review and do not constitute acceptance.
- Existing evidence that already covers the same candidate, agreement and required independence may be adopted by a stage review. The same content is not re-examined because a process has a different name.

---

## S4 · There is always a next thing to do

**Stops delivery when missing**: an instance finishes and finds nothing to take, and the project stalls until someone assigns work.

**Derives from**: delivery must not depend on the Owner assigning each task.

**Mechanism**. Take the highest-priority open Issue in the current Milestone that is not marked as requiring an Owner decision. If none remains, the deficit is itself the work: create the planning carrier per S2 and generate the next batch.

Before generating work that spans Issues, inspect existing planning carriers and converge on them rather than opening a parallel one.

Near-term work is refined to the point of being executable. Distant work keeps its intended outcome and known dependencies and nothing more — Specs written far ahead of their inputs are invalidated before they are used.

Native carriers: Milestone, Label.

**Guess removed**: whether to stop and wait.

**Known failures**
- Instances that have identified real product work but classify it as "might change a delivery commitment" and turn to infrastructure tidying instead. The authorisation to proceed was already written; it did not become behaviour. See the governing rule's burden of proof in [README.md](README.md).
- Improving the conditions for starting is not starting.
- Two planning efforts running in parallel because neither declared a carrier.

**Empirical, not derived**: which situations warrant the "requires Owner decision" label. The first principle yields the need for the distinction, not its content. Let it form in use.

---

## S5 · Irreversible actions have a small, explicit boundary

**Stops delivery when missing**: either every action waits for the Owner, which is indistinguishable from stalling, or an instance performs something unrecoverable.

**Derives from**: authorisation over irreversible actions belongs to the Owner.

**Mechanism**. The project declares its irreversible-action list. Branch protection and permissions enforce exactly that list and nothing else. Everything outside it executes without approval.

When an action does fall inside the list, the Owner's decision cost is part of the design: state the facts, the recommendation, the consequence, and the exact response needed. A pluggable presentation component adapts this to the Owner — an Owner who reads code wants the diff; an Owner who does not wants the consequence in plain language.

Native carriers: Branch protection rules, repository permissions.

**Guess removed**: whether I may decide this myself.

**Known failures**
- Treating an ordinary engineering trade-off as an Owner decision. Ordinary engineering judgement is the executor's.
- Silence, read receipts and elapsed time never grant authority.
- A replaced presentation component cannot grant merge rights, external sends, or any other permission.

---

## S6 · A work unit fits inside one instance's lifetime

**Stops delivery when missing**: the unit outlives the instance. It dies mid-way and leaves a state nobody can safely resume — S1's acceptance criteria cannot rescue it, because not even "how far did it get" is readable.

**Derives from**: executors are unreliable.

**Mechanism**. Two criteria, applied in order. First draw the boundary by independent deliverability: a unit is one result that can be delivered, verified and integrated on its own. Then check the grain against a single context window; if the unit cannot be completed within one, split it into sub-Issues.

The two are not equivalent — an independently deliverable unit can easily outlive one context. Boundary first, grain second.

Split for independent delivery, shared dependencies, handoff, or concurrency that actually pays. Do not split to distribute work among sub-agents; that is internal execution and needs no native Issue. If two units keep designing, changing and accepting the same result together, merge the responsibility or settle the shared agreement first.

Native carriers: sub-Issues, native blocked-by relationships.

**Guess removed**: whether I can finish this in one go or should split first.

**Known failures**
- A unit that requires the instance to "work something out" mid-way, where that understanding never reaches the shared layer, is split wrongly: its successor must work out the same thing again.
- A dependency graph duplicated in body text instead of native relationship fields.

---

## S7 · Abandoned occupation is discoverable and releasable

**Stops delivery when missing**: an instance dies mid-task without releasing its occupation. The task shows as taken, other instances route around it, and it stalls while the state reads as healthy.

**Derives from**: executors are unreliable, and no one is patrolling.

**Mechanism**. An occupation whose object has not changed for longer than the threshold may be taken over: verify the last state, existing PRs and remaining work, then self-assign. A returning former holder must stop its now-invalid execution rather than continue.

Detection uses fields GitHub maintains — `updated_at`, `assignee`, Issue events — not a record the executor writes. **This is deliberate: a self-maintained recovery record introduces its own failure mode.** One mistyped field has been enough to make an execution history unreplayable, forcing the work to move to a new Issue rather than be repaired. Fields the executor cannot mistype cannot be mistyped.

A new occupation inherits nothing from the old one: not its check applicability, not its authorisations.

Native carriers: `updated_at`, `assignee`, Issue events.

**Guess removed**: whether this work is dead and whether I may take it.

**Empirical, not derived**: the threshold. The first principle yields the need for a release path, not a number. Calibrate from observed runs; no default is set here.

---

## S8 · Direction and cross-cutting facts have a durable home

**Stops delivery when missing**: a new instance cannot read where the project is going, and picks work that is locally valid but off-direction. Contracts spanning modules, decisions and their reasons, and rejected options have nowhere to live, so each instance re-derives or re-proposes them.

**Derives from**: executors are unreliable — every new instance must be able to read this.

**Mechanism**. Canon is a routing table plus the authoritative content that has nowhere else to live. Both are files in Git.

The routing table answers: for this scope, which source is authoritative. Scope is expressed as a path prefix, optionally with a domain tag for constraints that cut across directories. Its targets are contract-bearing code, current delivery agreements (Issues), direction (Milestones), and evidence (checks, PRs).

Canon holds directly only what no single Issue or Milestone can hold: contracts spanning modules, architectural decisions with their reasons and revisiting conditions, and options explicitly rejected with why. Everything else is a pointer. Canon does not contain implementation code; it routes to the code that is authoritative for behaviour.

Git carries this rather than Issues, for four reasons that hold independently: content can be pinned to a commit; it is readable offline in a clone without network or token; it can be organised by path; and its lifetime is the fact's lifetime, not a task's. An Issue closes when its task ends, which is not when its facts stop being true.

Implemented behaviour and intended behaviour are both authoritative — they answer different questions. A discrepancy between them is an open difference to be resolved, not something to settle automatically by preferring code or preferring documents. Expose the conflict; the party authorised to change the agreement resolves it. **Search ranking holds no adjudicating power.** Code that has already been written does not retroactively redefine the goal.

An Owner reply that enters this layer keeps its attribution: responder, channel, time, applicable scope, available source. An attributable direct reply may be transcribed by an executor; the Owner need not publish the same decision twice. Received, adopted and executed are three distinct states.

The Owner also supplies input with no request pending — a meeting produced new information, a direction changed. That input enters here through the same attribution, with a lifecycle that ends either in adoption or in **explicit rejection recorded with its reason**. A rejected option with its reason is Canon: without it, the next instance proposes the same option again.

**`unknown` carries two meanings and they must be distinguished**: *undecided* — no decision has been made, and acting requires one; and *unrecorded* — a decision exists but was not written down, and the correct action is to find it, not to make it. Reading *unrecorded* as *undecided* leads an executor to prepare a decision that was never its to make.

**No result is not the same as no constraint.** A retrieval that returns nothing establishes only that this retrieval found nothing. When a known required source is unavailable, suspend the decisions that depend on it; independent work continues.

Native carriers: Git files, Milestone description, Issue attribution comments.

**Guess removed**: what is true, what is merely current, and where to look for either.

**Changing this rule set itself.** These rules are part of the project's authoritative facts, so amending them is a Canon change — but S1, S2 and S6 do not apply to it. There is no Issue to occupy, because the object is the rule set rather than a deliverable. The acceptance tooling may be replaced within the same change, so an acceptance hash computed by an implementation that no longer exists proves nothing. And the layer cannot be half-replaced, so splitting by grain does not apply.

What still applies: merging into the default branch needs the Owner (S5); the decision and its reasons enter the record; and the completion evidence is the test suite, the structure check and the decision record, plus the PR and its checks once pushed. **Say plainly in the PR that it is a mechanism change** — it is breaking for any project already running the previous layout, and that project's migration is its own change under its own agreement.

**Known failures**
- Announcing a changed goal by pointing at code that was already written.
- Letting retrieval relevance decide which of two conflicting sources is authoritative.
- Summary caches claiming to be more current than their source.
- An unmerged candidate treated as overriding the accepted baseline.
- Reading `unknown` as "undecided" when it means "not yet written down".
