"""
SentiVision - Color-Emotion Dataset Preprocessing Pipeline
Issue #11: 컬러-감정 매핑 데이터셋 전처리 파이프라인

이 모듈은 원시 CSV 데이터를 로드하고 정규화, 검증,
train/val/test 분할까지 일관된 인터페이스로 처리합니다.
"""

from __future__ import annotations

import os
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

logger = logging.getLogger(__name__)

# ── 상수 ──────────────────────────────────────────────────────────
RGB_COLS = ["R", "G", "B"]
NORM_COLS = ["R_norm", "G_norm", "B_norm"]
EMOTION_COL = "emotion"
REQUIRED_COLS = RGB_COLS + [EMOTION_COL]


# ── 설정 데이터클래스 ─────────────────────────────────────────────
@dataclass
class PreprocessConfig:
    """전처리 파이프라인 설정"""
    test_size: float = 0.2
    val_size: float = 0.1
    random_state: int = 42
    normalize: bool = True
    drop_duplicates: bool = True
    clip_rgb: bool = True           # RGB 값을 [0, 255]로 클리핑
    min_samples_per_class: int = 3  # 클래스별 최소 샘플 수
    extra_drop_cols: list[str] = field(default_factory=lambda: ["color_name"])


# ── 전처리 결과 데이터클래스 ──────────────────────────────────────
@dataclass
class PreprocessResult:
    """전처리 결과를 담는 컨테이너"""
    X_train: pd.DataFrame
    X_val: pd.DataFrame
    X_test: pd.DataFrame
    y_train: pd.Series
    y_val: pd.Series
    y_test: pd.Series
    label_encoder: LabelEncoder
    feature_cols: list[str]
    emotion_classes: list[str]
    stats: dict

    @property
    def n_classes(self) -> int:
        return len(self.emotion_classes)

    @property
    def train_size(self) -> int:
        return len(self.X_train)

    def summary(self) -> str:
        lines = [
            "=== Preprocessing Summary ===",
            f"  Feature columns : {self.feature_cols}",
            f"  Emotion classes : {self.emotion_classes}",
            f"  Train  samples  : {len(self.X_train)}",
            f"  Val    samples  : {len(self.X_val)}",
            f"  Test   samples  : {len(self.X_test)}",
            f"  Class balance   : {self.stats.get('class_counts', {})}",
        ]
        return "\n".join(lines)


# ── 핵심 함수들 ───────────────────────────────────────────────────

def load_csv(path: str | Path) -> pd.DataFrame:
    """CSV 파일 로드 및 기본 검증"""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"데이터 파일을 찾을 수 없습니다: {path}")

    df = pd.read_csv(path)
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"필수 컬럼이 없습니다: {missing}")

    logger.info("CSV 로드 완료: %s (%d rows)", path.name, len(df))
    return df


def clean(df: pd.DataFrame, config: PreprocessConfig) -> pd.DataFrame:
    """결측값 제거, 중복 제거, RGB 클리핑"""
    original_len = len(df)

    # 불필요한 컬럼 제거
    drop_cols = [c for c in config.extra_drop_cols if c in df.columns]
    if drop_cols:
        df = df.drop(columns=drop_cols)

    # 결측값 제거
    df = df.dropna(subset=REQUIRED_COLS)

    # 중복 제거
    if config.drop_duplicates:
        df = df.drop_duplicates(subset=RGB_COLS + [EMOTION_COL])

    # RGB 값 클리핑
    if config.clip_rgb:
        for col in RGB_COLS:
            df[col] = df[col].clip(0, 255).astype(int)

    # 클래스별 최소 샘플 수 필터링
    class_counts = df[EMOTION_COL].value_counts()
    valid_classes = class_counts[class_counts >= config.min_samples_per_class].index
    removed = set(df[EMOTION_COL].unique()) - set(valid_classes)
    if removed:
        logger.warning("샘플 수 부족으로 제거된 감정 클래스: %s", removed)
    df = df[df[EMOTION_COL].isin(valid_classes)]

    logger.info("정제 완료: %d → %d rows (제거: %d)", original_len, len(df), original_len - len(df))
    return df.reset_index(drop=True)


