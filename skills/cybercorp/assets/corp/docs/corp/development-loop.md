# Work in the Corp

Read the goal and relevant Canon through this repository's entry. Recover explicitly assigned work or choose the next useful action from the actual delivery goal, completed results, open work and dependencies. Your method, decomposition and tool use are yours to choose within the agreed result and authorization.

```sh
python3 .agents/corp/repo-context.py
python3 .agents/corp/repo-context.py --issue 7
```

The global read observes the native Milestone referenced by `current-delivery-focus`, its work and open PRs. Replace the example `7` with the actual Issue. Explicit ordinary work does not require unrelated global discovery to succeed. A coordination Issue also reads its current coordination collection. Neither output ranks work or grants execution rights; read the actual discussions, required inputs and artifacts. An unresolved focus calls for establishing the actual shared goal, not guessing the latest Issue.

## Match the work to a method

- Preparation or missing project inputs: `.agents/skills/prepare-corp/SKILL.md`.
- Implementation, investigation or bounded coordination: `.agents/skills/work-corp/SKILL.md`.
- Independent review of a substantive change: `.agents/skills/review-corp/SKILL.md`.

These files travel with the repo. Native skill discovery is optional; reading the file works too. Do not require every task to visit every method. Ordinary internal design choices can be resolved and returned to their fact owners by the authorized Agent. A Canon owner denotes responsibility and fact location, not automatically a human approver.

## Declare before coordinating

Before expensive planning or generating downstream work across Issues, inspect the current goal, existing outcomes and all open/closed `work:coordination` Issues in that native Milestone. Reuse an existing bounded coordination entry. Otherwise create only a minimal outcome Spec with that classification and Milestone, then reread the collection before deeper planning.

The lowest open number is an entry candidate, never execution authority. Read competing histories, actual holders and retained results. An existing holder is not displaced by a lower number or late label change; reconcile overlap and transfer results before retiring duplicates as not planned. A closed winner does not turn leftover duplicates into a new round. New coordination needs a new actual gap.

Use the normal accepted Spec and claim for the converged entry. If only its initial Spec structure is broken, declare a narrow structural repair in ordinary comments, converge on the first still-active repairer and repair only from shared decisions; then accept/claim normally. This does not permit deeper planning or damage repair of execution events. Ambiguity pauses the conflicting scope, not unrelated implementation or review. There is no permanent manager or planning queue for all work.

## Agree, execute and recover

An Issue holds its result and Spec; [spec-protocol.md](spec-protocol.md) explains the content pin and acceptance. Agent acceptance is a shared content record based on actual decisions and inputs, not routine human approval. Native sub-issues/dependencies are used only for real independent work or prerequisites.

Use [claim-protocol.md](claim-protocol.md) for execution occupancy and recovery. Work in independent worktrees. At meaningful progress, direction change, handoff or waiting, share the usable result and what comes next. Protect other Corpo's files and processes; clean up resources by the actual owned identity, not broad process-name patterns.

Before publishing an event, check it against freshly fetched complete comments:

```sh
python3 .agents/corp/format-event.py event.json --comments comments.json
```

This prints a valid prospective fence or an error; it does not publish or reserve execution rights. After the native comment is posted, reread actual server order and identity. Before consequential writes, verify the current Issue, Spec, claim and actual conflicts again. No helper is an atomic lock.

Current delivery work must have its actual native Milestone set and be discoverable through the global read; a goal link or parent relationship alone does not establish that membership. Read closed dependency outcomes before calling them satisfied. Shared decisions that affect other work must reach their existing owners before dependent execution continues.

When waiting, leave a usable checkpoint and release occupancy. Do not remake delivered work because its worker left. Review and CI claims must identify the actual object and what was checked. Follow the project's merge authority; the supplied default requires a specific PR/head/checks/method authorization for one attempt. Tool trust, a matching hash, a review or a coordination role cannot grant it.
