# Replacing an installed mechanism layer

Read this when a project already has a Corp and is moving to a different version of the layer. For a first install read [brief.md](brief.md). For amending the rules of the Corp you are working in, read the closing section of its own `mechanics.md` — that is a different act from this one.

This file is version-independent. **The list of what actually changed between two versions comes from the target version's `CHANGELOG.md`, not from here and not from inference.**

## Establish three facts before changing anything

**What is installed.** Read the files, not the version. `.agents/corp/install.json` records where the first install came from, which is not evidence of what is present now — the project may have edited generated files, and earlier migrations may have been partial.

**What you are moving to.** Pin one commit of the target package and work against that. A migration against a moving default branch cannot be reviewed, and cannot be repeated if it fails.

**The difference between them.** Take it from the target's change record. Breaking changes are the ones that matter: renamed outputs, changed check behaviour, rules that now require something they did not. Anything you infer rather than read is a guess you are about to build on.

## Sort the files into three kinds

The distinction, not the file list, is what carries over between versions.

**The product's.** Replace wholesale. Comparing them line by line wastes the effort that the next two kinds need.

**The project's own.** Must survive. The Owner communication card, the project's declared irreversible-action list, its routing table entries, its checks and CI wiring. A migration that loses these has failed no matter what the checks report.

**The project's edits to product files.** Judge one at a time. The installer refusing to overwrite a changed file is telling you an edit exists — that is information, not an obstacle. For each: does the new version make this edit unnecessary, or does the edit express something the project still needs?

## Migrate as ordinary work in that project

Occupy an object, state the outcome and acceptance, deliver a PR, and honour whatever review that project has promised. Infrastructure is not a reason to skip the project's own agreement. **Reinstallation is not a migration command**; the installer is built to refuse changed files.

Do not carry a second change in the same migration. Replacing the layer and adjusting the project's own rules are separately reviewable, and mixing them makes both unreviewable.

## In-flight work

A layer change alters the context **every** in-flight Spec was written against — not one of them, all of them. Prefer migrating after a batch closes. If you cannot wait, record explicitly whether in-flight work continues under the old agreement or re-aligns to the new one; leaving it implicit means each successor decides differently.

## References that live outside the layer

Anything pointing at the layer from outside it breaks when the layer is reorganised: native object descriptions, project documentation, CI configuration, external notes. **Checks that run inside the repository cannot see a remote object**, so nothing will report those.

Enumerate them, and repoint them at the entry or the routing table rather than at a file. That way the next migration cannot break them again.

## Acceptance has three layers, and they are not substitutes

1. **Files replaced.** The structure check passes and the project's own tests pass.
2. **Agreement in effect.** Nothing in the project still calls a removed helper, reads a renamed output, or links to a heading that no longer exists — including from outside the repository.
3. **An instance can actually work from it.** Give one that has not seen this migration only the project entry, and check that it can state what it may decide alone, what needs the Owner, and what to do next.

The first two can pass while the third fails, and the third is the one that says the migration worked. Report them separately.

## Say what it is

State in the PR that this replaces the mechanism layer, and name the version moved from and to. It is breaking for anything built against the previous layout, and the next instance to read that PR will need to know which agreement was in force when.
