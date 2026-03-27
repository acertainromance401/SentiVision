#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 30 2 16:56:32 2025
@author: acertainromance401

이 스크립트는 다음 파이프라인을 수행한다.
1) CSV의 RGB-감정 라벨 데이터로 KNN 분류기 학습 (main: 137~168행)
2) 입력 이미지에서 현저(salient) 영역 추출 (main: 185~217행)
3) 현저 영역의 대표 색상을 KMeans로 추출 (main: 219~234행)
4) 추출된 대표 색상의 감정을 예측하고 시각화 (main: 236~267행)
5) 사용자 피드백을 받아 CSV 데이터셋에 반영 (main: 269~295행)
"""

import pandas as pd
import matplotlib
matplotlib.use('Agg')  # 헤드리스 환경에서도 이미지를 파일로 저장
import matplotlib.pyplot as plt
import cv2
from sklearn.neighbors import KNeighborsClassifier
from sklearn.cluster import KMeans
import numpy as np
import sys
import os
import warnings


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'color_emotion_labeled_updated.csv')
OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs')

warnings.filterwarnings(
    "ignore",
    message="The number of unique classes is greater than 50% of the number of samples.*",
    category=UserWarning
)


def setup_plot_style():
    """플롯의 기본 표시 설정을 통일한다."""
    # 비대화형/다양한 실행 환경에서 안정적으로 동작하는 기본 폰트 설정
    plt.rcParams['font.family'] = 'DejaVu Sans'
    plt.rcParams['axes.unicode_minus'] = False


def finalize_plot(filename):
    """플롯을 파일로 저장한다. (Agg 백엔드 사용)"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    save_path = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✓ 이미지 저장: {filename}")


def emotion_from_rgb(knn_model, r, g, b):
    """단일 RGB 값을 KNN 입력 포맷으로 변환해 감정을 예측한다."""
    color_df = pd.DataFrame(
        [[r / 255, g / 255, b / 255]],
        columns=['R_norm', 'G_norm', 'B_norm']
    )
    return knn_model.predict(color_df)[0]


TYPO_LABEL_MAP = {
    'CORWARDICE': 'COWARDICE',
    'LONLINESS': 'LONELINESS',
}


def normalize_emotion_label(label):
    """감정 라벨의 대소문자/공백/오타를 정규화한다."""
    normalized = str(label).strip().upper()
    return TYPO_LABEL_MAP.get(normalized, normalized)


def save_feedback_rows(new_rows):
    """
    사용자 피드백 기반 신규 라벨을 CSV에 반영한다.
    - 기존 스키마를 최대한 유지
    - 감정 라벨 정규화 후 병합
    - 동일 (R,G,B,emotion) 중복 제거
    """
    if not new_rows:
        print("\n추가할 새로운 데이터가 없어 CSV를 변경하지 않았습니다.")
        return

    try:
        existing_df = pd.read_csv(DATA_PATH)
        new_df = pd.DataFrame(new_rows)

        # 기존 CSV 스키마를 최대한 그대로 유지한다.
        # 신규 데이터에 누락된 컬럼은 NaN으로 맞춘다.
        for col in existing_df.columns:
            if col not in new_df.columns:
                new_df[col] = np.nan

        # 반대로 신규 데이터에만 있는 컬럼이 있다면 기존 DF에도 컬럼을 추가해
        # concat 시 열 정렬/손실 문제를 피한다.
        for col in new_df.columns:
            if col not in existing_df.columns:
                existing_df[col] = np.nan

        # 최종 저장 전 열 순서를 원본 CSV 순서에 정렬한다.
        new_df = new_df[existing_df.columns]

        if 'emotion' in existing_df.columns:
            # 학습 데이터 라벨 일관성을 위해 기존/신규 라벨을 동일 규칙으로 정규화
            existing_df['emotion'] = existing_df['emotion'].map(normalize_emotion_label)
            new_df['emotion'] = new_df['emotion'].map(normalize_emotion_label)

        # 기존 + 신규 데이터를 하나로 결합
        updated_df = pd.concat([existing_df, new_df], ignore_index=True)

        # 동일 색상과 감정 조합은 마지막 입력(최신 피드백) 기준으로 유지
        dedupe_keys = ['R', 'G', 'B', 'emotion']
        if all(key in updated_df.columns for key in dedupe_keys):
            updated_df = updated_df.drop_duplicates(subset=dedupe_keys, keep='last')
        else:
            updated_df = updated_df.drop_duplicates(keep='last')

        updated_df.to_csv(DATA_PATH, index=False)
        print("\n감정 데이터가 성공적으로 추가되었습니다.")
    except Exception as e:
        print(f"CSV 저장 중 오류 발생: {e}")


