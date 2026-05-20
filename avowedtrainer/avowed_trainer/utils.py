"""Utility functions for data loading and preprocessing."""

import json
import random
from pathlib import Path
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)


def load_training_data(file_path: str) -> List[Dict]:
    """Load training data from a JSON file.

    Expected JSON format:
    [
        {
            "text": "Apple is looking at buying U.K. startup for $1 billion",
            "entities": [
                [0, 5, "ORG"],
                [24, 29, "GPE"],
                [39, 50, "MONEY"]
            ]
        },
        ...
    ]

    Args:
        file_path: Path to the JSON file.

    Returns:
        List of dictionaries with 'text' and 'entities' keys.

    Raises:
        FileNotFoundError: If the file does not exist.
        json.JSONDecodeError: If the file is not valid JSON.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Training data file not found: {file_path}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    logger.info(f"Loaded {len(data)} training examples from {file_path}")
    return data


def split_data(
    data: List[Dict],
    train_ratio: float = 0.8,
    seed: int = 42,
) -> Tuple[List[Dict], List[Dict]]:
    """Split data into training and development sets.

    Args:
        data: Full dataset as a list of dictionaries.
        train_ratio: Proportion of data to use for training (0.0 to 1.0).
        seed: Random seed for reproducibility.

    Returns:
        Tuple of (train_data, dev_data).
    """
    if not 0 < train_ratio < 1:
        raise ValueError("train_ratio must be between 0 and 1")

    random.seed(seed)
    shuffled = data.copy()
    random.shuffle(shuffled)

    split_idx = int(len(shuffled) * train_ratio)
    train_data = shuffled[:split_idx]
    dev_data = shuffled[split_idx:]

    logger.info(
        f"Split data: {len(train_data)} training, {len(dev_data)} development"
    )
    return train_data, dev_data


def prepare_entity_labels(data: List[Dict]) -> List[str]:
    """Extract unique entity labels from training data.

    Args:
        data: List of training examples with 'entities' key.

    Returns:
        Sorted list of unique entity labels.
    """
    labels = set()
    for item in data:
        for entity in item["entities"]:
            if len(entity) >= 3:
                labels.add(entity[2])
    return sorted(labels)
