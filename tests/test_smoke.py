from pathlib import Path

from src.data.preprocessing import PreprocessConfig, run_pipeline
from src.model.emotion_classifier import EmotionClassifier


def test_preprocessing_pipeline_smoke() -> None:
    csv_path = Path("base_model/color_emotion_labeled_updated.csv")
    assert csv_path.exists(), "Expected dataset file is missing"

    config = PreprocessConfig(
        test_size=0.2,
        val_size=0.1,
        random_state=42,
        normalize=True,
        min_samples_per_class=2,
    )
    result = run_pipeline(csv_path, config)

    total = len(result.X_train) + len(result.X_val) + len(result.X_test)
    assert total > 0
    assert result.n_classes >= 1


def test_emotion_classifier_smoke() -> None:
    csv_path = Path("base_model/color_emotion_labeled_updated.csv")
    clf = EmotionClassifier(n_neighbors=3)
    clf.fit(data_path=csv_path)

    pred = clf.predict_single(255, 0, 0)
    assert isinstance(pred, str)
    assert pred
