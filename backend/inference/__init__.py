"""Inference interfaces for the Genesis fake-news classifier."""

from .predictor import NewsPredictor, PredictionResult

__all__ = ["NewsPredictor", "PredictionResult"]
