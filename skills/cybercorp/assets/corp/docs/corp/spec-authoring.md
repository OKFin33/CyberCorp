# Create, change or finish an Issue agreement

Use the same Issue for its result and execution entry; no separate Spec numbering is needed. This extends [spec-protocol.md](spec-protocol.md).

## Create and accept

Put these within one pair of standalone Spec markers:

- Determinate shared `baseline_commit` and goal/decision sources.
- Outcome, scope, observable acceptance and direct verification.
- Versioned required Canon/technical inputs, unknowns, external effects and stop conditions.
- Lasting facts to return and their canonical owners.

Maintenance/investigation still needs an outcome and evidence. Link unchanged Canon instead of copying it. Navigation can remain outside the region; progress and execution events belong in comments, relationships in native fields.

When inputs resolve, necessary decisions have shared sources, unknowns no longer change this result, and active conflicts are handled, fetch the body and generate the acceptance line:

```sh
python3 .agents/corp/spec-checkpoint.py issue-body.md --checkpoint --issue <number> --source <decision-locator>
```

Publish it as an ordinary comment and retain its permalink. The tool normalizes newlines/trailing whitespace and hashes the unique nonempty region; it does not decide acceptance or publish. New product commitments and authority/external-effect decisions require their actual decision maker.

Use a shareable HTTPS source: a decision permalink, goal Milestone or fixed-commit blob. Relative paths/floating branches do not pin repository inputs. Verify access, authority and privacy; syntax validation alone proves none. Never put secrets in URLs. If an older acceptance uses unsupported source syntax, preserve it and append a valid acceptance after checking the same decision/current Spec. Unchanged content keeps its hash; affected consumers recheck the new acceptance permalink.

## Change and decompose

A Spec edit invalidates its old pin: stop affected writes, resolve decisions/inputs and accept the new content. Check actual child, implementation and review consumers; return compatibility/rework decisions and update required pins before they continue. Preserve old code/checks as evidence of their original inputs. Navigation, progress and relationship edits do not change the hash or waive acceptance; recheck changed dependencies and cycles.

Split into native sub-issues only for independent work, dependencies or handoff. Parent owns the overall result; children own their differences and reference the parent pin they need. Sub-issues are not automatically blockers. Native blocked-by/blocking fields own real prerequisites; do not duplicate a DAG in body text or split by team/directory alone.

Delivery work must have the actual focus Milestone set and appear in global discovery; parent/goal links alone do not establish membership. Cross-Issue work generation first uses [coordination.md](coordination.md).

## Finish or retire

Check the whole agreement, actual merge/result evidence and lasting Canon updates before closing. Use closing PR references only for complete results; partial/multi-PR work uses nonclosing links. Cancelled/duplicate/not-planned is not completed, and closed alone is not acceptance.

Keep overall evidence in the original Issue. Create more work only for a real remaining result, not an empty integration ticket/PR or terminal marker. Non-code work can close with direct evidence. Already integrated results need reconciliation with shared Git, not reimplementation.

Unreplayable execution history follows [damaged-history.md](damaged-history.md); closing an Issue cannot bypass its holder or turn incomplete work into completion.
