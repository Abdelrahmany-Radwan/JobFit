import unittest
from analyzer import analyze

class AnalyzerTests(unittest.TestCase):
    def test_detects_matching_skill_evidence(self):
        resume = "Built Python scripts to automate data analysis and reporting."
        job = "Required: experience with Python and data analysis."
        result = analyze(resume, job)
        skills = {m.skill for m in result["strengths"]}
        self.assertIn("Python", skills)
        self.assertIn("Data analysis", skills)

    def test_reports_missing_skill(self):
        resume = "Created dashboards in Excel for a class project."
        job = "Required: experience with Python."
        result = analyze(resume, job)
        gaps = {m.skill for m in result["gaps"]}
        self.assertIn("Python", gaps)

    def test_score_is_not_none_when_skills_found(self):
        resume = "Used SQL to query customer records."
        job = "Required: SQL experience."
        result = analyze(resume, job)
        self.assertIsNotNone(result["score"])

if __name__ == "__main__":
    unittest.main()
