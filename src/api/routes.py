"""
SentiVision - REST API Routes
Issue #12: /analyze 엔드포인트 구현

이미지 URL 또는 RGB 값을 받아 감정 분석 결과를 반환하는
FastAPI 라우터 모듈입니다.
"""

from __future__ import annotations

import io
import logging
from typing import Optional

import numpy as np
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["sentiment"])

# ── 요청/응답 스키마 ───────────────────────────────────────────────


class RGBInput(BaseModel):
    """단일 RGB 색상 직접 입력"""
    r: int = Field(..., ge=0, le=255, description="Red   (0-255)")
    g: int = Field(..., ge=0, le=255, description="Green (0-255)")
    b: int = Field(..., ge=0, le=255, description="Blue  (0-255)")


class AnalyzeRequest(BaseModel):
    """
    감정 분석 요청.
    rgb 필드로 단일 색상을 직접 전달하거나
    image_url 필드로 이미지를 전달할 수 있습니다.
    두 필드 중 하나는 반드시 존재해야 합니다.
    """
    rgb: Optional[RGBInput] = Field(None, description="직접 RGB 값 지정")
    image_url: Optional[str] = Field(None, description="분석할 이미지 URL")
    top_k: int = Field(3, ge=1, le=10, description="반환할 감정 후보 수")

    @field_validator("image_url")
    @classmethod
    def url_must_be_http(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.startswith(("http://", "https://")):
            raise ValueError("image_url은 http:// 또는 https://로 시작해야 합니다.")
        return v

    def model_post_init(self, __context) -> None:  # noqa: ANN001
        if self.rgb is None and self.image_url is None:
            raise ValueError("rgb 또는 image_url 중 하나를 반드시 제공해야 합니다.")


class EmotionScore(BaseModel):
    emotion: str
    score: float = Field(..., ge=0.0, le=1.0)


class DominantColor(BaseModel):
    r: int
    g: int
    b: int
    hex: str
    weight: float


class AnalyzeResponse(BaseModel):
    dominant_colors: list[DominantColor]
    emotions: list[EmotionScore]
    primary_emotion: str
    confidence: float


# ── 의존성 주입용 모델 로더 ────────────────────────────────────────

def get_model():
    """
    실행 시점에 KNN 모델을 지연 로드합니다.
    실제 배포에서는 app.state 또는 lifespan 이벤트로 캐싱하십시오.
    """
    try:
        from src.model.emotion_classifier import EmotionClassifier
        return EmotionClassifier.load_default()
    except Exception as exc:
        logger.error("모델 로드 실패: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="감정 분석 모델을 불러올 수 없습니다.",
        ) from exc


# ── 헬퍼 함수 ─────────────────────────────────────────────────────

def _extract_dominant_colors_from_url(image_url: str, n_colors: int = 5) -> list[dict]:
    """
    이미지 URL에서 주요 색상을 추출합니다.
    실제 구현은 Pillow + sklearn KMeans를 사용합니다.
    """
    try:
        import urllib.request
        from PIL import Image
        from sklearn.cluster import KMeans

        with urllib.request.urlopen(image_url, timeout=10) as resp:  # noqa: S310
            img = Image.open(io.BytesIO(resp.read())).convert("RGB")

        pixels = np.array(img).reshape(-1, 3).astype(float)
        sample = pixels[np.random.choice(len(pixels), min(10_000, len(pixels)), replace=False)]

        km = KMeans(n_clusters=n_colors, n_init=5, random_state=42)
        km.fit(sample)

        counts = np.bincount(km.labels_, minlength=n_colors)
        weights = counts / counts.sum()

        colors = []
        for center, weight in zip(km.cluster_centers_, weights):
            r, g, b = (int(c) for c in np.clip(center, 0, 255))
            colors.append({"r": r, "g": g, "b": b,
                           "hex": f"#{r:02x}{g:02x}{b:02x}",
                           "weight": round(float(weight), 4)})
        return sorted(colors, key=lambda c: c["weight"], reverse=True)

    except Exception as exc:
        logger.warning("이미지 색상 추출 실패: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"이미지를 처리할 수 없습니다: {exc}",
        ) from exc


def _build_dominant_from_rgb(rgb: RGBInput) -> list[dict]:
    r, g, b = rgb.r, rgb.g, rgb.b
    return [{"r": r, "g": g, "b": b,
             "hex": f"#{r:02x}{g:02x}{b:02x}",
             "weight": 1.0}]


def _predict_emotions(model, dominant_colors: list[dict], top_k: int) -> list[dict]:
    """주요 색상별 감정 예측 후 가중 평균으로 통합"""
    from collections import defaultdict

    aggregated: dict[str, float] = defaultdict(float)
    for color in dominant_colors:
        rgb_norm = np.array([[color["r"] / 255.0,
                              color["g"] / 255.0,
                              color["b"] / 255.0]])
        scores: dict[str, float] = model.predict_proba(rgb_norm)
        for emotion, prob in scores.items():
            aggregated[emotion] += prob * color["weight"]

    total = sum(aggregated.values()) or 1.0
    sorted_emotions = sorted(aggregated.items(),
                             key=lambda x: x[1], reverse=True)[:top_k]
    return [{"emotion": e, "score": round(v / total, 4)}
            for e, v in sorted_emotions]


# ── 엔드포인트 ────────────────────────────────────────────────────

@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    summary="이미지 또는 RGB 색상의 감정 분석",
    description=(
        "이미지 URL 또는 RGB 값을 입력받아 "
        "KNN 기반 컬러-감정 모델로 감정 점수를 반환합니다."
    ),
    status_code=status.HTTP_200_OK,
)
async def analyze(payload: AnalyzeRequest) -> AnalyzeResponse:
    """
    이미지 또는 RGB 색상으로부터 감정을 분석합니다.

    - **rgb**: `{"r": 255, "g": 87, "b": 51}` 형태의 직접 입력
    - **image_url**: 공개 이미지 URL (Pillow + KMeans로 주요 색상 추출)
    - **top_k**: 반환할 감정 후보 수 (기본 3, 최대 10)
    """
    model = get_model()

    # 1. 주요 색상 추출
    if payload.rgb is not None:
        dominant = _build_dominant_from_rgb(payload.rgb)
    else:
        dominant = _extract_dominant_colors_from_url(payload.image_url, n_colors=5)

    # 2. 감정 예측
    emotions = _predict_emotions(model, dominant, payload.top_k)

    if not emotions:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="감정 예측 결과를 생성할 수 없습니다.",
        )

    return AnalyzeResponse(
        dominant_colors=[DominantColor(**c) for c in dominant],
        emotions=[EmotionScore(**e) for e in emotions],
        primary_emotion=emotions[0]["emotion"],
        confidence=emotions[0]["score"],
    )


@router.get(
    "/health",
    summary="헬스 체크",
    status_code=status.HTTP_200_OK,
)
async def health() -> dict[str, str]:
    """API 서버 상태 확인"""
    return {"status": "ok"}
