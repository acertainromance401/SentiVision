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
import matplotlib
matplotlib.use('Agg')  # 헤드리스 환경에서도 이미지 파일 저장 보장
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
from datetime import datetime
from pathlib import Path
import json
import shutil


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'color_emotion_labeled_updated.csv')
OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs')
DATASET_VERSIONS_DIR = os.path.join(BASE_DIR, 'dataset_versions')
FIXED_VALIDATION_PATH = os.path.join(BASE_DIR, 'fixed_validation_indices.json')
UPDATE_HISTORY_PATH = os.path.join(BASE_DIR, 'model_update_history.csv')
RUN_TAG = datetime.now().strftime('%Y%m%d_%H%M%S')
OUTPUT_PREFIX = f'comparison_{RUN_TAG}'
SAVE_EXTRA_DEBUG_PLOTS = False  # True면 RGB 3D, Saliency 디버그 이미지를 추가 저장
REPEATED_EVAL_RUNS = 30  # 단일 분할 편차를 줄이기 위한 반복 평가 횟수
RF_ADV_MARGIN_ACC = 0.03  # RF 우세 판정용 최소 Accuracy 평균 격차
RF_ADV_MARGIN_F1 = 0.03   # RF 우세 판정용 최소 F1 평균 격차

LABEL_GROUPS = {
    '활력/행동': [
        'ALERTNESS', 'COURAGE', 'DYNAMIC', 'ENERGY', 'EXCITEMENT', 'HAPPINESS',
        'INTENSITY', 'LIVELY', 'OPTIMISM', 'PASSION', 'STRENGTH', 'URGENCY',
        'WARMTH',
    ],
    '안정/회복': [
        'BALANCE', 'CALMNESS', 'COMFORT', 'CONNECTION', 'DURABILITY', 'FREEDOM',
        'FRESHNESS', 'GROWTH', 'HARMONY', 'HEALING', 'HOPE', 'HONESTY',
        'PEACE', 'RENEWAL', 'SECURITY', 'STABILITY', 'STILLNESS', 'TRANQUILITY',
        'TRUST',
    ],
    '관계/애정': [
        'COOPERATION', 'FEMININE', 'FRIENDSHIP', 'LOVE', 'ROMANCE',
    ],
    '권위/가치': [
        'ABUNDANCE', 'AUTHORITY', 'CONFIDENCE', 'DEPTH', 'ELEGANCE', 'IDEALISTIC',
        'PRACTICAL', 'REALITY', 'ROYALTY', 'SOPHISTICATION', 'WEALTH',
    ],
    '창의/의미': [
        'BEAUTY', 'CREATIVITY', 'IDEALISTIC', 'MYSTERY', 'SPIRITUAL',
    ],
    '자연/중립': [
        'GROUNDED', 'IMMATURITY', 'MILITARY', 'NATURE', 'RESERVED',
    ],
    '긴장/위협': [
        'ANXIETY', 'CAUTION', 'CHAOS', 'COWARDICE', 'EGOTISM', 'FEAR', 'PROTEST',
        'SIN', 'TENSION', 'VULGARITY',
    ],
    '어둠/상실': [
        'ALIENATION', 'COLDNESS', 'DARKNESS', 'DEATH', 'DEPRESSION', 'DESPAIR',
        'DULLNESS', 'FATIGUE', 'ISOLATION', 'LONELINESS', 'LOSS', 'SAD',
    ],
}

PLOT_FILES = {
    'dashboard': f'{OUTPUT_PREFIX}_performance_dashboard.png',
    'rgb_3d': f'{OUTPUT_PREFIX}_rgb_3d_distribution.png',
    'saliency': f'{OUTPUT_PREFIX}_saliency_maps.png',
    'dominant': f'{OUTPUT_PREFIX}_dominant_color_emotions.png',
    'prediction_pair': f'{OUTPUT_PREFIX}_knn_rf_color_pair.png',
}

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
    """플롯을 파일로 저장한다. (Agg 백엔드 사용)"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    save_path = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✓ 이미지 저장: {save_path}")


def cleanup_old_comparison_outputs():
    """현재 실행 결과를 제외한 과거 comparison 출력 이미지를 정리한다."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    keep_files = set(PLOT_FILES.values())
    removed = 0
    for old_file in Path(OUTPUT_DIR).glob('comparison_*.png'):
        if old_file.name in keep_files:
            continue
        old_file.unlink()
        removed += 1

    if removed > 0:
        print(f"✓ 구버전 comparison 이미지 정리: {removed}개 삭제")


