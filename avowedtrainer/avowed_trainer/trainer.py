"""Core training module for Avowed Trainer.

Handles model initialization, training loops, and serialization.
"""

import spacy
from spacy.tokens import DocBin
from spacy.training import Example
from pathlib import Path
import logging
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class AvowedTrainer:
    """Main trainer class for creating custom NER models."""

    def __init__(
        self,
        model_name: str = "en_core_web_sm",
        output_dir: str = "./models",
        n_iter: int = 10,
        dropout: float = 0.2,
        batch_size: int = 32,
    ):
        """Initialize the trainer.

        Args:
            model_name: Base spaCy model to start from.
            output_dir: Directory to save trained models.
            n_iter: Number of training iterations.
            dropout: Dropout rate during training.
            batch_size: Number of examples per batch.
        """
        self.model_name = model_name
        self.output_dir = Path(output_dir)
        self.n_iter = n_iter
        self.dropout = dropout
        self.batch_size = batch_size
        self.nlp = None

    def load_base_model(self) -> None:
        """Load the base spaCy model with NER pipeline."""
        logger.info(f"Loading base model: {self.model_name}")
        self.nlp = spacy.load(self.model_name)
        if "ner" not in self.nlp.pipe_names:
            raise ValueError("Base model does not have an NER pipeline component")
        logger.info("Base model loaded successfully")

    def prepare_training_data(
        self, train_data: List[Dict]
    ) -> List[Example]:
        """Convert raw training data into spaCy Example objects.

        Args:
            train_data: List of dicts with 'text' and 'entities' keys.
                Entities should be list of (start, end, label) tuples.

        Returns:
            List of Example objects for training.
        """
        examples = []
        for item in train_data:
            text = item["text"]
            entities = item["entities"]
            doc = self.nlp.make_doc(text)
            example = Example.from_dict(doc, {"entities": entities})
            examples.append(example)
        return examples

    def train(
        self,
        train_examples: List[Example],
        dev_examples: Optional[List[Example]] = None,
    ) -> Dict[str, float]:
        """Run the training loop.

        Args:
            train_examples: Training examples.
            dev_examples: Optional development set for evaluation.

        Returns:
            Dictionary of final training metrics.
        """
        if self.nlp is None:
            self.load_base_model()

        # Get the NER component
        ner = self.nlp.get_pipe("ner")

        # Add labels from training data
        for example in train_examples:
            for ent in example.reference.ents:
                ner.add_label(ent.label_)

        # Disable other pipelines during training
        pipe_exceptions = ["ner", "trf_wordpiecer", "trf_tok2vec"]
        other_pipes = [
            pipe for pipe in self.nlp.pipe_names if pipe not in pipe_exceptions
        ]

        with self.nlp.disable_pipes(*other_pipes):
            optimizer = self.nlp.begin_training()
            logger.info(f"Starting training for {self.n_iter} iterations")

            for iteration in range(self.n_iter):
                losses = {}
                # Shuffle and batch
                import random
                random.shuffle(train_examples)
                batches = spacy.util.minibatch(train_examples, size=self.batch_size)

                for batch in batches:
                    self.nlp.update(
                        batch,
                        drop=self.dropout,
                        losses=losses,
                        sgd=optimizer,
                    )

                logger.info(
                    f"Iteration {iteration + 1}/{self.n_iter} - Losses: {losses}"
                )

                # Evaluate on dev set if provided
                if dev_examples:
                    scores = self.evaluate(dev_examples)
                    logger.info(f"Dev scores: {scores}")

        return losses

    def evaluate(self, examples: List[Example]) -> Dict[str, float]:
        """Evaluate the current model on a set of examples.

        Args:
            examples: List of Example objects to evaluate on.

        Returns:
            Dictionary of evaluation metrics (precision, recall, f1).
        """
        from spacy.scorer import Scorer

        scorer = Scorer()
        scores = scorer.score(examples)
        return {
            "ents_p": scores["ents_p"],
            "ents_r": scores["ents_r"],
            "ents_f": scores["ents_f"],
        }

    def save_model(self, model_name: str = "trained_model") -> Path:
        """Save the trained model to disk.

        Args:
            model_name: Name for the model directory.

        Returns:
            Path to the saved model.
        """
        if self.nlp is None:
            raise RuntimeError("No model to save. Train a model first.")

        output_path = self.output_dir / model_name
        output_path.mkdir(parents=True, exist_ok=True)
        self.nlp.to_disk(output_path)
        logger.info(f"Model saved to {output_path}")
        return output_path

    def load_model(self, model_path: str) -> None:
        """Load a previously trained model.

        Args:
            model_path: Path to the saved model directory.
        """
        self.nlp = spacy.load(model_path)
        logger.info(f"Model loaded from {model_path}")
