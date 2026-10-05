const $ = (id) => document.getElementById(id);
const resumeFile = $("resumeFile");
const resumeText = $("resumeText");
const jobText = $("jobText");
const analyzeBtn = $("analyzeBtn");
const sampleBtn = $("sampleBtn");
const statusEl = $("modelStatus");
const errorEl = $("error");
const resultsEl = $("results");

const requirementHint = /\b(require|required|requirements?|qualification|must|need|preferred|nice to have|experience with|proficien|familiar|knowledge of|ability to|skills? in|you have|you bring|responsibilit)/i;
const stop = new Set("the a an and or with for in of to on by as from is are be you your our their this that will have has working work skills experience knowledge ability strong good excellent including required preferred plus".split(" "));

let extractor = null;

function splitLines(text) {
  return text.split(/\n+/)
    .flatMap(raw => raw.split(/(?<=[.!?])\s+(?=[A-Z])/))
    .map(s => s.replace(/\s+/g," ").replace(/^[\s•\-–]+/,"").trim())
    .filter(s => s.length > 18 && s.length < 700);
}

function tokens(s) {
  return new Set((s.toLowerCase().match(/[a-z][a-z0-9+#.]{2,}/g) || []).filter(w => !stop.has(w)));
}

function lexical(a,b) {
  const A=tokens(a), B=tokens(b);
  if(!A.size || !B.size) return 0;
  let hit=0; for(const x of A) if(B.has(x)) hit++;
  return hit / Math.sqrt(A.size*B.size);
}

function cosine(a,b) {
  let dot=0,na=0,nb=0;
  for(let i=0;i<a.length;i++){dot+=a[i]*b[i];na+=a[i]*a[i];nb+=b[i]*b[i]}
  return dot/(Math.sqrt(na)*Math.sqrt(nb)+1e-9);
}

async function loadModel() {
  if (extractor) return extractor;
  statusEl.textContent = "Loading transformer model…";
  try {
    const { pipeline, env } = await import("https://cdn.jsdelivr.net/npm/@xenova/transformers@2.17.2/+esm");
    env.allowLocalModels = false;
    extractor = await pipeline("feature-extraction","Xenova/all-MiniLM-L6-v2",{quantized:true});
    statusEl.textContent = "AI model ready · MiniLM embeddings";
    return extractor;
  } catch (e) {
    statusEl.textContent = "Semantic fallback active";
    extractor = false;
    return false;
  }
}

async function embed(texts) {
  const model = await loadModel();
  if (!model) return null;
  const out=[];
  for(const t of texts){
    const x = await model(t,{pooling:"mean",normalize:true});
    out.push(Array.from(x.data));
  }
  return out;
}

async function extractFile(file){
  const name=file.name.toLowerCase();
  if(file.size>8_000_000) throw new Error("Please use a resume smaller than 8 MB.");
  if(name.endsWith(".txt")) return await file.text();

  if(name.endsWith(".docx")){
    if(!window.mammoth) throw new Error("DOCX parser could not load.");
    const ab=await file.arrayBuffer();
    return (await window.mammoth.extractRawText({arrayBuffer:ab})).value;
  }

  if(name.endsWith(".pdf")){
    const pdfjs = await import("https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.8.69/pdf.min.mjs");
    pdfjs.GlobalWorkerOptions.workerSrc="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.8.69/pdf.worker.min.mjs";
    const pdf=await pdfjs.getDocument({data:await file.arrayBuffer()}).promise;
    let text="";
    for(let i=1;i<=pdf.numPages;i++){
      const page=await pdf.getPage(i);
      const content=await page.getTextContent();
      text += "\n" + content.items.map(x=>x.str).join(" ");
    }
    return text;
  }
  throw new Error("Use PDF, DOCX, or TXT.");
}

function requirementsFrom(job){
  const lines=splitLines(job);
  const hinted=lines.filter(s=>requirementHint.test(s));
  const pool=(hinted.length>=3?hinted:lines).slice(0,18);
  return pool;
}

function resumeChunks(resume){
  const lines=splitLines(resume).filter(s=>s.length>=28);
  return lines.slice(0,80);
}

function renderItem(container,item,isGap=false){
  const d=document.createElement("div");
  d.className="match";
  d.innerHTML = '<div class="match-title"><span>'+escapeHtml(item.req)+'</span><span class="pill '+(isGap?"gap":"")+'">'+Math.round(item.score*100)+'% similar</span></div>'
    + (item.evidence?'<div class="evidence"><b>Resume evidence:</b> '+escapeHtml(item.evidence)+'</div>':"");
  container.appendChild(d);
}

function escapeHtml(s){return s.replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#039;"}[c]))}

async function analyze(resume,job){
  const reqs=requirementsFrom(job), chunks=resumeChunks(resume);
  if(!reqs.length||!chunks.length) throw new Error("I could not find enough readable resume/job text.");

  const reqEmb=await embed(reqs);
  const chunkEmb=reqEmb?await embed(chunks):null;
  const rows=[];

  for(let i=0;i<reqs.length;i++){
    let best={score:0,evidence:""};
    for(let j=0;j<chunks.length;j++){
      const lex=lexical(reqs[i],chunks[j]);
      const sem=reqEmb?cosine(reqEmb[i],chunkEmb[j]):lex;
      const score=reqEmb ? (0.82*sem + 0.18*Math.min(1,lex*2.2)) : lex;
      if(score>best.score) best={score,evidence:chunks[j]};
    }
    rows.push({req:reqs[i],...best});
  }
  rows.sort((a,b)=>b.score-a.score);
  return rows;
}


function extractJobKeywords(job){
  const words=(job.toLowerCase().match(/[a-z][a-z0-9+#.]{2,}/g)||[])
    .filter(w=>!stop.has(w) && w.length>2);
  const freq=new Map();
  words.forEach(w=>freq.set(w,(freq.get(w)||0)+1));
  return [...freq.entries()]
    .sort((a,b)=>b[1]-a[1] || a[0].localeCompare(b[0]))
    .map(([w])=>w)
    .slice(0,28);
}

function resumeHealth(resume){
  const lower=resume.toLowerCase();
  const lines=resume.split(/\n+/).map(s=>s.trim()).filter(Boolean);
  const bullets=lines.filter(s=>/^[•\-–]/.test(s) || /\b(built|created|developed|led|designed|implemented|analyzed|improved|managed|collaborated|presented|automated|configured|resolved|researched)\b/i.test(s));
  const quantified=lines.filter(s=>/\b\d+(?:\.\d+)?%?\b/.test(s));
  const hasExperience=/\bexperience\b/i.test(resume);
  const hasEducation=/\beducation\b/i.test(resume);
  const hasProjects=/\bprojects?\b/i.test(resume);
  const email=/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/i.test(resume);
  const phone=/(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}/.test(resume);
  const checks=[
    {name:"Core sections",pass:hasExperience&&hasEducation,detail:hasExperience&&hasEducation?"Experience and education found.":"Add clear Experience and Education sections."},
    {name:"Projects signal",pass:hasProjects,detail:hasProjects?"Projects section found.":"A Projects section can help technical work stand out."},
    {name:"Action-oriented bullets",pass:bullets.length>=3,detail:bullets.length>=3?`${bullets.length} action-oriented lines found.`:"Use stronger action verbs in experience/project bullets."},
    {name:"Quantified impact",pass:quantified.length>=2,detail:quantified.length>=2?`${quantified.length} quantified lines found.`:"Add numbers where they are truthful and useful."},
    {name:"Contact basics",pass:email||phone,detail:(email||phone)?"Contact information detected.":"Add at least an email or phone number."},
    {name:"Readable length",pass:resume.length>=500&&resume.length<=7000,detail:resume.length>=500&&resume.length<=7000?"Resume text length looks reasonable.":"Resume may be unusually short or long for a one-page early-career resume."}
  ];
  const score=Math.round(checks.filter(c=>c.pass).length/checks.length*100);
  return {checks,score};
}

function renderHealth(resume, rows){
  const health=resumeHealth(resume);
  $("healthScore").textContent=health.score+"%";
  const holder=$("healthChecks"); holder.innerHTML="";
  health.checks.forEach(c=>{
    const d=document.createElement("div");
    d.className="health-item "+(c.pass?"pass":"warn");
    d.innerHTML='<span>'+(c.pass?"✓":"↗")+'</span><div><b>'+escapeHtml(c.name)+'</b><p>'+escapeHtml(c.detail)+'</p></div>';
    holder.appendChild(d);
  });

  const queue=$("actionQueue"); queue.innerHTML="";
  const actions=[];
  rows.filter(x=>x.score<0.40).slice(0,3).forEach(x=>actions.push("Strengthen or add evidence for: "+x.req));
  health.checks.filter(c=>!c.pass).forEach(c=>actions.push(c.detail));
  if(!actions.length) actions.push("No major issues surfaced in the current checks. Review wording and accuracy before applying.");
  actions.slice(0,6).forEach((a,i)=>{
    const d=document.createElement("div"); d.className="action-item";
    d.innerHTML='<b>'+String(i+1).padStart(2,"0")+'</b><span>'+escapeHtml(a)+'</span>';
    queue.appendChild(d);
  });
}

function renderKeywords(resume,job){
  const kws=extractJobKeywords(job);
  const rt=tokens(resume.toLowerCase());
  const present=kws.filter(k=>rt.has(k));
  const missing=kws.filter(k=>!rt.has(k));
  $("keywordCoverage").textContent=(kws.length?Math.round(present.length/kws.length*100):0)+"%";
  const p=$("presentKeywords"),m=$("missingKeywords"); p.innerHTML="";m.innerHTML="";
  present.forEach(k=>{const s=document.createElement("span");s.textContent=k;p.appendChild(s)});
  missing.forEach(k=>{const s=document.createElement("span");s.textContent=k;m.appendChild(s)});
}

document.querySelectorAll(".report-tab").forEach(btn=>{
  btn.addEventListener("click",()=>{
    document.querySelectorAll(".report-tab").forEach(x=>{x.classList.remove("active");x.setAttribute("aria-selected","false")});
    document.querySelectorAll(".report-pane").forEach(x=>x.classList.remove("active"));
    btn.classList.add("active");btn.setAttribute("aria-selected","true");
    document.querySelector('[data-pane="'+btn.dataset.tab+'"]')?.classList.add("active");
  });
});

analyzeBtn.addEventListener("click", async () => {
  errorEl.classList.add("hidden");
  resultsEl.classList.add("hidden");
  analyzeBtn.disabled=true;
  analyzeBtn.textContent="Analyzing…";
  try{
    let resume=resumeText.value.trim();
    if(!resume && resumeFile.files[0]) resume=(await extractFile(resumeFile.files[0])).trim();
    const job=jobText.value.trim();
    if(resume.length<80||job.length<80) throw new Error("Add a readable resume and a full job description first.");

    const rows=await analyze(resume,job);
    const strong=rows.filter(x=>x.score>=0.52);
    const gaps=rows.filter(x=>x.score<0.40);
    const overall=Math.round((rows.reduce((s,x)=>s+Math.max(0,Math.min(1,(x.score-.18)/.52)),0)/rows.length)*100);

    $("score").textContent=overall+"%";
    $("matchedCount").textContent=strong.length;
    $("gapCount").textContent=gaps.length;

    const matches=$("matches"), gapsEl=$("gaps"), ranked=$("ranked");
    matches.innerHTML="";gapsEl.innerHTML="";ranked.innerHTML="";

    (strong.length?strong:rows.slice(0,4)).slice(0,6).forEach(x=>renderItem(matches,x,false));
    (gaps.length?gaps:rows.slice(-3)).slice(0,6).forEach(x=>renderItem(gapsEl,x,true));

    const seen=new Set();
    rows.filter(x=>x.score>=0.40).slice(0,8).forEach(x=>{
      if(seen.has(x.evidence)) return; seen.add(x.evidence);
      const d=document.createElement("div");d.className="match";
      d.innerHTML='<div class="match-title"><span>'+escapeHtml(x.evidence)+'</span><span class="pill">'+Math.round(x.score*100)+'%</span></div><div class="evidence">Best supports: '+escapeHtml(x.req)+'</div>';
      ranked.appendChild(d);
    });

    renderHealth(resume, rows);
    renderKeywords(resume, job);

    resultsEl.classList.remove("hidden");
    resultsEl.scrollIntoView({behavior:"smooth",block:"start"});
  }catch(e){
    errorEl.textContent=e.message||String(e);
    errorEl.classList.remove("hidden");
  }finally{
    analyzeBtn.disabled=false;
    analyzeBtn.innerHTML="connect the dots <span>→</span>";
  }
});

const fileLabel = document.querySelector(".dropzone b");
resumeFile.addEventListener("change", () => {
  if (resumeFile.files[0]) fileLabel.textContent = resumeFile.files[0].name;
});

const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) entry.target.classList.add("visible");
  });
}, { threshold: 0.12 });
document.querySelectorAll(".reveal").forEach((el) => observer.observe(el));

window.addEventListener("scroll", () => {
  const doc = document.documentElement;
  const max = doc.scrollHeight - doc.clientHeight;
  $("progress").style.width = (max > 0 ? (doc.scrollTop / max) * 100 : 0) + "%";
}, { passive: true });

document.querySelectorAll(".resume-card").forEach((card) => {
  card.addEventListener("pointermove", (event) => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const rect = card.getBoundingClientRect();
    const x = (event.clientX - rect.left) / rect.width - .5;
    const y = (event.clientY - rect.top) / rect.height - .5;
    card.style.setProperty("--px", x.toFixed(2));
    card.style.setProperty("--py", y.toFixed(2));
  });
  card.addEventListener("pointerleave", () => {
    card.style.removeProperty("--px");
    card.style.removeProperty("--py");
  });
});

const SAMPLE_RESUME = `
Jordan Lee
Data Analytics Student

Experience
Built Python scripts with pandas to clean survey data and automate weekly reporting.
Designed Power BI dashboards that summarized energy-use trends for a project presentation.
Collaborated with a six-person team to research smart-community technologies and present recommendations.
Presented cloud concepts to student attendees using step-by-step demos and plain-language explanations.

Projects
Built and deployed a resume-matching application that uses MiniLM sentence embeddings, cosine similarity, and lexical signals to connect job requirements to supporting resume evidence.
Managed source control, CI, model evaluation, architecture documentation, and deployment through GitHub.
`;

const SAMPLE_JOB = `
Data & AI Intern

Requirements:
Experience using Python to analyze datasets and automate workflows.
Ability to create clear data visualizations and communicate insights to stakeholders.
Strong written and verbal communication skills for explaining technical concepts.
Experience collaborating across a project team.
Familiarity with machine learning or natural language processing.
Ability to translate ambiguous requirements into working technical solutions.
Preferred: experience with Git and GitHub source control.
`;

sampleBtn?.addEventListener("click", () => {
  resumeText.value = SAMPLE_RESUME.trim();
  jobText.value = SAMPLE_JOB.trim();
  resumeFile.value = "";
  if (fileLabel) fileLabel.textContent = "Choose a resume";
  errorEl.classList.add("hidden");
  resultsEl.classList.add("hidden");
  analyzeBtn.scrollIntoView({behavior:"smooth", block:"center"});
});


document.querySelectorAll(".requirement[data-match]").forEach((req) => {
  const key = req.dataset.match;
  const evidence = document.querySelector('[data-evidence="' + key + '"]');
  const path = document.querySelector('[data-path="' + key + '"]');
  const on = () => {
    req.classList.add("is-active");
    evidence?.classList.add("is-active");
    path?.classList.add("is-active");
  };
  const off = () => {
    req.classList.remove("is-active");
    evidence?.classList.remove("is-active");
    path?.classList.remove("is-active");
  };
  req.addEventListener("mouseenter", on);
  req.addEventListener("mouseleave", off);
  req.addEventListener("focusin", on);
  req.addEventListener("focusout", off);
});
