"""Unit tests for hl7-message-diff."""

import io
import json
import os
import tempfile
import unittest

from hl7_message_diff.differ import diff_messages
from hl7_message_diff.parser import parse_message
from hl7_message_diff.labels import label_for
from hl7_message_diff.cli import main as cli_main


MSG_A = (
    "MSH|^~\\&|HIS|HOSPITAL|LIS|LAB|202601010900||ADT^A01|MSG001|P|2.6\r"
    "EVN|A01|202601010900\r"
    "PID|1||12345^^^MR||DOE^JOHN||19800101|M|||123 MAIN ST^^BOSTON^MA^02101\r"
    "PV1|1|I|2000^2012^01||||004777^ATTEND^AARON^A.\r"
)

MSG_B_DOB_CHANGED = (
    "MSH|^~\\&|HIS|HOSPITAL|LIS|LAB|202601010900||ADT^A01|MSG001|P|2.6\r"
    "EVN|A01|202601010900\r"
    "PID|1||12345^^^MR||DOE^JOHN||19800102|M|||123 MAIN ST^^BOSTON^MA^02101\r"
    "PV1|1|I|2000^2012^01||||004777^ATTEND^AARON^A.\r"
)

MSG_C_EXTRA_SEGMENT = MSG_A + "AL1|1|DA|PENICILLIN|SV|RASH\r"

MSG_D_SEGMENT_REORDER = (
    "MSH|^~\\&|HIS|HOSPITAL|LIS|LAB|202601010900||ADT^A01|MSG001|P|2.6\r"
    "PID|1||12345^^^MR||DOE^JOHN||19800101|M|||123 MAIN ST^^BOSTON^MA^02101\r"
    "EVN|A01|202601010900\r"
    "PV1|1|I|2000^2012^01||||004777^ATTEND^AARON^A.\r"
)


class TestParser(unittest.TestCase):
    def test_parses_msh_with_field_separator(self):
        segs = parse_message(MSG_A)
        self.assertEqual(segs[0].name, "MSH")
        # MSH-1 should be the field separator itself.
        self.assertEqual(segs[0].fields[0], "|")
        # MSH-9 is Message Type.
        self.assertEqual(segs[0].fields[8], "ADT^A01")

    def test_parses_pid(self):
        segs = parse_message(MSG_A)
        pid = next(s for s in segs if s.name == "PID")
        # PID-7 (DOB) is the 7th field, index 6.
        self.assertEqual(pid.fields[6], "19800101")

    def test_handles_lf_line_endings(self):
        msg = MSG_A.replace("\r", "\n")
        segs = parse_message(msg)
        self.assertEqual(len(segs), 4)


class TestLabels(unittest.TestCase):
    def test_known_label(self):
        self.assertEqual(label_for("PID", 7), "PID-7 Date/Time of Birth")

    def test_unknown_segment_fallback(self):
        self.assertEqual(label_for("ZZZ", 3), "ZZZ-3")


class TestDiffer(unittest.TestCase):
    def test_identical_messages_no_diff(self):
        diffs = diff_messages(MSG_A, MSG_A)
        self.assertEqual(diffs, [])

    def test_single_field_change_detected(self):
        diffs = diff_messages(MSG_A, MSG_B_DOB_CHANGED)
        self.assertEqual(len(diffs), 1)
        d = diffs[0]
        self.assertEqual(d.segment, "PID")
        self.assertEqual(d.field, 7)
        self.assertIn("Date/Time of Birth", d.field_name)
        self.assertEqual(d.before, "19800101")
        self.assertEqual(d.after, "19800102")
        self.assertEqual(d.kind, "changed")

    def test_added_segment_reported(self):
        diffs = diff_messages(MSG_A, MSG_C_EXTRA_SEGMENT)
        self.assertTrue(any(d.kind == "segment-only-in-b" for d in diffs))

    def test_removed_segment_reported(self):
        diffs = diff_messages(MSG_C_EXTRA_SEGMENT, MSG_A)
        self.assertTrue(any(d.kind == "segment-only-in-a" for d in diffs))

    def test_segment_reorder_detected_as_mismatch(self):
        diffs = diff_messages(MSG_A, MSG_D_SEGMENT_REORDER)
        # Reordering EVN and PID at positions 1 and 2 should produce
        # segment-type-mismatch entries.
        kinds = {d.kind for d in diffs}
        self.assertIn("segment-mismatch", kinds)


class TestCLI(unittest.TestCase):
    def _write_tmp(self, content: str) -> str:
        fd, path = tempfile.mkstemp(suffix=".hl7")
        os.close(fd)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path

    def test_cli_identical_exits_zero(self):
        a = self._write_tmp(MSG_A)
        b = self._write_tmp(MSG_A)
        try:
            out = io.StringIO()
            rc = cli_main([a, b, "--no-color"], stdout=out)
            self.assertEqual(rc, 0)
            self.assertIn("No differences", out.getvalue())
        finally:
            os.unlink(a)
            os.unlink(b)

    def test_cli_changed_exits_one_and_names_field(self):
        a = self._write_tmp(MSG_A)
        b = self._write_tmp(MSG_B_DOB_CHANGED)
        try:
            out = io.StringIO()
            rc = cli_main([a, b, "--no-color"], stdout=out)
            self.assertEqual(rc, 1)
            text = out.getvalue()
            self.assertIn("Date/Time of Birth", text)
            self.assertIn("19800101", text)
            self.assertIn("19800102", text)
        finally:
            os.unlink(a)
            os.unlink(b)

    def test_cli_json_output_is_valid(self):
        a = self._write_tmp(MSG_A)
        b = self._write_tmp(MSG_B_DOB_CHANGED)
        try:
            out = io.StringIO()
            rc = cli_main([a, b, "--format", "json"], stdout=out)
            self.assertEqual(rc, 1)
            payload = json.loads(out.getvalue())
            self.assertEqual(len(payload["differences"]), 1)
            self.assertEqual(payload["differences"][0]["field"], 7)
        finally:
            os.unlink(a)
            os.unlink(b)


if __name__ == "__main__":
    unittest.main()
