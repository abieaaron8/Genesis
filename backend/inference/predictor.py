"""Public, framework-agnostic prediction interface.

This module deliberately contains no FastAPI or frontend integration. Service
layers can depend on ``NewsPredictor`` while the model lifecycle remains
encapsulated in ``backend.services.model_service``.
"""

from __future__ import annotations

from backend.services.model_service import ModelService, PredictionResult, get_model_service


class NewsPredictor:
    """Small application-facing facade over the singleton model service."""

    def __init__(self, model_service: ModelService | None = None) -> None:
        self._model_service = model_service or get_model_service()

    def predict(self, text: str) -> PredictionResult:
        """Classify a complete title/body string."""

        return self._model_service.predict(text)

    def predict_article(self, title: str, body: str) -> PredictionResult:
        """Classify an article while preserving title context."""

        if not isinstance(title, str) or not isinstance(body, str):
            raise TypeError("title and body must both be strings.")
        return self.predict(f"{title.strip()} {body.strip()}".strip())
