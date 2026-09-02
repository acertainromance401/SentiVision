#!/usr/bin/env python3
"""
각 감정 패밀리의 대표색(RGB 평균)을 계산합니다.
"""

from collections import defaultdict
from pathlib import Path

import pandas as pd

data_path = Path(__file__).resolve().with_name(
    "color_emotion_labeled_augmented_with_family.csv"
)
df = pd.read_csv(data_path)

# 각 family별 RGB 평균 계산
family_colors = defaultdict(lambda: {'R': [], 'G': [], 'B': []})

for _, row in df.iterrows():
    family = row['family']
    family_colors[family]['R'].append(row['R'])
    family_colors[family]['G'].append(row['G'])
    family_colors[family]['B'].append(row['B'])

# 평균 계산 및 출력
print("감정 패밀리 대표색 (RGB 평균):\n")
print("Family\t\t| R\t| G\t| B\t| Hex")
print("-" * 60)

family_color_map = {}

for family in sorted(family_colors.keys()):
    avg_r = int(sum(family_colors[family]['R']) / len(family_colors[family]['R']))
    avg_g = int(sum(family_colors[family]['G']) / len(family_colors[family]['G']))
    avg_b = int(sum(family_colors[family]['B']) / len(family_colors[family]['B']))
    
    hex_color = f"#{avg_r:02X}{avg_g:02X}{avg_b:02X}"
    family_color_map[family] = (avg_r, avg_g, avg_b)
    
    print(f"{family}\t| {avg_r}\t| {avg_g}\t| {avg_b}\t| {hex_color}")

print("\n\nSwift 코드로 변환:\n")
print("let familyRepresentativeColors: [String: UIColor] = [")
for family in sorted(family_color_map.keys()):
    r, g, b = family_color_map[family]
    print(f'    "{family}": UIColor(red: {r}/255.0, green: {g}/255.0, blue: {b}/255.0, alpha: 1.0),')
print("]")
