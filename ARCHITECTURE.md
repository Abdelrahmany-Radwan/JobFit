# Architecture

JobFit is intentionally split into two implementations that share the same product principle: **surface evidence, do not invent it**.

## Public web application

The production-facing experience lives in `docs/` and is deployed through GitHub Pages.

### Data flow

```text
Resume file / pasted text
        │
        ▼
Client-side parsing
(PDF.js / Mammoth / plain text)
        │
        ▼
Resume + job segmentation
        │
        ▼
Sentence embeddings
(all-MiniLM-L6-v2 in browser)
        │
        ▼
Cosine similarity + lexical overlap
        │
        ▼
Requirement-to-evidence ranking
        │
        ▼
Explainable UI output
```

### Design decisions

**Client-side document processing**  
Resume contents stay in the browser. JobFit does not run an application backend that stores uploaded resumes.

**Semantic + lexical matching**  
Embeddings provide semantic recall while lexical overlap adds a deterministic signal. The combined score is used to rank evidence, not to generate claims.

**Evidence traceability**  
Each result points to source text from the resume. This keeps the output auditable and makes it easier for a user to decide whether a match is actually meaningful.

**Graceful fallback**  
If the embedding model cannot load, the application falls back to lexical similarity instead of failing entirely.

## Python baseline

`analyzer.py` contains the original deterministic skill-matching baseline. `app.py` provides a Streamlit interface around that implementation.

The baseline is retained because it is useful for comparison, debugging, and demonstrating the evolution from a rules-based matcher to a semantic one.

## Delivery

GitHub Actions is used for:

- Python syntax validation
- automated unit tests
- required static-file checks
- GitHub Pages deployment

The deployment workflow is separate from validation so product delivery and code-quality checks remain independently observable.
