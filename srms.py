# srms.py
#Python Program: Basic Student Record Management System (SRMS)
import json
import csv
from dataclasses import dataclass, asdict
from typing import List, Optional, Tuple
from pathlib import Path

DATA_FILE = Path("students.json")

@dataclass
class Student:
    roll_no: int
    name: str
    class_name: str
    marks: float  # percentage or total

class SRMS:
    def __init__(self, data_file: Path = DATA_FILE):
        self.data_file = data_file
        self.students: List[Student] = []
        self._load()

    # ---------- Persistence (JSON) ----------
    def _load(self) -> None:
        if self.data_file.exists():
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                self.students = [Student(**item) for item in raw]
            except Exception as e:
                print(f"[!] Failed to load data: {e}. Starting fresh.")

    def _save(self) -> None:
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump([asdict(s) for s in self.students], f, indent=2)
        except Exception as e:
            print(f"[!] Failed to save data: {e}")

    # ---------- Core Operations ----------
    def add_student(self, student: Student) -> bool:
        if self.get_student_by_roll(student.roll_no):
            print(f"[!] Roll number {student.roll_no} already exists.")
            return False
        self.students.append(student)
        self._save()
        print("[+] Student added.")
        return True

    def get_student_by_roll(self, roll_no: int) -> Optional[Student]:
        return next((s for s in self.students if s.roll_no == roll_no), None)

    def search_by_name(self, name_query: str) -> List[Student]:
        nq = name_query.strip().lower()
        return [s for s in self.students if nq in s.name.lower()]

    def update_student(self, roll_no: int, **kwargs) -> bool:
        s = self.get_student_by_roll(roll_no)
        if not s:
            print(f"[!] Student with roll {roll_no} not found.")
            return False
        for k, v in kwargs.items():
            if hasattr(s, k) and v is not None:
                setattr(s, k, v)
        self._save()
        print("[*] Student updated.")
        return True

    def delete_student(self, roll_no: int) -> bool:
        s = self.get_student_by_roll(roll_no)
        if not s:
            print(f"[!] Student with roll {roll_no} not found.")
            return False
        self.students.remove(s)
        self._save()
        print("[-] Student deleted.")
        return True

    def list_students(self) -> List[Student]:
        return sorted(self.students, key=lambda s: s.roll_no)

    # ---------- CSV Export ----------
    def export_csv(self, csv_path: Path) -> Tuple[int, Path]:
        """Export students to CSV with headers: roll_no,name,class_name,marks"""
        count = 0
        try:
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=["roll_no", "name", "class_name", "marks"]
                )
                writer.writeheader()
                for s in self.list_students():
                    writer.writerow(asdict(s))
                    count += 1
            print(f"[✓] Exported {count} records to '{csv_path}'.")
            return count, csv_path
        except Exception as e:
            print(f"[!] Failed to export CSV: {e}")
            return 0, csv_path

    # ---------- CSV Import ----------
    def import_csv(
        self,
        csv_path: Path,
        duplicate_policy: str = "skip",  # "skip", "overwrite", "reassign"
        validate_marks: bool = True
    ) -> dict:
        """
        Import students from CSV.
        duplicate_policy:
            - 'skip'      : Keep existing, skip incoming duplicates.
            - 'overwrite' : Replace existing student with incoming row.
            - 'reassign'  : Assign a new unique roll_no for duplicates.
        validate_marks: If True, ensures marks are numeric and between 0-100.
        Returns a summary dict with counts and errors.
        """
        summary = {
            "read_rows": 0,
            "imported": 0,
            "skipped_duplicates": 0,
            "overwritten": 0,
            "reassigned": 0,
            "invalid_rows": 0,
            "errors": []
        }

        if not Path(csv_path).exists():
            msg = f"File '{csv_path}' not found."
            print(f"[!] {msg}")
            summary["errors"].append(msg)
            return summary

        def next_free_roll() -> int:
            if not self.students:
                return 1
            return max(s.roll_no for s in self.students) + 1

        try:
            with open(csv_path, "r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                required = {"roll_no", "name", "class_name", "marks"}
                if set(reader.fieldnames or []) != required and not required.issubset(set(reader.fieldnames or [])):
                    msg = f"CSV must contain headers: {', '.join(required)}"
                    print(f"[!] {msg}")
                    summary["errors"].append(msg)
                    return summary

                for i, row in enumerate(reader, start=2):  # start=2 accounts for header line
                    summary["read_rows"] += 1
                    try:
                        roll_no_raw = row.get("roll_no", "").strip()
                        name = (row.get("name") or "").strip()
                        class_name = (row.get("class_name") or "").strip()
                        marks_raw = row.get("marks", "").strip()

                        # Basic validation
                        if not roll_no_raw.isdigit():
                            raise ValueError("roll_no must be an integer")
                        roll_no = int(roll_no_raw)

                        try:
                            marks = float(marks_raw)
                        except Exception:
                            raise ValueError("marks must be numeric")

                        if validate_marks and not (0.0 <= marks <= 100.0):
                            raise ValueError("marks must be between 0 and 100")

                        if not name:
                            raise ValueError("name cannot be empty")
                        if not class_name:
                            raise ValueError("class_name cannot be empty")

                        existing = self.get_student_by_roll(roll_no)
                        if existing:
                            if duplicate_policy == "skip":
                                summary["skipped_duplicates"] += 1
                                continue
                            elif duplicate_policy == "overwrite":
                                existing.name = name
                                existing.class_name = class_name
                                existing.marks = marks
                                summary["overwritten"] += 1
                            elif duplicate_policy == "reassign":
                                new_roll = next_free_roll()
                                self.students.append(Student(new_roll, name, class_name, marks))
                                summary["reassigned"] += 1
                            else:
                                raise ValueError(f"Unknown duplicate_policy '{duplicate_policy}'")
                        else:
                            self.students.append(Student(roll_no, name, class_name, marks))
                            summary["imported"] += 1
                    except Exception as e_row:
                        summary["invalid_rows"] += 1
                        err = f"Line {i}: {e_row}"
                        summary["errors"].append(err)

            # Save after processing all rows
            self._save()
            print(
                f"[✓] Import summary: imported={summary['imported']}, "
                f"overwritten={summary['overwritten']}, "
                f"skipped={summary['skipped_duplicates']}, "
                f"reassigned={summary['reassigned']}, "
                f"invalid={summary['invalid_rows']}"
            )
            return summary

        except Exception as e:
            msg = f"Failed to import CSV: {e}"
            print(f"[!] {msg}")
            summary["errors"].append(msg)
            return summary

# ---------- UI Helpers ----------
def print_table(students: List[Student]) -> None:
    if not students:
        print("(no records)")
        return
    print(f"{'Roll':<6} {'Name':<20} {'Class':<10} {'Marks':>6}")
    print("-" * 46)
    for s in students:
        print(f"{s.roll_no:<6} {s.name:<20} {s.class_name:<10} {s.marks:>6.2f}")

def main():
    srms = SRMS()

    MENU = """
    === Student Record Management System (JSON + CSV) ===
    1. Add Student
    2. View All Students
    3. Search by Name
    4. Update Student
    5. Delete Student
    6. Export to CSV
    7. Import from CSV
    0. Exit
    """
    while True:
        print(MENU)
        choice = input("Enter choice: ").strip()
        if choice == "1":
            try:
                roll = int(input("Roll No: "))
                name = input("Name: ").strip()
                cls = input("Class: ").strip()
                marks = float(input("Marks: "))
                srms.add_student(Student(roll, name, cls, marks))
            except ValueError:
                print("[!] Invalid input. Try again.")
        elif choice == "2":
            print_table(srms.list_students())
        elif choice == "3":
            q = input("Search name contains: ").strip()
            print_table(srms.search_by_name(q))
        elif choice == "4":
            try:
                roll = int(input("Roll No to update: "))
                name = input("New Name (leave blank to skip): ").strip()
                cls = input("New Class (leave blank): ").strip()
                marks_str = input("New Marks (leave blank): ").strip()
                marks = float(marks_str) if marks_str else None
                srms.update_student(
                    roll,
                    name=name or None,
                    class_name=cls or None,
                    marks=marks
                )
            except ValueError:
                print("[!] Invalid input.")
        elif choice == "5":
            try:
                roll = int(input("Roll No to delete: "))
                srms.delete_student(roll)
            except ValueError:
                print("[!] Invalid roll number.")
        elif choice == "6":
            path = Path(input("CSV export path (e.g., students.csv): ").strip() or "students.csv")
            srms.export_csv(path)
        elif choice == "7":
            path = Path(input("CSV import path (e.g., students.csv): ").strip() or "students.csv")
            policy = input("Duplicate policy [skip|overwrite|reassign] (default skip): ").strip().lower() or "skip"
            validate = input("Validate marks 0-100? [y/N]: ").strip().lower() == "y"
            srms.import_csv(path, duplicate_policy=policy, validate_marks=validate)
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("[!] Invalid choice. Try again.")

if __name__ == "__main__":
    main()
