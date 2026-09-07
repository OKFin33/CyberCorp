---
name: cybercorp
description: Create or adapt a repository into a self-contained Corp whose work can be continued by replaceable agents. Use when the user asks to establish Corp collaboration or initialize CyberCorp for a project.
---

# Create a Corp

Help the user's Agent establish a project that can continue after the creator leaves. The target repository and its native work system own the result; this skill is a portable creation tool.

Start from the user's goal, agreed project scope, existing owners/materials and actual authorization. Inspect the repository before choosing what to add. Reuse existing Canon and task systems. Ask only for missing decisions that change the product or permitted actions; ordinary engineering choices remain yours.

For a Git/GitHub project without an existing Corp entry, prepare the small input described in [brief.md](references/brief.md), then run:

```sh
python3 scripts/cybercorp.py /path/to/project --brief /path/to/brief.json
```

`--dry-run` shows the file plan. The installer initializes Git if needed, adds repo-local methods/helpers and appends root entry links; it does not commit, publish, create GitHub work or declare readiness. If existing files conflict, adapt their actual owners within the request rather than overwriting them or making a second system. For an already organized Corp, use its own entry and only add the missing capability.

Continue through the generated `docs/corp/README.md` and `.agents/skills/prepare-corp/SKILL.md`. Installing files alone does not complete the user's request. Establish the real shared entry and native work within existing authorization; verify its discoverability and run the relevant actual helpers. Then carry out the whole-project preparation or leave its unfinished work discoverable for another Corpo when the user requested a bounded creation slice.

Preparation covers the agreed project and its dependencies broadly. The depth of design follows actual need and value; do not exhaust every implementation choice or replicate another project's documents. Retain useful unknowns with their impact and acquisition path. Never make the creator's private history a required input.

When an independent consumer is available and authorized, let it enter from the repository without hidden Issue hints or desired conclusions and continue a meaningful outcome. Record what was observed and what remains untested. A structural check, process launch or native task write cannot establish that continuity by itself.

After installation, the target owns its files and can change its methods. Re-running with the same inputs preserves those edits. A version/input change requires an intentional adaptation, not an automatic overwrite. The package is independently copyable; no global installation, CyberCorp service or external skill is needed by generated Corp workers.

The optional separately portable CLI launcher scaffold (`corpo-launcher`) supports user-owned runtime integration and includes Kiro as an example. It is not a prerequisite for creation or subsequent work.
