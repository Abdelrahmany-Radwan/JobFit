# JobFit

[![Live Site](https://img.shields.io/badge/live-jobfit-2f6f62?style=flat-square)](https://abdelrahmany-radwan.github.io/JobFit/)
[![CI](https://img.shields.io/github/actions/workflow/status/Abdelrahmany-Radwan/JobFit/ci.yml?branch=main&label=CI&style=flat-square)](https://github.com/Abdelrahmany-Radwan/JobFit/actions/workflows/ci.yml)
[![Pages](https://img.shields.io/github/actions/workflow/status/Abdelrahmany-Radwan/JobFit/pages.yml?branch=main&label=Pages&style=flat-square)](https://github.com/Abdelrahmany-Radwan/JobFit/actions/workflows/pages.yml)

![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=flat-square&logo=python&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-F7DF1E?style=flat-square&logo=javascript&logoColor=111)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-CI%2FCD-2088FF?style=flat-square&logo=githubactions&logoColor=white)
![Transformers.js](https://img.shields.io/badge/Transformers.js-MiniLM-FFCC4D?style=flat-square)

JobFit is an explainable resume-to-job matching project built around a problem I saw students face: it is hard to tell which parts of a resume actually support a job application without either relying on exact keyword matching or rewriting experience beyond what really happened.

JobFit uses semantic sentence embeddings and transparent evidence matching to connect job requirements to existing resume text. The public application runs in the browser so the document can be analyzed without a JobFit resume-storage backend.

**[Open JobFit](https://abdelrahmany-radwan.github.io/JobFit/)**

## Product principles

- **Evidence first** — results point back to text that already exists in the resume.
- **Semantic matching** — sentence embeddings capture related meaning beyond exact keyword overlap.
- **Explainable output** — each match shows the job requirement and supporting resume evidence.
- **Privacy-aware processing** — the public application parses files and performs matching client-side.
- **Graceful fallback** — lexical similarity keeps the core experience available if the embedding model cannot load.

## How it works

```text
Resume + job description
          │
          ▼
Client-side document parsing
          │
          ▼
Requirement-oriented text segmentation
          │
          ▼
MiniLM sentence embeddings
          │
          ▼
Cosine similarity + lexical signals
          │
          ▼
Requirement ↔ resume evidence
```

The browser application uses `Xenova/all-MiniLM-L6-v2` through Transformers.js. Resume and job segments are embedded into vector representations, compared with cosine similarity, and combined with lexical overlap signals. The result is presented as evidence rather than generated experience.

## Technology

| Layer | Technology | Purpose |
| --- | --- | --- |
| Web UI | HTML, CSS, JavaScript | Responsive public product experience |
| Semantic matching | Transformers.js + MiniLM | In-browser sentence embeddings |
| Document parsing | PDF.js + Mammoth.js | PDF and DOCX text extraction |
| Matching logic | Cosine similarity + lexical signals | Evidence ranking |
| Python baseline | Python + Streamlit | Deterministic reference implementation |
| Delivery | GitHub Actions + GitHub Pages | Continuous validation and deployment |

## Repository structure

```text
JobFit/
├── .github/
│   └── workflows/
│       ├── ci.yml             # Repository validation
│       └── pages.yml          # GitHub Pages deployment
├── docs/
│   ├── index.html             # Public application
│   ├── style.css              # Responsive design system
│   ├── app.js                 # Parsing, embeddings, matching, UI behavior
│   └── .nojekyll              # Static Pages configuration
├── analyzer.py                # Deterministic Python matching baseline
├── app.py                     # Streamlit interface for the Python baseline
├── requirements.txt           # Python dependencies
├── CONTRIBUTING.md            # Contribution workflow
├── LICENSE                    # MIT license
└── README.md                  # Project documentation
```

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for the system design, data flow, implementation split, and delivery model.

## Engineering notes

The project keeps the public browser implementation and the Python baseline separate on purpose. The browser version focuses on semantic matching, privacy, and accessibility through a public URL. The Python implementation keeps the original deterministic skill-matching approach available as a readable baseline for comparison.

JobFit does not treat its similarity result as an ATS score or hiring prediction. The score summarizes evidence similarity within this application and is accompanied by the source text so the user can interpret it.

## AI-assisted development

AI tools were used as part of the development workflow for architecture discussion, implementation review, edge-case reasoning, and documentation. AI-assisted suggestions were reviewed against the project requirements and committed through normal source control rather than treated as authoritative output.

The product itself uses an embedding model for semantic matching. It does not use generative AI to create qualifications or claim experience that is absent from the resume.

## Local development

The public application is static: serve the `docs/` directory with any local HTTP server.

The Python baseline uses the dependencies in `requirements.txt` and runs through Streamlit.

## Contributing

Small, focused changes are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for the development and pull-request workflow.

## License

Released under the [MIT License](LICENSE).
