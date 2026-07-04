#!/usr/bin/env python3
import colorsys

import pandas as pd


INPUT_PATH = 'test/color_emotion_labeled_augmented.csv'

# 현재 데이터에 있는 대표 RGB와 충돌하는 항목은 하이브리드용으로만 아주 조금 조정한다.
CANONICAL_OVERRIDES = {
    'SAD': (124, 101, 78),
    'SPIRITUAL': (130, 85, 150),
}


def clamp_rgb(rgb):
    return tuple(max(0, min(255, int(v))) for v in rgb)


def rgb_to_hsv(rgb):
    r, g, b = [value / 255.0 for value in rgb]
    return colorsys.rgb_to_hsv(r, g, b)


def hsv_to_rgb(hsv):
    r, g, b = colorsys.hsv_to_rgb(*hsv)
    return clamp_rgb((round(r * 255), round(g * 255), round(b * 255)))


def make_variant(base_rgb, emotion, variant_index):
    hue, saturation, value = rgb_to_hsv(base_rgb)
    seed = sum(ord(ch) for ch in emotion)
    hue_shift = ((seed % 5) - 2) * 0.003
    sat_shift = 0.02 + (seed % 3) * 0.005
    val_shift = 0.02 + ((seed // 3) % 3) * 0.005

    if variant_index == 0:
        candidate = (
            hue + hue_shift,
            max(0.0, min(1.0, saturation * (1.0 - sat_shift))),
            max(0.0, min(1.0, value * (1.0 + val_shift))),
        )
    else:
        candidate = (
            hue - hue_shift,
            max(0.0, min(1.0, saturation * (1.0 + sat_shift))),
            max(0.0, min(1.0, value * (1.0 - val_shift))),
        )

    return hsv_to_rgb(candidate)


def nudge_rgb(rgb, step):
    r, g, b = rgb
    deltas = [
        (step, step, step),
        (step, 0, 0),
        (0, step, 0),
        (0, 0, step),
        (-step, -step, -step),
        (-step, 0, 0),
        (0, -step, 0),
        (0, 0, -step),
    ]
    return [clamp_rgb((r + dr, g + dg, b + db)) for dr, dg, db in deltas]


df = pd.read_csv(INPUT_PATH)
print(f"[초기] {len(df)}행, {df['emotion'].nunique()}개 감정")

print("\n[1단계] 정확 중복 제거")
before = len(df)
df = df.drop_duplicates(subset=['emotion', 'R', 'G', 'B'], keep='first').copy()
print(f"  제거: {before - len(df)}행")
print(f"  결과: {len(df)}행")

print("\n[2단계] 하이브리드 재구성")
emotion_order = []
for emotion in df['emotion']:
    if emotion not in emotion_order:
        emotion_order.append(emotion)

canonical_rows = {}
for emotion in emotion_order:
    canonical_rows[emotion] = df[df['emotion'] == emotion].iloc[0].to_dict()

new_rows = []
used_rgbs = set()

for emotion in emotion_order:
    base_row = canonical_rows[emotion].copy()
    base_rgb = CANONICAL_OVERRIDES.get(emotion, (int(base_row['R']), int(base_row['G']), int(base_row['B'])))

    # 대표 RGB를 먼저 확보하고, 이미 사용 중이면 아주 작게만 이동한다.
    candidate_bases = [base_rgb] + nudge_rgb(base_rgb, 2) + nudge_rgb(base_rgb, 3)
    chosen_base = None
    for candidate in candidate_bases:
        if candidate not in used_rgbs:
            chosen_base = candidate
            break
    if chosen_base is None:
        chosen_base = candidate_bases[-1]

    used_rgbs.add(chosen_base)
    base_row['R'], base_row['G'], base_row['B'] = chosen_base
    new_rows.append(base_row)

    for variant_index in range(2):
        variant_rgb = make_variant(chosen_base, emotion, variant_index)
        candidate_variants = [variant_rgb] + nudge_rgb(variant_rgb, 1) + nudge_rgb(variant_rgb, 2)

        chosen_variant = None
        for candidate in candidate_variants:
            if candidate not in used_rgbs:
                chosen_variant = candidate
                break
        if chosen_variant is None:
            chosen_variant = candidate_variants[-1]

        used_rgbs.add(chosen_variant)
        variant_row = base_row.copy()
        variant_row['R'], variant_row['G'], variant_row['B'] = chosen_variant
        new_rows.append(variant_row)

hybrid_df = pd.DataFrame(new_rows)
hybrid_df = hybrid_df.drop_duplicates(subset=['emotion', 'R', 'G', 'B'], keep='first').copy()

hybrid_df.to_csv(INPUT_PATH, index=False)

vc_final = hybrid_df['emotion'].value_counts()
rgb_conflicts = hybrid_df.groupby(['R', 'G', 'B'])['emotion'].nunique()
conflict_count = int((rgb_conflicts > 1).sum())

print(f"\n[최종] {len(hybrid_df)}행, {hybrid_df['emotion'].nunique()}개 감정")
print(f"  Singleton: {(vc_final == 1).sum()}")
print(f"  2샘플: {(vc_final == 2).sum()}")
print(f"  3+ 샘플: {(vc_final >= 3).sum()}")
print(f"  RGB 충돌: {conflict_count}")
