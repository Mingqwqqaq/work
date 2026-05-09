# PRCV Thinking-with-Images Experiments

This repository contains the first-stage experiment scaffold for the PRCV
thinking-with-images project. The current target is a minimal
Qwen2.5-VL-7B Direct Answer smoke test that can be edited locally, pushed to
GitHub, and run on AutoDL/SeetaCloud.

## Stage 1: Qwen2.5-VL smoke test

Create and activate a Python environment on the remote machine:

```bash
conda create -n prcv python=3.10 -y
conda activate prcv
```

Install a PyTorch build compatible with RTX 5090/Blackwell:

```bash
pip uninstall -y torch torchvision torchaudio
pip install --index-url https://download.pytorch.org/whl/cu128 torch torchvision torchaudio
```

Install project dependencies:

```bash
pip install -r requirements.txt
pip install -e .
```

If Hugging Face downloads are slow from the remote machine:

```bash
export HF_ENDPOINT=https://hf-mirror.com
```

Run a single-image smoke test:

```bash
python scripts/smoke_qwen25vl.py \
  --image data/debug/test.png \
  --question "What is in this image?"
```

The output is appended to:

```text
runs/debug/direct_answer_smoke.jsonl
```

## Local tests

```bash
python -m pytest
```
