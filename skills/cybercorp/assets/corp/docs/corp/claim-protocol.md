# Execute and leave recoverable work

For bounded implementation, investigation or coordination, first verify [spec-protocol.md](spec-protocol.md), required dependencies and actual cross-Issue/resource conflicts. A fixed PR review uses the review method without requiring a new Issue/claim.

## Claim and resume

Use one runtime-unique instance ID throughout this execution; otherwise generate one:

```sh
python3 -c 'import uuid; print("aid-v1-" + str(uuid.uuid4()))'
```

A new instance gets a new ID. Compression retains it only for the same execution with valid occupancy. IDs convey no authentication or rank.

Read **complete, fresh, paginated Issue comments** and replay them at a trusted UTC time:

```sh
python3 .agents/corp/work-state.py comments.json --at <trusted-UTC-time>
```

The input is a REST comments array or array of pages. The helper is offline: it cannot verify completeness, credentials or artifact reachability. If reads/time/order cannot be trusted, stop conflicting writes and coordinate. For a reported integrity error that persists after checking retrieval/time, read [damaged-history.md](damaged-history.md) before recovery; do not filter/edit the bad stream or append events to repair it.

An active claim cannot be displaced. After release/expiry without valid renewal, verify the last checkpoint, existing PRs and remaining work before claiming. Use your own branch/worktree from the verified shared result; never discard a predecessor's worktree, force-push or redo delivered work to take over. Normal expiry needs no extra Owner approval. A returning former holder must stop invalid execution.

Post a claim, reread complete comments and confirm that the first valid claim in server order is **your comment ID**. Before each new write segment, renewal, push, handoff and delivery, freshly verify the Issue is still open, its accepted Spec and required inputs remain valid, your claim still holds, and actual execution conflicts are resolved. Changed or missing grounds pause only dependent work until resolved. Losers stop conflicting writes. Comments are not atomic locks; scopes are expected change boundaries, not directory locks. Each branch/worktree has one writer; independent worktrees do not eliminate semantic conflicts.

## Publish events

Append one standalone `agent-event` JSON fence per machine-event comment. Server `created_at` and comment ID determine order/time; never edit/delete prior events. `claim` references below are comment IDs, not instance IDs.

| event | Fields in addition to `event`, `instance` |
|---|---|
| claim | `lease_until`, `base_commit`, `branch`, `scope` |
| renew | `claim`, `lease_until` |
| checkpoint | `claim`, `recovery` |
| release | `claim`, `checkpoint`, `reason` |

Use a future UTC lease and explain the proportionate bounded execution arrangement; no default duration. `base_commit` is the actual execution start, `branch` may be null for non-code work, `scope` is a list of expected paths/boundaries. Later events must match the active claim and instance. Renew before expiry and extend the lease; otherwise checkpoint/release before long checks cross it. Release references a checkpoint comment belonging to that active claim.

Validate against freshly fetched complete comments before posting:

```sh
python3 .agents/corp/format-event.py event.json --comments comments.json
```

This prints the fence without posting/reserving rights. Reread after actual publication. A rejected but replayable transition, such as a non-extending renew, can be corrected by a valid new event while rights remain; an integrity error cannot.

## Checkpoint, wait and hand off

At useful progress, decisive findings/failures, direction changes, handoff or waiting, publish a recovery object:

```json
{"commit":null,"branch":null,"artifacts":[],"done":"result or explicitly none","checks":[],"remaining":"unfinished or unverified work","next":"safe next action and stop condition","waiting_on":[]}
```

For code, pin a commit available on the shared feature branch. For non-code work, link shared artifacts or explicitly state no result. Record actual check commands/runs/results, relevant conclusions/reasons and specific waiting inputs/resume conditions. Keep the Spec pin on the Issue/PR; do not copy its body or private reasoning here.

Publisher and successor must verify remote commit/artifact reachability; helper shape checks do not. Local-only/unpushed work is not cross-machine recovery. If offline, save locally and disclose the unsaved shared-work risk without claiming publication succeeded.

When implementation cannot continue or awaits review/merge/input, checkpoint then release, naming the wait, responsible surface and PR. Release leaves the agreement and delivered work intact; later claim only the remaining result. Preserve others' files/processes and clean up only your owned resource identities.

## Review and integrate

Work owns self-checks and necessary tests. Independent review is triggered by the stage candidate, an explicit request or an accepted commitment, using `.agents/skills/review-corp/SKILL.md`; preserve earlier explicit review promises. Explain specific high-impact changes and evidence in merge communication so the Owner can decide whether that attempt needs extra review. Use [communication.md](communication.md) for the current card and response handling. Before merge, read actual PR/head/checks and obtain the Owner's specific PR/head/checks/method authorization for **one attempt**. Review, tool trust, claim and coordination do not grant it. For an uncertain merge or other external action, inspect the real result before retrying; recovery does not authorize repeated payments, notifications or device actions. Close against the actual agreement using [spec-authoring.md](spec-authoring.md).
