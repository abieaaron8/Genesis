"""Train DistilBERT on WELFake and persist a complete evaluation report."""

from __future__ import annotations

import argparse
import json
import logging
import time
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from torch.optim import AdamW
from torch.utils.data import DataLoader
from tqdm.auto import tqdm
from transformers import AutoModelForSequenceClassification, AutoTokenizer, get_linear_schedule_with_warmup

try:
    from .dataset import WELFakeDataset, load_welfake_csv
    from .preprocess import class_distribution, prepare_frame, set_seed, split_dataset
except ImportError:
    from dataset import WELFakeDataset, load_welfake_csv
    from preprocess import class_distribution, prepare_frame, set_seed, split_dataset

LOGGER = logging.getLogger("genesis.training")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-path", default="backend/data/WELFake_Dataset.csv")
    parser.add_argument("--output-dir", default="backend/models/genesis_distilbert")
    parser.add_argument("--model-name", default="distilbert-base-uncased")
    parser.add_argument("--max-length", type=int, default=256)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--learning-rate", type=float, default=2e-5)
    parser.add_argument("--weight-decay", type=float, default=0.01)
    parser.add_argument("--warmup-ratio", type=float, default=0.1)
    parser.add_argument("--patience", type=int, default=2)
    parser.add_argument("--validation-size", type=float, default=0.1)
    parser.add_argument("--test-size", type=float, default=0.1)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--num-workers", type=int, default=0)
    return parser.parse_args()


def get_device() -> torch.device:
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def compute_metrics(labels: np.ndarray, predictions: np.ndarray) -> dict[str, float]:
    return {
        "accuracy": float(accuracy_score(labels, predictions)),
        "precision": float(precision_score(labels, predictions, zero_division=0)),
        "recall": float(recall_score(labels, predictions, zero_division=0)),
        "f1": float(f1_score(labels, predictions, zero_division=0)),
    }


def run_epoch(model, loader, optimizer, scheduler, device, training: bool):
    model.train(training)
    total_loss = 0.0
    labels, predictions = [], []
    for batch in tqdm(loader, desc="train" if training else "validation", leave=False):
        batch = {key: value.to(device) for key, value in batch.items()}
        with torch.set_grad_enabled(training):
            output = model(**batch)
        if training:
            output.loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            scheduler.step()
            optimizer.zero_grad(set_to_none=True)
        total_loss += output.loss.item() * batch["labels"].size(0)
        predictions.extend(output.logits.argmax(dim=-1).detach().cpu().numpy())
        labels.extend(batch["labels"].detach().cpu().numpy())
    return total_loss / len(loader.dataset), compute_metrics(np.asarray(labels), np.asarray(predictions))


def evaluate_model(model, loader, device):
    model.eval()
    total_loss = 0.0
    labels, predictions = [], []
    with torch.inference_mode():
        for batch in tqdm(loader, desc="test", leave=False):
            batch = {key: value.to(device) for key, value in batch.items()}
            output = model(**batch)
            total_loss += output.loss.item() * batch["labels"].size(0)
            predictions.extend(output.logits.argmax(dim=-1).cpu().numpy())
            labels.extend(batch["labels"].cpu().numpy())
    metrics = compute_metrics(np.asarray(labels), np.asarray(predictions))
    metrics["loss"] = total_loss / len(loader.dataset)
    return metrics, confusion_matrix(labels, predictions, labels=[0, 1]).tolist()


