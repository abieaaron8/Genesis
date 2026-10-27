"""Evaluate a saved DistilBERT WELFake checkpoint on the held-out test set."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import torch
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score
from torch.utils.data import DataLoader
from tqdm.auto import tqdm
from transformers import AutoModelForSequenceClassification, AutoTokenizer

try:
    from .dataset import WELFakeDataset
except ImportError:  # Supports running this file directly from the training directory.
    from dataset import WELFakeDataset


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-dir", required=True)
    parser.add_argument("--test-path", help="Optional test CSV; defaults to model-dir/test.csv")
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--max-length", type=int, default=256)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    model_dir = Path(args.model_dir)
    test_path = Path(args.test_path) if args.test_path else model_dir / "test.csv"
    if not test_path.is_file():
        raise FileNotFoundError(f"Test split not found: {test_path}")

    frame = pd.read_csv(test_path)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    model = AutoModelForSequenceClassification.from_pretrained(model_dir).to(device)
    model.eval()
    loader = DataLoader(
        WELFakeDataset(frame["text"], frame["label"], tokenizer, args.max_length),
        batch_size=args.batch_size,
        shuffle=False,
        pin_memory=device.type == "cuda",
    )
    labels, predictions = [], []
    with torch.inference_mode():
        for batch in tqdm(loader, desc="test"):
            batch = {key: value.to(device) for key, value in batch.items()}
            output = model(**batch)
            predictions.extend(output.logits.argmax(dim=-1).cpu().numpy())
            labels.extend(batch["labels"].cpu().numpy())

    metrics = {
        "accuracy": float(accuracy_score(labels, predictions)),
        "precision": float(precision_score(labels, predictions, zero_division=0)),
        "recall": float(recall_score(labels, predictions, zero_division=0)),
        "f1": float(f1_score(labels, predictions, zero_division=0)),
        "confusion_matrix": confusion_matrix(labels, predictions, labels=[0, 1]).tolist(),
    }
    print(json.dumps(metrics, indent=2))
    with (model_dir / "test_metrics.json").open("w", encoding="utf-8") as file:
        json.dump(metrics, file, indent=2)


if __name__ == "__main__":
    main()
