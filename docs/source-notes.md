# Implementation sources

The initial native Spec and execution replay helpers were adapted from an earlier maintainer-owned pilot. The selected components are the Spec checkpoint, execution-state replay and repository-context helpers, their protocol/context tests, and the Spec/claim protocol documents.

CyberCorp routes generated helpers through `.agents/corp/` and navigation through `docs/corp/canon-map.yaml`, reads the actual remote default branch, and makes workgroup metadata optional. No pilot domain, prescribed workgroup set, personal filesystem path or fixed Milestone is generated. These are this package's implementations; they do not modify the original pilot.

The creation, preparation, work and review skills were written for CyberCorp's product requirements. They do not vendor the pilot's third-party skill adaptations. Method choice and testing order remain discretionary.

The optional launcher includes a Kiro CLI adapter derived from the maintainer's earlier personal launch tool. It is an example of native CLI integration. The generic command bridge and user-owned adapter entry provide extension points without standardizing provider authentication, model selection, tool trust or native session behavior.

Original private development receipts are local working records, not build inputs or required runtime documentation. The source package, examples and tests can be used independently of them. Verification limits are documented in the README and implementation plan.
