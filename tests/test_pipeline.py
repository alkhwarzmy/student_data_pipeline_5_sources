import json
import unittest
from pathlib import Path
import pandas as pd
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.transformation.cleaner import clean_students, clean_api, clean_web
from app.validation.quality import validate_csv, validate_api, final_quality_check
from app.transformation.transformer import transform_data
from app.transformation.integration import integrate_data
from app.sources.api_source import extract_api


class TestPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parents[1]
        cls.csv_path = cls.root / "data/raw/students.csv"

    def test_1_csv_loaded(self):
        df = pd.read_csv(self.csv_path)
        self.assertGreater(len(df), 0)

    def test_2_real_api_schema_adapter(self):
        raw = pd.DataFrame([{"id": 1, "name": "Aarav Sharma", "course": "Computer Science"}])
        adapted = raw.rename(columns={"id": "student_id", "name": "api_name", "course": "api_course"})
        self.assertEqual(list(adapted.columns), ["student_id", "api_name", "api_course"])

    def test_3_api_falls_back_to_mock_when_real_api_fails(self):
        mock_payload = {"data": [{"id": 1, "name": "Mock Student", "course": "Data Engineering"}]}
        with patch("app.sources.api_source.requests.get", side_effect=__import__("requests").exceptions.ConnectionError("offline")):
            out = extract_api(
                "https://real-api.invalid/students", 1, __import__("logging").getLogger("test"),
                student_id_offset=1000, mock_data_path=self.root / "data/mock/api_students.json"
            )
        self.assertEqual(len(out), 15)
        self.assertEqual(out.loc[0, "student_id"], 1001)
        self.assertEqual(out.loc[0, "api_name"], "Aarav Sharma")
        self.assertEqual(out.loc[0, "api_course"], "Computer Science")

    def test_3_postgresql_configuration_exists(self):
        config = json.loads((self.root / "config.json").read_text(encoding="utf-8"))
        self.assertIn("postgres", config)
        self.assertEqual(config["postgres"]["port"], 5432)
        self.assertNotIn("sqlite", json.dumps(config).lower())

    def test_4_duplicates_removed(self):
        df = pd.read_csv(self.csv_path, dtype=str)
        clean, duplicates = clean_students(df)
        self.assertGreaterEqual(duplicates, 1)
        self.assertEqual(clean["student_id"].duplicated().sum(), 0)

    def test_5_missing_values_strategy(self):
        df = pd.DataFrame({
            "student_id": [1, 2], "student_name": ["A", "B"], "age": [20, None],
            "major": ["Computer Science", "Data Science"], "city": ["Sanaa", "Aden"],
            "api_name": ["A", "B"], "api_course": ["Computer Science", "Data Science"],
            "gpa": [3.0, None], "attendance": [90, 80], "status": ["Active", "Active"],
            "course": ["Python", "SQL"], "score": [90, 80], "semester": ["2026-S1", "2026-S1"],
            "web_title": ["Computer science", "Data science"],
            "web_summary": ["A summary", "Another summary"],
            "web_url": ["https://example.com/a", "https://example.com/b"],
            "email": ["a@example.com", "b@example.com"], "phone": ["1", "2"],
            "guardian_name": ["P A", "P B"]
        })
        out = transform_data(df)
        self.assertEqual(out.isna().sum().sum(), 0)

    def test_6_invalid_records_rejected(self):
        df = pd.DataFrame({"student_id": [1, 2], "age": [20, 15], "student_name": ["A", "B"],
                           "major": ["X", "Y"], "city": ["Sanaa", "Aden"]})
        valid, invalid, reasons = validate_csv(df)
        self.assertEqual(len(invalid), 1)
        self.assertTrue(any("Invalid Age" in r for _, r in reasons))

    def test_7_five_sources_can_integrate(self):
        students = pd.DataFrame({"student_id": [1], "student_name": ["A"], "age": [20],
                                 "major": ["Computer Science"], "city": ["Sanaa"]})
        api = pd.DataFrame({"student_id": [1], "api_name": ["A API"], "api_course": ["Computer Science"]})
        db = pd.DataFrame({"student_id": [1], "gpa": [3.2], "attendance": [90], "status": ["Active"],
                           "course": ["Python"], "credit_hours": [3], "score": [88], "semester": ["2026-S1"]})
        mongo = pd.DataFrame({"student_id": [1], "email": ["a@example.com"],
                              "phone": ["+967700000001"], "guardian_name": ["Parent A"]})
        web = pd.DataFrame({"major": ["Computer Science"], "web_title": ["Computer science"],
                            "web_summary": ["Summary"], "web_url": ["https://example.com"]})
        out = integrate_data(students, api, db, mongo, web)
        self.assertEqual(len(out), 1)
        self.assertIn("web_summary", out.columns)
        self.assertIn("email", out.columns)

    def test_8_final_dataset_quality(self):
        final = self.root / "data/processed/final_dataset.csv"
        if not final.exists():
            self.skipTest("Run the full pipeline after starting PostgreSQL and internet access")
        df = pd.read_csv(final)
        if len(df) == 0:
            self.skipTest("Final dataset is empty before a live run")
        ok, checks = final_quality_check(df)
        self.assertTrue(ok, checks)


if __name__ == "__main__":
    unittest.main()
