"""Dataset utilities for the WELFake binary classification task.

The module intentionally keeps data loading separate from tokenization and
training so that the same validated examples can be reused by training,
evaluation, and prediction tooling.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Sequence
from urllib.request import Request, urlopen

import pandas as pd
import torch
from torch.utils.data import Dataset
from transformers import PreTrainedTokenizerBase


TEXT_COLUMNS = ("title", "text")
LABEL_COLUMN = "label"
WELFAKE_URLS = (
    "https://raw.githubusercontent.com/samriddhisingh01/datasets/main/WELFake_Dataset.csv",
)


def download_welfake_dataset(data_path: str | Path) -> Path:
    """Download WELFake when it is absent and return the local CSV path."""

    path = Path(data_path)
    if path.is_file():
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(path.suffix + ".part")
    errors = []
    for url in WELFAKE_URLS:
        try:
            request = Request(url, headers={"User-Agent": "Genesis-ML-Pipeline/1.0"})
            with urlopen(request, timeout=120) as response, temporary_path.open("wb") as output:
                while chunk := response.read(1024 * 1024):
                    output.write(chunk)
            temporary_path.replace(path)
            return path
        except Exception as error:  # Try the next official mirror and preserve the cause.
            errors.append(f"{url}: {error}")
            if temporary_path.exists():
                temporary_path.unlink()
    raise RuntimeError(
        "Unable to download WELFake automatically. Tried:\n" + "\n".join(errors)
    )


def load_welfake_csv(data_path: str | Path) -> pd.DataFrame:
    """Load and validate a WELFake CSV file.

    WELFake files commonly contain ``title``, ``text`` and ``label`` columns.
    A missing title or body is accepted and replaced with an empty string, but
    the label column must be present because this is a supervised task.
    """

    path = download_welfake_dataset(data_path)

    frame = pd.read_csv(path)
    missing_columns = [column for column in (LABEL_COLUMN,) if column not in frame]
    if missing_columns:
        raise ValueError(
            f"Dataset is missing required columns: {', '.join(missing_columns)}"
        )

    for column in TEXT_COLUMNS:
        if column not in frame:
            frame[column] = ""

    frame["title"] = frame["title"].fillna("").astype(str)
    frame["text"] = frame["text"].fillna("").astype(str)
    frame[LABEL_COLUMN] = pd.to_numeric(frame[LABEL_COLUMN], errors="raise")

    invalid_labels = set(frame[LABEL_COLUMN].unique()) - {0, 1}
    if invalid_labels:
        raise ValueError(
            f"Labels must be binary values 0 or 1; found {sorted(invalid_labels)}"
        )

    frame = frame[["title", "text", LABEL_COLUMN]].copy()
    frame = frame.drop_duplicates().reset_index(drop=True)
    if frame.empty:
        raise ValueError("The WELFake dataset contains no usable rows.")
    return frame


class WELFakeDataset(Dataset[dict[str, torch.Tensor]]):
    """PyTorch dataset that tokenizes WELFake examples on demand."""

    def __init__(
        self,
        texts: Sequence[str] | Iterable[str],
        labels: Sequence[int] | Iterable[int],
        tokenizer: PreTrainedTokenizerBase,
        max_length: int = 256,
    ) -> None:
        self.texts = list(texts)
        self.labels = [int(label) for label in labels]
        self.tokenizer = tokenizer
        self.max_length = max_length

        if len(self.texts) != len(self.labels):
            raise ValueError("texts and labels must have the same length.")
        if not self.texts:
            raise ValueError("A WELFakeDataset cannot be empty.")

    def __len__(self) -> int:
        return len(self.labels)

    def __getitem__(self, index: int) -> dict[str, torch.Tensor]:
        encoded = self.tokenizer(
            self.texts[index],
            truncation=True,
            max_length=self.max_length,
            padding="max_length",
            return_tensors="pt",
        )
        item = {key: value.squeeze(0) for key, value in encoded.items()}
        item["labels"] = torch.tensor(self.labels[index], dtype=torch.long)
        return item
