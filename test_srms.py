# test_srms.py

import csv
import json
import unittest
import tempfile
from pathlib import Path
from dataclasses import asdict

from srms import SRMS, Student


class TestSRMS(unittest.TestCase):
    def setUp(self):
        # Temporary directory so tests don't affect your real data
        self.tmpdir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmpdir.name)
        self.data_file = self.tmp_path / "students.json"
        self.srms = SRMS(data_file=self.data_file)

    def tearDown(self):
        self.tmpdir.cleanup()

    # ----------------- Helpers -----------------
    def seed(self):
        self.srms.add_student(Student(1, "Alice Johnson", "10-A", 88.5))
        self.srms.add_student(Student(2, "Bob Singh", "10-A", 76.0))
        self.srms.add_student(Student(3, "Chirag Mehta", "10-B", 91.2))

    def read_json_students(self, path: Path):
        if not path.exists():
            return []
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    # ----------------- Core Operations -----------------
    def test_add_and_get_student(self):
        added = self.srms.add_student(Student(10, "Dev Patel", "9-A", 82.0))
        self.assertTrue(added)
        s = self.srms.get_student_by_roll(10)
        self.assertIsNotNone(s)
        self.assertEqual(s.name, "Dev Patel")
        self.assertEqual(s.class_name, "9-A")
        self.assertAlmostEqual(s.marks, 82.0)

    def test_add_duplicate_roll(self):
        self.srms.add_student(Student(1, "A", "X", 10))
        added2 = self.srms.add_student(Student(1, "B", "Y", 20))
        self.assertFalse(added2)  # duplicate roll_no should be blocked

    def test_update_student(self):
        self.srms.add_student(Student(5, "Name", "Class", 50))
        ok = self.srms.update_student(5, name="New Name", class_name="11-C", marks=97.5)
        self.assertTrue(ok)
        s = self.srms.get_student_by_roll(5)
        self.assertEqual(s.name, "New Name")
        self.assertEqual(s.class_name, "11-C")
        self.assertAlmostEqual(s.marks, 97.5)

    def test_update_nonexistent(self):
        ok = self.srms.update_student(999, name="Nobody")
        self.assertFalse(ok)

    def test_delete_student(self):
        self.srms.add_student(Student(7, "To Delete", "9-B", 60))
        ok = self.srms.delete_student(7)
        self.assertTrue(ok)
        self.assertIsNone(self.srms.get_student_by_roll(7))

    def test_delete_nonexistent(self):
        ok = self.srms.delete_student(404)
        self.assertFalse(ok)

    def test_list_students_sorted(self):
        self.srms.add_student(Student(3, "Three", "X", 30))
        self.srms.add_student(Student(1, "One", "X", 10))
        self.srms.add_student(Student(2, "Two", "X", 20))
        rolls = [s.roll_no for s in self.srms.list_students()]
        self.assertEqual(rolls, [1, 2, 3])

    def test_search_by_name_case_insensitive_partial(self):
        self.seed()
        res = self.srms.search_by_name("ali")  # matches "Alice"
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].name, "Alice Johnson")
        res2 = self.srms.search_by_name("A")    # matches Alice + (possibly others)
        self.assertTrue(any(s.name == "Alice Johnson" for s in res2))

    # ----------------- Persistence (JSON) -----------------
    def test_persistence_json_load_save(self):
        self.srms.add_student(Student(11, "Persist", "12-A", 77.7))
        self.srms.add_student(Student(12, "Persist2", "12-A", 88.8))

        # Ensure JSON actually holds records
        raw = self.read_json_students(self.data_file)
        self.assertEqual(len(raw), 2)

        # New instance with the same file should load existing data
        srms2 = SRMS(data_file=self.data_file)
        s = srms2.get_student_by_roll(12)
        self.assertIsNotNone(s)
        self.assertEqual(s.name, "Persist2")

    # ----------------- CSV Export -----------------
    def test_export_csv(self):
        self.seed()
        csv_path = self.tmp_path / "export.csv"
        count, out_path = self.srms.export_csv(csv_path)
        self.assertEqual(out_path, csv_path)
        self.assertEqual(count, 3)
        self.assertTrue(csv_path.exists())

        with open(csv_path, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        self.assertEqual(reader.fieldnames, ["roll_no", "name", "class_name", "marks"])
        self.assertEqual(len(rows), 3)
        # Check one row
        row1 = rows[0]
        self.assertIn(row1["roll_no"], {"1", "2", "3"})

    # ----------------- CSV Import: duplicate policies -----------------
    def test_import_csv_skip_duplicates(self):
        # Existing student with roll 1
        self.srms.add_student(Student(1, "Existing", "X", 55.5))

        # Incoming CSV: one duplicate roll 1, one new roll 2
        csv_path = self.tmp_path / "in_skip.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["roll_no", "name", "class_name", "marks"])
            writer.writeheader()
            writer.writerow({"roll_no": 1, "name": "NewName", "class_name": "Y", "marks": 99})
            writer.writerow({"roll_no": 2, "name": "Brand New", "class_name": "Z", "marks": 77})

        summary = self.srms.import_csv(csv_path, duplicate_policy="skip", validate_marks=True)
        self.assertEqual(summary["imported"], 1)
        self.assertEqual(summary["skipped_duplicates"], 1)
        # Existing record unchanged
        s1 = self.srms.get_student_by_roll(1)
        self.assertEqual(s1.name, "Existing")
        self.assertIsNotNone(self.srms.get_student_by_roll(2))

    def test_import_csv_overwrite_duplicates(self):
        self.srms.add_student(Student(1, "Old Name", "X", 10))
        csv_path = self.tmp_path / "in_overwrite.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["roll_no", "name", "class_name", "marks"])
            writer.writeheader()
            writer.writerow({"roll_no": 1, "name": "New Name", "class_name": "Y", "marks": 95})

        summary = self.srms.import_csv(csv_path, duplicate_policy="overwrite", validate_marks=True)
        self.assertEqual(summary["overwritten"], 1)
        s = self.srms.get_student_by_roll(1)
        self.assertEqual(s.name, "New Name")
        self.assertEqual(s.class_name, "Y")
        self.assertAlmostEqual(s.marks, 95.0)

    def test_import_csv_reassign_duplicates(self):
        self.srms.add_student(Student(1, "Keep Me", "A", 60))
        csv_path = self.tmp_path / "in_reassign.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["roll_no", "name", "class_name", "marks"])
            writer.writeheader()
            writer.writerow({"roll_no": 1, "name": "Duplicate", "class_name": "B", "marks": 70})

        summary = self.srms.import_csv(csv_path, duplicate_policy="reassign", validate_marks=True)
        self.assertEqual(summary["reassigned"], 1)

        # Original remains, plus one new with a different roll_no
        orig = self.srms.get_student_by_roll(1)
        self.assertEqual(orig.name, "Keep Me")
        rolls = [s.roll_no for s in self.srms.list_students()]
        self.assertGreaterEqual(len(rolls), 2)
        self.assertIn(1, rolls)
        # New roll should be max + 1 logic; check that there exists a student not roll 1
        self.assertTrue(any(s.roll_no != 1 and s.name == "Duplicate" for s in self.srms.list_students()))

    # ----------------- CSV Import: validation -----------------
    def test_import_csv_validation_errors(self):
        csv_path = self.tmp_path / "in_invalid.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["roll_no", "name", "class_name", "marks"])
            writer.writeheader()
            # Invalid: non-integer roll
            writer.writerow({"roll_no": "abc", "name": "X", "class_name": "Y", "marks": "10"})
            # Invalid: non-numeric marks
            writer.writerow({"roll_no": "2", "name": "Y", "class_name": "Z", "marks": "ten"})
            # Invalid: marks out of range (with validation ON)
            writer.writerow({"roll_no": "3", "name": "Z", "class_name": "Z", "marks": "150"})
            # Invalid: empty name
            writer.writerow({"roll_no": "4", "name": "", "class_name": "Z", "marks": "50"})
            # Valid row
            writer.writerow({"roll_no": "5", "name": "Valid", "class_name": "10-A", "marks": "90"})

        summary = self.srms.import_csv(csv_path, duplicate_policy="skip", validate_marks=True)
        self.assertEqual(summary["read_rows"], 5)
        self.assertEqual(summary["invalid_rows"], 4)
        self.assertEqual(summary["imported"], 1)
        self.assertIsNotNone(self.srms.get_student_by_roll(5))

    def test_import_csv_no_marks_validation_allows_out_of_range(self):
        csv_path = self.tmp_path / "in_no_validate.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["roll_no", "name", "class_name", "marks"])
            writer.writeheader()
            writer.writerow({"roll_no": "1", "name": "OutOfRange", "class_name": "10-A", "marks": "150"})

        summary = self.srms.import_csv(csv_path, duplicate_policy="skip", validate_marks=False)
        self.assertEqual(summary["invalid_rows"], 0)
        s = self.srms.get_student_by_roll(1)
        self.assertIsNotNone(s)
        self.assertAlmostEqual(s.marks, 150.0)

    # ----------------- Round-trip -----------------
    def test_round_trip_export_then_import(self):
        self.seed()
        export_path = self.tmp_path / "roundtrip.csv"
        count, _ = self.srms.export_csv(export_path)
        self.assertEqual(count, 3)

        # Import into a fresh SRMS with a different file
        new_data_file = self.tmp_path / "fresh.json"
        srms2 = SRMS(data_file=new_data_file)
        summary = srms2.import_csv(export_path, duplicate_policy="skip", validate_marks=True)
        self.assertEqual(summary["imported"], 3)

        # Compare sets of roll numbers
        rolls1 = set(s.roll_no for s in self.srms.list_students())
        rolls2 = set(s.roll_no for s in srms2.list_students())
        self.assertEqual(rolls1, rolls2)

        # Compare some fields as sanity check
        s1a = sorted([asdict(s) for s in self.srms.list_students()], key=lambda d: d["roll_no"])
        s2a = sorted([asdict(s) for s in srms2.list_students()], key=lambda d: d["roll_no"])
        self.assertEqual(len(s1a), len(s2a))
        for a, b in zip(s1a, s2a):
            self.assertEqual(a["roll_no"], b["roll_no"])
            self.assertEqual(a["name"], b["name"])
            self.assertEqual(a["class_name"], b["class_name"])
            self.assertAlmostEqual(a["marks"], b["marks"], places=6)


if __name__ == "__main__":
    main()