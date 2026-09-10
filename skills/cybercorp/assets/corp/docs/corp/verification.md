# Check the actual result and continue from failure

Use the project's build/test entry and declared inputs. New behavior needs checks in that actual entry; zero tests or an old scaffold's green build is not behavior evidence. Reuse existing checks and CI, adding the smallest missing wiring. Keep dependencies/toolchain reproducible from project sources; obtain secrets or external access through the project's authorization.

## Connect the checks

The portable local check is:

```sh
python3 .agents/corp/check.py
```

It checks local Corp routes/method links, helper syntax/self-checks and the reported Git difference. It does not contact GitHub, evaluate natural-language quality, run business tests or establish preparation readiness. Unresolved and remote routes remain explicitly unverified. Run project behavior checks as well. Use the same project-owned command sequence locally and in CI; the installer does not create a project test framework or CI configuration.

For GitHub CI, adapt to the actual default branch. Cover PR candidates and default-branch pushes; retain a manual entry when useful. Fetch the needed Git history. Only superseded runs of the same PR should cancel each other; use separate run identities for default-branch/manual runs. CI does not claim work, merge, deploy, notify or wake instances.

## Identify the tested version

`check.py` reports actual HEAD, working-tree changes, event/run/attempt/job identity and the selected difference. PR events use the event's base commit; pushes use `before` (an initial push uses the empty tree). A manual run uses the previous commit, or the whole initial tree. Local runs default to HEAD plus staged/unstaged and untracked changes. Override with `--base <commit>` or `--base empty` for reproduction. Required missing/unavailable baselines fail; do not substitute an empty range. Keep the event file, checkout and environment evidence with the relevant CI run.

Record project commands, inputs/environment, actual tested commit, job/step and result. Distinguish the PR head from a platform-created merge checkout. Final default-branch evidence must apply to the delivered version; changed bases or heads require an impact judgment and only the necessary rechecks. Local modifications mean the commit alone does not identify the tested tree; retain the diff/new files or a fixed candidate.

## Continue from failure

Locate the failing command/step and actual version. Distinguish code/contract failures, missing environment, cancelled/superseded runs and checks that never executed. Preserve the failure on its native work/CI surface, obtain the same inputs in your checkout, reproduce, fix the cause and check the new result and affected behavior. A diagnosed temporary platform failure may justify a bounded retry, not endless reruns or disabling checks.

Prefer the original work and check for an existing repair holder. A shared-default-branch failure takes priority within its affected scope; continue independent work. Necessary input/permission gaps use the existing checkpoint/release and resume conditions, not a new failure queue. Communicate impact, fixes and unverified scope through [communication.md](communication.md), linking actual evidence. Passing checks prove only their executed scope.
