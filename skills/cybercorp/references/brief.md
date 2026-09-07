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

For an existing Corp adopting the 0.1.0a3 method revision, compare the package's `docs/corp/` method documents and three `.agents/skills/` methods with the project-owned versions. This revision splits authoring, coordination and damaged-history recovery into linked on-demand documents; include those targets when adapting the routes. Carry only the relevant method changes through the target project's existing change process, preserving its decisions, links and edits. Reinstallation remains non-overwriting; installation provenance is not evidence of later adoption.
