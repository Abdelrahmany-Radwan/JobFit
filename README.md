# JobFit — Resume Match Explainer

JobFit is a local-first resume-to-job comparison tool. It helps candidates understand which job skills are already supported by their resume, which requirements do not have visible evidence yet, and which existing resume lines are most relevant to move higher before applying.

## Why I built it

Many resume tools jump straight to rewriting. That can create a different problem: candidates may end up with bullets that sound stronger than what they actually did.

I built JobFit around a different question:

**What does the resume already prove, and where is the evidence missing?**

The project is intentionally transparent. It shows the exact job line and resume line used for each match, and it never invents qualifications.

## What it does

1. Accepts a PDF, DOCX, TXT, or pasted resume.
2. Accepts a pasted job description.
3. Detects recognized technical and professional skills in the posting.
4. Checks whether the resume contains supporting evidence for each skill.
5. Calculates a documented skill coverage score.
6. Ranks the candidate's existing resume lines that are most relevant to the job.
7. Surfaces requirement lines that still need manual review.

## Scoring

- Required skill: weight 2
- Preferred skill: weight 1
- Coverage = weighted skills with resume evidence / total weighted detected skills

This score is not an ATS score, hiring probability, or recruiter prediction. It only measures coverage of the skills currently recognized by the matcher.

## Design decisions

- Local-first: resume files are processed locally while the app runs.
- Explainable: every match points back to evidence in both documents.
- No hallucinated qualifications: the system does not create credentials, employers, projects, or skills.
- Separation of concerns: Streamlit UI/file handling lives in app.py; matching logic lives in analyzer.py.
- Extensible matcher: the skill dictionary can be expanded for specific industries.

## Tech stack

Python, Streamlit, pypdf, python-docx, regular expressions, and lightweight text ranking.

## Run locally

python -m pip install -r requirements.txt

python -m streamlit run app.py

Then open the local Streamlit URL, usually http://localhost:8501.

## Interview demo flow

1. Open Why I built it and explain the problem.
2. Switch to Live demo.
3. Paste a resume and one real job description.
4. Show the coverage score.
5. Open one Strongest match to show evidence from both sides.
6. Show one Gap and explain that the system refuses to pretend the skill exists.
7. Show Existing resume evidence to move higher.
8. Close with what you would build next.

## What I would improve next

- Replace the hand-built phrase matcher with embeddings or a trained NLP classifier.
- Add section-aware resume parsing.
- Detect equivalent skills and semantic matches.
- Benchmark precision and recall on a labeled dataset.
- Add tests for file extraction, scoring, and skill detection.
- Add optional deployment while keeping privacy controls clear.

## Important limitations

- Scanned image PDFs may require OCR or manual text paste.
- The current skill matcher is dictionary-based.
- The tool does not evaluate education, work authorization, location, scheduling, or every job requirement automatically.
