---
layout: default
title: SentiVision AI Portfolio
---

# SentiVision AI Portfolio

SentiVision은 사용자의 드로잉 색감을 바탕으로 감정 톤을 분석하는 AI 프로젝트입니다.  
색상 특징 추출과 분류 모델을 통해 감정 예측 결과를 제공하고, 피드백 기반으로 데이터셋을 점진적으로 개선합니다.

## About Project

- **문제 정의**: 창작 과정에서 감정 상태를 정량화해 기록하기 어려운 문제 해결
- **핵심 아이디어**: 이미지의 주요 색상 분포와 감정 라벨의 연관 학습
- **활용 시나리오**: 개인 창작자의 감정 기록, 작품 회고, 패턴 분석

## Key Features

1. 이미지 salient 영역 추출
2. 대표 색상(KMeans) 추출
3. 감정 라벨 예측(KNN/RandomForest 비교)
4. 사용자 피드백 기반 데이터셋 업데이트
5. 시각화 산출물 자동 생성

## Tech Stack

- **Language**: Python
- **ML/Data**: scikit-learn, pandas, numpy
- **Vision**: OpenCV
- **Visualization**: matplotlib
- **DevOps/Quality**: GitHub Actions

## Portfolio Highlights

- 감정 예측 파이프라인 구축 및 고도화
- KNN vs RandomForest 성능 비교 리포트 자동 생성
- CSV 데이터셋 버전 백업 + 업데이트 이력 관리
- DORA 지표 자동 수집 워크플로 운영

## Artifacts

- 프로젝트 설명 문서: `Project_Descriptions/`
- 분석 코드: `test/main_.py`, `test/test_model_comparison.py`
- 실행 결과: `test/outputs/`

## Contact

- GitHub: [acertainromance401/SentiVision](https://github.com/acertainromance401/SentiVision)
