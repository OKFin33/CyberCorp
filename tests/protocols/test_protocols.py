#!/usr/bin/env python3
"""Behavioral tests for the repository's pure Issue protocol helpers."""
import importlib.util
import json
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "skills/cybercorp/assets/corp/.agents/corp"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


spec = load("spec_checkpoint", "spec-checkpoint.py")
work = load("work_state", "work-state.py")
SHA = "a" * 40
AT = "2026-09-05T13:30:00Z"


def comment(cid, minute, event, **fields):
    payload = {"event": event, "instance": fields.pop("instance", "a"), **fields}
    return {"id": cid, "created_at": f"2026-09-05T13:{minute:02d}:00Z",
            "body": "```agent-event\n" + json.dumps(payload) + "\n```"}


def claim(cid=1, minute=0, instance="a", until="2026-09-05T13:20:00Z"):
    return comment(cid, minute, "claim", instance=instance, workgroup="repo-system",
                   base_commit=SHA, branch="feat/test", scope=["docs/"], lease_until=until)


def recovery(**fields):
    return {"commit": SHA, "branch": "feat/test", "artifacts": [],
            "done": "partial implementation", "checks": ["unit: pass"],
            "remaining": "independent review", "next": "review fixed head",
            "waiting_on": ["review"], **fields}


class SpecTests(unittest.TestCase):
    def body(self, core="Outcome: one", prefix="", suffix=""):
        return f"{prefix}\n{spec.START}\n{core}\n{spec.END}\n{suffix}".encode()

    def test_only_normative_area_is_hashed(self):
        self.assertEqual(spec.digest_body(self.body()),
                         spec.digest_body(self.body(prefix="claimed", suffix="waiting")))

    def test_normative_change_invalidates_pin(self):
        self.assertNotEqual(spec.digest_body(self.body()), spec.digest_body(self.body("Outcome: two")))

    def test_normalization(self):
        self.assertEqual(spec.digest_body(self.body("Outcome: one  \r\n")),
                         spec.digest_body(self.body()))

    def test_reject_missing_empty_duplicate_reversed_inline(self):
        cases = [b"no markers", self.body("  "), self.body() + self.body(),
                 f"{spec.END}\nx\n{spec.START}".encode(),
                 f"x{spec.START}\nx\n{spec.END}".encode()]
        for body in cases:
            with self.subTest(body=body), self.assertRaises(ValueError):
                spec.digest_body(body)

    def test_unicode_is_preserved(self):
        self.assertNotEqual(spec.digest_body(self.body("A")), spec.digest_body(self.body("Ａ")))


