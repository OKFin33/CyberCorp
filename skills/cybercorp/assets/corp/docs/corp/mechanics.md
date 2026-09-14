# Mechanics

Every rule in the Corp is defined here, once. Other files may reference a rule; none may restate it.

Each section is one sub-problem: something that must be solved or delivery stops. A rule earns its place only by naming the sub-problem it serves and the guess it removes. A statement that forbids something without removing a guess is not a rule; it belongs in that section's **Known failures**, which you read when something breaks, not before you start.

The governing rule lives in [README.md](README.md). It decides which rules may demand Owner involvement. Nothing here overrides it.

Sections follow the order an execution meets them.

| Sub-problem | The guess it removes |
|---|---|
| There is always a next thing to do | whether to stop and wait |
| Occupation is visible, and an abandoned one can be taken over | whether someone is already on it, and whether that someone is me |
| A work unit carries its own acceptance | how far to take this |
| A work unit fits inside one instance's lifetime | whether I can finish this in one go |
| Completion rests on evidence that is not self-reported | whether this "done" can be relied on |
| The work, the occupation and the execution site end separately | whether this branch or checkout may go, and what my release proved |
| Irreversible actions have a small, explicit boundary | whether I may decide this myself |
| Direction and cross-cutting facts have a durable home | what is true, and where to look |

---

## There is always a next thing to do

**Stops delivery when missing**: an instance finishes and finds nothing to take, and the project stalls until someone assigns work.

**Derives from**: delivery must not depend on the Owner assigning each task.

**Mechanism**. Take **any Issue that is takeable now**: in the current Milestone, not marked as requiring an Owner decision, and with every native prerequisite satisfied. More than one qualifies — take either. If none does, the deficit is itself the work: create the planning carrier, occupy it, and generate the next batch.

**There is no priority order to read, and none to maintain.** An Issue being in the current Milestone already says this stage delivers it, so which one goes first does not change whether the stage completes. Sequencing that does matter is already in the dependency relations. Ranking beyond that would be a judgement no one else can recheck, held in an instance that will be replaced — and throughput comes from starting more instances, not from ordering one instance's queue.

**Open does not mean takeable.** An open Issue may be unstarted work, or work already delivered and waiting on an Owner decision. Two signals carry the difference, and neither alone is enough: **an unmerged candidate referencing the Issue** — reported per Issue by the observation, so it holds even when nobody labelled anything — and **the Owner-decision label**, which is the only one that survives the candidate being closed or merged while the Issue stays open for a remaining acceptance criterion. A rule that depends on an executor remembering an extra action is a rule that will be unenforced somewhere; the candidate signal is there for exactly that case. A third belongs beside them: **prerequisites that are not yet satisfied**, reported per Issue as the open ones only. It is not interchangeable with the other two — an Issue with no candidate and no label is still not takeable while something it declares as a real dependency remains open, and an observation that omits this makes the rule below unenforceable by the executor it addresses.

**Bounded planning is bounded by four limits.** It arranges work under an accepted outcome, and those limits are what keep it from becoming a second decision-maker: it does not implement; it does not change the accepted outcome or its acceptance; it does not judge whether a stage is near done, only states the conditions by which anyone can check; and its output must be takeable by an instance that never spoke to it. **That last one is its completion — not a PR, which this kind of work does not produce.**

Parallelism is derived from the native dependency relations, not from a stored batch. An instance starts anything whose prerequisites are met; it does not wait for a round to close. A separate list of what is in this round is a second source of truth that goes stale as soon as an Issue moves.

Before generating work that spans Issues, inspect existing planning carriers and converge on them rather than opening a parallel one.

Near-term work is refined to the point of being executable. Distant work keeps its intended outcome and known dependencies and nothing more — Specs written far ahead of their inputs are invalidated before they are used.

Native carriers: Milestone, Label.

**Guess removed**: whether to stop and wait, and which of several open Issues to take.

