# JobFit — AI Resume Match Explainer

**Live demo:** https://abdelrahmany-radwan.github.io/JobFit/

JobFit is a privacy-first, explainable resume-to-job matching application. It uses transformer sentence embeddings plus deterministic evidence matching to compare what a role asks for with what a resume can actually support.

The core idea is simple:

> **Use AI to understand meaning. Use evidence to keep the result honest.**

## Why I built it

Keyword-only resume scanners can miss semantic matches. Generative resume tools can create the opposite problem: rewriting experience in ways that sound stronger than what the candidate actually did.

JobFit is designed between those two extremes. It uses semantic AI to understand similarity, but it only surfaces evidence that already exists in the candidate's resume.

## What the live app does

- Accepts PDF, DOCX, TXT, or pasted resume content.
- Accepts a pasted job description.
- Identifies requirement-oriented job statements.
- Runs **all-MiniLM-L6-v2 sentence embeddings in the browser** with Transformers.js.
- Combines semantic similarity with lexical evidence signals.
- Shows the strongest requirement-to-resume matches.
- Flags job requirements that do not have strong visible evidence.
- Ranks existing resume lines the candidate should lead with.
- Keeps resume processing client-side; JobFit has no resume-storage backend.
- Falls back to local lexical similarity if the transformer model is unavailable.

## AI / ML architecture

\`\`\`
Resume + Job Description
        ↓
Client-side file parsing
        ↓
Requirement-oriented sentence extraction
        ↓
Transformer sentence embeddings
(all-MiniLM-L6-v2 via Transformers.js)
        ↓
Cosine similarity + lexical evidence signals
        ↓
Explainable requirement ↔ resume evidence pairs
\`\`\`

The transformer model improves matching beyond exact keywords. The output remains explainable because every score is tied back to an exact line from the user-provided resume.

## Engineering decisions

### Semantic AI instead of keyword-only matching
The live version uses a real sentence-transformer embedding model to represent resume and job text semantically.

### Explainability by design
JobFit does not ask a model to invent a credential. It ranks evidence that already exists and displays the supporting text.

### Privacy-aware inference
The public application is static. PDF/DOCX parsing and embedding inference run in the user's browser instead of sending resume content to a JobFit application server.

### Resilient execution
If the transformer model cannot load, the interface continues with local lexical similarity instead of failing completely.

## Tech stack

- JavaScript / HTML / CSS
- Transformers.js
- Xenova/all-MiniLM-L6-v2
- PDF.js
- Mammoth.js
- GitHub Pages
- Python / Streamlit reference implementation
- Git / GitHub

## AI-assisted development workflow

JobFit was developed with an AI-native engineering workflow. ChatGPT was used for architecture discussion, code review, edge-case reasoning, UX refinement, and documentation while implementation decisions remained reviewable in GitHub source control.

I use AI coding tools as development accelerators rather than replacements for technical ownership: suggested changes are inspected, tested against intended behavior, and kept explainable enough to defend technically.

## Repository structure

- \`docs/\` — recruiter-facing public web application deployed to GitHub Pages.
- \`app.py\` — Streamlit reference implementation.
- \`analyzer.py\` — transparent Python matching baseline.
- \`.github/workflows/pages.yml\` — GitHub Pages deployment workflow.