class ExecutionTests(unittest.TestCase):
    def test_damaged_history_stays_invalid_after_correction_and_takeover(self):
        for damaged in ({}, recovery(next="")):
            rows = [claim(), comment(2, 1, "checkpoint", claim=1, recovery=recovery()),
                    comment(3, 2, "checkpoint", claim=1, recovery=damaged),
                    comment(4, 3, "checkpoint", claim=1, recovery=recovery()),
                    comment(5, 4, "release", claim=1, checkpoint=4, reason="corrected"),
                    claim(6, 21, "b", "2026-09-05T14:00:00Z")]
            with self.subTest(damaged=damaged), self.assertRaises(ValueError):
                work.replay(rows, AT)

    def test_separate_successor_history_retains_results_not_old_execution_rights(self):
        # This measures replay only. Artifact/quiescence/relationship verification is a method scenario,
        # not something these fixture fields or a valid new claim can certify.
        prior = recovery(artifacts=["https://github.com/example/project/issues/7#issuecomment-2"])
        rows = [claim(10, 21, "b", "2026-09-05T14:00:00Z"),
                comment(11, 22, "checkpoint", instance="b", claim=10, recovery=prior),
                comment(12, 23, "release", instance="a", claim=1, checkpoint=2, reason="old execution")]
        state = work.replay(rows, AT)
        self.assertEqual(state["current_claim"]["id"], 10)
        self.assertEqual(state["latest_checkpoint"]["recovery"], prior)
        self.assertEqual(state["rejected_events"], [{"id": 12, "reason": "stale-or-nonholder"}])

    def test_empty_history(self):
        self.assertIsNone(work.replay([], AT)["current_claim"])

    def test_inline_mentions_and_quoted_fences_are_not_events(self):
        discussion = {"id": 2, "created_at": "2026-09-05T13:01:00Z",
                      "body": "Use the ```agent-event fence from the protocol.\n> ```agent-event"}
        rows = [claim(), discussion, comment(3, 2, "checkpoint", claim=1, recovery=recovery())]
        self.assertEqual(work.replay(rows, AT)["latest_checkpoint"]["id"], 3)

    def test_inline_mention_does_not_invalidate_one_real_event(self):
        row = claim()
        row["body"] = "Using the ```agent-event form below.\n\n" + row["body"]
        self.assertEqual(work.replay([row], "2026-09-05T13:05:00Z")["current_claim"]["id"], 1)

    def test_invalid_renewal_can_be_corrected_by_append(self):
        rows = [claim(), comment(2, 1, "renew", claim=1, lease_until="2026-09-05T13:20:00Z"),
                comment(3, 2, "renew", claim=1, lease_until="2026-09-05T14:00:00Z")]
        result = work.replay(rows, AT)
        self.assertEqual(result["current_claim"]["lease_until"], "2026-09-05T14:00:00Z")
        self.assertEqual(result["rejected_events"], [{"id": 2, "reason": "renewal-not-extended"}])

    def test_first_valid_claim_wins_not_client_array_order(self):
        result = work.replay([claim(2, 1, "b"), claim()], "2026-09-05T13:05:00Z")
        self.assertEqual(result["current_claim"]["instance"], "a")
        self.assertEqual(result["rejected_events"], [{"id": 2, "reason": "already-held"}])

    def test_renew_then_contender(self):
        rows = [claim(), comment(2, 10, "renew", claim=1, lease_until="2026-09-05T14:00:00Z"),
                claim(3, 21, "b", "2026-09-05T14:00:00Z")]
        self.assertEqual(work.replay(rows, AT)["current_claim"]["id"], 1)

    def test_expiry_allows_takeover_and_rejects_old_instance(self):
        rows = [claim(), comment(2, 1, "checkpoint", claim=1, recovery=recovery()),
                claim(3, 21, "b", "2026-09-05T14:00:00Z"),
                comment(4, 22, "checkpoint", claim=1, recovery=recovery())]
        result = work.replay(rows, AT)
        self.assertEqual(result["current_claim"]["id"], 3)
        self.assertEqual(result["latest_checkpoint"]["id"], 2)
        self.assertEqual(result["rejected_events"][-1]["id"], 4)

    def test_renew_at_expiry_cannot_revive(self):
        rows = [claim(), comment(2, 20, "renew", claim=1, lease_until="2026-09-05T14:00:00Z")]
        result = work.replay(rows, AT)
        self.assertIsNone(result["current_claim"])
        self.assertEqual(result["rejected_events"][0]["reason"], "stale-or-nonholder")

    def test_wait_release_keeps_recovery(self):
        rows = [claim(), comment(2, 1, "checkpoint", claim=1, recovery=recovery()),
                comment(3, 2, "release", claim=1, checkpoint=2, reason="waiting for review")]
        result = work.replay(rows, AT)
        self.assertIsNone(result["current_claim"])
        self.assertEqual(result["latest_checkpoint"]["recovery"]["waiting_on"], ["review"])

    def test_release_cannot_use_another_claims_checkpoint(self):
        rows = [claim(), comment(2, 1, "checkpoint", claim=1, recovery=recovery()),
                claim(3, 21, "b", "2026-09-05T14:00:00Z"),
                comment(4, 22, "release", instance="b", claim=3, checkpoint=2, reason="done")]
        with self.assertRaises(ValueError):
            work.replay(rows, AT)

    def test_stale_claim_id_rejected_even_when_instance_reused(self):
        rows = [claim(), claim(2, 21, "a", "2026-09-05T14:00:00Z"),
                comment(3, 22, "renew", claim=1, lease_until="2026-09-05T15:00:00Z")]
        self.assertEqual(work.replay(rows, AT)["current_claim"]["lease_until"], "2026-09-05T14:00:00Z")

    def test_paginated_input(self):
        rows = [[claim()], [comment(2, 1, "checkpoint", claim=1, recovery=recovery())]]
        self.assertEqual(work.replay(rows, AT)["latest_checkpoint"]["id"], 2)

    def test_reject_duplicate_comment_and_edited_event(self):
        with self.assertRaises(ValueError):
            work.replay([claim(), claim()], AT)
        row = claim()
        row["updated_at"] = "2026-09-05T13:01:00Z"
        with self.assertRaises(ValueError):
            work.replay([row], AT)

    def test_reject_bad_observation_time(self):
        with self.assertRaises(ValueError):
            work.replay([claim()], "2026-09-05T12:00:00Z")
        with self.assertRaises(ValueError):
            work.replay([], "2026-09-05T13:00:00")

    def test_reject_malformed_event_and_duplicate_json_key(self):
        for payload in ('{"event":"claim","event":"renew"}', "{bad", '{"event":"new"}'):
            row = {"id": 1, "created_at": "2026-09-05T13:00:00Z",
                   "body": "```agent-event\n" + payload + "\n```"}
            with self.assertRaises(ValueError):
                work.replay([row], AT)

    def test_recovery_rejects_local_only_artifacts_and_missing_fields(self):
        for data in (recovery(artifacts=["/private/work"]), {}, recovery(commit="short")):
            with self.assertRaises(ValueError):
                work.validate_recovery(data)

    def test_late_release_does_not_release_successor(self):
        rows = [claim(), comment(2, 1, "checkpoint", claim=1, recovery=recovery()),
                claim(3, 21, "b", "2026-09-05T14:00:00Z"),
                comment(4, 22, "release", claim=1, checkpoint=2, reason="old completion")]
        self.assertEqual(work.replay(rows, AT)["current_claim"]["id"], 3)


if __name__ == "__main__":
    unittest.main()
