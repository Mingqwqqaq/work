"""Small helpers for the Qwen2.5-VL smoke-test CLI."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable


def build_qwen_vl_messages(image: str, question: str) -> list[dict[str, Any]]:
    """Build the chat message format expected by Qwen-VL processors."""
    return [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": image},
                {"type": "text", "text": question},
            ],
        }
    ]


def trim_generated_token_ids(
    input_ids: Iterable[Iterable[int]],
    generated_ids: Iterable[Iterable[int]],
) -> list[list[int]]:
    """Remove prompt tokens from generated token ids for batch decoding."""
    return [
        list(output_ids)[len(list(prompt_ids)) :]
        for prompt_ids, output_ids in zip(input_ids, generated_ids)
    ]


def build_direct_answer_record(
    *,
    model: str,
    image: str,
    question: str,
    answer: str,
    latency_sec: float,
) -> dict[str, Any]:
    """Return the stable JSONL schema for direct-answer smoke results."""
    return {
        "model": model,
        "variant": "direct_answer_smoke",
        "image": image,
        "question": question,
        "answer": answer,
        "latency_sec": round(latency_sec, 3),
    }


def append_jsonl(path: str | Path, record: dict[str, Any]) -> None:
    """Append one UTF-8 JSON record and create the parent directory."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
