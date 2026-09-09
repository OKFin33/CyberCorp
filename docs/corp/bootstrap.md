# Enter an existing clone

Preserve the original checkout, WIP and Git operations. For a new independent task, observe its intended remote's fixed default-branch commit and optionally create your own checkout:

```sh
python3 .agents/corp/enter.py
python3 .agents/corp/enter.py --worktree /path/to/new-checkout
```

Both read the network, including `--dry-run`; local creation does not require them. `--remote` chooses an existing remote; `--branch` an explicit remote branch. `--dry-run --worktree ...` plans without fetching/writing. Failures do not establish that cached state is current.

The helper fetches the observed SHA without changing FETCH_HEAD and creates its own branch in a new destination. It does not pull/reset/stash/clean the original. Read the new checkout's root/path contracts in the actual runtime; reload incompatible cached instructions or start a fresh session. Updated files do not change accepted task pins or prove runtime reload.

For resumed work, use its verified shared checkpoint in your own worktree and recheck current execution rights. An old clone lacking this entry first needs explicit distribution of a current entry/clone.

Helpers need Python 3.9+, Git and ordinary authenticated `gh`; they install nothing or change tool trust. Equivalent native CLI/API/UI operations are valid under the same contracts and observation limits.
