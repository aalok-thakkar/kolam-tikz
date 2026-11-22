#!/usr/bin/env python3
"""Regression tests for the independent kolam grammar auditor."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDITOR_PATH = ROOT / "tools" / "kolam-audit.py"
SPEC = importlib.util.spec_from_file_location("kolam_audit", AUDITOR_PATH)
if SPEC is None or SPEC.loader is None:  # pragma: no cover - import invariant
    raise RuntimeError("cannot load kolam-audit.py")
AUDITOR = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = AUDITOR
SPEC.loader.exec_module(AUDITOR)


class AuditTests(unittest.TestCase):
    def parse_text(self, source: str):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.tex"
            path.write_text(source, encoding="utf-8")
            return AUDITOR.parse(path)

    def test_advertised_example_certificates(self) -> None:
        expected = {
            "01-minimal-loop.tex": (4, 2),
            "02-hourglass.tex": (8, 1),
            "03-braided-ladder.tex": (10, 1),
            "04-diamond-weave.tex": (21, 3),
            "05-one-stroke-21.tex": (21, 1),
            "07-nine-row-diamond.tex": (41, 3),
        }
        for filename, (pulli, strokes) in expected.items():
            with self.subTest(filename=filename):
                dots, gates = AUDITOR.parse(ROOT / "examples" / filename)
                report = AUDITOR.audit(dots, gates)
                self.assertEqual(report["dots"], pulli)
                self.assertEqual(report["components"], strokes)

    def test_helper_declares_the_complete_21_pulli_field(self) -> None:
        dots, gates = self.parse_text(r"\KolamThreeFiveFiveFiveThree")
        self.assertEqual(len(dots), 21)
        self.assertEqual(gates, {})

    def test_malformed_generic_gate_is_rejected(self) -> None:
        with self.assertRaises(AUDITOR.AuditError):
            self.parse_text(
                r"\KolamPulli{0}{0}\KolamPulli{1}{0}"
                r"\KolamGate{0}{0}{1}{0}{twist}"
            )

    def test_auditor_matches_tex_literal_grammar(self) -> None:
        invalid_sources = (
            r"\KolamPulli{0}{0}\KolamPulli{1}{0}"
            r"\KolamGate{0}{0}{1}{0}{OPEN}",
            r"\KolamPulli{+1}{0}",
            r"\KolamPulli{00}{0}",
            r"\KolamPulli{-0}{0}",
        )
        for source in invalid_sources:
            with self.subTest(source=source):
                with self.assertRaises(AUDITOR.AuditError):
                    self.parse_text(source)

    def test_reversed_duplicate_gate_is_rejected(self) -> None:
        with self.assertRaises(AUDITOR.AuditError):
            self.parse_text(
                r"\KolamPulli{0}{0}\KolamPulli{1}{0}"
                r"\KolamOpenGate{0}{0}{1}{0}"
                r"\KolamClosedGate{1}{0}{0}{0}"
            )

    def test_diagonal_gate_is_rejected(self) -> None:
        with self.assertRaises(AUDITOR.AuditError):
            self.parse_text(
                r"\KolamPulli{0}{0}\KolamPulli{1}{1}"
                r"\KolamOpenGate{0}{0}{1}{1}"
            )


if __name__ == "__main__":
    unittest.main()
