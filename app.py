import io
import streamlit as st
from docx import Document
from pypdf import PdfReader
from analyzer import analyze

st.set_page_config(page_title="JobFit — Interview Demo", page_icon="🎯", layout="wide")

st.markdown("""
<style>
.block-container{max-width:1180px;padding-top:1.5rem;padding-bottom:3rem}
h1,h2,h3{letter-spacing:-.03em}
.hero{
    padding:2rem 2.2rem;border:1px solid #2f3640;border-radius:18px;
    background:linear-gradient(135deg,#111827 0%,#0f172a 60%,#111827 100%);
    margin-bottom:1.2rem;
}
.hero h1{margin:0 0 .4rem 0;font-size:3rem}
.hero p{font-size:1.08rem;color:#d1d5db;max-width:760px}
.badge{
    display:inline-block;padding:.35rem .65rem;border:1px solid #4b5563;
    border-radius:999px;margin:.2rem .35rem .2rem 0;color:#e5e7eb;font-size:.86rem
}
.card{
    padding:1rem 1.1rem;border:1px solid #e5e7eb;border-radius:14px;height:100%;
}
[data-testid="stMetricValue"]{font-size:2.4rem}
.stButton button{border-radius:10px;font-weight:600}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <div class="badge">Local-first</div>
  <div class="badge">Transparent scoring</div>
  <div class="badge">No invented qualifications</div>
  <h1>🎯 JobFit</h1>
  <p>
    A resume-to-job comparison tool built to help students understand
    <strong>what their resume actually proves</strong>, what the job still asks for,
    and which real experience should be moved higher before applying.
  </p>
</div>
""", unsafe_allow_html=True)

about, demo = st.tabs(["Why I built it", "Live demo"])

