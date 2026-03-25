#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 30 2 16:56:32 2025
@author: acertainromance401
"""

import pandas as pd
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
    # 비대화형/다양한 실행 환경에서 안정적으로 동작하는 기본 폰트 설정
    plt.rcParams['font.family'] = 'DejaVu Sans'
    plt.rcParams['axes.unicode_minus'] = False


def finalize_plot(filename):
    backend = plt.get_backend().lower()
    if 'agg' in backend:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        save_path = os.path.join(OUTPUT_DIR, filename)
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"[plot saved] {save_path}")
    else:
        plt.show()


def emotion_from_rgb(knn_model, r, g, b):
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
    normalized = str(label).strip().upper()
    return TYPO_LABEL_MAP.get(normalized, normalized)


def save_feedback_rows(new_rows):
    if not new_rows:
        print("\n추가할 새로운 데이터가 없어 CSV를 변경하지 않았습니다.")
        return

    try:
        existing_df = pd.read_csv(DATA_PATH)
        new_df = pd.DataFrame(new_rows)

        # 기존 CSV 스키마를 최대한 그대로 유지한다.
        for col in existing_df.columns:
            if col not in new_df.columns:
                new_df[col] = np.nan

        for col in new_df.columns:
            if col not in existing_df.columns:
                existing_df[col] = np.nan

        new_df = new_df[existing_df.columns]

        if 'emotion' in existing_df.columns:
            existing_df['emotion'] = existing_df['emotion'].map(normalize_emotion_label)
            new_df['emotion'] = new_df['emotion'].map(normalize_emotion_label)

        updated_df = pd.concat([existing_df, new_df], ignore_index=True)

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
    setup_plot_style()

    # 데이터 로드
    color_map = pd.read_csv(DATA_PATH)
    color_map = pd.DataFrame(color_map)

    if 'emotion' in color_map.columns:
        color_map['emotion'] = color_map['emotion'].map(normalize_emotion_label)

    # RGB 정규화
    color_map['R_norm'] = color_map['R'] / 255
    color_map['G_norm'] = color_map['G'] / 255
    color_map['B_norm'] = color_map['B'] / 255

    # KNeighborsClassifier 학습용 데이터
    X = color_map[['R_norm', 'G_norm', 'B_norm']]
    y = color_map['emotion']

    knn = KNeighborsClassifier(n_neighbors=3)
    knn.fit(X, y)

    pred = knn.predict(X)
    print("예측 결과:", pred)

    result_df = pd.DataFrame(X)
    result_df['actual_emotion'] = y.values
    result_df['predicted_emotion'] = pred
    print(result_df)

    accuracy = knn.score(X, y)
    print("정확도:", accuracy)

    # 색상 시각화
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

    # 이미지 경로 입력
    try:
        image_path = input("분석할 이미지 파일 경로를 입력하세요: ").strip()
    except KeyboardInterrupt:
        print("\n입력이 취소되었습니다.")
        sys.exit(1)

    # 이미지 로딩 및 전처리
    img = cv2.imread(image_path)
    if img is None:
        print("이미지를 불러올 수 없습니다. 경로를 확인하세요.")
        sys.exit(1)

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_resized = cv2.resize(img, (100, 100))

    # 현저성
    gray = cv2.cvtColor(img_resized, cv2.COLOR_RGB2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    laplacian = cv2.Laplacian(blurred, cv2.CV_64F)
    saliencyMap = np.uint8(np.absolute(laplacian))
    _, salient_mask = cv2.threshold(saliencyMap, 10, 255, cv2.THRESH_BINARY)

    salient_pixels = img_resized[salient_mask == 255].reshape(-1, 3)

    if len(salient_pixels) == 0:
        print("현저한 영역이 감지되지 않았습니다.")
        sys.exit(1)

    # KMeans 클러스터링으로 주요 색상 추출
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
    dominant_colors = kmeans.cluster_centers_

    print("\n[saliency] Extracted Color-Emotions:")
    for i, color in enumerate(dominant_colors):
        r, g, b = color
        predicted_emotion = emotion_from_rgb(knn, r, g, b)
        print(f"color {i+1}: RGB = ({int(r)}, {int(g)}, {int(b)}) | 감정 예측 = {predicted_emotion}")

    # 현저성 맵 시각화
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

    # 주요 색상 및 감정 시각화
    plt.figure(figsize=(12, 6))
    for i, (r, g, b) in enumerate(dominant_colors):
        emotion = emotion_from_rgb(knn, r, g, b)
        plt.bar(i, 1, color=(r / 255, g / 255, b / 255))
        plt.text(i, 1.05, emotion, ha='center', va='bottom', fontsize=10, rotation=0)

    plt.xticks(range(len(dominant_colors)), [f'Color {i + 1}' for i in range(len(dominant_colors))])
    plt.yticks([])
    plt.tight_layout()
    finalize_plot('dominant_color_emotions.png')

    # 평가 및 반영
    new_rows = []
    for i, (r, g, b) in enumerate(dominant_colors):
        predicted_emotion = emotion_from_rgb(knn, r, g, b)

        print(f"\n[{i+1}] 예측된 색상 RGB = ({int(r)}, {int(g)}, {int(b)}) → 예측 감정: {predicted_emotion}")
        user_input = input("이 감정이 맞습니까? (Enter/yes/y/예 = 예, 아니면 원하는 감정 입력): ").strip()

        if user_input == "" or user_input.lower() in ["yes", "y", "예"]:
            print("기존 예측 감정 유지, CSV에 추가하지 않습니다.")
            continue

        final_emotion = normalize_emotion_label(user_input)

        new_rows.append({
            'R': int(r),
            'G': int(g),
            'B': int(b),
            'emotion': final_emotion,
            'color_name': np.nan,
            'color_label': np.nan,
        })

    save_feedback_rows(new_rows)


if __name__ == '__main__':
    main()