def load_or_create_fixed_validation_indices(color_map, emotion_series, path=FIXED_VALIDATION_PATH):
    """고정 검증셋 인덱스를 로드하거나 최초 1회 생성한다."""
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            payload = json.load(f)
        indices = payload.get('indices', [])
        if indices and max(indices) < len(color_map):
            print(f"✓ 고정 검증셋 로드: {len(indices)} samples")
            return indices
        print("! 고정 검증셋 인덱스가 현재 데이터셋 길이와 맞지 않아 재생성합니다.")

    all_indices = np.arange(len(color_map))
    class_counts = emotion_series.value_counts()
    stratify_target = emotion_series if class_counts.min() >= 2 else None

    _, validation_indices = train_test_split(
        all_indices,
        test_size=0.2,
        random_state=42,
        stratify=stratify_target,
    )
    validation_indices = sorted(validation_indices.tolist())

    payload = {
        'created_at': datetime.now().isoformat(),
        'dataset_rows_at_creation': len(color_map),
        'indices': validation_indices,
    }
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"✓ 고정 검증셋 생성: {len(validation_indices)} samples")
    return validation_indices


def split_with_fixed_validation(X, y, validation_indices):
    """고정 검증셋 인덱스를 사용해 train/validation을 분리한다."""
    validation_index_set = set(validation_indices)
    train_mask = [idx not in validation_index_set for idx in range(len(X))]
    val_mask = [idx in validation_index_set for idx in range(len(X))]

    X_train = X.iloc[train_mask].reset_index(drop=True)
    y_train = y.iloc[train_mask].reset_index(drop=True)
    X_val = X.iloc[val_mask].reset_index(drop=True)
    y_val = y.iloc[val_mask].reset_index(drop=True)
    return X_train, X_val, y_train, y_val


def build_grouped_label_menu(labels):
    """감정 라벨을 감정군별로 묶고 선택 순서를 만든다."""
    unique_labels = []
    seen = set()
    for label in labels:
        if label not in seen:
            unique_labels.append(label)
            seen.add(label)

    grouped = []
    assigned = set()
    for group_name, group_labels in LABEL_GROUPS.items():
        current_labels = [label for label in group_labels if label in seen and label not in assigned]
        if current_labels:
            grouped.append((group_name, current_labels))
            assigned.update(current_labels)

    remaining = sorted([label for label in unique_labels if label not in assigned])
    if remaining:
        grouped.append(('기타', remaining))

    ordered_labels = []
    for _, group_labels in grouped:
        ordered_labels.extend(group_labels)

    return ordered_labels, grouped


def render_label_menu(labels, columns=3):
    """선택 가능한 감정 라벨 목록을 감정군별 번호 목록으로 출력한다."""
    print("\n[선택 가능한 감정 라벨 목록]")
    ordered_labels, grouped = build_grouped_label_menu(labels)
    label_to_index = {label: idx for idx, label in enumerate(ordered_labels, start=1)}

    for group_name, group_labels in grouped:
        print(f"\n- {group_name}")
        rows = [f"{label_to_index[label]:>2}. {label:<15}" for label in group_labels]
        for start in range(0, len(rows), columns):
            print("  ".join(rows[start:start + columns]))


