# JobFit

[![CI](https://img.shields.io/github/actions/workflow/status/Abdelrahmany-Radwan/JobFit/ci.yml?branch=main&label=build&style=flat-square)](https://github.com/Abdelrahmany-Radwan/JobFit/actions/workflows/ci.yml)
[![Evaluation](https://img.shields.io/github/actions/workflow/status/Abdelrahmany-Radwan/JobFit/evaluation.yml?branch=main&label=evaluation&style=flat-square)](https://github.com/Abdelrahmany-Radwan/JobFit/actions/workflows/evaluation.yml)
[![Deploy](https://img.shields.io/github/actions/workflow/status/Abdelrahmany-Radwan/JobFit/pages.yml?branch=main&label=deploy&style=flat-square)](https://github.com/Abdelrahmany-Radwan/JobFit/actions/workflows/pages.yml)

JobFit is an evidence-first resume-to-job matching system. It maps individual job requirements to supporting resume text using in-browser sentence embeddings, then exposes the evidence behind each match instead of generating new qualifications.

**[Live application](https://abdelrahmany-radwan.github.io/JobFit/)** · **[Architecture](ARCHITECTURE.md)**

> **Product direction:** JobFit is designed around evidence as a visual object: resumes, requirements, source lines, and their connections. The interface intentionally avoids presenting semantic matching as a black-box “AI score.”

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

JobFit includes a reproducible retrieval benchmark with thresholds selected on a **development split** and metrics reported on a **held-out test split**.

| Method | Precision | Recall | F1 | Accuracy |
| --- | ---: | ---: | ---: | ---: |
| Lexical baseline | 0.625 | 1.000 | 0.769 | 0.625 |
| MiniLM semantic | 0.833 | 1.000 | 0.909 | 0.875 |
| JobFit hybrid | 0.833 | 1.000 | 0.909 | 0.875 |

On the GitHub Actions CPU runner, lexical scoring averaged **0.01 ms/pair** and MiniLM semantic scoring had a **7.98 ms median/pair**, excluding model download/load time.

The benchmark currently contains 24 curated requirement/evidence pairs (16 dev, 8 held-out test). It is a regression benchmark for comparing retrieval behavior—not a claim about ATS, hiring, or population-level recruiting accuracy. The full methodology and generated results live in `evaluation/` and the **Evaluate matching model** workflow.

## Product + engineering principles

The interface and retrieval system follow the same constraint: **show the connection before asking the user to trust the score.** Visual states expose source evidence alongside similarity output, while the retrieval layer remains independently testable.

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