def main() -> None:
    args = parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    if args.epochs < 1 or args.batch_size < 1 or args.max_length < 8:
        raise ValueError("epochs, batch-size, and max-length must be positive.")
    set_seed(args.seed)
    torch.manual_seed(args.seed)
    started_at = time.perf_counter()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    device = get_device()
    LOGGER.info("Using device: %s", device)

    frame = prepare_frame(load_welfake_csv(args.data_path))
    train_frame, validation_frame, test_frame = split_dataset(
        frame, args.validation_size, args.test_size, args.seed
    )
    for name, split in (("train", train_frame), ("validation", validation_frame), ("test", test_frame)):
        split.to_csv(output_dir / f"{name}.csv", index=False)

    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    model = AutoModelForSequenceClassification.from_pretrained(
        args.model_name,
        num_labels=2,
        id2label={0: "REAL", 1: "FAKE"},
        label2id={"REAL": 0, "FAKE": 1},
    ).to(device)
    datasets = {
        "train": WELFakeDataset(train_frame["text"], train_frame["label"], tokenizer, args.max_length),
        "validation": WELFakeDataset(validation_frame["text"], validation_frame["label"], tokenizer, args.max_length),
        "test": WELFakeDataset(test_frame["text"], test_frame["label"], tokenizer, args.max_length),
    }
    loaders = {
        name: DataLoader(
            dataset,
            batch_size=args.batch_size,
            shuffle=name == "train",
            num_workers=args.num_workers,
            pin_memory=device.type == "cuda",
        )
        for name, dataset in datasets.items()
    }
    optimizer = AdamW(model.parameters(), lr=args.learning_rate, weight_decay=args.weight_decay)
    total_steps = len(loaders["train"]) * args.epochs
    scheduler = get_linear_schedule_with_warmup(
        optimizer, int(total_steps * args.warmup_ratio), total_steps
    )
    best_f1, stale_epochs, history = -1.0, 0, []

    for epoch in range(1, args.epochs + 1):
        train_loss, train_metrics = run_epoch(
            model, loaders["train"], optimizer, scheduler, device, True
        )
        validation_loss, validation_metrics = run_epoch(
            model, loaders["validation"], optimizer, scheduler, device, False
        )
        record = {
            "epoch": epoch,
            "train_loss": train_loss,
            "validation_loss": validation_loss,
            "train": train_metrics,
            "validation": validation_metrics,
        }
        history.append(record)
        LOGGER.info("Epoch %d/%d: %s", epoch, args.epochs, record)
        if validation_metrics["f1"] > best_f1:
            best_f1, stale_epochs = validation_metrics["f1"], 0
            model.save_pretrained(output_dir)
            tokenizer.save_pretrained(output_dir)
            (output_dir / "best_metrics.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
        else:
            stale_epochs += 1
            if stale_epochs >= args.patience:
                LOGGER.info("Early stopping after %d stale epoch(s).", stale_epochs)
                break

    best_model = AutoModelForSequenceClassification.from_pretrained(output_dir).to(device)
    test_metrics, test_matrix = evaluate_model(best_model, loaders["test"], device)
    (output_dir / "training_history.json").write_text(json.dumps(history, indent=2), encoding="utf-8")
    (output_dir / "test_metrics.json").write_text(
        json.dumps({**test_metrics, "confusion_matrix": test_matrix}, indent=2),
        encoding="utf-8",
    )
    duration_seconds = time.perf_counter() - started_at
    metadata = {
        "model_name": args.model_name,
        "max_length": args.max_length,
        "batch_size": args.batch_size,
        "learning_rate": args.learning_rate,
        "weight_decay": args.weight_decay,
        "warmup_ratio": args.warmup_ratio,
        "epochs_requested": args.epochs,
        "epochs_completed": len(history),
        "patience": args.patience,
        "seed": args.seed,
        "device": str(device),
        "cuda_available": torch.cuda.is_available(),
        "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        "training_duration_seconds": round(duration_seconds, 2),
        "label_mapping": {"0": "REAL", "1": "FAKE"},
        "class_distribution": {
            name: class_distribution(split)
            for name, split in (("all", frame), ("train", train_frame), ("validation", validation_frame), ("test", test_frame))
        },
    }
    (output_dir / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    report = f"""# Genesis DistilBERT Training Report

## Dataset statistics

- Dataset: WELFake
- Total usable examples: {len(frame):,}
- Train examples: {len(train_frame):,}
- Validation examples: {len(validation_frame):,}
- Test examples: {len(test_frame):,}
- Label mapping: `0 = REAL`, `1 = FAKE`
- Class distribution: `{metadata["class_distribution"]}`

## Hyperparameters

- Base model: `{args.model_name}`
- Maximum sequence length: `{args.max_length}`
- Batch size: `{args.batch_size}`
- Learning rate: `{args.learning_rate}`
- Weight decay: `{args.weight_decay}`
- Warmup ratio: `{args.warmup_ratio}`
- Epochs requested/completed: `{args.epochs}/{len(history)}`
- Early-stopping patience: `{args.patience}`
- Seed: `{args.seed}`

## Hardware used and duration

- Device: `{device}`
- CUDA available: `{torch.cuda.is_available()}`
- GPU: `{metadata["gpu_name"] or "CPU"}`
- Training duration: `{duration_seconds:.2f} seconds`

## Held-out test results

| Metric | Value |
|---|---:|
| Accuracy | {test_metrics["accuracy"]:.6f} |
| Precision | {test_metrics["precision"]:.6f} |
| Recall | {test_metrics["recall"]:.6f} |
| F1 | {test_metrics["f1"]:.6f} |

### Confusion matrix

Rows are actual labels and columns are predicted labels, ordered as
`[REAL (0), FAKE (1)]`.

```text
{np.array(test_matrix)}
```

## Saved model path

`{output_dir.resolve()}`

The directory contains the best model weights, tokenizer, `config.json`,
metrics, training history, split data, and metadata.
"""
    (output_dir / "TRAINING_REPORT.md").write_text(report, encoding="utf-8")
    LOGGER.info("Training complete. Artifacts saved to %s", output_dir)


if __name__ == "__main__":
    main()
