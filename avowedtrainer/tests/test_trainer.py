"""Unit tests for the Avowed Trainer module."""

import pytest
from pathlib import Path
import tempfile
import json
from avowed_trainer import AvowedTrainer, load_training_data, split_data


@pytest.fixture
def sample_training_data():
    """Fixture providing sample training data for tests."""
    return [
        {
            "text": "Helsinki is the capital of Finland.",
            "entities": [
                [0, 8, "GPE"],
                [26, 33, "GPE"],
            ],
        },
        {
            "text": "Microsoft was founded by Bill Gates.",
            "entities": [
                [0, 9, "ORG"],
                [25, 35, "PERSON"],
            ],
        },
        {
            "text": "Apple released the iPhone in 2007.",
            "entities": [
                [0, 5, "ORG"],
                [19, 25, "PRODUCT"],
            ],
        },
    ]


@pytest.fixture
def trainer():
    """Fixture providing a trainer instance with a temporary output directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield AvowedTrainer(
            model_name="en_core_web_sm",
            output_dir=tmpdir,
            n_iter=2,
            batch_size=2,
        )


class TestAvowedTrainer:
    """Test suite for the AvowedTrainer class."""

    def test_initialization(self, trainer):
        """Test that the trainer initializes with correct attributes."""
        assert trainer.model_name == "en_core_web_sm"
        assert trainer.n_iter == 2
        assert trainer.batch_size == 2
        assert trainer.dropout == 0.2

    def test_load_base_model(self, trainer):
        """Test loading the base spaCy model."""
        trainer.load_base_model()
        assert trainer.nlp is not None
        assert "ner" in trainer.nlp.pipe_names

    def test_prepare_training_data(self, trainer, sample_training_data):
        """Test conversion of raw data to spaCy examples."""
        trainer.load_base_model()
        examples = trainer.prepare_training_data(sample_training_data)
        assert len(examples) == 3
        for example in examples:
            assert example.reference.ents is not None

    def test_train_and_save(self, trainer, sample_training_data):
        """Test full training and saving pipeline."""
        trainer.load_base_model()
        examples = trainer.prepare_training_data(sample_training_data)
        losses = trainer.train(examples)
        assert isinstance(losses, dict)
        assert "ner" in losses

        model_path = trainer.save_model("test_model")
        assert model_path.exists()
        assert (model_path / "config.cfg").exists()

    def test_evaluate(self, trainer, sample_training_data):
        """Test evaluation on training data."""
        trainer.load_base_model()
        examples = trainer.prepare_training_data(sample_training_data)
        trainer.train(examples)
        scores = trainer.evaluate(examples)
        assert "ents_p" in scores
        assert "ents_r" in scores
        assert "ents_f" in scores
        assert all(0 <= v <= 1 for v in scores.values())


class TestUtils:
    """Test suite for utility functions."""

    def test_load_training_data(self, tmp_path):
        """Test loading training data from a JSON file."""
        data = [
            {"text": "Test sentence.", "entities": [[0, 4, "TEST"]]}
        ]
        file_path = tmp_path / "train.json"
        with open(file_path, "w") as f:
            json.dump(data, f)

        loaded = load_training_data(str(file_path))
        assert len(loaded) == 1
        assert loaded[0]["text"] == "Test sentence."

    def test_load_training_data_file_not_found(self):
        """Test that FileNotFoundError is raised for missing file."""
        with pytest.raises(FileNotFoundError):
            load_training_data("nonexistent.json")

    def test_split_data(self, sample_training_data):
        """Test data splitting into train and dev sets."""
        train, dev = split_data(sample_training_data, train_ratio=0.7, seed=42)
        assert len(train) == 2
        assert len(dev) == 1
        assert len(train) + len(dev) == len(sample_training_data)

    def test_split_data_invalid_ratio(self, sample_training_data):
        """Test that invalid ratio raises ValueError."""
        with pytest.raises(ValueError):
            split_data(sample_training_data, train_ratio=1.5)

    def test_prepare_entity_labels(self, sample_training_data):
        """Test extraction of unique entity labels."""
        from avowed_trainer.utils import prepare_entity_labels
        labels = prepare_entity_labels(sample_training_data)
        assert "GPE" in labels
        assert "ORG" in labels
        assert "PERSON" in labels
        assert "PRODUCT" in labels
        assert len(labels) == 4
