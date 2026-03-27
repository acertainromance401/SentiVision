#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2026-03-25
@author: acertainromance401

이 스크립트는 다음을 수행한다.
1) main_.py와 동일하게 이미지에서 현저 영역 추출 및 색상 추출 (1~8단계)
2) 감정 예측 시 KNN vs RandomForest 모델 비교
3) 학습/검증 분리 및 교차검증으로 일반화 성능 평가
4) 정확도, F1, confusion matrix를 시각화해 성능 비교
"""

import pandas as pd
import matplotlib.pyplot as plt
import cv2
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score, cross_validate
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, classification_report
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
    plt.rcParams['font.family'] = 'DejaVu Sans'
    plt.rcParams['axes.unicode_minus'] = False


def finalize_plot(filename):
    """
    백엔드에 따라 플롯 출력 방식을 분기한다.
    - Agg 계열(헤드리스 환경): 파일 저장
    - GUI 백엔드: 화면 표시
    """
    backend = plt.get_backend().lower()
    if 'agg' in backend:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        save_path = os.path.join(OUTPUT_DIR, filename)
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"[plot saved] {save_path}")
    else:
        plt.show()


TYPO_LABEL_MAP = {
    'CORWARDICE': 'COWARDICE',
    'LONLINESS': 'LONELINESS',
}


def normalize_emotion_label(label):
    """감정 라벨의 대소문자/공백/오타를 정규화한다."""
    normalized = str(label).strip().upper()
    return TYPO_LABEL_MAP.get(normalized, normalized)


def emotion_from_rgb_knn(knn_model, r, g, b):
    """단일 RGB 값을 KNN 모델로 감정 예측한다."""
    color_df = pd.DataFrame(
        [[r / 255, g / 255, b / 255]],
        columns=['R_norm', 'G_norm', 'B_norm']
    )
    return knn_model.predict(color_df)[0]


def emotion_from_rgb_rf(rf_model, r, g, b):
    """단일 RGB 값을 RandomForest 모델로 감정 예측한다."""
    color_df = pd.DataFrame(
        [[r / 255, g / 255, b / 255]],
        columns=['R_norm', 'G_norm', 'B_norm']
    )
    return rf_model.predict(color_df)[0]


def train_models(X_train, y_train):
    """
    KNN과 RandomForest 모델을 학습한다.
    
    Returns:
        tuple: (knn_model, rf_model)
    """
    # KNN 모델 학습 (n_neighbors=3)
    knn = KNeighborsClassifier(n_neighbors=3)
    knn.fit(X_train, y_train)
    
    # RandomForest 모델 학습
    rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    
    return knn, rf


def evaluate_models(knn, rf, X_test, y_test):
    """
    모델 성능을 평가한다.
    
    Returns:
        dict: 평가 지표
    """
    # 예측
    knn_pred = knn.predict(X_test)
    rf_pred = rf.predict(X_test)
    
    # 정확도
    knn_acc = accuracy_score(y_test, knn_pred)
    rf_acc = accuracy_score(y_test, rf_pred)
    
    # F1 스코어 (weighted)
    knn_f1 = f1_score(y_test, knn_pred, average='weighted', zero_division=0)
    rf_f1 = f1_score(y_test, rf_pred, average='weighted', zero_division=0)
    
    # Confusion Matrix
    knn_cm = confusion_matrix(y_test, knn_pred)
    rf_cm = confusion_matrix(y_test, rf_pred)
    
    # 클래스 이름 추출
    classes = sorted(np.unique(y_test))
    
    results = {
        'knn_acc': knn_acc,
        'rf_acc': rf_acc,
        'knn_f1': knn_f1,
        'rf_f1': rf_f1,
        'knn_cm': knn_cm,
        'rf_cm': rf_cm,
        'knn_pred': knn_pred,
        'rf_pred': rf_pred,
        'y_test': y_test,
        'classes': classes,
    }
    
    return results


def plot_model_comparison(results):
    """모델 성능 비교 시각화."""
    knn_acc = results['knn_acc']
    rf_acc = results['rf_acc']
    knn_f1 = results['knn_f1']
    rf_f1 = results['rf_f1']
    
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # 정확도 비교
    models = ['KNN', 'RandomForest']
    accuracies = [knn_acc, rf_acc]
    colors = ['#FF6B6B', '#4ECDC4']
    axes[0].bar(models, accuracies, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
    axes[0].set_ylabel('Accuracy', fontsize=12)
    axes[0].set_title('Model Accuracy Comparison', fontsize=14, fontweight='bold')
    axes[0].set_ylim([0, 1])
    for i, acc in enumerate(accuracies):
        axes[0].text(i, acc + 0.02, f'{acc:.3f}', ha='center', fontsize=11, fontweight='bold')
    
    # F1 스코어 비교
    f1_scores = [knn_f1, rf_f1]
    axes[1].bar(models, f1_scores, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
    axes[1].set_ylabel('F1 Score (Weighted)', fontsize=12)
    axes[1].set_title('Model F1 Score Comparison', fontsize=14, fontweight='bold')
    axes[1].set_ylim([0, 1])
    for i, f1 in enumerate(f1_scores):
        axes[1].text(i, f1 + 0.02, f'{f1:.3f}', ha='center', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    finalize_plot('model_comparison_metrics.png')


def plot_confusion_matrices(results):
    """혼동 행렬 시각화."""
    knn_cm = results['knn_cm']
    rf_cm = results['rf_cm']
    classes = results['classes']
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # KNN 혼동 행렬
    im0 = axes[0].imshow(knn_cm, cmap='Blues', aspect='auto')
    axes[0].set_title('KNN Confusion Matrix', fontsize=14, fontweight='bold')
    axes[0].set_ylabel('True Label', fontsize=11)
    axes[0].set_xlabel('Predicted Label', fontsize=11)
    axes[0].set_xticks(range(len(classes)))
    axes[0].set_yticks(range(len(classes)))
    axes[0].set_xticklabels(classes, rotation=45, ha='right')
    axes[0].set_yticklabels(classes)
    # 셀에 값 표시
    for i in range(len(classes)):
        for j in range(len(classes)):
            text = axes[0].text(j, i, int(knn_cm[i, j]),
                              ha="center", va="center", color="black", fontsize=10)
    plt.colorbar(im0, ax=axes[0], label='Count')
    
    # RandomForest 혼동 행렬
    im1 = axes[1].imshow(rf_cm, cmap='Greens', aspect='auto')
    axes[1].set_title('RandomForest Confusion Matrix', fontsize=14, fontweight='bold')
    axes[1].set_ylabel('True Label', fontsize=11)
    axes[1].set_xlabel('Predicted Label', fontsize=11)
    axes[1].set_xticks(range(len(classes)))
    axes[1].set_yticks(range(len(classes)))
    axes[1].set_xticklabels(classes, rotation=45, ha='right')
    axes[1].set_yticklabels(classes)
    # 셀에 값 표시
    for i in range(len(classes)):
        for j in range(len(classes)):
            text = axes[1].text(j, i, int(rf_cm[i, j]),
                              ha="center", va="center", color="black", fontsize=10)
    plt.colorbar(im1, ax=axes[1], label='Count')
    
    plt.tight_layout()
    finalize_plot('confusion_matrices_comparison.png')


def print_detailed_report(results):
    """상세 성능 보고서 출력."""
    print("\n" + "="*70)
    print("MODEL PERFORMANCE COMPARISON REPORT")
    print("="*70)
    
    print(f"\n[ACCURACY]")
    print(f"  KNN           : {results['knn_acc']:.4f}")
    print(f"  RandomForest  : {results['rf_acc']:.4f}")
    print(f"  Improvement   : {results['rf_acc'] - results['knn_acc']:+.4f}")
    
    print(f"\n[F1 SCORE (Weighted)]")
    print(f"  KNN           : {results['knn_f1']:.4f}")
    print(f"  RandomForest  : {results['rf_f1']:.4f}")
    print(f"  Improvement   : {results['rf_f1'] - results['knn_f1']:+.4f}")
    
    print("\n" + "="*70)
    print("END OF REPORT")
    print("="*70 + "\n")


def main():
    """모델 비교 파이프라인 실행."""
    setup_plot_style()
    
    print("[Step 1] CSV 로드 및 데이터 준비")
    # 데이터 로드
    color_map = pd.read_csv(DATA_PATH)
    color_map = pd.DataFrame(color_map)
    
    if 'emotion' in color_map.columns:
        color_map['emotion'] = color_map['emotion'].map(normalize_emotion_label)
    
    print(f"  Total samples: {len(color_map)}")
    print(f"  Emotion classes: {color_map['emotion'].nunique()}")
    
    # RGB 정규화
    color_map['R_norm'] = color_map['R'] / 255
    color_map['G_norm'] = color_map['G'] / 255
    color_map['B_norm'] = color_map['B'] / 255
    
    # 학습용 데이터 분리
    X = color_map[['R_norm', 'G_norm', 'B_norm']]
    y = color_map['emotion']
    
    # Train/Test 분리 (8:2 비율, stratified)
    print("\n[Step 2] Train/Test 분리 (80/20, stratified)")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"  Train set: {len(X_train)} samples")
    print(f"  Test set : {len(X_test)} samples")
    
    # 모델 학습
    print("\n[Step 3] 모델 학습")
    print("  Training KNN...")
    print("  Training RandomForest...")
    knn, rf = train_models(X_train, y_train)
    print("  ✓ 모델 학습 완료")
    
    # 성능 평가
    print("\n[Step 4] 성능 평가 (테스트 셋)")
    results = evaluate_models(knn, rf, X_test, y_test)
    
    # 교차검증 (5-fold)
    print("\n[Step 5] 교차검증 (5-fold)")
    knn_cv_scores = cross_val_score(knn, X_train, y_train, cv=5, scoring='accuracy')
    rf_cv_scores = cross_val_score(rf, X_train, y_train, cv=5, scoring='accuracy')
    
    print(f"  KNN CV Accuracy       : {knn_cv_scores.mean():.4f} (+/- {knn_cv_scores.std():.4f})")
    print(f"  RandomForest CV Accuracy : {rf_cv_scores.mean():.4f} (+/- {rf_cv_scores.std():.4f})")
    
    # 상세 보고서 출력
    print_detailed_report(results)
    
    # 시각화
    print("[Step 6] 시각화")
    plot_model_comparison(results)
    plot_confusion_matrices(results)
    print("  ✓ 시각화 완료")
    
    # 시뮬레이션: 원본 main_.py처럼 이미지 분석 후 모델 적용
    print("\n[Step 7] 실시간 이미지 분석 (선택)")
    try:
        image_path = input("분석할 이미지 파일 경로 입력 (또는 Enter 스킵): ").strip()
    except KeyboardInterrupt:
        print("\n입력이 취소되었습니다.")
        return
    
    if not image_path:
        print("이미지 분석을 건너뜁니다.")
        return
    
    # 이미지 로딩 및 전처리
    img = cv2.imread(image_path)
    if img is None:
        print("이미지를 불러올 수 없습니다. 경로를 확인하세요.")
        return
    
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_resized = cv2.resize(img, (100, 100))
    
    # 현저성 계산
    gray = cv2.cvtColor(img_resized, cv2.COLOR_RGB2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    laplacian = cv2.Laplacian(blurred, cv2.CV_64F)
    saliencyMap = np.uint8(np.absolute(laplacian))
    _, salient_mask = cv2.threshold(saliencyMap, 10, 255, cv2.THRESH_BINARY)
    
    salient_pixels = img_resized[salient_mask == 255].reshape(-1, 3)
    
    if len(salient_pixels) == 0:
        print("현저한 영역이 감지되지 않았습니다.")
        return
    
    # KMeans로 대표 색상 추출
    desired_k = 3
    unique_salient_count = np.unique(salient_pixels, axis=0).shape[0]
    k = min(desired_k, len(salient_pixels), unique_salient_count)
    
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(salient_pixels)
    dominant_colors = kmeans.cluster_centers_
    
    # 두 모델로 감정 예측
    print("\n[결과] 추출 색상 감정 예측 (KNN vs RandomForest)")
    print("-" * 70)
    for i, (r, g, b) in enumerate(dominant_colors):
        knn_emotion = emotion_from_rgb_knn(knn, r, g, b)
        rf_emotion = emotion_from_rgb_rf(rf, r, g, b)
        agreement = "✓" if knn_emotion == rf_emotion else "✗"
        print(f"Color {i+1} RGB({int(r)}, {int(g)}, {int(b)})")
        print(f"  KNN          : {knn_emotion}")
        print(f"  RandomForest : {rf_emotion} {agreement}")


if __name__ == '__main__':
    main()