def prompt_for_label_choice(labels, default_label):
    """라벨 번호 선택형 입력을 제공한다."""
    ordered_labels, _ = build_grouped_label_menu(labels)
    while True:
        raw = input("  최종 감정 번호 입력 (Enter=RF 사용, ?=목록 다시 보기): ").strip()
        if raw == "":
            return default_label, 'rf_default'
        if raw == '?':
            render_label_menu(labels)
            continue
        if raw.isdigit():
            selected_index = int(raw)
            if 1 <= selected_index <= len(ordered_labels):
                return ordered_labels[selected_index - 1], 'user_select'
        print("  올바른 번호를 입력하세요.")


def backup_dataset_version(data_path):
    """CSV 수정 전 버전 백업을 저장한다."""
    os.makedirs(DATASET_VERSIONS_DIR, exist_ok=True)
    backup_name = f"color_emotion_labeled_updated_{RUN_TAG}.csv"
    backup_path = os.path.join(DATASET_VERSIONS_DIR, backup_name)
    shutil.copy2(data_path, backup_path)
    print(f"✓ CSV 백업 저장: {backup_path}")
    return backup_path


def log_update_history(results, repeated_summary, stats, rows_before, rows_after, backup_path):
    """업데이트 전후 성능 및 데이터 변경 이력을 CSV로 남긴다."""
    history_row = pd.DataFrame([{
        'timestamp': datetime.now().isoformat(),
        'run_tag': RUN_TAG,
        'backup_path': backup_path,
        'rows_before': rows_before,
        'rows_after': rows_after,
        'appended_rows': stats['appended'],
        'duplicates_skipped': stats['duplicates_skipped'],
        'conflicts_skipped': stats['conflicts_skipped'],
        'conflicts_appended': stats['conflicts_appended'],
        'knn_val_acc': results['knn_acc'],
        'rf_val_acc': results['rf_acc'],
        'knn_val_f1': results['knn_f1'],
        'rf_val_f1': results['rf_f1'],
        'repeated_knn_acc_mean': repeated_summary['knn_acc_mean'],
        'repeated_rf_acc_mean': repeated_summary['rf_acc_mean'],
        'repeated_knn_f1_mean': repeated_summary['knn_f1_mean'],
        'repeated_rf_f1_mean': repeated_summary['rf_f1_mean'],
        'rf_better_margin': repeated_summary['rf_better_margin'],
    }])

    if os.path.exists(UPDATE_HISTORY_PATH):
        old_history = pd.read_csv(UPDATE_HISTORY_PATH)
        history_df = pd.concat([old_history, history_row], ignore_index=True)
    else:
        history_df = history_row

    history_df.to_csv(UPDATE_HISTORY_PATH, index=False)
    print(f"✓ 업데이트 이력 저장: {UPDATE_HISTORY_PATH}")


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


