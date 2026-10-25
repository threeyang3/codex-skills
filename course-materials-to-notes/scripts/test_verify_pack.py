"""Regression tests for course-pack integrity and lecture coverage."""
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
        self.write_checksum()
        (self.root / "README.md").write_text(
            "[Note](notes/Lecture-01_Test.md)\n[Source](<materials/source with spaces.txt>)\n",
            encoding="utf-8")

    def write_manifest(self, fieldnames=None):
        fields = fieldnames or list(self.rows[0])
        with (self.root / "source_manifest.tsv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", extrasaction="ignore")
            writer.writeheader()
            writer.writerows(self.rows)

    def write_checksum(self):
        digest = hashlib.sha256(self.material.read_bytes()).hexdigest()
        (self.root / "checksums.sha256").write_text(
            f"{digest}  materials/source with spaces.txt\n", encoding="utf-8")

    def test_valid_pack_and_shared_material(self):
        self.rows.append(dict(self.rows[0], lecture="Lecture-02"))
        (self.root / "notes" / "Lecture-02_Second.md").write_text("# Second\n", encoding="utf-8")
        self.rows.append(dict(self.rows[0], lecture="Lecture-03", status="unavailable", target_path=""))
        self.write_manifest()
        self.assertEqual(verify(self.root, 2), [])

    def test_tamper_is_detected(self):
        self.material.write_text("changed content", encoding="utf-8")
        self.assertTrue(any("checksum mismatch" in error for error in verify(self.root)))

    def test_missing_file_and_checksum_coverage(self):
        self.material.unlink()
        (self.root / "checksums.sha256").write_text("", encoding="utf-8")
        errors = verify(self.root)
        self.assertTrue(any("missing material" in error for error in errors))
        self.assertTrue(any("lacks checksum" in error for error in errors))

    def test_broken_links_and_heading(self):
        self.note.write_text("# Test\n[[Missing]]\n[[#Gone]]\n[Broken](missing.md)\n", encoding="utf-8")
        errors = verify(self.root)
        self.assertTrue(any("wiki target" in error for error in errors))
        self.assertTrue(any("wiki heading" in error for error in errors))
        self.assertTrue(any("relative link" in error for error in errors))

    def test_code_and_escaped_dollars_do_not_trigger_math_or_links(self):
        self.note.write_text(
            '# Test\n\\$5 and `$bad [[Missing]]`\n```python\n$bad [[Missing]]\n```\n'
            '$$\nx^2\n$$\n', encoding="utf-8")
        self.assertEqual(verify(self.root), [])

    def test_unbalanced_math(self):
        self.note.write_text("# Test\n$x\n$$\nx^2\n", encoding="utf-8")
        errors = verify(self.root)
        self.assertTrue(any("inline math" in error for error in errors))
        self.assertTrue(any("display math" in error for error in errors))

    def test_manifest_cannot_escape_pack(self):
        self.rows[0]["target_path"] = "../outside.txt"
        self.write_manifest()
        self.assertTrue(any("escapes course pack" in error for error in verify(self.root)))

    def test_note_count_is_configurable(self):
        self.assertEqual(verify(self.root), [])
        self.assertTrue(any("expected 2 notes" in error for error in verify(self.root, 2)))

    def test_missing_required_role_column(self):
        self.write_manifest(fieldnames=["lecture", "original_path", "source_url", "target_path", "status"])
        errors = verify(self.root)
        self.assertTrue(any("manifest missing required columns" in error and "role" in error for error in errors))

    def test_empty_status_is_rejected(self):
        self.rows[0]["status"] = "   "
        self.write_manifest()
        errors = verify(self.root)
        self.assertTrue(any("invalid or empty status" in error for error in errors))

    def test_invalid_status_is_rejected(self):
        self.rows[0]["status"] = "missing"
        self.write_manifest()
        errors = verify(self.root)
        self.assertTrue(any("invalid or empty status" in error for error in errors))

    def test_manifest_lecture_without_note_is_detected(self):
        self.rows.append(dict(self.rows[0], lecture="Lecture-02"))
        self.write_manifest()
        errors = verify(self.root)
        self.assertTrue(any("Lecture-02" in error and "no matching note" in error for error in errors))

    def test_note_without_manifest_lecture_is_detected(self):
        (self.root / "notes" / "Lecture-02_Extra.md").write_text("# Extra\n", encoding="utf-8")
        errors = verify(self.root)
        self.assertTrue(any("Lecture-02" in error and "no matching lecture" in error for error in errors))

    def test_empty_role_is_rejected(self):
        self.rows[0]["role"] = " "
        self.write_manifest()
        errors = verify(self.root)
        self.assertTrue(any("empty role" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
