"""Run a single-image Qwen2.5-VL Direct Answer smoke test.

Heavy ML imports stay inside the runtime path so local unit tests can run
without installing the model stack.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from prcv.smoke_helpers import (
    append_jsonl,
    build_direct_answer_record,
    build_qwen_vl_messages,
    trim_generated_token_ids,
)


DEFAULT_MODEL = "Qwen/Qwen2.5-VL-7B-Instruct"
DEFAULT_OUT = "runs/debug/direct_answer_smoke.jsonl"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", required=True, help="Path or URL to one image.")
    parser.add_argument("--question", required=True, help="Question about the image.")
    parser.add_argument("--out", default=DEFAULT_OUT, help="JSONL output path.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="HF model id or path.")
    parser.add_argument("--max-new-tokens", type=int, default=256)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    image_path = Path(args.image)
    if not args.image.startswith(("http://", "https://")) and not image_path.exists():
        raise FileNotFoundError(f"Image not found: {args.image}")

    import torch
    from qwen_vl_utils import process_vision_info
    from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration

    start = time.time()
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        args.model,
        torch_dtype=torch.bfloat16,
        device_map="auto",
    )
    processor = AutoProcessor.from_pretrained(args.model)

    messages = build_qwen_vl_messages(args.image, args.question)
    prompt = processor.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )
    image_inputs, video_inputs = process_vision_info(messages)
    inputs = processor(
        text=[prompt],
        images=image_inputs,
        videos=video_inputs,
        padding=True,
        return_tensors="pt",
    ).to(model.device)

    with torch.no_grad():
        generated_ids = model.generate(
            **inputs,
            max_new_tokens=args.max_new_tokens,
            do_sample=False,
        )

    trimmed_ids = trim_generated_token_ids(inputs.input_ids, generated_ids)
    answer = processor.batch_decode(
        trimmed_ids,
        skip_special_tokens=True,
        clean_up_tokenization_spaces=False,
    )[0]

    record = build_direct_answer_record(
        model=args.model,
        image=args.image,
        question=args.question,
        answer=answer,
        latency_sec=time.time() - start,
    )
    append_jsonl(args.out, record)

    print(answer)
    print(f"\nSaved to {args.out}")


if __name__ == "__main__":
    main()