def repeated_holdout_comparison(X, y, runs=REPEATED_EVAL_RUNS, test_size=0.2):
    """여러 랜덤 분할로 KNN/RF를 반복 평가해 평균/분산을 계산한다."""
    knn_acc_scores = []
    rf_acc_scores = []
    knn_f1_scores = []
    rf_f1_scores = []

    class_counts = y.value_counts()
    can_stratify = class_counts.min() >= 2
    stratify_target = y if can_stratify else None

    for seed in range(runs):
        X_train_r, X_test_r, y_train_r, y_test_r = train_test_split(
            X,
            y,
            test_size=test_size,
            random_state=42 + seed,
            stratify=stratify_target,
        )

        knn_r, rf_r = train_models(X_train_r, y_train_r)
        eval_r = evaluate_models(knn_r, rf_r, X_test_r, y_test_r)

        knn_acc_scores.append(eval_r['knn_acc'])
        rf_acc_scores.append(eval_r['rf_acc'])
        knn_f1_scores.append(eval_r['knn_f1'])
        rf_f1_scores.append(eval_r['rf_f1'])

    knn_acc_arr = np.array(knn_acc_scores)
    rf_acc_arr = np.array(rf_acc_scores)
    knn_f1_arr = np.array(knn_f1_scores)
    rf_f1_arr = np.array(rf_f1_scores)

    summary = {
        'runs': runs,
        'can_stratify': can_stratify,
        'knn_acc_mean': float(knn_acc_arr.mean()),
        'rf_acc_mean': float(rf_acc_arr.mean()),
        'knn_acc_std': float(knn_acc_arr.std()),
        'rf_acc_std': float(rf_acc_arr.std()),
        'knn_f1_mean': float(knn_f1_arr.mean()),
        'rf_f1_mean': float(rf_f1_arr.mean()),
        'knn_f1_std': float(knn_f1_arr.std()),
        'rf_f1_std': float(rf_f1_arr.std()),
        'acc_diff_mean': float((rf_acc_arr - knn_acc_arr).mean()),
        'f1_diff_mean': float((rf_f1_arr - knn_f1_arr).mean()),
        'rf_acc_win_rate': float((rf_acc_arr > knn_acc_arr).mean()),
        'rf_f1_win_rate': float((rf_f1_arr > knn_f1_arr).mean()),
    }

    summary['rf_better_mean'] = (
        summary['rf_acc_mean'] > summary['knn_acc_mean']
        and summary['rf_f1_mean'] > summary['knn_f1_mean']
    )
    summary['rf_better_margin'] = (
        summary['acc_diff_mean'] >= RF_ADV_MARGIN_ACC
        and summary['f1_diff_mean'] >= RF_ADV_MARGIN_F1
    )
    summary['rf_better_robust'] = summary['rf_better_margin']

    return summary


