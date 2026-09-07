---
name: corpo-launcher
description: Launch a repository worker through a user-configured CLI runtime, or adapt the supplied Kiro example. Use when the user asks to start a Corpo or connect another CLI runtime to the launcher.
---

# Corpo CLI launcher scaffold

This is a portable starting point for user-owned runtime integration. It calls installed CLIs; it does not install them, authenticate, choose a provider or promise ready-made support for every runtime. The target Corp can operate without this launcher.

Resolve the repository, launch directory and intended runtime from the request. The user owns CLI setup, credentials, model choices, tool approval and the native command syntax. Inspect the installed CLI's help when configuring it; never guess flags or copy Kiro's trust/session assumptions into another runtime. Work selection and method remain in the repository.

## Connect a CLI

Use Python 3.9+ and provide the native command explicitly after `--`:

```sh
python3 scripts/corpo.py --runtime cli start --repo /path/to/repo --dry-run -- your-cli your-flags '{prompt}'
```

Replace the example command with one supported by the user's installed CLI. `{prompt}`, `{repo}` and `{cwd}` are substituted only when they occupy a whole argument; all other arguments pass through unchanged. No shell expansion occurs. The prompt contains a correlation tag, repository locator and the request to work under repository rules with no merge authorization. The tag is not a native session identity.

Remove `--dry-run` to hand over the current terminal to the selected CLI. This generic bridge starts only: native session listing, resume, tool approval and background flags differ by runtime and remain the user's integration work. Do not automatically add broad tool permissions or change authentication. Avoid passing secrets in command arguments; use the CLI's native credential setup.

For runtime-specific behavior, supply a user-owned Python adapter:

```sh
python3 scripts/corpo.py --adapter /path/to/my_adapter.py start your-options
```

The adapter receives the remaining arguments and inherits the current terminal, environment and working directory. It is executable local code, not a sandboxed config. It owns supported actions, validation, native invocation and result reporting; use only an adapter selected or created within the request. No plugin registry or common native-session database is needed.

## Kiro example

`--runtime kiro` selects the included working example for `start`, `sessions` and `resume`. Read [kiro.md](references/kiro.md) when using or adapting it. Its model defaults, native session format and trust flags are Kiro-specific; users must reconcile them with their installed version. Kiro is an example integration, not a dependency or default provider for other runtimes.

Verification: `python3 -m unittest discover -s scripts/tests`. Tests exercise local fake CLIs and exact process arguments. A successful handoff, PID or dry-run does not prove native login, model identity, repository consumption or business delivery. Launch real model work only within the user's request.
