import io
import streamlit as st
from docx import Document
from pypdf import PdfReader
from analyzer import analyze

st.set_page_config(page_title='JobFit — Resume Match',page_icon='🎯',layout='wide')
st.markdown('''<style>
.block-container{max-width:1100px;padding-top:2rem} h1{letter-spacing:-.04em}
[data-testid="stMetricValue"]{font-size:2.5rem} .stButton button{border-radius:9px}
</style>''',unsafe_allow_html=True)
st.title('🎯 JobFit')
st.caption('See where your resume matches a job, what it does not show yet, and which true details to put first.')


def extract(upload):
    data=upload.getvalue()
    if len(data)>8_000_000: raise ValueError('Use a resume smaller than 8 MB.')
    name=upload.name.lower()
    if name.endswith('.txt'): return data.decode('utf-8-sig', errors='replace')
    if name.endswith('.pdf'):
        reader=PdfReader(io.BytesIO(data))
        if len(reader.pages)>20: raise ValueError('Use a resume of 20 pages or fewer.')
        return '\n'.join(page.extract_text() or '' for page in reader.pages)
    if name.endswith('.docx'):
        doc=Document(io.BytesIO(data))
        parts=[p.text for p in doc.paragraphs]
        for table in doc.tables:
            for row in table.rows:
                parts.append(' | '.join(cell.text for cell in row.cells))
        return '\n'.join(parts)
    raise ValueError('Use a PDF, DOCX, or TXT resume.')

left,right=st.columns(2,gap='large')
with left:
    uploaded=st.file_uploader('Upload your resume',type=['pdf','docx','txt'])
    resume_paste=st.text_area('Or paste your resume text',height=240,placeholder='Paste text here if your resume is scanned or you prefer not to upload.')
with right:
    job=st.text_area('Paste the job description',height=340,placeholder='Paste the responsibilities and qualifications for one job.')

if st.button('Analyze match',type='primary',use_container_width=True):
    try:
        resume=resume_paste.strip() or (extract(uploaded).strip() if uploaded else '')
        if len(resume)<50 or len(job.strip())<50:
            st.warning('Add at least 50 characters of resume text and job description.')
            st.stop()
        result=analyze(resume,job)
        st.session_state['analysis']=(result,uploaded.name if uploaded else 'Pasted resume')
    except Exception as exc:
        st.error(f'Could not analyze this file: {exc}')

if 'analysis' in st.session_state:
    result,source=st.session_state['analysis']
    st.divider()
    if result['score'] is None:
        st.info('No skills from the current skill list were found in the job description. Try pasting the full qualifications section. No match score is available for this posting.')
    else:
        a,b,c=st.columns(3)
        a.metric('Documented skill coverage',f"{result['score']}%")
        b.metric('Skills with resume evidence',len(result['strengths']))
        c.metric('Skills not found in resume',len(result['gaps']))
        st.caption('This percentage covers only detected skill phrases, weighting required items twice as much as preferred items. It is not an ATS score or a hiring prediction.')
    st.subheader('Your strongest matches')
    if result['strengths']:
        for m in result['strengths']:
            with st.expander(f'✓ {m.skill}' + (' · preferred' if m.preferred else '')):
                st.markdown('**Job says:**');st.write(m.job_evidence)
                st.markdown('**Your resume says:**');st.write(m.evidence)
    else: st.write('No skill phrases matched yet. Check that text extracted correctly or paste it manually.')
    st.subheader('Gaps to check')
    st.caption('“Not found” means the wording or evidence was not detected in the resume. You may still have the experience.')
    for m in result['gaps']:
        st.markdown(f"**{m.skill}**" + (' *(preferred)*' if m.preferred else ''))
        st.caption(m.job_evidence)
    if not result['gaps']: st.write('All detected skills have supporting text in the resume.')
    st.subheader('Tailor your resume using existing evidence')
    st.write('Consider moving the most relevant existing lines higher under the appropriate experience or projects. Keep their original employer and dates; edit wording only when it stays true.')
    if result['ranked']:
        for _,_,s,hits in result['ranked']:
            st.markdown('**' + ', '.join(hits) + '**')
            st.write('“'+s+'”')
        suggested='RELEVANT EXISTING RESUME LINES — review and place under their original roles\n\n'+'\n'.join('• '+s for _,_,s,_ in result['ranked'])
        st.download_button('Download suggested lines (.txt)',suggested,file_name='jobfit-resume-lines.txt',mime='text/plain')
    st.subheader('Questions to resolve before applying')
    for m in result['gaps'][:6]:
        st.write(f'• Do you have real {m.skill} experience you can describe with a specific example? If yes, add it accurately. If no, leave it off.')
    if not result['gaps']: st.write('Review the listed job requirements for education, work authorization, location, and schedule separately.')
    if result['requirements']:
        with st.expander('Job requirement lines to review manually'):
            for s in result['requirements']: st.write('• '+s)
    st.caption('Files and job descriptions are processed locally while this app is running. Nothing is sent to an AI service. Scanned image PDFs may need OCR or manual paste.')
