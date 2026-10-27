"""Text normalization and reproducible train/validation/test splitting."""

from __future__ import annotations

import re
import random
from typing import Any

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split


def combine_article_fields(frame: pd.DataFrame) -> pd.Series:
    """Combine title and article body while preserving useful title context."""

    return (
        frame["title"].fillna("").astype(str).str.strip()
        + " "
        + frame["text"].fillna("").astype(str).str.strip()
    ).str.strip()


def normalize_text(text: str) -> str:
    """Apply conservative normalization without removing linguistic signal.

    DistilBERT's tokenizer handles punctuation and casing well, so this avoids
    aggressive stemming or stop-word removal that could hide misinformation
    patterns such as emphatic punctuation, numbers, and named entities.
    """

    text = re.sub(r"\s+", " ", str(text)).strip()
    return text


def prepare_frame(frame: pd.DataFrame) -> pd.DataFrame:
    """Create the model text field and remove unusable examples."""

    prepared = frame.copy()
    prepared["text"] = combine_article_fields(prepared).map(normalize_text)
    prepared = prepared[prepared["text"].str.len() > 0].copy()
    prepared["label"] = prepared["label"].astype(int)
    return prepared[["text", "label"]].reset_index(drop=True)


def set_seed(seed: int) -> None:
    """Seed Python, NumPy, and PyTorch for repeatable experiments."""

    random.seed(seed)
    np.random.seed(seed)


def split_dataset(
    frame: pd.DataFrame,
    validation_size: float = 0.1,
    test_size: float = 0.1,
    seed: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Return stratified train, validation, and test dataframes."""

    if validation_size <= 0 or test_size <= 0 or validation_size + test_size >= 1:
        raise ValueError("validation_size and test_size must be positive and sum to < 1.")

    train_frame, held_out = train_test_split(
        frame,
        test_size=validation_size + test_size,
        random_state=seed,
        stratify=frame["label"],
    )
    relative_test_size = test_size / (validation_size + test_size)
    validation_frame, test_frame = train_test_split(
        held_out,
        test_size=relative_test_size,
        random_state=seed,
        stratify=held_out["label"],
    )
    return (
        train_frame.reset_index(drop=True),
        validation_frame.reset_index(drop=True),
        test_frame.reset_index(drop=True),
    )


def class_distribution(frame: pd.DataFrame) -> dict[str, Any]:
    """Return JSON-serializable class counts for experiment metadata."""

    counts = frame["label"].value_counts().sort_index().to_dict()
    return {str(label): int(count) for label, count in counts.items()}
