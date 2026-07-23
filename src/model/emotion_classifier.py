"""
SentiVision - KNN Emotion Classifier Module
Issue #10: 감정 분석 모델 파이프라인 모듈화

base_model/main_.py에 인라인으로 작성된 KNN 학습 로직을
재사용 가능한 클래스로 분리합니다.
"""

from __future__ import annotations

import logging
import os
import pickle
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier

logger = logging.getLogger(__name__)

# 기본 모델 학습 데이터 경로 (프로젝트 루트 기준)
_DEFAULT_DATA_PATH = Path(__file__).resolve().parent.parent.parent / \
    "base_model" / "color_emotion_labeled_updated.csv"
_DEFAULT_MODEL_PATH = Path(__file__).resolve().parent / "saved" / "knn_emotion.pkl"

RGB_NORM_COLS = ["R_norm", "G_norm", "B_norm"]
EMOTION_COL = "emotion"


class EmotionClassifier:
    """
    RGB 색상 → 감정 예측 KNN 분류기.

    Examples
    --------
    >>> clf = EmotionClassifier()
    >>> clf.fit(data_path="base_model/color_emotion_labeled_updated.csv")
    >>> print(clf.predict_single(255, 87, 51))
    """

    def __init__(self, n_neighbors: int = 3, random_state: int = 42) -> None:
        self.n_neighbors = n_neighbors
        self.random_state = random_state
        self._model: Optional[KNeighborsClassifier] = None
        self._classes: list[str] = []

    # ── 학습 ────────────────────────────────────────────────────────

    def fit(self, data_path: str | Path | None = None,
            X: Optional[pd.DataFrame] = None,
            y: Optional[pd.Series] = None) -> "EmotionClassifier":
        """
        CSV 파일 또는 DataFrame으로 모델을 학습합니다.

        Args:
            data_path: CSV 파일 경로 (X/y 미제공 시 사용)
            X: 정규화된 RGB 특성 DataFrame (R_norm, G_norm, B_norm)
            y: 감정 레이블 Series

        Returns:
            self (메서드 체이닝 지원)
        """
        if X is None or y is None:
            path = Path(data_path) if data_path else _DEFAULT_DATA_PATH
            X, y = self._load_training_data(path)

        self._model = KNeighborsClassifier(n_neighbors=self.n_neighbors)
        self._model.fit(X, y)
        self._classes = list(self._model.classes_)
        logger.info("모델 학습 완료: %d 샘플, %d 클래스",
                    len(X), len(self._classes))
        return self

    @staticmethod
    def _load_training_data(path: Path) -> tuple[pd.DataFrame, pd.Series]:
        """CSV에서 정규화된 RGB 특성과 감정 레이블을 로드합니다."""
        if not path.exists():
            raise FileNotFoundError(f"학습 데이터를 찾을 수 없습니다: {path}")

        df = pd.read_csv(path).drop(columns=["color_name"], errors="ignore")
        df = df.dropna(subset=["R", "G", "B", EMOTION_COL])

        for col in ["R", "G", "B"]:
            df[col] = df[col].clip(0, 255)

        df["R_norm"] = df["R"] / 255.0
        df["G_norm"] = df["G"] / 255.0
        df["B_norm"] = df["B"] / 255.0

        return df[RGB_NORM_COLS], df[EMOTION_COL]

    # ── 예측 ────────────────────────────────────────────────────────

    def _check_fitted(self) -> None:
        if self._model is None:
            raise RuntimeError("모델이 학습되지 않았습니다. fit()을 먼저 호출하세요.")

    def predict_single(self, r: int, g: int, b: int) -> str:
        """단일 RGB 색상의 주요 감정을 반환합니다."""
        self._check_fitted()
        x = np.array([[r / 255.0, g / 255.0, b / 255.0]])
        return str(self._model.predict(x)[0])

    def predict_proba(self, X_norm: np.ndarray) -> dict[str, float]:
        """
        정규화된 RGB 배열에 대해 클래스별 확률 사전을 반환합니다.

        Args:
            X_norm: shape (1, 3) numpy 배열 또는 호환 형태

        Returns:
            {emotion: probability} 형태의 사전
        """
        self._check_fitted()
        proba = self._model.predict_proba(X_norm)[0]
        return {cls: float(p) for cls, p in zip(self._classes, proba)}

    def predict_batch(self, df: pd.DataFrame) -> pd.Series:
        """
        DataFrame에 대해 배치 예측을 수행합니다.

        Args:
            df: R_norm, G_norm, B_norm 컬럼을 포함하는 DataFrame

        Returns:
            예측 감정 레이블 Series
        """
        self._check_fitted()
        return pd.Series(
            self._model.predict(df[RGB_NORM_COLS]),
            index=df.index,
            name="predicted_emotion",
        )

    # ── 저장 / 로드 ─────────────────────────────────────────────────

    def save(self, path: str | Path | None = None) -> Path:
        """학습된 모델을 pickle로 저장합니다."""
        self._check_fitted()
        save_path = Path(path) if path else _DEFAULT_MODEL_PATH
        save_path.parent.mkdir(parents=True, exist_ok=True)
        with save_path.open("wb") as f:
            pickle.dump({"model": self._model, "classes": self._classes}, f)
        logger.info("모델 저장 완료: %s", save_path)
        return save_path

    @classmethod
    def load(cls, path: str | Path | None = None) -> "EmotionClassifier":
        """저장된 pickle 파일에서 모델을 불러옵니다."""
        load_path = Path(path) if path else _DEFAULT_MODEL_PATH
        if not load_path.exists():
            raise FileNotFoundError(f"저장된 모델 파일을 찾을 수 없습니다: {load_path}")
        with load_path.open("rb") as f:
            data = pickle.load(f)  # noqa: S301 — 신뢰된 내부 파일만 로드
        instance = cls()
        instance._model = data["model"]
        instance._classes = data["classes"]
        logger.info("모델 로드 완료: %d 클래스", len(instance._classes))
        return instance

    @classmethod
    def load_default(cls) -> "EmotionClassifier":
        """
        저장된 모델이 있으면 로드하고, 없으면 기본 데이터로 학습합니다.
        """
        if _DEFAULT_MODEL_PATH.exists():
            return cls.load(_DEFAULT_MODEL_PATH)
        logger.info("저장된 모델 없음 — 기본 데이터로 재학습합니다.")
        instance = cls()
        instance.fit(_DEFAULT_DATA_PATH)
        instance.save(_DEFAULT_MODEL_PATH)
        return instance

    # ── 정보 ────────────────────────────────────────────────────────

    @property
    def classes(self) -> list[str]:
        return list(self._classes)

    @property
    def is_fitted(self) -> bool:
        return self._model is not None

    def __repr__(self) -> str:
        status = f"fitted, {len(self._classes)} classes" if self.is_fitted else "not fitted"
        return f"EmotionClassifier(n_neighbors={self.n_neighbors}, status={status})"


# ── CLI 진입점 ────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    parser = argparse.ArgumentParser(description="KNN 감정 분류기 학습/예측")
    sub = parser.add_subparsers(dest="cmd")

    train_p = sub.add_parser("train", help="모델 학습 후 저장")
    train_p.add_argument("--data", default=str(_DEFAULT_DATA_PATH))
    train_p.add_argument("--out",  default=str(_DEFAULT_MODEL_PATH))

    pred_p = sub.add_parser("predict", help="단일 RGB 감정 예측")
    pred_p.add_argument("r", type=int)
    pred_p.add_argument("g", type=int)
    pred_p.add_argument("b", type=int)

    args = parser.parse_args()

    if args.cmd == "train":
        clf = EmotionClassifier()
        clf.fit(data_path=args.data)
        clf.save(args.out)
        print(f"학습 완료: {clf}")
    elif args.cmd == "predict":
        clf = EmotionClassifier.load_default()
        emotion = clf.predict_single(args.r, args.g, args.b)
        print(f"RGB({args.r},{args.g},{args.b}) → {emotion}")
    else:
        parser.print_help()