def plot_performance_dashboard(results, repeated_summary=None):
    """정확도/F1/혼동행렬을 2x2 대시보드 한 장으로 저장한다."""
    knn_acc = results['knn_acc']
    rf_acc = results['rf_acc']
    knn_f1 = results['knn_f1']
    rf_f1 = results['rf_f1']

    knn_cm = results['knn_cm']
    rf_cm = results['rf_cm']
    classes = results['classes']

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    # 정확도 비교
    models = ['KNN', 'RandomForest']
    accuracies = [knn_acc, rf_acc]
    colors = ['#FF6B6B', '#4ECDC4']
    axes[0, 0].bar(models, accuracies, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
    axes[0, 0].set_ylabel('Accuracy', fontsize=12)
    axes[0, 0].set_title('Model Accuracy Comparison', fontsize=14, fontweight='bold')
    axes[0, 0].set_ylim([0, 1])
    for i, acc in enumerate(accuracies):
        axes[0, 0].text(i, acc + 0.02, f'{acc:.3f}', ha='center', fontsize=11, fontweight='bold')

    # F1 스코어 비교
    f1_scores = [knn_f1, rf_f1]
    axes[0, 1].bar(models, f1_scores, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
    axes[0, 1].set_ylabel('F1 Score (Weighted)', fontsize=12)
    axes[0, 1].set_title('Model F1 Score Comparison', fontsize=14, fontweight='bold')
    axes[0, 1].set_ylim([0, 1])
    for i, f1 in enumerate(f1_scores):
        axes[0, 1].text(i, f1 + 0.02, f'{f1:.3f}', ha='center', fontsize=11, fontweight='bold')

    # KNN 혼동 행렬
    im0 = axes[1, 0].imshow(knn_cm, cmap='Blues', aspect='auto')
    axes[1, 0].set_title('KNN Confusion Matrix', fontsize=14, fontweight='bold')
    axes[1, 0].set_ylabel('True Label', fontsize=11)
    axes[1, 0].set_xlabel('Predicted Label', fontsize=11)
    axes[1, 0].set_xticks(range(len(classes)))
    axes[1, 0].set_yticks(range(len(classes)))
    axes[1, 0].set_xticklabels(classes, rotation=45, ha='right')
    axes[1, 0].set_yticklabels(classes)
    # 셀에 값 표시
    for i in range(len(classes)):
        for j in range(len(classes)):
            axes[1, 0].text(
                j,
                i,
                int(knn_cm[i, j]),
                ha="center",
                va="center",
                color="black",
                fontsize=10,
            )
    plt.colorbar(im0, ax=axes[1, 0], label='Count')

    # RandomForest 혼동 행렬
    im1 = axes[1, 1].imshow(rf_cm, cmap='Greens', aspect='auto')
    axes[1, 1].set_title('RandomForest Confusion Matrix', fontsize=14, fontweight='bold')
    axes[1, 1].set_ylabel('True Label', fontsize=11)
    axes[1, 1].set_xlabel('Predicted Label', fontsize=11)
    axes[1, 1].set_xticks(range(len(classes)))
    axes[1, 1].set_yticks(range(len(classes)))
    axes[1, 1].set_xticklabels(classes, rotation=45, ha='right')
    axes[1, 1].set_yticklabels(classes)
    # 셀에 값 표시
    for i in range(len(classes)):
        for j in range(len(classes)):
            axes[1, 1].text(
                j,
                i,
                int(rf_cm[i, j]),
                ha="center",
                va="center",
                color="black",
                fontsize=10,
            )
    plt.colorbar(im1, ax=axes[1, 1], label='Count')

    if repeated_summary is not None:
        summary_text = (
            f"Repeated({repeated_summary['runs']}) "
            f"Acc KNN/RF: {repeated_summary['knn_acc_mean']:.3f}/{repeated_summary['rf_acc_mean']:.3f} "
            f"Win {repeated_summary['rf_acc_win_rate'] * 100:.1f}% | "
            f"F1 KNN/RF: {repeated_summary['knn_f1_mean']:.3f}/{repeated_summary['rf_f1_mean']:.3f} "
            f"Win {repeated_summary['rf_f1_win_rate'] * 100:.1f}% | "
            f"Margin(Acc/F1) >= {RF_ADV_MARGIN_ACC:.2f}/{RF_ADV_MARGIN_F1:.2f}"
        )
        fig.text(
            0.5,
            0.995,
            summary_text,
            ha='center',
            va='top',
            fontsize=10,
            bbox={'facecolor': 'white', 'alpha': 0.8, 'edgecolor': '#cccccc'},
        )

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    finalize_plot(PLOT_FILES['dashboard'])


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


def print_repeated_report(summary):
    """반복 분할 평가 결과를 출력한다."""
    print("\n" + "="*70)
    print(f"REPEATED HOLDOUT REPORT ({summary['runs']} runs)")
    print("="*70)
    print(f"  Stratified split 가능 여부: {summary['can_stratify']}")

    print("\n[ACCURACY - mean ± std]")
    print(f"  KNN          : {summary['knn_acc_mean']:.4f} ± {summary['knn_acc_std']:.4f}")
    print(f"  RandomForest : {summary['rf_acc_mean']:.4f} ± {summary['rf_acc_std']:.4f}")
    print(f"  평균 차이(RF-KNN): {summary['acc_diff_mean']:+.4f}")
    print(f"  RF 승률         : {summary['rf_acc_win_rate'] * 100:.1f}%")

    print("\n[F1 Weighted - mean ± std]")
    print(f"  KNN          : {summary['knn_f1_mean']:.4f} ± {summary['knn_f1_std']:.4f}")
    print(f"  RandomForest : {summary['rf_f1_mean']:.4f} ± {summary['rf_f1_std']:.4f}")
    print(f"  평균 차이(RF-KNN): {summary['f1_diff_mean']:+.4f}")
    print(f"  RF 승률         : {summary['rf_f1_win_rate'] * 100:.1f}%")

    robust_label = "RF 우세" if summary['rf_better_robust'] else "우세 불확실/비우세"
    print("\n[판정 기준]")
    print("  RF가 KNN보다 정확하다고 판단: "
          "(반복 평균 Accuracy/F1 격차가 각각 margin 이상일 때)")
    print(f"  margin 조건: Accuracy ≥ {RF_ADV_MARGIN_ACC:.2f}, F1 ≥ {RF_ADV_MARGIN_F1:.2f}")
    print(f"  평균 우세 여부: {summary['rf_better_mean']}")
    print(f"  margin 우세 여부: {summary['rf_better_margin']}")
    print(f"  판정 결과: {robust_label}")
    print("="*70 + "\n")


def plot_rgb_3d_distribution(color_map):
    """학습 데이터 RGB 분포를 3D로 시각화해 저장한다."""
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    for _, row in color_map.iterrows():
        color = (row['R_norm'], row['G_norm'], row['B_norm'])
        ax.scatter(row['R'], row['G'], row['B'], color=color, s=100)
        ax.text(row['R'], row['G'], row['B'] + 5, f"{row['emotion']}", fontsize=8)
    ax.set_xlabel('Red')
    ax.set_ylabel('Green')
    ax.set_zlabel('Blue')
    ax.set_title('RGB 3Dimension', fontsize=15)
    plt.tight_layout()
    finalize_plot(PLOT_FILES['rgb_3d'])


def plot_saliency_maps(saliency_map, salient_mask):
    """Saliency map과 mask를 저장한다."""
    plt.figure(figsize=(8, 4))
    plt.subplot(1, 2, 1)
    plt.title("Saliency Map")
    plt.imshow(saliency_map, cmap="gray")
    plt.axis("off")

    plt.subplot(1, 2, 2)
    plt.title("Salient Region Mask")
    plt.imshow(salient_mask, cmap="gray")
    plt.axis("off")
    plt.tight_layout()
    finalize_plot(PLOT_FILES['saliency'])


def plot_dominant_color_emotions(dominant_colors, knn, rf):
    """대표 색상과 KNN/RF 예측 감정을 함께 시각화해 저장한다."""
    plt.figure(figsize=(14, 6))
    for i, (r, g, b) in enumerate(dominant_colors):
        knn_emotion = emotion_from_rgb_knn(knn, r, g, b)
        rf_emotion = emotion_from_rgb_rf(rf, r, g, b)
        plt.bar(i, 1, color=(r / 255, g / 255, b / 255))
        plt.text(
            i,
            1.05,
            f"KNN: {knn_emotion}\nRF: {rf_emotion}",
            ha='center',
            va='bottom',
            fontsize=9,
        )

    plt.xticks(range(len(dominant_colors)), [f'Color {i + 1}' for i in range(len(dominant_colors))])
    plt.yticks([])
    plt.tight_layout()
    finalize_plot(PLOT_FILES['dominant'])


def plot_knn_rf_color_pair(dominant_colors, knn, rf):
    """대표 색상에 대한 KNN/RF 예측을 좌우 서브플롯 한 쌍으로 저장한다."""
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    model_specs = [
        (axes[0], 'KNN', knn, emotion_from_rgb_knn),
        (axes[1], 'RandomForest', rf, emotion_from_rgb_rf),
    ]

    for ax, model_name, model_obj, predictor in model_specs:
        for i, (r, g, b) in enumerate(dominant_colors):
            emotion = predictor(model_obj, r, g, b)
            ax.bar(i, 1, color=(r / 255, g / 255, b / 255))
            ax.text(i, 1.05, emotion, ha='center', va='bottom', fontsize=10)

        ax.set_title(f'{model_name} Color Emotion Prediction', fontsize=13, fontweight='bold')
        ax.set_xticks(range(len(dominant_colors)))
        ax.set_xticklabels([f'Color {i + 1}' for i in range(len(dominant_colors))])
        ax.set_yticks([])
        ax.set_ylim([0, 1.2])

    plt.tight_layout()
    finalize_plot(PLOT_FILES['prediction_pair'])


def collect_user_emotion_feedback(dominant_colors, knn, rf, data_path, labels, results, repeated_summary):
    """사용자 최종 감정을 선택형으로 받아 데이터셋에 규칙적으로 반영한다."""
    print("\n[Step 8] 사용자 감정 입력(선택)")
    print("- Enter: RF 예측값 사용")
    print("- 번호 입력: 기존 라벨 목록 중 하나 선택")
    render_label_menu(labels)

    feedback_rows = []
    for i, (r, g, b) in enumerate(dominant_colors):
        knn_emotion = emotion_from_rgb_knn(knn, r, g, b)
        rf_emotion = emotion_from_rgb_rf(rf, r, g, b)

        print(f"\n[{i+1}] RGB({int(r)}, {int(g)}, {int(b)})")
        print(f"  KNN: {knn_emotion}")
        print(f"  RF : {rf_emotion}")

        try:
            final_emotion, input_source = prompt_for_label_choice(labels, rf_emotion)
        except (KeyboardInterrupt, EOFError):
            print("\n입력이 중단되어 사용자 감정 입력 단계를 종료합니다.")
            break

        feedback_rows.append({
            'emotion': final_emotion,
            'R': int(r),
            'G': int(g),
            'B': int(b),
            'color_name': np.nan,
            'color_label': np.nan,
            'input_source': input_source,
            'knn_emotion': knn_emotion,
            'rf_emotion': rf_emotion,
        })

    if not feedback_rows:
        print("사용자 피드백이 없어 저장하지 않습니다.")
        return

    existing_df = pd.read_csv(data_path)
    rows_before = len(existing_df)

    stats = {
        'appended': 0,
        'duplicates_skipped': 0,
        'conflicts_skipped': 0,
        'conflicts_appended': 0,
    }

    accepted_rows = []
    working_df = existing_df.copy()

    for row in feedback_rows:
        exact_duplicate = (
            (working_df['emotion'] == row['emotion'])
            & (working_df['R'] == row['R'])
            & (working_df['G'] == row['G'])
            & (working_df['B'] == row['B'])
        )
        if exact_duplicate.any():
            stats['duplicates_skipped'] += 1
            print(f"- 중복 스킵: {row['emotion']} / RGB({row['R']}, {row['G']}, {row['B']})")
            continue

        conflict_mask = (
            (working_df['R'] == row['R'])
            & (working_df['G'] == row['G'])
            & (working_df['B'] == row['B'])
            & (working_df['emotion'] != row['emotion'])
        )
        conflict_labels = sorted(working_df.loc[conflict_mask, 'emotion'].dropna().astype(str).unique())
        if conflict_labels:
            print(
                f"- 충돌 감지: RGB({row['R']}, {row['G']}, {row['B']})에 기존 감정 {conflict_labels} 존재"
            )
            try:
                conflict_input = input("  이 감정을 추가로 저장할까요? (y/N): ").strip().lower()
            except (KeyboardInterrupt, EOFError):
                conflict_input = 'n'

            if conflict_input not in {'y', 'yes'}:
                stats['conflicts_skipped'] += 1
                print("  → 충돌 항목 저장 안 함")
                continue

            stats['conflicts_appended'] += 1

        accepted_rows.append(row)
        working_df = pd.concat([
            working_df,
            pd.DataFrame([{
                'emotion': row['emotion'],
                'R': row['R'],
                'G': row['G'],
                'B': row['B'],
                'color_name': np.nan,
                'color_label': np.nan,
            }])
        ], ignore_index=True)
        stats['appended'] += 1

    if not accepted_rows:
        print("저장할 신규 데이터가 없습니다.")
        return

    backup_path = backup_dataset_version(data_path)
    new_feedback_df = pd.DataFrame(accepted_rows)
    new_feedback_df = new_feedback_df.drop(columns=['input_source', 'knn_emotion', 'rf_emotion'])

    # 기존 CSV 스키마 순서에 맞춰 신규 데이터를 정렬한다.
    for col in existing_df.columns:
        if col not in new_feedback_df.columns:
            new_feedback_df[col] = np.nan
    new_feedback_df = new_feedback_df[existing_df.columns]

    merged_df = pd.concat([existing_df, new_feedback_df], ignore_index=True)
    merged_df.to_csv(data_path, index=False)
    print(f"✓ 사용자 감정 피드백 {len(new_feedback_df)}건 추가 저장: {data_path}")
    log_update_history(results, repeated_summary, stats, rows_before, len(merged_df), backup_path)


def main():
    """모델 비교 파이프라인 실행."""
    setup_plot_style()
    cleanup_old_comparison_outputs()
    
    print("[Step 1] CSV 로드 및 데이터 준비")
    # 데이터 로드
    color_map = pd.read_csv(DATA_PATH)
    color_map = pd.DataFrame(color_map)
    
    # 데이터셋 스키마 차이를 흡수: emotion/Emotion 모두 지원
    if 'emotion' in color_map.columns:
        emotion_col = 'emotion'
    elif 'Emotion' in color_map.columns:
        emotion_col = 'Emotion'
    else:
        raise KeyError("감정 라벨 컬럼(emotion 또는 Emotion)을 찾을 수 없습니다.")

    color_map[emotion_col] = color_map[emotion_col].map(normalize_emotion_label)
    
    print(f"  Total samples: {len(color_map)}")
    print(f"  Emotion classes: {color_map[emotion_col].nunique()}")
    
    # RGB 정규화
    color_map['R_norm'] = color_map['R'] / 255
    color_map['G_norm'] = color_map['G'] / 255
    color_map['B_norm'] = color_map['B'] / 255
    
    # 학습용 데이터 분리
    X = color_map[['R_norm', 'G_norm', 'B_norm']]
    y = color_map[emotion_col]

    # 출력 파일 과다 생성을 줄이기 위해 디버그 플롯은 선택 저장
    if SAVE_EXTRA_DEBUG_PLOTS:
        print("\n[Step 1-1] RGB 3D 분포 시각화 저장")
        plot_rgb_3d_distribution(color_map)
    
    # 고정 검증셋 분리
    print("\n[Step 2] 고정 검증셋 분리")
    validation_indices = load_or_create_fixed_validation_indices(color_map, y)
    X_train, X_test, y_train, y_test = split_with_fixed_validation(X, y, validation_indices)
    print(f"  Train set      : {len(X_train)} samples")
    print(f"  Validation set : {len(X_test)} samples")
    
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
    print("\n[Step 5] 교차검증")
    train_min_class = y_train.value_counts().min()
    cv_folds = min(5, int(train_min_class))

    if cv_folds >= 2:
        print(f"  - CV folds: {cv_folds}")
        knn_cv_scores = cross_val_score(knn, X_train, y_train, cv=cv_folds, scoring='accuracy')
        rf_cv_scores = cross_val_score(rf, X_train, y_train, cv=cv_folds, scoring='accuracy')

        print(f"  KNN CV Accuracy          : {knn_cv_scores.mean():.4f} (+/- {knn_cv_scores.std():.4f})")
        print(f"  RandomForest CV Accuracy : {rf_cv_scores.mean():.4f} (+/- {rf_cv_scores.std():.4f})")
    else:
        print("  - 교차검증 생략 (훈련 데이터의 최소 클래스 샘플 수 < 2)")
    
    # 상세 보고서 출력
    print_detailed_report(results)

    # 반복 분할 평가로 안정적인 우세 판정
    print("[Step 5-1] 반복 분할 평가")
    repeated_summary = repeated_holdout_comparison(X_train, y_train)
    print_repeated_report(repeated_summary)
    
    # 시각화
    print("[Step 6] 시각화")
    plot_performance_dashboard(results, repeated_summary)
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

    # 출력 파일 과다 생성을 줄이기 위해 디버그 플롯은 선택 저장
    if SAVE_EXTRA_DEBUG_PLOTS:
        plot_saliency_maps(saliencyMap, salient_mask)
    
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

    # KNN/RF를 좌우 서브플롯 한 쌍으로 저장
    plot_knn_rf_color_pair(dominant_colors, knn, rf)

    # 사용자 최종 감정 입력(선택)
    label_choices = sorted(y.dropna().astype(str).unique())
    collect_user_emotion_feedback(dominant_colors, knn, rf, DATA_PATH, label_choices, results, repeated_summary)


if __name__ == '__main__':
    main()