**Known failures**
- Identifying real product work, then classifying it as "might change a delivery commitment" and turning to infrastructure tidying instead. See the governing rule's burden of proof in [README.md](README.md).
- Improving the conditions for starting is not starting.
- Ranking the open Issues before starting, or waiting for someone to rank them. Every one whose prerequisites are met is takeable; the ordering that matters is already expressed as dependencies.
- Two planning efforts running in parallel because neither declared a carrier.
- Planning around work that was already delivered and only waiting for an authorisation, because open was read as unstarted.
- Adding units to a stage whose closing conditions were already declared, without updating them: the stale conditions stay satisfiable and review reopens on a stage that has moved.

**Empirical, not derived**: which situations warrant the "requires Owner decision" label. The first principle yields the need for the distinction, not its content. Let it form in use.

---

## Occupation is visible, and an abandoned one can be taken over

**Stops delivery when missing**: two instances — or one instance and its own restarted successor — take the same work and produce conflicting output that someone must later discard. Or an instance dies still holding an occupation: the task reads as taken, others route around it, and it stalls while the state looks healthy.

**Derives from**: executors are unreliable, and no one is patrolling.

**Mechanism**. Before starting any action, leave a visible occupation on a native object: a self-assignment **plus a comment naming an instance ID unique within your runtime**. The assignment shows that this account has something running; only the ID tells one execution from another under it.

One ID per execution, generated once and used throughout it:

```sh
python3 -c 'import uuid; print("aid-v1-" + str(uuid.uuid4()))'
```

**A new instance gets a new ID.** Context compaction keeps the ID only within the same execution that still holds the occupation. An ID carries no authentication and no rank — it identifies, it does not authorise.

Where the occupation goes:

- Work on an Issue: self-assign it, then comment with your instance ID, the object and the scope.
- Review of a change: add yourself to the PR's requested reviewers, then comment the same way.
- Work whose object does not exist yet — generating the next batch of work, reorganising priorities, any planning that will create Issues: **create the carrier Issue first, occupy it, then begin.** Occupation cannot be expressed on an object that has not been created, so create it.

After posting, reread the complete comments and confirm that the **first valid occupation in server order is yours**. Comments are not atomic locks and this is not an atomic read-then-write: server order is what arbitrates, the loser stops its conflicting writes rather than negotiating, and visible occupation reduces collisions without eliminating them. Scopes state expected change boundaries, not directory locks.

**Taking over.** Every existing occupation is taken over the same way, including one left behind by your own site — a restarted instance is a different instance with none of its predecessor's context, and treating an occupation as already-mine invites resuming a half-state without checking it.

Takeover is conditioned on a recorded observation, not on a waiting period. Read the object's last change time, its open PRs and the remaining work; record what you found on the object; then self-assign. A returning former holder must stop its now-invalid execution rather than continue — that obligation is what bounds the cost of taking over early, so the decision never requires proving the predecessor is dead. A project may declare a threshold as a shortcut past the recorded observation; where none is declared, the observation is the condition.

Detection uses fields GitHub maintains — `updated_at`, `assignee`, Issue events — not a record the executor writes. A new occupation inherits nothing from the old one: not its check applicability, not its authorisations.

Native carriers: `assignee`, `requested_reviewers`, occupation comments, `updated_at`, Issue events.

**Guess removed**: whether someone is already doing what I am about to do, whether that someone is me, and what I must do before taking it.

**Known failures**
- An action with no pre-existing object goes unoccupied: two instances each start planning the next batch, or three each review the same PR to completion, before discovering the duplication. Planning and reviewing are actions; they need a carrier like any other.
- Posting an occupation and starting work without rereading. Two instances can post before either sees the other; only the reread establishes who holds it.
- Reading `assignee` alone on a shared account and concluding either "someone else has this" or "that was me" — accounts cannot tell those apart, instance IDs can. Conversely, reading an ID as authority: it says which execution is here, not what it may do.
- An occupation that looks alive because someone edited a label or a title, while the work itself has not moved. Activity on the object is not progress on the work.
- Taking over without reading the last state and existing PRs first — the previous holder may have merged something. Or the opposite: treating an undeclared threshold as a reason to wait, when the recorded observation is the condition and the absence of a number blocks nothing.
- A returning former holder continuing from where it stopped, unaware its occupation lapsed and the work moved on.

