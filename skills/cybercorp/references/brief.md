# Installer inputs

Create this JSON from the user's actual request and repository inspection. It is a local installation input, not a second product or task record. Keep it outside the target repository unless it has an explicit source role.

New project example:

```json
{
  "name": "Receipt Desk",
  "goal": "Help a user turn their own receipts into a monthly expense summary.",
  "scope": ["Import receipts", "Correct extracted values", "Export a monthly summary"],
  "sources": [],
  "canon": []
}
```

For an existing project, route to its actual goal owner instead of duplicating it:

```json
{
  "name": "Receipt Desk",
  "project_ref": "docs/product.md",
  "sources": ["docs/research"],
  "canon": [
    {"id": "api", "target": "api/openapi.yaml", "status": "active"},
    {"id": "import-provider", "target": null, "status": "unresolved"}
  ],
  "github": "example/receipt-desk",
  "milestone": 2
}
```

`name` and either `goal`+`scope` or `project_ref` are required. Other fields are optional. `sources` are existing repository-relative paths to read selectively. Active Canon routes must exist; other statuses are `pending-relocation` and `unresolved`. A listed source is not thereby adopted as Canon. Do not point generated workers at private machine paths or include credentials in inputs.

`github` and `milestone` refer to an actual repository and native Milestone. Omit the Milestone when it has not been established; the resulting route stays unresolved. The installer does not verify GitHub state or create it. The creating Agent follows the generated preparation method to establish and read back shared work within the user's authorization.

Existing root instructions and READMEs remain in place with one appended Corp link. Installation checks all planned file collisions before writing. Repeating the same input/package preserves subsequent project edits. Changed package content requires adaptation even if its version label stayed the same. A failed filesystem write can still leave a partial installation: inspect the reported error and actual files rather than assuming completion. No existing file is replaced to resolve a conflict automatically.

For an existing Corp adopting a newer package, compare package `docs/corp/`, `.agents/skills/` and `.agents/corp/` with project-owned versions. Carry the current entry and `mechanics.md` together with the portable `check.py`, and connect checks to the project's actual command/CI entry per `mechanics.md` section S3. Preserve existing Owner cards, explicit review promises and installation provenance; reinstallation still refuses changed packages. No new installer input is needed.

Carry relevant method changes through the target's normal change process. A project still holding the pre-2026-09-12 layout has eleven separate method documents under `docs/corp/`; replace them with the current entry plus `mechanics.md`, keeping its own Owner card. The rules formerly spread across `development-loop`, `claim-protocol`, `spec-authoring`, `spec-protocol`, `verification`, `milestone-delivery`, `coordination`, `communication`, `damaged-history` and `bootstrap` are now defined once under the eight sub-problems in `mechanics.md`; the old ordinary-PR default review trigger is replaced by section S3, where stage review opens on machine-checkable closing conditions. Preserve accepted explicit review promises, task Spec pins, project edits and initial install provenance. The adopting change itself follows its pre-change agreement, including independent review. Check file adoption, effective agreement and actual instance consumption separately. Reinstallation continues refusing changed packages; it is not a migration command.
