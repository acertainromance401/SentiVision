#!/usr/bin/env python3
"""
감정 패밀리의 의미에 기반한 대표색 선정 (두번째 방식)
각 패밀리의 semantic 의미를 반영한 색상 정의
"""

# 의미 기반 대표색 정의
semantic_family_colors = {
    "고요": {
        "name": "차분한 자연색",
        "R": 120,
        "G": 140,
        "B": 110,
        "hex": "#788C6E",
        "description": "숲과 자연을 연상시키는 안정적인 녹색"
    },
    "권위": {
        "name": "고급 금색",
        "R": 184,
        "G": 134,
        "B": 11,
        "hex": "#B8860B",
        "description": "왕실과 권위를 상징하는 골드"
    },
    "그늘": {
        "name": "깊은 검은색",
        "R": 40,
        "G": 40,
        "B": 40,
        "hex": "#282828",
        "description": "그림자와 신비로움을 나타내는 진검은색"
    },
    "긴장": {
        "name": "경고 주황",
        "R": 255,
        "G": 102,
        "B": 0,
        "hex": "#FF6600",
        "description": "긴장과 주의를 나타내는 뚜렷한 주황색"
    },
    "신비": {
        "name": "깊은 보라색",
        "R": 75,
        "G": 0,
        "B": 130,
        "hex": "#4B0082",
        "description": "신비와 마법을 상징하는 인디고"
    },
    "연결": {
        "name": "따뜻한 핑크",
        "R": 219,
        "G": 39,
        "B": 119,
        "hex": "#DB2777",
        "description": "사람 간의 연결과 감정을 나타내는 핑크"
    },
    "온기": {
        "name": "따뜻한 빨강",
        "R": 220,
        "G": 20,
        "B": 60,
        "hex": "#DC143C",
        "description": "온기와 사랑을 상징하는 크림슨"
    },
    "집중": {
        "name": "진한 갈색",
        "R": 101,
        "G": 67,
        "B": 33,
        "hex": "#654321",
        "description": "흙과 안정성을 나타내는 진갈색"
    },
    "활력": {
        "name": "생생한 초록",
        "R": 0,
        "G": 204,
        "B": 0,
        "hex": "#00CC00",
        "description": "생명력과 에너지를 나타내는 밝은 녹색"
    },
    "회복": {
        "name": "밝은 연두",
        "R": 144,
        "G": 238,
        "B": 144,
        "hex": "#90EE90",
        "description": "회복과 치유를 상징하는 밝은 연두색"
    }
}

print("의미 기반 감정 패밀리 대표색 (두번째 방식):\n")
print("Family\t\t| Meaning\t\t| R\t| G\t| B\t| Hex")
print("-" * 80)

for family in sorted(semantic_family_colors.keys()):
    info = semantic_family_colors[family]
    print(f"{family}\t| {info['name']}\t| {info['R']}\t| {info['G']}\t| {info['B']}\t| {info['hex']}")

print("\n\nSwift 코드로 변환:\n")
print("let familyRepresentativeColorsSemanticV2: [String: UIColor] = [")
for family in sorted(semantic_family_colors.keys()):
    info = semantic_family_colors[family]
    print(f'    "{family}": UIColor(red: {info["R"]}/255.0, green: {info["G"]}/255.0, blue: {info["B"]}/255.0, alpha: 1.0),  // {info["description"]}')
print("]")

print("\n\n설명:")
for family in sorted(semantic_family_colors.keys()):
    info = semantic_family_colors[family]
    print(f"- {family}: {info['name']} ({info['hex']}) - {info['description']}")