**Empirical, not derived**: any threshold a project declares as a shortcut. The first principle yields the need for a release path and a visible takeover record, not a number. Calibrate one from observed runs if the shortcut is worth it; the recorded observation works without it.

---

## A work unit carries its own acceptance

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

## A work unit fits inside one instance's lifetime

**Stops delivery when missing**: the unit outlives the instance. It dies mid-way and leaves a state nobody can safely resume — the unit's own acceptance criteria cannot rescue it, because not even "how far did it get" is readable.

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

## Completion rests on evidence that is not self-reported

**Stops delivery when missing**: with nobody checking, an instance reports completion that did not happen, downstream work builds on it, and the waste spreads along the dependency chain until it surfaces late and expensively.

**Derives from**: executors are unreliable.

**Mechanism**. Completion means a PR exists and its checks pass. No prose asserts completion.

Evidence has two parts. The automatable part is CI. The non-automatable part — whether the implementation satisfies the intent — cannot be produced by checks. At Issue granularity the cost of judging intent exceeds its return; at Milestone granularity it is both necessary and affordable. **Independent review is therefore this section's mechanism at Milestone granularity, not a separate quality process.**

The Plan that designs a stage states the stage's closing conditions **in machine-checkable form**: named Issues closed, named PRs merged, named checks green. Write them as a list a reader can verify without judgement — `closes #12, #14`, `merges #15`, `checks: tests` — not as prose like "when the export path is solid". When those conditions hold, review may open. No instance judges whether the stage is "near done" — that judgement does not exist in this design. The reviewer then judges only substance: does the result satisfy the intent.

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

## The work, the occupation and the execution site end separately

**Stops delivery when missing**: an execution ends and leaves branches, worktrees and temporary checkouts nobody can classify. The next instance either treats an abandoned half-state as live work, or clears the site holding the only copy of a result. The first wastes a run; the second is unrecoverable.

**Derives from**: executors are unreliable, and the site an execution runs in outlives it.

**Mechanism**. Three endings, each with its own evidence and its own remaining action:

| Ending | Its evidence | What it does not establish |
|---|---|---|
| The result | what the rule above on evidence that is not self-reported requires | that any local object may now go |
| The occupation | a release, or a takeover recorded on the object | that a process stopped, or that the candidate is discardable |
| The execution site | the object absent on readback, nothing reachable only from it lost | that the work is finished, or that another site is clean |

**One comment can end an occupation.** The checkpoint — what was delivered, where the candidate is, what remains, what would resume it — and the release are the same act seen from two sides; splitting them into two comments adds a round trip and a second thing to read without adding a fact. Say both in one, and say plainly that the occupation is released.

Verify before acting, against the current state rather than your memory of it: who occupies the object now, which commits exist only there, which shared result supersedes it, and what still reads it. Then act on that one object and read the result back.

Continuing is the default: take over the existing branch and its PR rather than opening a parallel site. **Do not use `--force` or `--ignore-other-worktrees` to get around the same-branch checkout limit** — that limit is what keeps one writer per branch, and bypassing it produces exactly the conflicting writes occupation exists to prevent. A candidate handed back stays open and findable, or the successor has nothing to continue. Isolate only from a verified result, and record on both objects which replaced which and where the superseded result went. Whatever you keep states its purpose or the condition for resuming it — a retained object with no stated reason cannot be told from a forgotten one.

Closeout splits along who can see what: **the site's creator ends the local one; whoever integrated the change ends the shared branch and PR.** An integrator who leaves merged branches behind has not finished integrating. Either way it belongs to the work itself, not to a routine-cleanup Issue. A cleanup claim carries the scope it was observed in: one machine says nothing about another, and an unrecovered site does not subtract from a delivered result.

Native carriers: branches, PR head refs, `git worktree list`, the Issue or PR comment recording what was kept, why, and what replaced it.

**Guess removed**: whether this branch, worktree or checkout may go, and what my release actually proved.

