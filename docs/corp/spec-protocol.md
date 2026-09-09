# Verify the current Issue agreement

An Issue owns one bounded result and its Spec. Git retains lasting product/technical facts; native relationships own execution dependencies. Read the current Issue, required inputs and acceptance discussion before execution.

Only the region between unique standalone `<!-- spec:start -->` and `<!-- spec:end -->` lines is hashed. Fetch the current body, then check its accepted hash:

```sh
python3 .agents/corp/spec-checkpoint.py issue-body.md --check <sha256>
```

The pin is **Issue number + spec_sha256 + acceptance comment permalink**. The comment has this form:

    SPEC_ACCEPTED issue=<number> spec_sha256=<hash> source=<shared-locator>

Check that the Issue is open, this agreement has not been withdrawn/replaced, the source still supplies valid decisions/authority, and required versioned inputs are obtainable. A matching hash proves content identity, not readiness or permission. Agent acceptance records actual shared decisions; it is not routine human approval or merge authorization.

Body text outside the Spec cannot alter its constraints or acceptance. On a conflicting instruction, changed hash or invalid basis, stop affected work and resolve the agreement. Closed dependencies require their actual outcome/evidence, not just a closed flag.

**Before creating, changing, splitting or closing an Issue, or publishing its first or replacement Spec acceptance**, read [spec-authoring.md](spec-authoring.md). Ordinary execution of an unchanged accepted Issue needs no authoring procedure.