def normalize_rgb(df: pd.DataFrame) -> pd.DataFrame:
    """RGB 값을 [0, 1] 범위로 정규화"""
    df = df.copy()
    for raw_col, norm_col in zip(RGB_COLS, NORM_COLS):
        df[norm_col] = df[raw_col] / 255.0
    return df


def encode_labels(y: pd.Series) -> tuple[np.ndarray, LabelEncoder]:
    """감정 레이블을 정수로 인코딩"""
    le = LabelEncoder()
    encoded = le.fit_transform(y)
    return encoded, le


def split_dataset(
    X: pd.DataFrame,
    y: np.ndarray,
    config: PreprocessConfig,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame,
           np.ndarray, np.ndarray, np.ndarray]:
    """train / val / test 분할 (stratify 불가 시 random fallback)"""
    def _try_split(X, y, test_size, random_state, stratify=None):
        try:
            return train_test_split(X, y, test_size=test_size,
                                    random_state=random_state, stratify=stratify)
        except ValueError:
            logger.warning("stratify 분할 실패 — random 분할로 대체합니다.")
            return train_test_split(X, y, test_size=test_size,
                                    random_state=random_state)

    X_train_val, X_test, y_train_val, y_test = _try_split(
        X, y, config.test_size, config.random_state, stratify=y
    )
    relative_val = config.val_size / (1 - config.test_size)
    X_train, X_val, y_train, y_val = _try_split(
        X_train_val, y_train_val, relative_val, config.random_state,
        stratify=y_train_val
    )
    return X_train, X_val, X_test, y_train, y_val, y_test


# ── 통합 파이프라인 ────────────────────────────────────────────────

def run_pipeline(
    csv_path: str | Path,
    config: Optional[PreprocessConfig] = None,
) -> PreprocessResult:
    """
    전체 전처리 파이프라인 실행.

    Args:
        csv_path: 원시 CSV 파일 경로
        config: PreprocessConfig 인스턴스 (없으면 기본값 사용)

    Returns:
        PreprocessResult: 분할된 데이터셋 및 메타데이터
    """
    if config is None:
        config = PreprocessConfig()

    # 1. 로드
    df = load_csv(csv_path)

    # 2. 정제
    df = clean(df, config)

    # 3. 정규화
    if config.normalize:
        df = normalize_rgb(df)
        feature_cols = NORM_COLS
    else:
        feature_cols = RGB_COLS

    # 4. 레이블 인코딩
    y_encoded, le = encode_labels(df[EMOTION_COL])
    X = df[feature_cols]

    # 5. 분할
    X_train, X_val, X_test, y_train, y_val, y_test = split_dataset(
        X, y_encoded, config
    )

    # 6. 통계
    stats = {
        "total_samples": len(df),
        "class_counts": df[EMOTION_COL].value_counts().to_dict(),
        "n_classes": len(le.classes_),
    }

    result = PreprocessResult(
        X_train=X_train.reset_index(drop=True),
        X_val=X_val.reset_index(drop=True),
        X_test=X_test.reset_index(drop=True),
        y_train=pd.Series(y_train, name=EMOTION_COL),
        y_val=pd.Series(y_val, name=EMOTION_COL),
        y_test=pd.Series(y_test, name=EMOTION_COL),
        label_encoder=le,
        feature_cols=feature_cols,
        emotion_classes=list(le.classes_),
        stats=stats,
    )

    logger.info(result.summary())
    return result


# ── CLI 진입점 ────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    parser = argparse.ArgumentParser(description="컬러-감정 데이터셋 전처리")
    parser.add_argument("csv_path", help="입력 CSV 파일 경로")
    parser.add_argument("--no-normalize", action="store_true")
    parser.add_argument("--test-size", type=float, default=0.2)
    args = parser.parse_args()

    cfg = PreprocessConfig(
        normalize=not args.no_normalize,
        test_size=args.test_size,
    )
    result = run_pipeline(args.csv_path, cfg)
    print(result.summary())
