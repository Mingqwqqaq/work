"""Helpers for Direct Answer baseline runs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REQUIRED_SAMPLE_FIELDS = ("sample_id", "image", "question")


def load_direct_answer_samples(path: str | Path) -> list[dict[str, Any]]:
    """Load Direct Answer samples from JSONL and validate core fields."""
    input_path = Path(path)
    samples: list[dict[str, Any]] = []
    with input_path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            sample = json.loads(stripped)
            for field in REQUIRED_SAMPLE_FIELDS:
                if field not in sample:
                    raise ValueError(
                        f"{input_path}:{line_no} missing required field '{field}'"
                    )
            samples.append(sample)
    return samples


def build_direct_answer_batch_record(
    *,
    sample: dict[str, Any],
    model: str,
    prediction: str,
    latency_sec: float,
) -> dict[str, Any]:
    """Return one stable JSONL output record for Direct Answer baseline runs."""
    return {
        "sample_id": sample["sample_id"],
        "model": model,
        "variant": "direct_answer",
        "image": sample["image"],
        "question": sample["question"],
        "prediction": prediction,
        "ground_truth": sample.get("answer"),
        "latency_sec": round(latency_sec, 3),
    }
