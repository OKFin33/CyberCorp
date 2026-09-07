# Kiro Corpo launcher

Use `scripts/corpo.py --runtime kiro` with Python 3.9+. It calls the user's installed `kiro-cli`, not a model API. No global installation, authentication changes, or repo edits are required. Read its `--help` for options.

Resolve the intended repository and launch directory from the user's request. The repository must be a local Git root with `AGENTS.md` and `README.md`. `--cwd` defaults to that root; use the user's explicit launch directory when supplied. The start prompt contains only a local correlation tag, JSON-encoded repository locator, the request to enter and work under repository rules, and the absence of merge authorization. The repository decides work selection and method; do not insert private history, Issue hints, work ordering or another copy of its policy.

```sh
python3 scripts/corpo.py --runtime kiro start --repo /path/to/repo --cwd /path/to/dev --dry-run
python3 scripts/corpo.py --runtime kiro start --repo /path/to/repo --model claude-opus-5
python3 scripts/corpo.py --runtime kiro start --repo /path/to/repo --tools all --background
python3 scripts/corpo.py --runtime kiro sessions --cwd /path/to/dev
python3 scripts/corpo.py --runtime kiro resume --cwd /path/to/dev --session SESSION_ID
```

Interactive `ask` is the default and needs an actual terminal. Background mode needs the user's authorization for automatic tool approval (`--tools all`). This enables every Kiro tool, including shell; it is not a sandbox or technical merge block. Tool trust does not enlarge project or external-effect authority. Do not retry a permission failure by switching to `all` automatically.

`--dry-run` prints a plan without a worker. Background mode returns a PID and a private local output directory. `process_spawned` means process creation only, not authentication, verified model, readiness or later liveness. Logs may contain sensitive output; inspect the needed part locally, do not dump or upload them wholesale. The displayed model is requested, not independently verified runtime metadata.

Use the returned `launch_tag` with `sessions --match` to locate a new native session by title nonce and exact cwd. Zero/multiple matches or a rewritten title remain unresolved; never select the most recent unrelated session. The nonce is not a repo Agent ID or claim. Resume requires a unique native session in that cwd; the launcher does not detect active execution, so avoid concurrent resume of the same session.

Native session discovery uses Kiro's public JSON listing, not private database schemas. The caller owns any ongoing observation. Do not schedule polling, start extra workers, stop existing workers, retry a launch, or change auth/global trust without the corresponding request. Repository and native tasks continue to own ordinary work.

Verification: `python3 -m unittest discover -s scripts/tests -v`. Tests use a fake CLI and temporary repos. A real model smoke test requires explicit authorization and a disposable project; do not launch unsolicited business work to validate this adapter.
