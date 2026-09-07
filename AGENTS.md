# CyberCorp development

Read `docs/product.md` for the product contract, `docs/plan.md` for current implementation scope, and the relevant package before editing. If `docs/anchor/TODO.md` exists, it contains optional local workline context; its absence does not block development. Shared product decisions and required development information belong in the versioned source.

CyberCorp helps a user's Agent establish a self-contained Corp. Preserve the agreed project scope and the model's discretion over ordinary methods. A pilot project's domain, document count, role layout or preparation depth is not a universal requirement.

The creation package is `skills/cybercorp/`. The optional CLI launcher scaffold is `skills/corpo-launcher/`; Kiro is one example adapter, and users own each runtime integration. Both packages must remain independently portable. Generated files belong to the target project and must not be silently overwritten on later installation.

Run `python3 -m unittest discover -s tests` and the relevant package's documented checks. Distinguish file installation, fake-CLI checks, actual runtime behavior, independent handoff and business outcomes. Test success alone is not acceptance of all those capabilities.

Preserve unrelated work and local data. Commit, push, remote creation and merge follow the actual request's authorization; tool access does not grant it. Test repositories are disposable fixtures, not business execution surfaces.

Keep personal logs, real credentials and private project evidence outside the tracked source. Do not force-add ignored files. Public instructions and tests must work from the versioned files alone.
