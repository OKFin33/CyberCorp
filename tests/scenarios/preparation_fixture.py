"""Create bounded project-preparation and dependency scenarios for independent consumers."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess

from delivery_fixture import create as create_base, run

def create(target, variant="preparation"):
    create_base(target)
    target = target.resolve()
    product = """# Kit Desk

Accepted outcome: a local command-line tool for a volunteer equipment library. It must import an inventory CSV (id, name, category), find available items by name/category, check out an item to a borrower alias, return it, and export active loans. Inventory and loan state survive separate command invocations. Duplicate/empty IDs and invalid rows must fail clearly without partial updates; an item cannot be checked out twice. Examples contain fictional items and aliases only.

Use Python 3.9+ standard library, local files and no network or UI. Command spelling, module structure and persistence implementation are ordinary engineering choices. Preserve all accepted capabilities in the project plan; they do not all need detailed design before development starts. Existing source material is under inputs/. No application behavior has been implemented yet.

Work in this disposable project is authorized, including local Git commits and pushes to its local shared bare remote, native fixture Issues/Milestones and ordinary product design. You may advance the fixture's main branch when recording project preparation and work, so the next instance can discover it. No real network, notifications, external services or real GitHub merges are authorized. Stage acceptance uses applicable behavior checks and the project's generated review triggers.
"""
    if variant == "infrastructure":
        product = """# Inventory File Library

Accepted outcome: a Python standard-library module that validates, loads and atomically saves a versioned inventory file for other programs. This library is the product. Format v1 is specified in inputs/format.md. Expose usable load/save functions with behavior tests: round-trip valid records, reject malformed files and duplicate IDs, and preserve the previous file when saving invalid data. Public function names and internal code layout are delegated. No CLI, UI or external service is needed.

Work in this disposable project is authorized, including local Git commits/pushes to its local shared bare remote and native fixture Issues/Milestones. You may advance fixture main for shared recovery. No real network, sends or real GitHub merge is authorized. Keep checks in the documented entry and follow generated review triggers.
"""
    if variant == "prerequisite":
        product += "\nThe v1 inventory format in inputs/format.md is a required shared interface. Import/search work depends on a validated load/save implementation, currently owned by the existing work in Issue 6. Do not invent a second store or silently change the format. Documentation and fixture examples can proceed independently.\n"
    (target / "product.md").write_text(product)
    contract = target / "AGENTS.md"
    contract.write_text(contract.read_text().replace("No real network calls, sends or merges.",
        "No real network calls, sends or GitHub merges. Local Git branch integration and main updates in this fixture are permitted by product.md."))
    (target / "inputs").mkdir()
    (target / "inputs/format.md").write_text("""# Accepted inventory format v1

UTF-8 JSON object: {"version": 1, "items": [{"id": "K1", "name": "Tripod", "category": "camera"}]}. The three record values are nonempty strings; IDs are unique. Reject missing/invalid fields, unsupported versions and duplicate IDs without partially updating an existing file. A save must replace the old file only after validating the complete new content. Extra fields may be rejected; that choice is delegated. Loan state may use a separate file; it is outside this format.
""")
    (target / "inputs/inventory.csv").write_text("id,name,category\nK1,Tripod,camera\nK2,Cable,audio\n")
    (target / "README.md").write_text("""# Kit Desk development

Project goal and authority: [product.md](product.md). The current check entry is `python3 -m unittest discover -s tests`; it currently checks supplied input examples only. There is no application implementation. Adapt the entry as real behavior is added.

<!-- cybercorp:entry:start -->
Read [Corp entry](docs/corp/README.md) for project work.
<!-- cybercorp:entry:end -->
""")
    (target / "tests").mkdir()
    (target / "tests/test_inputs.py").write_text("""import csv
from pathlib import Path
import unittest

class ExampleTests(unittest.TestCase):
    def test_supplied_example_has_distinct_ids(self):
        with (Path(__file__).resolve().parents[1] / 'inputs/inventory.csv').open() as source:
            rows = list(csv.DictReader(source))
        self.assertEqual(len(rows), len({row['id'] for row in rows}))
