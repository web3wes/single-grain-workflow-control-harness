import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from workflow_control_harness import build_report, inspect_event, missing_controls, priority_score  # noqa: E402


class WorkflowControlHarnessTests(unittest.TestCase):
    def test_high_risk_action_requires_human_approval(self):
        request = {
            "id": "REQ-X",
            "name": "High impact action",
            "owner": "ops",
            "frequency_per_month": 10,
            "minutes_per_run": 10,
            "error_cost": 5,
            "feasibility": 4,
            "risk": 5,
            "maintenance_burden": 2,
            "validation_rule": "check",
            "retry_limit": 1,
            "alert_route": "alerts",
            "evidence_sink": "log",
            "human_approval_required": False,
        }
        self.assertIn("human_approval_required_for_high_risk_action", missing_controls(request))

    def test_score_rewards_value_and_feasibility(self):
        low = {
            "frequency_per_month": 5,
            "minutes_per_run": 2,
            "error_cost": 1,
            "feasibility": 2,
            "risk": 3,
            "maintenance_burden": 3,
        }
        high = {
            "frequency_per_month": 100,
            "minutes_per_run": 15,
            "error_cost": 4,
            "feasibility": 5,
            "risk": 2,
            "maintenance_burden": 2,
        }
        self.assertGreater(priority_score(high), priority_score(low))

    def test_missing_evidence_routes_run_to_exception_queue(self):
        request = {"id": "REQ-X", "human_approval_required": False}
        event = {
            "request_id": "REQ-X",
            "status": "success",
            "validated": True,
            "evidence_written": False,
            "approval_recorded": False,
        }
        self.assertIn("evidence_not_written", inspect_event(event, {"REQ-X": request}))

    def test_report_separates_priority_from_readiness(self):
        request = {
            "id": "REQ-X",
            "name": "Valuable but unsafe",
            "owner": "ops",
            "frequency_per_month": 500,
            "minutes_per_run": 20,
            "error_cost": 5,
            "feasibility": 5,
            "risk": 5,
            "maintenance_burden": 1,
            "validation_rule": "",
            "retry_limit": 0,
            "alert_route": "",
            "evidence_sink": "",
            "human_approval_required": False,
        }
        report = build_report([request], [])
        self.assertGreater(report["portfolio"][0]["priority_score"], 0)
        self.assertFalse(report["portfolio"][0]["production_ready"])
        self.assertEqual(report["portfolio"][0]["decision"], "route_to_design_review")


if __name__ == "__main__":
    unittest.main()

