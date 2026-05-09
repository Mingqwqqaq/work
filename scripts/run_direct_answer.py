"""Run the Qwen2.5-VL Direct Answer baseline on a JSONL sample file."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from prcv.direct_answer import (
    build_direct_answer_batch_record,
    load_direct_answer_samples,
)
from prcv.smoke_helpers import (
    append_jsonl,
    build_qwen_vl_messages,
    trim_generated_token_ids,
)


DEFAULT_MODEL = "Qwen/Qwen2.5-VL-7B-Instruct"
DEFAULT_INPUT = "data/debug/smoke_samples.jsonl"
DEFAULT_OUT = "runs/debug/direct_answer.jsonl"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=DEFAULT_INPUT, help="Input JSONL file.")
    parser.add_argument("--out", default=DEFAULT_OUT, help="Output JSONL file.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="HF model id or path.")
    parser.add_argument("--max-new-tokens", type=int, default=256)
    return parser.parse_args()


def validate_sample_images(samples: list[dict[str, object]]) -> None:
    for sample in samples:
        image = str(sample["image"])
        if image.startswith(("http://", "https://")):
            continue
        if not Path(image).exists():
            raise FileNotFoundError(f"Image not found for {sample['sample_id']}: {image}")


def main() -> None:
    args = parse_args()
    samples = load_direct_answer_samples(args.input)
    validate_sample_images(samples)

    import torch
    from qwen_vl_utils import process_vision_info
    from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration

    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        args.model,
        torch_dtype=torch.bfloat16,
        device_map="auto",
    )
    processor = AutoProcessor.from_pretrained(args.model)

    for index, sample in enumerate(samples, start=1):
        start = time.time()
        messages = build_qwen_vl_messages(
            image=str(sample["image"]),
            question=str(sample["question"]),
        )
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
        prediction = processor.batch_decode(
            trimmed_ids,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False,
        )[0]
        record = build_direct_answer_batch_record(
            sample=sample,
            model=args.model,
            prediction=prediction,
            latency_sec=time.time() - start,
        )
        append_jsonl(args.out, record)
        print(f"[{index}/{len(samples)}] {sample['sample_id']}: {prediction}")

    print(f"\nSaved {len(samples)} records to {args.out}")


if __name__ == "__main__":
    main()