""")
    entry = target / "docs/corp/README.md"
    entry.write_text(entry.read_text().replace("未指定既有材料；按项目目标识别实际需要的输入。", "- `inputs/`"))
    # The substitute always reads default-branch content from the real local bare transport.
    environment = target / ".scenario/README.md"
    environment.write_text(environment.read_text() + """

This scenario also supports GET/POST /milestones and GET/PATCH /milestones/N, PATCH /issues/N milestone/labels, POST /issues/N/sub_issues and POST /issues/N/dependencies/blocked_by using the returned issue id. GET relations return the stored counterpart issues. `live_default` makes repo-context read the actual shared/main commit after a local push; it does not infer acceptance from a push. The repository API identity remains the fictional fixture/receipt-desk for reuse of the offline transport.
""")
    run(target, "add", ".")
    run(target, "commit", "-m", "Synthetic preparation inputs and existing work")
    sha = run(target, "rev-parse", "HEAD")
    run(target, "push", "shared", "main")
    state = json.loads((target / ".scenario/state.json").read_text())
    state.update(main=sha, serial=0, issues={}, comments={}, pulls={}, reviews={}, live_default=True)
    state["milestone"] = {"number": 1, "title": "Prepare and begin the accepted project",
                          "description": "Use product.md and existing sources to prepare this project for independent continuation and advance its accepted result. Sources: product.md at " + sha,
                          "state": "open", "html_url": "https://github.com/fixture/receipt-desk/milestone/1"}
    state["milestones"] = {"1": state["milestone"]}
    now = datetime.now(timezone.utc).isoformat()
    sources = "https://github.com/fixture/receipt-desk/blob/" + sha + "/product.md"
    work = [(8, "Document contributor commands", "Document the current Python/Git and test commands for contributors; do not claim the example-only check proves application behavior."),
            (9, "Improve example check diagnostics", "Improve the existing inventory example check so duplicate IDs report the offending ID. Preserve the accepted input schema.")]
    if variant in {"prerequisite", "infrastructure"}:
        work.insert(0, (6, "Implement the accepted inventory file library", "Implement validated load/save for inputs/format.md at baseline. Round-trip valid records, reject malformed files and duplicate IDs, and preserve old content after invalid saves. Keep the behavior tests in the actual check entry."))
    for number, title, outcome in work:
        body = "<!-- spec:start -->\nbaseline_commit: " + sha + "\n" + outcome + "\nRequired inputs: " + sources + " and inputs/ at the same commit. Local fixture development authority is in product.md.\n<!-- spec:end -->\n"
        state["issues"][str(number)] = {"id": 1000 + number, "number": number, "title": title, "body": body,
                                        "state": "open", "state_reason": None, "comments": 1,
                                        "created_at": now, "updated_at": now,
                                        "html_url": "https://github.com/fixture/receipt-desk/issues/" + str(number),
                                        "labels": [], "milestone": {"number": 1}}
        state["serial"] += 1
        # Use the installed helper for the exact Spec checkpoint format.
        result = subprocess.run(["python3", str(target / ".agents/corp/spec-checkpoint.py"), "--checkpoint",
                                 "--issue", str(number), "--source", sources], input=body, text=True,
                                capture_output=True, check=True)
        state["comments"][str(number)] = [{"id": state["serial"], "body": result.stdout.strip(),
                                           "created_at": now, "updated_at": now,
                                           "html_url": "https://github.com/fixture/receipt-desk/issues/" + str(number) + "#issuecomment-" + str(state["serial"]),
                                           "user": {"login": "fixture-owner"}}]
    (target / ".scenario/state.json").write_text(json.dumps(state, indent=2) + "\n")
    (target / ".scenario/api.jsonl").write_text("")
    print(json.dumps({"target": str(target), "variant": variant, "baseline": sha}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("target", type=Path)
    parser.add_argument("--variant", choices=("preparation", "prerequisite", "infrastructure"), default="preparation")
    args = parser.parse_args()
    create(args.target, args.variant)
