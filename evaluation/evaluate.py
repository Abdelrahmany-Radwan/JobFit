"""JobFit retrieval evaluation.

Methodology:
- benchmark examples carry an explicit split: "dev" or "test"
- decision thresholds are selected on dev only
- final metrics are reported on the untouched test split
- lexical, MiniLM semantic, and hybrid scorers use the same examples
- latency is measured separately from model loading

This is a small, curated product benchmark—not a claim of general hiring accuracy.
"""
from __future__ import annotations

import json
import math
import re
import statistics
import time
from pathlib import Path

DATA = Path(__file__).with_name("benchmark.json")
OUT = Path(__file__).with_name("results.json")
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
STOP = set("the a an and or with for in of to on by as from is are be you your our their this that will have has using use experience strong skills".split())


def tokens(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z][a-z0-9+#.]{2,}", text.lower()) if w not in STOP}


def lexical(a: str, b: str) -> float:
    left, right = tokens(a), tokens(b)
    if not left or not right:
        return 0.0
    return len(left & right) / math.sqrt(len(left) * len(right))


def classification_metrics(labels, scores, threshold):
    pred = [int(score >= threshold) for score in scores]
    tp = sum(p == 1 and y == 1 for p, y in zip(pred, labels))
    fp = sum(p == 1 and y == 0 for p, y in zip(pred, labels))
    fn = sum(p == 0 and y == 1 for p, y in zip(pred, labels))
    tn = sum(p == 0 and y == 0 for p, y in zip(pred, labels))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    accuracy = (tp + tn) / len(labels) if labels else 0.0
    return {
        "threshold": round(threshold, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "accuracy": round(accuracy, 4),
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
    }


def choose_threshold(labels, scores):
    candidates = sorted(set([0.0, 1.0] + [round(score, 4) for score in scores]))
    rows = [classification_metrics(labels, scores, threshold) for threshold in candidates]
    return max(rows, key=lambda row: (row["f1"], row["accuracy"], row["precision"]))


def evaluate_method(dev_rows, test_rows, dev_scores, test_scores):
    selected = choose_threshold([row["label"] for row in dev_rows], dev_scores)
    test = classification_metrics([row["label"] for row in test_rows], test_scores, selected["threshold"])
    return {"selected_on_dev": selected, "test": test}


def main():
    rows = json.loads(DATA.read_text())
    dev_rows = [row for row in rows if row["split"] == "dev"]
    test_rows = [row for row in rows if row["split"] == "test"]
    if not dev_rows or not test_rows:
        raise ValueError("benchmark.json must contain both dev and test examples")

    from sentence_transformers import SentenceTransformer
    import numpy as np

    model = SentenceTransformer(MODEL_NAME)

    def score_rows(items):
        requirements = [row["requirement"] for row in items]
        evidence = [row["evidence"] for row in items]

        lexical_start = time.perf_counter()
        lex = [lexical(a, b) for a, b in zip(requirements, evidence)]
        lexical_ms = (time.perf_counter() - lexical_start) * 1000 / len(items)

        semantic_times = []
        semantic = None
        for _ in range(3):
            start = time.perf_counter()
            req = model.encode(requirements, normalize_embeddings=True)
            ev = model.encode(evidence, normalize_embeddings=True)
            semantic = np.sum(req * ev, axis=1).tolist()
            semantic_times.append((time.perf_counter() - start) * 1000 / len(items))

        hybrid = [0.82 * sem + 0.18 * min(1.0, lx * 2.2) for sem, lx in zip(semantic, lex)]
        return lex, semantic, hybrid, lexical_ms, statistics.median(semantic_times)

    dev_lex, dev_sem, dev_hyb, _, _ = score_rows(dev_rows)
    test_lex, test_sem, test_hyb, lexical_ms, semantic_ms = score_rows(test_rows)

    result = {
        "methodology": "threshold selected on dev; metrics reported on held-out test",
        "dataset": {
            "total": len(rows),
            "dev": len(dev_rows),
            "test": len(test_rows),
            "source": "curated synthetic requirement/evidence pairs for product regression testing",
        },
        "model": MODEL_NAME,
        "latency_ms_per_pair": {
            "lexical": round(lexical_ms, 3),
            "semantic_median": round(semantic_ms, 3),
            "note": "CPU GitHub Actions runner; excludes model download/load",
        },
        "lexical": evaluate_method(dev_rows, test_rows, dev_lex, test_lex),
        "semantic": evaluate_method(dev_rows, test_rows, dev_sem, test_sem),
        "hybrid": evaluate_method(dev_rows, test_rows, dev_hyb, test_hyb),
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
