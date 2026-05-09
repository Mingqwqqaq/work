import json

from prcv.smoke_helpers import (
    append_jsonl,
    build_direct_answer_record,
    build_qwen_vl_messages,
    trim_generated_token_ids,
)


def test_build_qwen_vl_messages_uses_single_image_and_question():
    messages = build_qwen_vl_messages("data/debug/test.jpg", "What is shown?")

    assert messages == [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": "data/debug/test.jpg"},
                {"type": "text", "text": "What is shown?"},
            ],
        }
    ]


def test_trim_generated_token_ids_removes_prompt_prefix():
    trimmed = trim_generated_token_ids(
        input_ids=[[10, 11, 12], [20, 21]],
        generated_ids=[[10, 11, 12, 99, 100], [20, 21, 88]],
    )

    assert trimmed == [[99, 100], [88]]


def test_build_direct_answer_record_has_stable_schema():
    record = build_direct_answer_record(
        model="Qwen/Qwen2.5-VL-7B-Instruct",
        image="data/debug/test.jpg",
        question="What is shown?",
        answer="A car.",
        latency_sec=1.23456,
    )

    assert record == {
        "model": "Qwen/Qwen2.5-VL-7B-Instruct",
        "variant": "direct_answer_smoke",
        "image": "data/debug/test.jpg",
        "question": "What is shown?",
        "answer": "A car.",
        "latency_sec": 1.235,
    }


def test_append_jsonl_creates_parent_and_appends_utf8_json(tmp_path):
    out_path = tmp_path / "runs" / "debug" / "smoke.jsonl"

    append_jsonl(out_path, {"answer": "red car"})
    append_jsonl(out_path, {"answer": "blue car"})

    lines = out_path.read_text(encoding="utf-8").splitlines()
    assert [json.loads(line) for line in lines] == [
        {"answer": "red car"},
        {"answer": "blue car"},
    ]
