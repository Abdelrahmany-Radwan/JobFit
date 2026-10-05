# JobFit

[![CI](https://img.shields.io/github/actions/workflow/status/Abdelrahmany-Radwan/JobFit/ci.yml?branch=main&label=build&style=flat-square)](https://github.com/Abdelrahmany-Radwan/JobFit/actions/workflows/ci.yml)
[![Evaluation](https://img.shields.io/github/actions/workflow/status/Abdelrahmany-Radwan/JobFit/evaluation.yml?branch=main&label=evaluation&style=flat-square)](https://github.com/Abdelrahmany-Radwan/JobFit/actions/workflows/evaluation.yml)
[![Deploy](https://img.shields.io/github/actions/workflow/status/Abdelrahmany-Radwan/JobFit/pages.yml?branch=main&label=deploy&style=flat-square)](https://github.com/Abdelrahmany-Radwan/JobFit/actions/workflows/pages.yml)

JobFit is an evidence-first resume-to-job matching system. It maps individual job requirements to supporting resume text using in-browser sentence embeddings, then exposes the evidence behind each match instead of generating new qualifications.

**[Live application](https://abdelrahmany-radwan.github.io/JobFit/)** · **[Architecture](ARCHITECTURE.md)**

## System

```text
PDF / DOCX / text
        │
        ▼
client-side parsing
        │
        ▼
requirement + resume segmentation
        │
        ▼
all-MiniLM-L6-v2 embeddings
        │
        ├──────────────┐
        ▼              ▼
cosine similarity   lexical overlap
        │              │
        └──────┬───────┘
               ▼
       hybrid evidence ranker
               │
               ▼
 requirement → source evidence
```

The public application uses Transformers.js to run `Xenova/all-MiniLM-L6-v2` in the browser. PDF.js and Mammoth.js extract document text locally. Semantic similarity is combined with a lexical signal and the interface returns the original resume text supporting each requirement.

If the embedding model is unavailable, the matcher falls back to lexical scoring rather than blocking the workflow.

## Evaluation

The repository includes a reproducible retrieval benchmark comparing:

| Method | Role |
| --- | --- |
| Lexical overlap | deterministic baseline |
| MiniLM cosine similarity | semantic baseline |
| Hybrid scorer | JobFit retrieval strategy |

Thresholds are selected on a **development split** and final metrics are calculated on a **held-out test split**. The workflow also records inference latency on the GitHub Actions CPU runner.

The current benchmark is intentionally a small curated regression set. It is useful for comparing implementation changes; it is **not** presented as a general measure of hiring, ATS, or real-world recruiting accuracy.

Run details and generated metrics are available from the **Evaluate matching model** GitHub Actions workflow.

## Engineering decisions

- **Evidence over generation.** Matching output must point back to source resume text.
- **Local document processing.** The public app does not require a JobFit backend to store resumes.
- **Hybrid retrieval.** Semantic similarity handles wording variation; lexical overlap preserves an interpretable exact-match signal.
- **Independent baseline.** The original deterministic Python matcher remains in the repository for regression and architectural comparison.
- **Failure tolerance.** Lexical matching remains available when browser model loading fails.
- **Measured changes.** Model behavior is evaluated separately from application CI and deployment.

## Repository

```text
.
├── docs/                 # browser application
├── evaluation/           # labeled benchmark + evaluator
├── tests/                # Python baseline tests
├── .github/
│   ├── ISSUE_TEMPLATE/   # structured bug / feature reports
│   └── workflows/        # CI, evaluation, Pages deployment
├── analyzer.py           # deterministic matching baseline
├── app.py                # Streamlit reference interface
├── ARCHITECTURE.md
├── CONTRIBUTING.md
└── LICENSE
```

## Development

The browser application is static and can be served directly from `docs/`.

The Python reference implementation uses the dependencies in `requirements.txt` and runs with Streamlit. Model evaluation has isolated dependencies in `evaluation/requirements.txt`.

Pull requests run syntax validation, unit tests, and static-site checks. Model evaluation and Pages deployment run as separate workflows so code quality, retrieval behavior, and delivery remain independently observable.

## License

MIT
