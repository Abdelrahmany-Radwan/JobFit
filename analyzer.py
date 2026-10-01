"""Transparent, local resume-to-job comparison. No generated credentials or claims."""
import re
from dataclasses import dataclass

SKILLS = {
    'Python': [r'\bpython\b'],
    'SQL': [r'\bsql\b', r'\bpostgres(?:ql)?\b', r'\bmysql\b'],
    'Excel': [r'\bexcel\b', r'\bspreadsheets?\b'],
    'Power BI': [r'\bpower\s*bi\b'],
    'Tableau': [r'\btableau\b'],
    'Data analysis': [r'\bdata analys(?:is|t|e)\b', r'\bdata analytics\b', r'\banaly[sz](?:e|ing|ed) data\b'],
    'Data visualization': [r'\bdata visuali[sz]ation\b', r'\bvisuali[sz](?:e|ing) data\b'],
    'Machine learning': [r'\bmachine learning\b', r'\bml models?\b'],
    'Artificial intelligence': [r'\bartificial intelligence\b', r'\bai tools?\b', r'\bai solutions?\b'],
    'Generative AI': [r'\bgenerative ai\b', r'\bgen\s*ai\b', r'\bllms?\b', r'\blarge language models?\b'],
    'Azure': [r'\bazure\b'],
    'AWS': [r'\baws\b', r'\bamazon web services\b'],
    'Cloud computing': [r'\bcloud computing\b', r'\bcloud infrastructure\b'],
    'Java': [r'\bjava\b'],
    'JavaScript': [r'\bjavascript\b', r'\bjs\b'],
    'TypeScript': [r'\btypescript\b'],
    'HTML': [r'\bhtml\b'],
    'CSS': [r'\bcss\b'],
    'React': [r'\breact(?:\.js)?\b'],
    'Git': [r'\bgit\b', r'\bgithub\b'],
    'APIs': [r'\bapis?\b', r'\brest(?:ful)?\b'],
    'Cybersecurity': [r'\bcyber\s*security\b', r'\binformation security\b'],
    'Networking': [r'\bnetwork(?:ing|s)?\b'],
    'Troubleshooting': [r'\btroubleshoot(?:ing|ed)?\b'],
    'Customer service': [r'\bcustomer service\b', r'\bcustomer support\b', r'\buser assistance\b'],
    'Communication': [r'\bcommunicat(?:ion|e|ed|ing)\b', r'\bpresent(?:ation|ations|ed|ing)\b'],
    'Collaboration': [r'\bcollaborat(?:ion|e|ed|ing)\b', r'\bteamwork\b', r'\bcross.functional\b'],
    'Project management': [r'\bproject management\b', r'\bproject planning\b'],
    'Research': [r'\bresearch\b'],
    'Risk analysis': [r'\brisk analys(?:is|es)\b', r'\brisk assessment\b'],
    'Documentation': [r'\bdocument(?:ation|s|ed|ing)?\b', r'\btechnical writing\b'],
}
REQUIREMENT_HINT = re.compile(r'\b(require[ds]?|qualification|must|need(?:ed)?|preferred|nice to have|experience with|proficien|familiar|knowledge of|ability to|skills? in|you have|you bring)\b', re.I)
PREFERRED_HINT = re.compile(r'\b(preferred|nice to have|bonus|plus|desirable)\b', re.I)
STOPWORDS = set('the a an and or with for in of to on by as from is are be you your our their this that will have has working work skills experience knowledge ability strong good excellent including required preferred plus'.split())

@dataclass
class Match:
    skill: str
    evidence: str | None
    job_evidence: str
    preferred: bool


def lines(text):
    result=[]
    for raw in text.splitlines():
        for part in re.split(r'(?<=[.!?])\s+(?=[A-Z])', raw):
            s=re.sub(r'\s+', ' ', part).strip(' \t•-–')
            if s and len(s)>2: result.append(s[:600])
    return result


def has_skill(text, patterns):
    return any(re.search(p, text, re.I) for p in patterns)


def tokenize(s):
    return {w for w in re.findall(r'[a-z][a-z0-9+#.]{2,}', s.lower()) if w not in STOPWORDS}


def analyze(resume, job):
    resume_lines=lines(resume)
    job_lines=lines(job)
    if not resume_lines or not job_lines: raise ValueError('Add both a readable resume and a job description.')
    if len(resume)>150000 or len(job)>100000: raise ValueError('The input is too long. Please use a resume and one job description.')
    found=[]
    for skill,patterns in SKILLS.items():
        job_evidence=next((s for s in job_lines if has_skill(s,patterns)),None)
        if job_evidence:
            resume_evidence=next((s for s in resume_lines if has_skill(s,patterns)),None)
            found.append(Match(skill,resume_evidence,job_evidence,bool(PREFERRED_HINT.search(job_evidence))))
    strengths=[m for m in found if m.evidence]
    gaps=[m for m in found if not m.evidence]
    total=sum(1 if m.preferred else 2 for m in found)
    covered=sum(1 if m.preferred else 2 for m in strengths)
    score=round(100*covered/total) if total else None
    # Prioritize existing text without inventing facts. Preserve original wording.
    ranked=[]
    for i,s in enumerate(resume_lines):
        hit=[m.skill for m in strengths if has_skill(s,SKILLS[m.skill])]
        if hit and len(s)>=25:
            overlap=len(tokenize(s) & tokenize(job))
            ranked.append((len(hit)*3+overlap,i,s,hit))
    ranked.sort(key=lambda x:(-x[0],x[1]))
    requirements=[]
    for s in job_lines:
        if REQUIREMENT_HINT.search(s) and len(s)>20 and len(s)<400:
            requirements.append(s)
    return {'score':score,'strengths':strengths,'gaps':gaps,'ranked':ranked[:7],
            'requirements':requirements[:12], 'skills_count':len(found),
            'resume_lines':len(resume_lines)}
