"""Contract tests for the User 3 checker entry point."""

import unittest

from checks import run_checks


class ContractTests(unittest.TestCase):
    def test_unfinished_checker_cannot_claim_success(self) -> None:
        report = run_checks({}, "")
        self.assertEqual(set(report), {"ok", "degraded", "checks", "failures", "revisions"})
        self.assertFalse(report["ok"])
        self.assertTrue(report["degraded"])
        self.assertTrue(report["failures"])

