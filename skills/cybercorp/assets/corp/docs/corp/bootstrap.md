# Enter an existing clone

Use the actual repository root and its intended remote. Preserve existing worktrees, commits, local data and Git operations. For a new independent task, the included helper observes the remote's default branch at a fixed commit and can create an independent worktree:

```sh
python3 .agents/corp/enter.py
python3 .agents/corp/enter.py --worktree /path/to/new-checkout
```

Both commands read the remote, including `--dry-run`. Use them within the user's network authorization; local creation does not require this step. `--remote` selects an existing named remote; `--branch` selects an explicit remote branch when needed. `--dry-run` with `--worktree` plans from that live read without fetching or writing. Network/identity failures are errors, not proof that an old cache is current.

The creation command fetches the observed SHA without writing FETCH_HEAD, creates its own branch and checks the actual result. It leaves the original checkout in place rather than pulling, resetting, stashing or cleaning it. This avoids relying on a clean status or branch name to prove that the original directory may safely be updated. Existing worktree destinations are not reused.

Continue from the new checkout's root and path contracts. If the runtime has cached incompatible old instructions, reliably reload them or use a fresh session before dependent work. File update, runtime reload and accepted task inputs are distinct.

For a resumed task, use its verified shared checkpoint commit and your own worktree rather than starting its implementation again from the latest default branch. Confirm current native execution rights and protect the predecessor's artifacts. A release/expiry only changes execution occupancy.

An old clone that never contained this entry cannot discover a new rule by itself. The first distribution must provide a current clone or explicit available entry. Thereafter the repository owns the entry; the startup prompt need not copy it.

## Ordinary environment

The included helpers use Python 3.9+, Git and the user's normal GitHub CLI authentication. They do not install dependencies, read secrets or change tool trust. The context reader uses GitHub's actual default branch; its read-only result is not an atomic snapshot, authorization or readiness judgment.

Equivalent native CLI/API/UI operations are valid. If a helper is unavailable, use the same shared owners and preserve its observation limits; do not invent empty work/claims from an error.