**Known failures**
- `git clean` leaves ignored content untouched, and `-x` destroys local data the project deliberately keeps untracked. Neither outcome is "the site is empty".
- Reading a release, an expired lease or a closed Issue as evidence that a process stopped.
- Reading "it was merged", or a delete command's exit status, as evidence about the remaining state: the tip may carry commits made after the merge, and the command describes itself.
- Assuming a squash or a rebase preserved the content. Compare the actual result against the tip before dropping the source.
- Removing a checkout directory while leaving its worktree registered in the repository that owns it — or pruning that registration while something is still writing there.
- Declaring everything clean from the one machine you can see.

**Empirical, not derived**: which sites a project treats as disposable. Absent a declared policy, recover the sites this execution created whose unique content is reachable from a shared result, and keep the rest with the reason stated.

---

## Irreversible actions have a small, explicit boundary

**Stops delivery when missing**: either every action waits for the Owner, which is indistinguishable from stalling, or an instance performs something unrecoverable.

**Derives from**: authorisation over irreversible actions belongs to the Owner.

**Mechanism**. The project declares its irreversible-action list. Branch protection and permissions enforce exactly that list and nothing else. Everything outside it executes without approval.

When an action does fall inside the list, the Owner's decision cost is part of the design: state the facts, the recommendation, the consequence, and the exact response needed. A pluggable presentation component adapts this to the Owner — an Owner who reads code wants the diff; an Owner who does not wants the consequence in plain language. **The card is a project-owned file and may live anywhere**: route to it through the entry rather than hardcoding its path.

**The reply is the other half of the same exchange.** An Owner reply keeps its attribution wherever it lands: responder, channel, time, applicable scope, available source. An attributable direct reply may be transcribed by an executor; the Owner need not publish the same decision twice. Received, adopted and executed are three distinct states.

The Owner also supplies input with no request pending — a meeting produced new information, a direction changed, a technology was swapped. **This is the main way Canon changes**, not a side effect of doing the work: most of what makes a fact non-derivable arrives from outside the repository. That input takes the same attribution, and its lifecycle ends either in adoption or in **explicit rejection recorded with its reason**. A rejected option with its reason belongs in Canon: without it, the next instance proposes the same option again. An input in neither state is the one a successor rediscovers and re-asks about.

**Record the input before judging it, and take it before other work.** It exists only in a conversation until it is written to a native object, so an instance that evaluates first and dies loses it. And a stage whose premise has changed produces work that must be redone — discovering that after three Issues close costs all three.

**The material and the fact are different things.** What arrives may be fifty pages; what cannot be re-derived may be three sentences. Requirement descriptions, interaction details and acceptance scenarios regenerate from intent plus constraints. External constraints, settled trade-offs and rejected options do not. **Material does not automatically enter the repository**: what enters is the extracted fact plus a reference to an available source — and that reference may be *none*, recorded as such. Whether the material itself may live here is an authorisation question, not a convenience one. A copy also drifts from its own source, and a drifted copy is worse than none because the next instance believes it.

Naming what a change invalidates is part of adopting it: Canon entries now wrong, Issues whose fixed inputs no longer describe the agreement, consumers built against the old contract, closing conditions that assumed the old direction. **Listing them and repairing them are separate acts** — anything spanning several objects is organised as work rather than swept through in one execution.

Native carriers: Branch protection rules, repository permissions, attribution comments.

**Guess removed**: whether I may decide this myself, and what a reply I did not witness authorises.

**Known failures**
- Treating an ordinary engineering trade-off as an Owner decision. Ordinary engineering judgement is the executor's.
- Silence, read receipts and elapsed time never grant authority.
- A replaced presentation component cannot grant merge rights, external sends, or any other permission.
- A reply adopted without its scope: an answer about one module applied to the whole system.
- An input neither adopted nor rejected, left in place for the next instance to rediscover and re-ask.

---

## Direction and cross-cutting facts have a durable home

**Stops delivery when missing**: a new instance cannot read where the project is going, and picks work that is locally valid but off-direction. Contracts spanning modules, decisions and their reasons, and rejected options have nowhere to live, so each instance re-derives or re-proposes them.

**Derives from**: executors are unreliable — every new instance must be able to read this.

**Mechanism**. Canon is a routing table plus the authoritative content that has nowhere else to live. Both are files in Git.

