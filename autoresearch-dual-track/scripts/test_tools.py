#!/usr/bin/env python3

import argparse
import importlib.util
import pathlib
import unittest


HERE = pathlib.Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


capacity = load("plan_capacity")
preflight = load("preflight")
lineage = load("verify_lineage")


class ToolsTest(unittest.TestCase):
    def test_capacity_includes_reacquire_risk(self):
        args = argparse.Namespace(hourly_price=10, daily_price=180, pilot_hours=2, formal_hours=20, api_cost=150, storage_cost=0, reacquire_probability=0.5, reacquire_impact=200)
        result = capacity.calculate(args)
        self.assertEqual(result["expected_cost"]["hourly"], 470)
        self.assertEqual(result["arithmetic_recommendation"], "daily")

    def test_preflight_rejects_placeholder_contract(self):
        data = {"agent_tracks": ["codex", "codex"]}
        self.assertGreater(len(preflight.validate(data)), 5)

    def test_preflight_accepts_complete_contract(self):
        data = {
            "task_id": "task-1",
            "requires_gpu": True,
            "metric": {"name": "loss", "direction": "minimize"},
            "acceptance": {"improvement_threshold": "sourced rule", "randomness_protocol": "seeds 1,2,3"},
            "agent_tracks": ["codex", "seed"],
            "infrastructure": {
                "development_runtime": "compose",
                "target_harness": "harbor",
                "target_backend": "verified-provider",
                "backend_gpu_support_evidence": "versioned official source",
                "persistent_snapshot": "object-store/run-1",
            },
            "cost": {"stop_loss": 1000},
        }
        self.assertEqual(preflight.validate(data), [])

    def test_lineage_rejects_spliced_trial(self):
        h = "a" * 64
        data = {"runs": [{"run_id": "r1", "role": "baseline", "training_seed": 42, "replicate_id": "p1", "source_sha256": h, "config_sha256": h, "receipt_run_id": "r2", "artifact_run_id": "r1"}]}
        self.assertTrue(any("receipt_run_id" in item for item in lineage.validate(data)))

    def test_lineage_accepts_consistent_trial(self):
        h = "b" * 64
        data = {"runs": [{"run_id": "r1", "role": "reference", "training_seed": 17, "replicate_id": "p1", "source_sha256": h, "config_sha256": h, "receipt_run_id": "r1", "artifact_run_id": "r1"}]}
        self.assertEqual(lineage.validate(data), [])


if __name__ == "__main__":
    unittest.main()
