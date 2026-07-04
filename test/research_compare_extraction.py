#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Research script for comparing color extraction strategies without touching main_.py.

Supported strategies:
- baseline_laplacian: current research baseline used in the original pipeline
- paint_region: proposed direction for drawn/digital artwork, focusing on painted areas
- paint_region_conservative: stricter version that favors precision over recall

The script prints extracted dominant colors and predicted emotions side by side,
and saves a comparison plot for visual inspection.
"""

import argparse
import glob
import os
from datetime import datetime

import cv2
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.neighbors import KNeighborsClassifier


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DATASET = os.path.join(BASE_DIR, 'color_emotion_labeled_augmented.csv')
DEFAULT_OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs')
DEFAULT_IMAGE_GLOBS = [
    os.path.join(BASE_DIR, 'C500x500.jpeg'),
    os.path.join(BASE_DIR, '94ElQ-mXfi0rKA9BWrrsxvSLNtRsvSEqaJzgmXM8a3SNwwxyJPgrqC-jiJo-BbajvE3g4AiI19ziwQrfe2ReVM2xJBfVRObuSrHh6T6nXTORV_vGCklbk9aVBzK9vFTO2LS9QR1keNSl3nw93CbSdA.jpg'),
]


def setup_plot_style():
    plt.rcParams['font.family'] = 'DejaVu Sans'
    plt.rcParams['axes.unicode_minus'] = False


def train_knn(dataset_path):
    df = pd.read_csv(dataset_path)
    for col in ['R', 'G', 'B']:
        df[col] = df[col] / 255.0

    model = KNeighborsClassifier(n_neighbors=3)
    model.fit(df[['R', 'G', 'B']].values, df['emotion'].values)
    return model


def emotion_from_rgb(model, rgb):
    r, g, b = rgb
    return model.predict([[r / 255.0, g / 255.0, b / 255.0]])[0]


def normalize_to_unit_interval(values):
    values = values.astype(np.float32)
    min_value = float(values.min())
    max_value = float(values.max())
    if max_value <= min_value:
        return np.zeros_like(values, dtype=np.float32)
    return (values - min_value) / (max_value - min_value)


def extract_baseline_laplacian(img_resized):
    gray = cv2.cvtColor(img_resized, cv2.COLOR_RGB2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    laplacian = cv2.Laplacian(blurred, cv2.CV_64F)
    saliency_map = np.uint8(np.absolute(laplacian))
    _, salient_mask = cv2.threshold(saliency_map, 10, 255, cv2.THRESH_BINARY)
    salient_pixels = img_resized[salient_mask == 255].reshape(-1, 3)
    return saliency_map, salient_mask, salient_pixels


def extract_paint_region(img_resized):
    hsv = cv2.cvtColor(img_resized, cv2.COLOR_RGB2HSV)
    saturation = hsv[:, :, 1].astype(np.float32) / 255.0
    value = hsv[:, :, 2].astype(np.float32) / 255.0

    gray = cv2.cvtColor(img_resized, cv2.COLOR_RGB2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edge_strength = np.abs(cv2.Laplacian(blurred, cv2.CV_64F))
    edge_strength = normalize_to_unit_interval(edge_strength)

    channel_max = img_resized.max(axis=2).astype(np.float32)
    channel_min = img_resized.min(axis=2).astype(np.float32)
    colorfulness = normalize_to_unit_interval(channel_max - channel_min)

    height, width = gray.shape
    yy, xx = np.mgrid[0:height, 0:width]
    center_x = (width - 1) / 2.0
    center_y = (height - 1) / 2.0
    center_distance = np.sqrt((xx - center_x) ** 2 + (yy - center_y) ** 2)
    centrality = 1.0 - (center_distance / center_distance.max())
    centrality = np.clip(centrality, 0.0, 1.0).astype(np.float32)

    # 그림에서는 경계보다 실제로 칠해진 면적과 화면 중심성이 더 중요하다고 가정한다.
    paint_score = (
        (0.33 * saturation)
        + (0.20 * value)
        + (0.20 * edge_strength)
        + (0.17 * colorfulness)
        + (0.10 * centrality)
    )
    paint_score = normalize_to_unit_interval(paint_score)

    threshold = float(np.percentile(paint_score, 70))
    salient_mask = np.uint8(paint_score >= threshold) * 255
    kernel = np.ones((3, 3), np.uint8)
    salient_mask = cv2.morphologyEx(salient_mask, cv2.MORPH_CLOSE, kernel)
    salient_mask = cv2.morphologyEx(salient_mask, cv2.MORPH_OPEN, kernel)

    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(salient_mask, connectivity=8)
    if num_labels > 1:
        component_areas = [(label, stats[label, cv2.CC_STAT_AREA]) for label in range(1, num_labels)]
        component_areas.sort(key=lambda item: item[1], reverse=True)
        keep_labels = {label for label, area in component_areas[:3] if area >= 25}
        refined_mask = np.zeros_like(salient_mask)
        for label in keep_labels:
            refined_mask[labels == label] = 255
        if refined_mask.any():
            salient_mask = cv2.dilate(refined_mask, kernel, iterations=1)

    salient_pixels = img_resized[salient_mask == 255].reshape(-1, 3)
    paint_map = np.uint8(paint_score * 255)
    return paint_map, salient_mask, salient_pixels


def extract_paint_region_conservative(img_resized):
    hsv = cv2.cvtColor(img_resized, cv2.COLOR_RGB2HSV)
    saturation = hsv[:, :, 1].astype(np.float32) / 255.0
    value = hsv[:, :, 2].astype(np.float32) / 255.0

    gray = cv2.cvtColor(img_resized, cv2.COLOR_RGB2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edge_strength = np.abs(cv2.Laplacian(blurred, cv2.CV_64F))
    edge_strength = normalize_to_unit_interval(edge_strength)

    channel_max = img_resized.max(axis=2).astype(np.float32)
    channel_min = img_resized.min(axis=2).astype(np.float32)
    colorfulness = normalize_to_unit_interval(channel_max - channel_min)

    height, width = gray.shape
    yy, xx = np.mgrid[0:height, 0:width]
    center_x = (width - 1) / 2.0
    center_y = (height - 1) / 2.0
    center_distance = np.sqrt((xx - center_x) ** 2 + (yy - center_y) ** 2)
    centrality = 1.0 - (center_distance / center_distance.max())
    centrality = np.clip(centrality, 0.0, 1.0).astype(np.float32)

    # precision 우선: 배경성 신호를 더 강하게 줄이고, 핵심 피사체 중심을 더 강하게 본다.
    paint_score = (
        (0.40 * saturation)
        + (0.15 * value)
        + (0.12 * edge_strength)
        + (0.13 * colorfulness)
        + (0.20 * centrality)
    )
    paint_score = normalize_to_unit_interval(paint_score)

    threshold = float(np.percentile(paint_score, 82))
    salient_mask = np.uint8(paint_score >= threshold) * 255
    kernel = np.ones((3, 3), np.uint8)
    salient_mask = cv2.morphologyEx(salient_mask, cv2.MORPH_CLOSE, kernel)
    salient_mask = cv2.morphologyEx(salient_mask, cv2.MORPH_OPEN, kernel)

    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(salient_mask, connectivity=8)
    if num_labels > 1:
        component_areas = [(label, stats[label, cv2.CC_STAT_AREA]) for label in range(1, num_labels)]
        component_areas.sort(key=lambda item: item[1], reverse=True)
        keep_labels = {label for label, area in component_areas[:2] if area >= 40}
        refined_mask = np.zeros_like(salient_mask)
        for label in keep_labels:
            refined_mask[labels == label] = 255
        if refined_mask.any():
            salient_mask = cv2.dilate(refined_mask, kernel, iterations=1)

    salient_pixels = img_resized[salient_mask == 255].reshape(-1, 3)
    paint_map = np.uint8(paint_score * 255)
    return paint_map, salient_mask, salient_pixels


def collect_image_paths(image_args):
    if image_args:
        paths = []
        for item in image_args:
            expanded = glob.glob(item)
            if expanded:
                paths.extend(expanded)
            else:
                paths.append(item)
        return [path for path in paths if os.path.exists(path)]

    paths = [path for path in DEFAULT_IMAGE_GLOBS if os.path.exists(path)]
    if paths:
        return paths

    collected = []
    for pattern in [
        os.path.join(BASE_DIR, '*.jpg'),
        os.path.join(BASE_DIR, '*.jpeg'),
        os.path.join(BASE_DIR, '*.png'),
        os.path.join(BASE_DIR, '*.webp'),
        os.path.join(BASE_DIR, '**', '*.jpg'),
        os.path.join(BASE_DIR, '**', '*.jpeg'),
        os.path.join(BASE_DIR, '**', '*.png'),
        os.path.join(BASE_DIR, '**', '*.webp'),
    ]:
        collected.extend(glob.glob(pattern, recursive=True))
    return sorted({path for path in collected if os.path.isfile(path)})


def dominant_colors_from_pixels(salient_pixels, desired_k=3):
    if len(salient_pixels) == 0:
        return np.empty((0, 3), dtype=int)

    unique_salient_count = np.unique(salient_pixels, axis=0).shape[0]
    k = min(desired_k, len(salient_pixels), unique_salient_count)
    if k <= 0:
        return np.empty((0, 3), dtype=int)

    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(salient_pixels)
    return np.clip(np.round(kmeans.cluster_centers_), 0, 255).astype(int)


def run_strategy(name, img_resized, knn_model):
    if name == 'baseline_laplacian':
        saliency_map, salient_mask, salient_pixels = extract_baseline_laplacian(img_resized)
    elif name == 'paint_region':
        saliency_map, salient_mask, salient_pixels = extract_paint_region(img_resized)
    elif name == 'paint_region_conservative':
        saliency_map, salient_mask, salient_pixels = extract_paint_region_conservative(img_resized)
    else:
        raise ValueError(f'Unknown strategy: {name}')

    colors = dominant_colors_from_pixels(salient_pixels)
    predictions = [(tuple(color.tolist()), emotion_from_rgb(knn_model, color)) for color in colors]
    return saliency_map, salient_mask, colors, predictions


def save_comparison_figure(output_dir, image_name, img_resized, result_map):
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = os.path.join(output_dir, f'research_extraction_compare_{timestamp}.png')

    plt.figure(figsize=(14, 10))

    plt.subplot(2, 3, 1)
    plt.title('Input Image')
    plt.imshow(img_resized)
    plt.axis('off')

    for idx, (strategy_name, payload) in enumerate(result_map.items(), start=2):
        saliency_map, salient_mask, colors, predictions = payload

        plt.subplot(2, 3, idx)
        plt.title(f'{strategy_name}\nSaliency')
        plt.imshow(saliency_map, cmap='gray')
        plt.axis('off')

        plt.subplot(2, 3, idx + 2)
        plt.title(f'{strategy_name}\nMask')
        plt.imshow(salient_mask, cmap='gray')
        plt.axis('off')

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f'✓ 비교 이미지 저장: {output_path}')


def print_strategy_result(strategy_name, colors, predictions):
    print(f'\n[{strategy_name}]')
    if len(colors) == 0:
        print('  추출된 대표 색상이 없습니다.')
        return

    for index, (color, emotion) in enumerate(predictions, start=1):
        r, g, b = color
        print(f'  Color {index}: RGB({r}, {g}, {b}) -> {emotion}')


def summarize_batch(results_by_image):
    total_images = len(results_by_image)
    if total_images == 0:
        print('\n[batch] 평가할 이미지가 없습니다.')
        return

    strategy_names = ['baseline_laplacian', 'paint_region', 'paint_region_conservative']
    summary = {name: {'top1': [], 'color_count': [], 'mask_ratio': []} for name in strategy_names}
    agreement_count = 0
    conservative_wins = 0

    print('\n[batch] Strategy Comparison Summary')
    print('-' * 72)
    for image_path, result_map in results_by_image.items():
        baseline_preds = [emotion for _, emotion in result_map['baseline_laplacian'][3]]
        paint_preds = [emotion for _, emotion in result_map['paint_region'][3]]
        conservative_preds = [emotion for _, emotion in result_map['paint_region_conservative'][3]]

        if baseline_preds and paint_preds and baseline_preds[0] == paint_preds[0]:
            agreement_count += 1

        if paint_preds and conservative_preds and paint_preds[0] != conservative_preds[0]:
            conservative_wins += 1

        print(f'Image: {os.path.basename(image_path)}')
        for strategy_name in strategy_names:
            saliency_map, salient_mask, colors, predictions = result_map[strategy_name]
            top1 = predictions[0][1] if predictions else 'N/A'
            mask_ratio = float(np.count_nonzero(salient_mask)) / salient_mask.size
            summary[strategy_name]['top1'].append(top1)
            summary[strategy_name]['color_count'].append(len(colors))
            summary[strategy_name]['mask_ratio'].append(mask_ratio)
            print(
                f'  {strategy_name:<20} top1={top1:<14} '
                f'colors={len(colors):<2} mask_ratio={mask_ratio:.3f}'
            )
        print()

    print('[batch] Aggregate Metrics')
    print('-' * 72)
    for strategy_name in strategy_names:
        avg_colors = float(np.mean(summary[strategy_name]['color_count'])) if summary[strategy_name]['color_count'] else 0.0
        avg_mask_ratio = float(np.mean(summary[strategy_name]['mask_ratio'])) if summary[strategy_name]['mask_ratio'] else 0.0
        top1_distribution = pd.Series(summary[strategy_name]['top1']).value_counts().to_dict()
        print(f'{strategy_name}:')
        print(f'  평균 대표 색상 수: {avg_colors:.2f}')
        print(f'  평균 마스크 비율: {avg_mask_ratio:.3f}')
        print(f'  top1 결과 분포: {top1_distribution}')

    print(f'\n[batch] baseline vs paint_region top1 일치율: {agreement_count}/{total_images} = {agreement_count / total_images:.2%}')
    print(f'[batch] paint_region 대비 conservative top1 차이 발생 이미지 수: {conservative_wins}/{total_images} = {conservative_wins / total_images:.2%}')


def main():
    parser = argparse.ArgumentParser(description='Compare baseline Laplacian vs paint-region extraction.')
    parser.add_argument('--image', help='Path to a single input image')
    parser.add_argument('--images', nargs='*', help='Multiple input images for batch evaluation')
    parser.add_argument('--dataset', default=DEFAULT_DATASET, help='Path to the color-emotion dataset CSV')
    parser.add_argument('--output-dir', default=DEFAULT_OUTPUT_DIR, help='Directory for comparison outputs')
    args = parser.parse_args()

    setup_plot_style()

    knn_model = train_knn(args.dataset)

    image_paths = collect_image_paths([args.image] if args.image else (args.images or []))
    if not image_paths:
        raise SystemExit('이미지를 찾을 수 없습니다. --image 또는 --images를 지정하세요.')

    results_by_image = {}
    print(f'\n데이터셋: {args.dataset}')
    print(f'배치 이미지 수: {len(image_paths)}')

    for image_path in image_paths:
        img = cv2.imread(image_path)
        if img is None:
            print(f'! 이미지를 불러올 수 없습니다: {image_path}')
            continue

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_resized = cv2.resize(img, (100, 100))

        result_map = {}
        for strategy_name in ['baseline_laplacian', 'paint_region', 'paint_region_conservative']:
            result_map[strategy_name] = run_strategy(strategy_name, img_resized, knn_model)

        results_by_image[image_path] = result_map

        print(f'\n비교 대상 이미지: {image_path}')
        for strategy_name, (_, _, colors, predictions) in result_map.items():
            print_strategy_result(strategy_name, colors, predictions)

        save_comparison_figure(args.output_dir, os.path.basename(image_path), img_resized, result_map)

    summarize_batch(results_by_image)


if __name__ == '__main__':
    main()