import json

import pytest

from prcv.direct_answer import (
    build_direct_answer_batch_record,
    load_direct_answer_samples,
)


def test_load_direct_answer_samples_reads_jsonl_and_ignores_blank_lines(tmp_path):
    input_path = tmp_path / "samples.jsonl"
    input_path.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "sample_id": "debug_001",
                        "image": "data/debug/test.png",
                        "question": "What is in this image?",
                        "answer": "cat",
                    }
                ),
                "",
                json.dumps(
                    {
                        "sample_id": "debug_002",
                        "image": "data/debug/test.png",
                        "question": "What color is the cat?",
                    }
                ),
            ]
        ),
        encoding="utf-8",
    )

    samples = load_direct_answer_samples(input_path)

    assert samples == [
        {
            "sample_id": "debug_001",
            "image": "data/debug/test.png",
            "question": "What is in this image?",
            "answer": "cat",
        },
        {
            "sample_id": "debug_002",
            "image": "data/debug/test.png",
            "question": "What color is the cat?",
        },
    ]


def test_load_direct_answer_samples_requires_core_fields(tmp_path):
    input_path = tmp_path / "bad.jsonl"
    input_path.write_text(
        json.dumps({"sample_id": "bad_001", "image": "data/debug/test.png"}),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="missing required field 'question'"):
        load_direct_answer_samples(input_path)


def test_build_direct_answer_batch_record_has_stable_schema():
    record = build_direct_answer_batch_record(
        sample={
            "sample_id": "debug_001",
            "image": "data/debug/test.png",
            "question": "What is in this image?",
            "answer": "cat",
        },
        model="/root/autodl-tmp/models/Qwen2.5-VL-7B-Instruct",
        prediction="The image shows a cat.",
        latency_sec=2.71828,
    )

    assert record == {
        "sample_id": "debug_001",
        "model": "/root/autodl-tmp/models/Qwen2.5-VL-7B-Instruct",
        "variant": "direct_answer",
        "image": "data/debug/test.png",
        "question": "What is in this image?",
        "prediction": "The image shows a cat.",
        "ground_truth": "cat",
        "latency_sec": 2.718,
    }
