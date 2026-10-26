"""Exercise manifest validation, integrity failures and lecture coverage."""
import csv
import hashlib
import tempfile
import unittest
from pathlib import Path

from verify_pack import verify


class CoursePackTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "materials").mkdir()
        (self.root / "notes").mkdir()
        self.material = self.root / "materials" / "source with spaces.txt"
        self.material.write_text("original source", encoding="utf-8")
        self.note = self.root / "notes" / "Lecture-01_Test.md"
        self.note.write_text("# Test\n## Definition\n$x^2$\n[[#Definition]]\n", encoding="utf-8")
        self.rows = [dict(lecture="Lecture-01", role="slides", original_path="source.txt",
                          source_url="local:source.txt", target_path="materials/source with spaces.txt",
                          status="downloaded")]
        self.write_manifest()
        self.checksum = self.root / "checksums.sha256"
        digest = hashlib.sha256(self.material.read_bytes()).hexdigest()
        self.checksum.write_text(f"{digest}  materials/source with spaces.txt\n", encoding="utf-8")
        (self.root / "README.md").write_text(
            "[Note](notes/Lecture-01_Test.md)\n[Source](<materials/source with spaces.txt>)\n",
            encoding="utf-8")

    def write_manifest(self):
        fields = list(self.rows[0])
        with (self.root / "source_manifest.tsv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t")
            writer.writeheader()
            writer.writerows(self.rows)

    def errors(self, expected_notes=None, expected_lectures=None):
        return verify(self.root, expected_notes, expected_lectures)

    def test_valid_pack_shared_material_and_unavailable_row(self):
        self.rows.append(dict(self.rows[0], lecture="Lecture-02"))
        self.rows.append(dict(self.rows[0], lecture="Lecture-03", status="unavailable", target_path=""))
        self.write_manifest()
        self.assertEqual(self.errors(1, {"Lecture-01"}), [])

    def test_missing_required_role_column(self):
        self.rows[0].pop("role")
        self.write_manifest()
        self.assertTrue(any("missing columns" in error and "role" in error for error in self.errors()))

    def test_missing_required_status_column(self):
        self.rows[0].pop("status")
        self.write_manifest()
        self.assertTrue(any("missing columns" in error and "status" in error for error in self.errors()))

    def test_blank_status_is_rejected(self):
        self.rows[0]["status"] = "   "
        self.write_manifest()
        self.assertTrue(any("empty status" in error for error in self.errors()))

    def test_invalid_status_is_rejected(self):
        self.rows[0]["status"] = "pending"
        self.write_manifest()
        self.assertTrue(any("invalid status" in error for error in self.errors()))

    def test_unavailable_row_must_not_claim_target_file(self):
        self.rows[0]["status"] = "unavailable"
        self.write_manifest()
        self.assertTrue(any("unavailable material must have an empty target_path" in error
                            for error in self.errors()))

    def test_tamper_is_detected(self):
        self.material.write_text("changed content", encoding="utf-8")
        self.assertTrue(any("checksum mismatch" in error for error in self.errors()))

    def test_missing_file_and_checksum_coverage(self):
        self.material.unlink()
        self.checksum.write_text("", encoding="utf-8")
        errors = self.errors()
        self.assertTrue(any("missing material" in error for error in errors))
        self.assertTrue(any("lacks checksum" in error for error in errors))

    def test_broken_links_and_heading(self):
        self.note.write_text("# Test\n[[Missing]]\n[[#Gone]]\n[Broken](missing.md)\n", encoding="utf-8")
        errors = self.errors()
        self.assertTrue(any("wiki target" in error for error in errors))
        self.assertTrue(any("wiki heading" in error for error in errors))
        self.assertTrue(any("relative link" in error for error in errors))

    def test_code_and_escaped_dollars_do_not_trigger_math_or_links(self):
        self.note.write_text(
            '# Test\n\\$5 and `$bad [[Missing]]`\n```python\n$bad [[Missing]]\n```\n'
            '$$\nx^2\n$$\n', encoding="utf-8")
        self.assertEqual(self.errors(), [])

    def test_unbalanced_math(self):
        self.note.write_text("# Test\n$x\n$$\nx^2\n", encoding="utf-8")
        errors = self.errors()
        self.assertTrue(any("inline math" in error for error in errors))
        self.assertTrue(any("display math" in error for error in errors))

    def test_manifest_cannot_escape_pack(self):
        self.rows[0]["target_path"] = "../outside.txt"
        self.write_manifest()
        self.assertTrue(any("escapes course pack" in error for error in self.errors()))

    def test_note_count_is_configurable(self):
        self.assertEqual(self.errors(), [])
        self.assertTrue(any("expected 2 notes" in error for error in self.errors(2)))

    def test_expected_lecture_missing_from_manifest_and_notes(self):
        errors = self.errors(expected_lectures={"Lecture-01", "Lecture-02"})
        self.assertTrue(any("manifest missing expected lectures" in error for error in errors))
        self.assertTrue(any("missing lecture notes" in error for error in errors))

    def test_downloaded_lecture_without_note_is_reported(self):
        self.rows.append(dict(self.rows[0], lecture="Lecture-02"))
        self.write_manifest()
        errors = self.errors()
        self.assertTrue(any("downloaded lectures missing notes" in error for error in errors))

    def test_note_for_unexpected_lecture_is_reported(self):
        (self.root / "notes" / "Lecture-02_Unexpected.md").write_text("# Extra\n", encoding="utf-8")
        errors = self.errors(expected_lectures={"Lecture-01"})
        self.assertTrue(any("unexpected lecture notes" in error for error in errors))

    def test_nested_wiki_path_with_dots(self):
        nested = self.root / "notes" / "unit"
        nested.mkdir()
        (nested / "Lecture-02_V1.2.md").write_text("# Next\n", encoding="utf-8")
        self.note.write_text("# Test\n[[unit/Lecture-02_V1.2]]\n", encoding="utf-8")
        self.assertEqual(self.errors(), [])


if __name__ == "__main__":
    unittest.main()
