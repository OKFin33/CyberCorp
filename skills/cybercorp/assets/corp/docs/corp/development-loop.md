# Work in the Corp

Recover assigned work from the entry's goal, required inputs and actual results. If no work is assigned, discover the native delivery focus and its gaps:

```sh
python3 .agents/corp/repo-context.py              # focus, work and open PRs
python3 .agents/corp/repo-context.py --issue 7    # actual assigned Issue
```

Replace `7` with the actual Issue. Read relevant discussions/artifacts behind the output. Helpers neither grant rights nor rank work; failure is not empty work. An unresolved focus needs a real shared goal, but does not block unrelated assigned work.

## Choose the needed method

- Implementation/investigation: `.agents/skills/work-corp/SKILL.md`.
- Fixed candidate review: `.agents/skills/review-corp/SKILL.md`.
- Preparation gap: `.agents/skills/prepare-corp/SKILL.md`.
- Before expensive cross-Issue planning or generating downstream work: [coordination.md](coordination.md), then the work method for the converged Issue.

Read files directly if native skill discovery is unavailable. A fact owner identifies responsibility, not an automatic human approver. Return shared premise changes to affected existing owners before their dependent execution continues.

## Notice an anomaly and keep work scoped

Check a concrete discrepancy only far enough to determine its effect on correctness, authority, required inputs, acceptance or shared state.

- Unaffected action: continue; briefly record the discrepancy, suspected impact and disposition on an appropriate existing surface. Reuse equivalent records unless evidence changes. A report does not assign repair/tracking, require a reply or create a task; speculative possibilities need no report.
- Correction already within your agreement and authority: perform and verify it; a report cannot replace owned work.
- Affected action, or unresolved relevant impact: pause only dependent execution/acceptance, state the missing basis and resume condition, and continue independent authorized work.

Preserve accepted conditions and pins until changed through [spec-authoring.md](spec-authoring.md). Waiting for final acceptance/merge need not stop independent implementation or checks; it grants no new product commitment or external authority. For local-only work, use its existing local record; do not invent a remote reporting prerequisite. Protect private inputs and preserve actual accepted reporting conditions. Claimed work entering a wait still needs the checkpoint/release in [claim-protocol.md](claim-protocol.md).
