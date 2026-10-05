const $ = (id) => document.getElementById(id);
const resumeFile = $("resumeFile");
const resumeText = $("resumeText");
const jobText = $("jobText");
const analyzeBtn = $("analyzeBtn");
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

    resultsEl.classList.remove("hidden");
    resultsEl.scrollIntoView({behavior:"smooth",block:"start"});
  }catch(e){
    errorEl.textContent=e.message||String(e);
    errorEl.classList.remove("hidden");
  }finally{
    analyzeBtn.disabled=false;
    analyzeBtn.innerHTML="Find my evidence <span>→</span>";
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
