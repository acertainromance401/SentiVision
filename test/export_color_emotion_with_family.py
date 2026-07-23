#!/usr/bin/env python3
import csv
from collections import defaultdict
from pathlib import Path

INPUT_CSV = Path('test/color_emotion_labeled_augmented.csv')
FAMILY_CSV = Path('test/emotion_family_classification.csv')
OUTPUT_CSV = Path('test/color_emotion_labeled_augmented_with_family.csv')

family_rows = defaultdict(list)
with FAMILY_CSV.open(newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        emotion = (row['emotion'] or '').strip().upper()
        family = (row['family'] or '').strip()
        role = (row['role'] or '').strip().lower()
        try:
            weight = float(row['weight'])
        except (TypeError, ValueError):
            weight = 0.0
        family_rows[emotion].append((family, role, weight))

role_priority = {'primary': 0, 'secondary': 1, 'fallback': 2}


def choose_family(emotion: str) -> str:
    emotion = (emotion or '').strip().upper()
    candidates = family_rows.get(emotion, [])
    if not candidates:
        return '기타'
    candidates = sorted(candidates, key=lambda item: (-item[2], role_priority.get(item[1], 9), item[0]))
    return candidates[0][0]


with INPUT_CSV.open(newline='', encoding='utf-8') as f_in, OUTPUT_CSV.open('w', newline='', encoding='utf-8') as f_out:
    reader = csv.DictReader(f_in)
    fieldnames = list(reader.fieldnames or []) + ['family']
    writer = csv.DictWriter(f_out, fieldnames=fieldnames)
    writer.writeheader()
    for row in reader:
        row['family'] = choose_family(row.get('emotion', ''))
        writer.writerow(row)

print(f'wrote {OUTPUT_CSV}')
