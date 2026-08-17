import json
import unittest
from pathlib import Path

from backend.app.search import find_relevant_runbooks, runbook_tag_matches, tokenize


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class RunbookSearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (PROJECT_ROOT / "data" / "runbooks.json").open(encoding="utf-8") as file:
            cls.runbooks = json.load(file)

    def assert_runbook_ids(self, alert_text, extracted, expected_ids):
        matches = find_relevant_runbooks(
            alert_text,
            self.runbooks,
            extracted,
            limit=len(self.runbooks),
        )
        self.assertEqual(
            [match["runbook"]["id"] for match in matches],
            expected_ids,
        )

    def test_cart_oom_returns_only_oom_runbook(self):
        self.assert_runbook_ids(
            "Service: cart-service Severity: P2 Kubernetes pod OOM restart",
            {"service": "cart-service", "severity": "P2"},
            ["RB-003"],
        )

    def test_slow_database_returns_only_database_runbook(self):
        self.assert_runbook_ids(
            "Service: orders-api Severity: P2 Database slow query latency",
            {"service": "orders-api", "severity": "P2"},
            ["RB-004"],
        )

    def test_dns_failure_returns_only_dns_runbook(self):
        self.assert_runbook_ids(
            "Service: user-service Severity: P2 DNS service discovery network failure",
            {"service": "user-service", "severity": "P2"},
            ["RB-009"],
        )

    def test_upload_iam_does_not_return_unrelated_runbooks(self):
        self.assert_runbook_ids(
            "Service: upload-service Severity: P2 Upload denied by object storage IAM policy",
            {"service": "upload-service", "severity": "P2"},
            [],
        )

    def test_severity_alone_is_not_enough(self):
        self.assert_runbook_ids(
            "Service: unknown-service Severity: P1 Unclassified problem",
            {"service": "unknown-service", "severity": "P1"},
            [],
        )

    def test_generic_tag_is_ignored(self):
        self.assertFalse(runbook_tag_matches("api", tokenize("orders-api is unavailable")))

    def test_tag_matching_uses_complete_tokens(self):
        self.assertFalse(runbook_tag_matches("dns", tokenize("adnservice is unavailable")))
        self.assertTrue(runbook_tag_matches("dns", tokenize("dns is unavailable")))


if __name__ == "__main__":
    unittest.main()
