# JobFit — local resume match project

Upload a PDF, DOCX, or TXT resume, paste a job description, and see detected strengths, missing resume evidence, and which existing resume lines to highlight. It never invents qualifications or sends files to an AI service. The score only measures coverage of its recognized skill phrases; it is not an ATS score or hiring prediction.

## Windows setup

1. Install Python 3.11 or newer from python.org. Check **Add python.exe to PATH** during installation.
2. Extract this ZIP, open the `jobfit` folder, click the File Explorer address bar, type `cmd`, and press Enter.
3. Install packages: `py -m pip install -r requirements.txt`
4. Start: `py -m streamlit run app.py`
5. Open the local address shown in the terminal, usually `http://localhost:8501`.
6. To stop, focus the terminal and press Ctrl+C. To run it again, repeat step 4.

If `py` is unavailable, try `python -m pip install -r requirements.txt` and `python -m streamlit run app.py`.

## Notes

- PDF extraction works for selectable text. Scanned PDF images need OCR or manual text paste.
- The matching dictionary is in `analyzer.py`. Expand it for roles you care about.
- The app does not rewrite your original file. Downloaded suggested lines are copies of exact resume lines for you to place under their original jobs or projects.
- Review location, scheduling, degree, and other eligibility requirements yourself; the score covers detected skill phrases only.