with about:
    st.subheader("The problem")
    st.write(
        "When students tailor resumes, it is easy to over-focus on keywords or let an AI tool "
        "rewrite bullets in a way that sounds stronger than the experience really was. "
        "I wanted a tool that gives useful feedback without creating fake qualifications."
    )

    a, b, c = st.columns(3)
    with a:
        st.markdown('<div class="card"><h3>1. Read the job</h3><p>Detect the skills and requirement lines the posting actually mentions.</p></div>', unsafe_allow_html=True)
    with b:
        st.markdown('<div class="card"><h3>2. Verify evidence</h3><p>Search the resume for supporting text instead of assuming the candidate has the skill.</p></div>', unsafe_allow_html=True)
    with c:
        st.markdown('<div class="card"><h3>3. Explain the gap</h3><p>Show matches, missing evidence, and the candidate\\'s existing lines that are most relevant.</p></div>', unsafe_allow_html=True)

    st.subheader("How it works")
    st.markdown(
        """
**Pipeline**

Resume PDF / DOCX / TXT → text extraction → skill detection → evidence matching → weighted coverage score → ranked resume evidence

- Required skills count **2×** and preferred skills count **1×** in the coverage score.
- The score is only a **recognized-skill coverage metric**. It is not an ATS score or hiring prediction.
- Existing resume wording is preserved when ranking evidence.
- The app runs locally and does not send resume files to an AI service.
        """
    )

    st.subheader("Engineering decisions I can explain in an interview")
    st.markdown(
        """
- **Separated UI from analysis logic:** app.py handles interaction and file extraction; analyzer.py handles matching.
- **Made the system explainable:** every detected skill points back to the exact job line and resume line.
- **Designed against hallucination:** the tool never creates credentials or claims the user did not provide.
- **Added practical guardrails:** input length checks, file-size limits, and clear warnings for scanned PDFs.
- **Made the matching layer extensible:** the skill dictionary can be expanded for specific industries or roles.
        """
    )

    st.info(
        "Next version: replace the hand-built phrase dictionary with embeddings or an NLP model, "
        "add better section-aware resume parsing, and benchmark precision/recall on a labeled dataset."
    )

with demo:
    def extract(upload):
        data = upload.getvalue()
        if len(data) > 8_000_000:
            raise ValueError("Use a resume smaller than 8 MB.")

        name = upload.name.lower()

        if name.endswith(".txt"):
            return data.decode("utf-8-sig", errors="replace")

        if name.endswith(".pdf"):
            reader = PdfReader(io.BytesIO(data))
            if len(reader.pages) > 20:
                raise ValueError("Use a resume of 20 pages or fewer.")
            return "\n".join(page.extract_text() or "" for page in reader.pages)

        if name.endswith(".docx"):
            doc = Document(io.BytesIO(data))
            parts = [p.text for p in doc.paragraphs]
            for table in doc.tables:
                for row in table.rows:
                    parts.append(" | ".join(cell.text for cell in row.cells))
            return "\n".join(parts)

        raise ValueError("Use a PDF, DOCX, or TXT resume.")

    left, right = st.columns(2, gap="large")

    with left:
        uploaded = st.file_uploader("Upload your resume", type=["pdf", "docx", "txt"])
        resume_paste = st.text_area(
            "Or paste your resume text",
            height=260,
            placeholder="Paste resume text here if you prefer not to upload a file.",
        )

    with right:
        job = st.text_area(
            "Paste the job description",
            height=360,
            placeholder="Paste the responsibilities and qualifications for one role.",
        )

    if st.button("Analyze match", type="primary", use_container_width=True):
        try:
            resume = resume_paste.strip() or (extract(uploaded).strip() if uploaded else "")

            if len(resume) < 50 or len(job.strip()) < 50:
                st.warning("Add at least 50 characters of resume text and job description.")
                st.stop()

            result = analyze(resume, job)
            st.session_state["analysis"] = (
                result,
                uploaded.name if uploaded else "Pasted resume",
            )
        except Exception as exc:
            st.error(f"Could not analyze this file: {exc}")

    if "analysis" in st.session_state:
        result, source = st.session_state["analysis"]

        st.divider()
        st.caption(f"Source: {source}")

        if result["score"] is None:
            st.info(
                "No skills from the current skill list were found in the job description. "
                "Try pasting the full qualifications section."
            )
        else:
            m1, m2, m3 = st.columns(3)
            m1.metric("Documented skill coverage", f"{result['score']}%")
            m2.metric("Skills with resume evidence", len(result["strengths"]))
            m3.metric("Skills not found in resume", len(result["gaps"]))
            st.caption(
                "Required skills are weighted twice as much as preferred skills. "
                "This is not an ATS score or hiring prediction."
            )

        st.subheader("Strongest matches")
        if result["strengths"]:
            for m in result["strengths"]:
                label = f"✓ {m.skill}" + (" · preferred" if m.preferred else "")
                with st.expander(label):
                    st.markdown("**Job says:**")
                    st.write(m.job_evidence)
                    st.markdown("**Resume evidence:**")
                    st.write(m.evidence)
        else:
            st.write("No recognized skills matched yet.")

        st.subheader("Gaps to check")
        st.caption(
            '"Not found" means the wording or evidence was not detected in the resume. '
            "The candidate may still have the experience."
        )
        for m in result["gaps"]:
            st.markdown(f"**{m.skill}**" + (" *(preferred)*" if m.preferred else ""))
            st.caption(m.job_evidence)

        if not result["gaps"]:
            st.write("All detected skills have supporting text in the resume.")

        st.subheader("Existing resume evidence to move higher")
        st.write(
            "These are exact lines from the resume that are already relevant to the job. "
            "The tool does not invent new experience."
        )

        if result["ranked"]:
            for _, _, sentence, hits in result["ranked"]:
                st.markdown("**" + ", ".join(hits) + "**")
                st.write("“" + sentence + "”")

            suggested = (
                "RELEVANT EXISTING RESUME LINES — review and place under their original roles\n\n"
                + "\n".join("• " + sentence for _, _, sentence, _ in result["ranked"])
            )

            st.download_button(
                "Download relevant existing lines (.txt)",
                suggested,
                file_name="jobfit-resume-lines.txt",
                mime="text/plain",
            )

        st.subheader("Questions to resolve before applying")
        for m in result["gaps"][:6]:
            st.write(
                f"• Do you have real {m.skill} experience you can describe with a specific example? "
                "If yes, add it accurately. If no, leave it off."
            )

        if result["requirements"]:
            with st.expander("Requirement lines to review manually"):
                for sentence in result["requirements"]:
                    st.write("• " + sentence)

        st.caption(
            "Files and job descriptions are processed locally while this app is running. "
            "Nothing is sent to an AI service."
        )
