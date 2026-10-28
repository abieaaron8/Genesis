# Machine Learning

## Model status

Genesis includes a trained DistilBERT classifier at `backend/models/genesis_distilbert/` and modular training code under `backend/training/`.

## Training

`dataset.py` loads WELFake data and wraps it for PyTorch. `preprocess.py` cleans text, sets seeds, and creates train/validation/test splits. `train.py` fine-tunes DistilBERT with GPU support, early stopping, checkpointing, and best-model export. `evaluate.py` calculates accuracy, precision, recall, F1, and confusion matrix. `predict.py` provides standalone inference.

## Inference

`services/model_service.py` is a lazy, thread-safe singleton. It loads tokenizer/config/model once, chooses CUDA when available, otherwise CPU, and returns label, confidence, class probabilities, and device. `/api/model/predict` exposes this signal directly; `/api/verify` includes it as part of the full response.

## Role in verification

DistilBERT is one signal in a broader evidence pipeline. It can influence retrieval context and is displayed to the user, but evidence retrieval, agent stance analysis, judge logic, known-fact rules, and verdict hardening also affect the final verdict.

## Limitations

WELFake distribution may not represent current events or every domain. A classifier can learn dataset artifacts, cannot independently validate fresh sources, and may be overconfident. Provider outages and unrelated evidence can degrade the final result even when model inference succeeds.
