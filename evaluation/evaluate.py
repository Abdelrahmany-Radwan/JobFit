"""Reproducible JobFit retrieval benchmark.

Compares:
1. lexical token-overlap baseline
2. MiniLM semantic cosine similarity
3. JobFit hybrid score

Run:
    python evaluation/evaluate.py
"""
from __future__ import annotations
import json
import math
import re
from pathlib import Path

DATA = Path(__file__).with_name("benchmark.json")
OUT = Path(__file__).with_name("results.json")
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
STOP = set("the a an and or with for in of to on by as from is are be you your our their this that will have has using use experience strong skills".split())

def tokens(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z][a-z0-9+#.]{2,}", text.lower()) if w not in STOP}

def lexical(a: str, b: str) -> float:
    A, B = tokens(a), tokens(b)
    if not A or not B:
        return 0.0
    return len(A & B) / math.sqrt(len(A) * len(B))

def metrics(labels, scores, threshold):
    pred = [1 if s >= threshold else 0 for s in scores]
    tp = sum(p == 1 and y == 1 for p, y in zip(pred, labels))
    fp = sum(p == 1 and y == 0 for p, y in zip(pred, labels))
    fn = sum(p == 0 and y == 1 for p, y in zip(pred, labels))
    tn = sum(p == 0 and y == 0 for p, y in zip(pred, labels))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    accuracy = (tp + tn) / len(labels)
    return {"threshold": threshold, "precision": precision, "recall": recall, "f1": f1, "accuracy": accuracy,
            "tp": tp, "fp": fp, "fn": fn, "tn": tn}

def best_threshold(labels, scores):
    candidates = sorted(set(round(x, 4) for x in scores))
    best = None
    for t in candidates:
        row = metrics(labels, scores, t)
        if best is None or (row["f1"], row["accuracy"]) > (best["f1"], best["accuracy"]):
            best = row
    return best

def main():
    rows = json.loads(DATA.read_text())
    labels = [r["label"] for r in rows]
    lexical_scores = [lexical(r["requirement"], r["evidence"]) for r in rows]

    from sentence_transformers import SentenceTransformer
    import numpy as np

    model = SentenceTransformer(MODEL_NAME)
    req = model.encode([r["requirement"] for r in rows], normalize_embeddings=True)
    ev = model.encode([r["evidence"] for r in rows], normalize_embeddings=True)
    semantic_scores = np.sum(req * ev, axis=1).tolist()
    hybrid_scores = [
        0.82 * sem + 0.18 * min(1.0, lex * 2.2)
        for sem, lex in zip(semantic_scores, lexical_scores)
    ]

    result = {
        "dataset_size": len(rows),
        "positive_pairs": sum(labels),
        "negative_pairs": len(labels) - sum(labels),
        "model": MODEL_NAME,
        "lexical": best_threshold(labels, lexical_scores),
        "semantic": best_threshold(labels, semantic_scores),
        "hybrid": best_threshold(labels, hybrid_scores),
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
