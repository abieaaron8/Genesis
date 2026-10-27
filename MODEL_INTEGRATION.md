# Genesis DistilBERT Model Integration

## Overview

The trained classifier is stored at:

```text
backend/models/genesis_distilbert/
```

The FastAPI backend uses `backend/services/model_service.py` as the single
model lifecycle owner. The existing verification workflow remains responsible
for retrieval, evidence analysis, and agent reasoning. DistilBERT is now
available both as an independent prediction endpoint and as an additional
prediction attached to `/api/verify` responses.

## Architecture

```text
FastAPI route
    ↓
_model_prediction()
    ↓
get_model_service()  ── process-wide singleton
    ↓
ModelService.predict()
    ├── lazy tokenizer loading
    ├── lazy DistilBERT loading
    ├── CUDA when available
    ├── CPU fallback
    └── torch.inference_mode()
    ↓
prediction + confidence + class probabilities
```

## Loading and concurrency

- Importing the service does not load model weights.
- `get_model_service()` creates one process-wide `ModelService`.
- An `RLock` protects singleton creation and first-load initialization.
- The service checks that `config.json`, `tokenizer_config.json`, and
  `model.safetensors` exist before loading.
- Hugging Face loading uses `local_files_only=True`, so inference does not
  download or replace the trained artifact.
- The model is moved to CUDA when available; otherwise it runs on CPU.
- The loaded model is placed in evaluation mode and inference uses
  `torch.inference_mode()`.

## Prediction contract

`POST /api/model/predict` accepts:

```json
{
  "claim": "Example news text"
}
```

Successful responses contain:

```json
{
  "success": true,
  "prediction": "REAL",
  "label": "REAL",
  "confidence": 0.91,
  "probabilities": {
    "REAL": 0.91,
    "FAKE": 0.09
  },
  "device": "cuda"
}
```

The same object is included in the `model_prediction` field of
`POST /api/verify` responses. This is supplementary to the existing
retrieval-and-agent verdict and does not replace that verdict.

## Error handling

- Missing or incomplete artifacts raise `ModelNotFoundError`.
- Transformer/tokenizer loading failures raise `ModelLoadError`.
- Invalid or empty text raises `PredictionError`.
- The standalone model endpoint returns HTTP 503 when the classifier is
  unavailable.
- The main `/api/verify` pipeline preserves its existing behavior when model
  inference is unavailable; it returns `model_prediction: null` and an
  explanatory `model_prediction_error` field instead of fabricating a result.

## Configuration

- Default artifact path: `backend/models/genesis_distilbert`
- Optional override: `GENESIS_MODEL_PATH`
- Optional sequence length override: `GENESIS_MAX_LENGTH`
