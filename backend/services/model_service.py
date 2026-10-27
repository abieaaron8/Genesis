"""Thread-safe lazy lifecycle and prediction service for Genesis DistilBERT."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from threading import RLock

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

DEFAULT_MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "genesis_distilbert"
DEFAULT_MAX_LENGTH = 256


class ModelServiceError(RuntimeError):
    """Base exception for expected model lifecycle and inference failures."""


class ModelNotFoundError(ModelServiceError):
    """Raised when prediction is requested before a trained model exists."""


class ModelLoadError(ModelServiceError):
    """Raised when tokenizer/model loading fails."""


class PredictionError(ModelServiceError):
    """Raised when input validation or model inference fails."""


@dataclass(frozen=True)
class PredictionResult:
    """Stable output contract for one news classification request."""

    label: str
    confidence: float
    probabilities: dict[str, float]
    device: str

    def as_dict(self) -> dict[str, object]:
        return {
            "prediction": self.label,
            "label": self.label,
            "confidence": self.confidence,
            "probabilities": self.probabilities,
            "device": self.device,
        }


@dataclass(frozen=True)
class ModelRuntime:
    """Immutable runtime metadata exposed for diagnostics."""

    model_path: str
    device: str
    max_length: int


class ModelService:
    """Lazily load one model/tokenizer pair and reuse it across requests.

    ``RLock`` protects initialization and replacement so concurrent first
    requests cannot load duplicate model copies. Inference itself is safe for
    the read-only ``eval`` model; the lock is also held during prediction to
    provide conservative safety for shared CUDA contexts and mutable tokenizer
    implementations.
    """

    def __init__(
        self,
        model_path: str | Path = DEFAULT_MODEL_PATH,
        max_length: int = DEFAULT_MAX_LENGTH,
    ) -> None:
        if max_length < 8:
            raise ValueError("max_length must be at least 8.")
        self._model_path = Path(model_path)
        self._max_length = max_length
        self._device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )
        self._lock = RLock()
        self._tokenizer = None
        self._model = None

    @property
    def runtime(self) -> ModelRuntime:
        """Return runtime metadata without triggering model loading."""

        return ModelRuntime(
            model_path=str(self._model_path),
            device=str(self._device),
            max_length=self._max_length,
        )

    @property
    def is_loaded(self) -> bool:
        with self._lock:
            return self._model is not None and self._tokenizer is not None

    def _load_locked(self) -> None:
        if self._model is not None and self._tokenizer is not None:
            return
        if not self._model_path.is_dir():
            raise ModelNotFoundError(
                f"Trained model directory does not exist: {self._model_path}"
            )
        required_files = ("config.json", "tokenizer_config.json", "model.safetensors")
        missing = [name for name in required_files if not (self._model_path / name).is_file()]
        if missing:
            raise ModelNotFoundError(
                f"Model directory is incomplete ({', '.join(missing)} missing): "
                f"{self._model_path}"
            )
        try:
            tokenizer = AutoTokenizer.from_pretrained(self._model_path, local_files_only=True)
            model = AutoModelForSequenceClassification.from_pretrained(
                self._model_path, local_files_only=True
            )
            model.to(self._device)
            model.eval()
        except Exception as error:
            raise ModelLoadError(
                f"Unable to load model from {self._model_path}: {error}"
            ) from error
        self._tokenizer = tokenizer
        self._model = model

    def load(self) -> ModelRuntime:
        """Load the model on first use and return runtime metadata."""

        with self._lock:
            self._load_locked()
            return self.runtime

    def predict(self, text: str) -> PredictionResult:
        """Return label probabilities for one non-empty article string."""

        if not isinstance(text, str):
            raise PredictionError("text must be a string.")
        text = " ".join(text.split())
        if not text:
            raise PredictionError("text must contain at least one non-whitespace character.")

        with self._lock:
            self._load_locked()
            assert self._model is not None
            assert self._tokenizer is not None
            try:
                encoded = self._tokenizer(
                    text,
                    return_tensors="pt",
                    truncation=True,
                    max_length=self._max_length,
                )
                encoded = {key: value.to(self._device) for key, value in encoded.items()}
                with torch.inference_mode():
                    probabilities = torch.softmax(self._model(**encoded).logits, dim=-1)[0]
                label_id = int(probabilities.argmax().item())
                id2label = self._model.config.id2label or {}
                label = str(id2label.get(label_id, label_id)).upper()
                scores = {
                    str(id2label.get(index, index)).upper(): round(float(score), 6)
                    for index, score in enumerate(probabilities)
                }
                return PredictionResult(
                    label=label,
                    confidence=round(float(probabilities[label_id]), 6),
                    probabilities=scores,
                    device=str(self._device),
                )
            except ModelServiceError:
                raise
            except Exception as error:
                raise PredictionError(f"Inference failed: {error}") from error


_SERVICE: ModelService | None = None
_SERVICE_LOCK = RLock()


def get_model_service() -> ModelService:
    """Return the process-wide, lazily initialized service singleton."""

    global _SERVICE
    with _SERVICE_LOCK:
        if _SERVICE is None:
            configured_path = os.getenv("GENESIS_MODEL_PATH")
            try:
                configured_length = int(
                    os.getenv("GENESIS_MAX_LENGTH", str(DEFAULT_MAX_LENGTH))
                )
            except ValueError as error:
                raise ModelServiceError(
                    "GENESIS_MAX_LENGTH must be an integer."
                ) from error
            _SERVICE = ModelService(configured_path or DEFAULT_MODEL_PATH, configured_length)
        return _SERVICE