def main():
    """학습-추론-시각화-사용자 피드백 반영까지 전체 파이프라인 실행."""
    setup_plot_style()

    # 1) 데이터 로드: RGB-감정 매핑 CSV를 읽는다.
    color_map = pd.read_csv(DATA_PATH)
    color_map = pd.DataFrame(color_map)

    if 'emotion' in color_map.columns:
        # 라벨 변형(오타/대소문자)을 통일해 모델 입력 일관성 확보
        color_map['emotion'] = color_map['emotion'].map(normalize_emotion_label)

    # 2) RGB 정규화: 0~255 범위를 0~1로 스케일링해 거리기반 KNN 안정화
    color_map['R_norm'] = color_map['R'] / 255
    color_map['G_norm'] = color_map['G'] / 255
    color_map['B_norm'] = color_map['B'] / 255

    # 3) KNN 학습용 특성/라벨 분리
    X = color_map[['R_norm', 'G_norm', 'B_norm']]
    y = color_map['emotion']

    # 최근접 이웃 3개 기준으로 감정을 다수결 분류
    knn = KNeighborsClassifier(n_neighbors=3)
    knn.fit(X, y)

    # 참고용: 학습 데이터 자체 예측 결과(훈련셋 성능 확인)
    pred = knn.predict(X)
    print("예측 결과:", pred)

    result_df = pd.DataFrame(X)
    result_df['actual_emotion'] = y.values
    result_df['predicted_emotion'] = pred
    print(result_df)

    accuracy = knn.score(X, y)
    print("정확도:", accuracy)

    # 4) 학습 데이터 RGB 분포를 3D로 시각화
    #    축은 원본 RGB(0~255), 점 색상은 정규화 RGB를 사용한다.
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    for _, row in color_map.iterrows():
        color = (row['R_norm'], row['G_norm'], row['B_norm'])
        ax.scatter(row['R'], row['G'], row['B'], color=color, s=100)
        ax.text(row['R'], row['G'], row['B'] + 5, f"{row['emotion']}", fontsize=8)
    ax.set_xlabel('Red')
    ax.set_ylabel('Green')
    ax.set_zlabel('Blue')
    ax.set_title('RGB 3Dimention', fontsize=15)
    plt.tight_layout()
    finalize_plot('rgb_3d_distribution.png')

    # 5) 분석할 이미지 경로 입력
    try:
        image_path = input("분석할 이미지 파일 경로를 입력하세요: ").strip()
    except KeyboardInterrupt:
        print("\n입력이 취소되었습니다.")
        sys.exit(1)

    # 6) 이미지 로딩 및 전처리
    img = cv2.imread(image_path)
    if img is None:
        print("이미지를 불러올 수 없습니다. 경로를 확인하세요.")
        sys.exit(1)

    # OpenCV는 BGR로 로드하므로 RGB로 변환
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # 연산량/노이즈 균형을 위해 분석 해상도 축소
    img_resized = cv2.resize(img, (100, 100))

    # 7) 현저성(saliency) 계산
    #    Laplacian 기반으로 경계/변화가 큰 영역을 현저 영역으로 간주
    gray = cv2.cvtColor(img_resized, cv2.COLOR_RGB2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    laplacian = cv2.Laplacian(blurred, cv2.CV_64F)
    saliencyMap = np.uint8(np.absolute(laplacian))
    # 임계값 이진화로 salient mask 생성
    _, salient_mask = cv2.threshold(saliencyMap, 10, 255, cv2.THRESH_BINARY)

    # 마스크가 255인 픽셀만 추출하여 색상 군집화 대상으로 사용
    salient_pixels = img_resized[salient_mask == 255].reshape(-1, 3)

    if len(salient_pixels) == 0:
        print("현저한 영역이 감지되지 않았습니다.")
        sys.exit(1)

    # 8) KMeans로 주요 색상 추출
    #    목표 클러스터 수는 3이지만, 데이터 부족 시 가능한 범위로 자동 축소
    desired_k = 3
    unique_salient_count = np.unique(salient_pixels, axis=0).shape[0]
    k = min(desired_k, len(salient_pixels), unique_salient_count)

    if k < desired_k:
        print(
            f"현저 픽셀/고유 색상 수가 부족하여 클러스터 수를 "
            f"{desired_k} -> {k}로 조정합니다."
        )

    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(salient_pixels)
    # 각 클러스터 중심값(대표 RGB)
    dominant_colors = kmeans.cluster_centers_

    # 9) 추출 색상별 감정 예측 결과 출력
    print("\n[saliency] Extracted Color-Emotions:")
    for i, color in enumerate(dominant_colors):
        r, g, b = color
        predicted_emotion = emotion_from_rgb(knn, r, g, b)
        print(f"color {i+1}: RGB = ({int(r)}, {int(g)}, {int(b)}) | 감정 예측 = {predicted_emotion}")

    # 10) 현저성 맵 시각화
    plt.figure(figsize=(8, 4))
    plt.subplot(1, 2, 1)
    plt.title("Saliency Map")
    plt.imshow(saliencyMap, cmap="gray")
    plt.axis("off")

    plt.subplot(1, 2, 2)
    plt.title("Salient Region Mask")
    plt.imshow(salient_mask, cmap="gray")
    plt.axis("off")
    plt.tight_layout()
    finalize_plot('saliency_maps.png')

    # 11) 주요 색상과 예측 감정을 막대 형태로 시각화
    plt.figure(figsize=(12, 6))
    for i, (r, g, b) in enumerate(dominant_colors):
        emotion = emotion_from_rgb(knn, r, g, b)
        plt.bar(i, 1, color=(r / 255, g / 255, b / 255))
        plt.text(i, 1.05, emotion, ha='center', va='bottom', fontsize=10, rotation=0)

    plt.xticks(range(len(dominant_colors)), [f'Color {i + 1}' for i in range(len(dominant_colors))])
    plt.yticks([])
    plt.tight_layout()
    finalize_plot('dominant_color_emotions.png')

    # 12) 사용자 검증/피드백 수집
    #     사용자가 예측에 동의하지 않으면 해당 RGB에 새 감정 라벨을 기록
    new_rows = []
    for i, (r, g, b) in enumerate(dominant_colors):
        predicted_emotion = emotion_from_rgb(knn, r, g, b)

        print(f"\n[{i+1}] 예측된 색상 RGB = ({int(r)}, {int(g)}, {int(b)}) → 예측 감정: {predicted_emotion}")
        user_input = input("이 감정이 맞습니까? (Enter/yes/y/예 = 예, 아니면 원하는 감정 입력): ").strip()

        if user_input == "" or user_input.lower() in ["yes", "y", "예"]:
            print("기존 예측 감정 유지, CSV에 추가하지 않습니다.")
            continue

        # 자유입력 라벨도 동일 정규화 규칙 적용
        final_emotion = normalize_emotion_label(user_input)

        new_rows.append({
            'R': int(r),
            'G': int(g),
            'B': int(b),
            'emotion': final_emotion,
            'color_name': np.nan,
            'color_label': np.nan,
        })

    # 13) 수집된 피드백을 데이터셋에 저장
    save_feedback_rows(new_rows)


if __name__ == '__main__':
    # 스크립트 직접 실행 시에만 메인 파이프라인 동작
    main()

