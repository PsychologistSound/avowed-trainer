# Avowed Trainer - A CLI tool for training custom named entity recognition models
# using spaCy. This package provides utilities for data preparation, training,
# and evaluation of NER models.

from .trainer import AvowedTrainer
from .utils import load_training_data, split_data

__version__ = "0.1.0"
__all__ = ["AvowedTrainer", "load_training_data", "split_data"]
