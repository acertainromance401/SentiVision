---
layout: default
title: SentiVision AI Portfolio
---

# SentiVision AI Portfolio

SentiVision은 사용자의 드로잉 색감을 바탕으로 감정의 결을 전시형으로 해석하는 iPad 우선 제품입니다.  
초기 세팅에서 개인 프로필과 기준 색상/기준 감정을 먼저 정하고, 이후 결과는 개인 분포를 반영해 보여줍니다.

## About Project

- **문제 정의**: 창작 과정에서 감정 상태를 정량화해 기록하기 어려운 문제 해결
- **핵심 아이디어**: 이미지의 주요 색상 분포와 감정 라벨의 연관 해석
- **활용 시나리오**: 개인 창작자의 감정 기록, 작품 회고, 개인 분포 확인

## Key Features

1. 이미지 주요(두드러진) 영역 추출
2. 대표 색상(KMeans) 추출
3. 감정 라벨 비교(KNN/RandomForest 비교)
4. 사용자 피드백 기반 데이터셋 업데이트
5. 개인 분포/시각화 산출물 자동 생성

## Tech Stack

- **Language**: Python
- **ML/Data**: scikit-learn, pandas, numpy
- **Vision**: OpenCV
- **Visualization**: matplotlib
- **DevOps/Quality**: GitHub Actions

## Portfolio Highlights

- 전시형 감정 해석 파이프라인 구축 및 고도화
- KNN vs RandomForest 성능 비교 리포트 자동 생성
- CSV 데이터셋 버전 백업 + 업데이트 이력 관리
- DORA 지표 자동 수집 워크플로 운영

## Artifacts

- iPad 데모 앱: `app-development/iPadCanvasDemo/`
- 프로젝트 설명 문서: `Project_Descriptions/`
- 분석 코드: `test/main_.py`, `test/test_model_comparison.py`
- 실행 결과: `test/outputs/`

## Contact

- GitHub: [acertainromance401/SentiVision](https://github.com/acertainromance401/SentiVision)
