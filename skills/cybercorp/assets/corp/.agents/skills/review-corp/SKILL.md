---
name: review-corp
description: Independently review a substantive Corp change against its actual agreement, implementation and evidence. Use when assigned a fixed candidate for review; the reviewer must not have implemented it.
---

# Review the actual candidate

Read the current Spec and required Canon, actual base/head and changed implementation from an independent checkout. Preserve earlier valid evidence when its inputs are unchanged. Select checks that can expose concrete errors, omitted behavior or avoidable complexity; challenge proposed fixes or approvals that lack a real reason.

State actionable findings with the affected behavior, evidence and minimum correction. Do not require speculative abstraction, a bigger framework, universal test ordering or repeated full checks just to show process compliance. A review with no blocking finding is valid when supported by the inspected scope.

Identify your instance and that you did not implement this candidate. Distinguish checks you executed, evidence you relied on and behavior still untested. Build/CI success is not unexecuted runtime behavior, multiple profiles are not different applications, and tool success is not user value.

Return the conclusion to the existing PR for the exact reviewed head and relevant Spec pin. Changed inputs require relevant re-evaluation. Review does not grant merge authority or change the product agreement.