The routing table answers: for this scope, which source is authoritative. Scope is expressed as a path prefix, optionally with a domain tag for constraints that cut across directories. **Each entry says what question it answers**, so an executor can tell which one it needs without opening several — the cost of a vague route is paid by every instance that has to guess. Its targets are contract-bearing code, current delivery agreements (Issues), direction (Milestones), and evidence (checks, PRs).

Canon holds directly only what no single Issue or Milestone can hold: contracts spanning modules, architectural decisions with their reasons and revisiting conditions, and options explicitly rejected with why. Everything else is a pointer. Canon does not contain implementation code; it routes to the code that is authoritative for behaviour.

Git carries this rather than Issues, for four reasons that hold independently: content can be pinned to a commit; it is readable offline in a clone without network or token; it can be organised by path; and its lifetime is the fact's lifetime, not a task's. An Issue closes when its task ends, which is not when its facts stop being true.

**Reference the entry, not the file behind it.** Anything outside this directory that points at a rule — a Milestone description, an Issue body, a project README, an external document — routes through the entry or the routing table. Both are stable; the files behind them are reorganised. A pointer straight at a method file breaks silently the next time this layer is restructured, and nothing in the repository can detect that a remote object went stale.

Implemented behaviour and intended behaviour are both authoritative — they answer different questions. A discrepancy between them is an open difference to be resolved, not something to settle automatically by preferring code or preferring documents. Expose the conflict; the party authorised to change the agreement resolves it. **Search ranking holds no adjudicating power.** Code that has already been written does not retroactively redefine the goal.

**`unknown` carries two meanings and they must be distinguished**: *undecided* — no decision has been made, and acting requires one; and *unrecorded* — a decision exists but was not written down, and the correct action is to find it, not to make it. Reading *unrecorded* as *undecided* leads an executor to prepare a decision that was never its to make.

**No result is not the same as no constraint.** A retrieval that returns nothing establishes only that this retrieval found nothing. When a known required source is unavailable, suspend the decisions that depend on it; independent work continues.

Native carriers: Git files, Milestone description, Issue attribution comments.

**Guess removed**: what is true, what is merely current, and where to look for either.

**Known failures**
- A criterion formed while doing the work, applied to that work, and never written down. The next instance re-derives it or contradicts it.
- Announcing a changed goal by pointing at code that was already written.
- Letting retrieval relevance decide which of two conflicting sources is authoritative.
- Summary caches claiming to be more current than their source.
- An unmerged candidate treated as overriding the accepted baseline.
- Reading `unknown` as "undecided" when it means "not yet written down".
- Storing arriving material because it was easier than extracting the fact from it, leaving a copy that drifts from its own source.
- Adopting an Owner's answer without its scope, then applying it where it was never given.
- A remote object linking to a method file that has since moved. The link reads as valid until someone follows it.

---

## Changing these rules

This section is not one of the sub-problems. It governs edits to this document.

Amending the rule set is a Canon change, but three sections do not apply to it: the object is the rule set rather than a deliverable, so **carrying its own acceptance**, **visible occupation** and **fitting one lifetime** are not the operative constraints — the acceptance tooling may be replaced within the same change, and the layer cannot be half-replaced. What still applies unchanged: the **irreversible-action boundary**, **taking over an abandoned occupation**, and the durable-home rules above.

The rule goes here; its reason goes to the decision record. This document carries rules, the guess each removes, and reproducible failure shapes — not past incidents, justification, or argument that persuades rather than instructs. **The same holds for any method file that routes into this one**: it sequences and points, it does not restate rules or repeat their failure lists.

A blank is allowed where content can only form in use, but **a blank must carry a default action** — otherwise the executor stops to guess, which is the failure this document exists to prevent. State what to do in the absence of the missing value.

Every "guess removed" line is itself a claim. Before adding one, take the least favourable legal state — the project declared nothing, several instances share one account, the previous instance vanished without a word — and check that the guess is actually gone. The same test applies to a tool's field name: it may not claim more than it computes.

The completion evidence for a change here is the test suite, the structure check and the decision record, plus the PR and its checks once pushed. **Say plainly in the PR that it is a mechanism change** — it is breaking for any project already running the previous layout, and that project's migration is its own change under its own agreement.
