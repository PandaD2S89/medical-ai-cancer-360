"""Run: python -m unittest discover -s tests -v (no dependencies)."""

import json
from pathlib import Path
import subprocess
import sys
import unittest

from medical_ai_360_demo import Coordinator, load_fictional_scenario
from medical_ai_360_demo.coordinator import validate_fictional_scenario
from medical_ai_360_demo.councils import COUNCILS


ROOT = Path(__file__).resolve().parent.parent


def sample() -> dict:
    return load_fictional_scenario(ROOT / "example_data" / "fictional_case.json")


class DemoTests(unittest.TestCase):
    def setUp(self):
        self.data = sample()
        self.result = Coordinator().run(self.data)

    def test_eight_distinct_councils(self):
        self.assertEqual(len(COUNCILS), 8)
        self.assertEqual(len({x.key for x in COUNCILS}), 8)

    def test_all_eight_receive_and_reply(self):
        routed = [e.recipient for e in self.result.events if e.action == "task_routed"]
        replied = [e.sender for e in self.result.events if e.action == "receipt_returned"]
        self.assertEqual(set(routed), {x.key for x in COUNCILS})
        self.assertEqual(set(replied), set(routed))
        self.assertEqual(len(self.result.council_receipts), 8)

    def test_evidence_retains_source_and_ids(self):
        self.assertEqual([e["id"] for e in self.result.evidence], ["E1", "E2", "E3"])
        self.assertEqual(self.result.evidence[1]["source"], "invented_caregiver_observation")

    def test_synthetic_alert_occurs_before_review_and_routing(self):
        actions = [e.action for e in self.result.events]
        self.assertIn("simulated_safety_alert", actions)
        alert_step = actions.index("simulated_safety_alert")
        self.assertLess(alert_step, actions.index("sealed_review_submitted"))
        self.assertLess(alert_step, actions.index("task_routed"))
        self.assertLess(actions.index("safety_example_completed"), actions.index("task_routed"))

    def test_alert_is_simulation_only(self):
        self.assertEqual(len(self.result.alerts), 1)
        self.assertEqual(self.result.alerts[0].evidence_id, "E2")
        self.assertEqual(self.result.alerts[0].status, "SIMULATED_ONLY")

    def test_no_marker_means_no_demo_alert(self):
        self.data["evidence"] = [{"id": "N1", "source": "invented", "statement": "A made-up person reads a book."}]
        self.assertFalse(Coordinator().run(self.data).alerts)

    def test_two_separate_reviews_same_evidence(self):
        reviews = self.result.reviews
        self.assertEqual([r.reviewer for r in reviews], ["oncology_A", "oncology_B"])
        self.assertEqual(reviews[0].evidence_ids, reviews[1].evidence_ids)
        self.assertNotEqual(reviews[0].perspective, reviews[1].perspective)
        self.assertNotEqual(reviews[0].result, reviews[1].result)

    def test_reviews_not_revealed_before_two_submissions(self):
        events = self.result.events
        submitted = [e.step for e in events if e.action == "sealed_review_submitted"]
        revealed = [e.step for e in events if e.action == "reviews_unsealed_for_comparison"]
        self.assertEqual(len(submitted), 2)
        self.assertEqual(len(revealed), 1)
        self.assertLess(max(submitted), revealed[0])

    def test_sharing_is_selective_and_traceable(self):
        shared = [e for e in self.result.events if e.action == "example_evidence_shared"]
        self.assertEqual({(e.sender, e.recipient) for e in shared},
                         {("nutrition", "rehabilitation"), ("sleep", "organ_health")})
        for event in shared:
            self.assertTrue(event.evidence_ids)
            self.assertTrue(set(event.evidence_ids).issubset({"E1", "E2", "E3"}))

    def test_no_sharing_on_unmatched_notes(self):
        self.data["evidence"] = [{"id": "N1", "source": "invented", "statement": "A made-up person reads a book."}]
        result = Coordinator().run(self.data)
        self.assertFalse([e for e in result.events if e.action == "example_evidence_shared"])

    def test_events_have_monotonic_sequence_numbers(self):
        self.assertEqual([e.step for e in self.result.events], list(range(1, len(self.result.events) + 1)))

    def test_serializable_json_includes_disclaimer(self):
        output = json.loads(self.result.as_json())
        self.assertEqual(output["scenario_id"], "DEMO-CASE-001")
        self.assertEqual(len(output["council_receipts"]), 8)
        self.assertIn("SIMULATION ONLY", output["disclaimer"])

    def test_reject_nonfictional_scenario(self):
        self.data["fictional"] = False
        with self.assertRaises(ValueError):
            Coordinator().run(self.data)

    def test_reject_missing_fictional_marker(self):
        self.data.pop("fictional")
        with self.assertRaises(ValueError):
            Coordinator().run(self.data)

    def test_reject_duplicate_evidence_id(self):
        self.data["evidence"][1]["id"] = "E1"
        with self.assertRaisesRegex(ValueError, "duplicate"):
            Coordinator().run(self.data)

    def test_reject_empty_or_oversized_evidence(self):
        self.data["evidence"] = []
        with self.assertRaises(ValueError):
            validate_fictional_scenario(self.data)
        self.data["evidence"] = [{"id": "X", "source": "fictional", "statement": "a" * 501}]
        with self.assertRaises(ValueError):
            validate_fictional_scenario(self.data)

    def test_cli_json_smoke(self):
        p = subprocess.run([sys.executable, "-m", "medical_ai_360_demo", "--json"],
                           cwd=ROOT, text=True, capture_output=True, check=True)
        doc = json.loads(p.stdout)
        self.assertEqual(doc["scenario_id"], "DEMO-CASE-001")
        self.assertEqual(len(doc["reviews"]), 2)

    def test_output_avoids_treatment_instructions(self):
        result_json = self.result.as_json().lower()
        for phrase in ("start taking ", "stop taking ", "increase your dose", "take this drug"):
            self.assertNotIn(phrase, result_json)


if __name__ == "__main__":
    unittest.main()
