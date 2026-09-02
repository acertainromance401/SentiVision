---
layout: default
title: SentiVision AI Portfolio
---

# SentiVision AI Portfolio

SentiVision은 사용자의 드로잉 색감을 바탕으로 감정의 결을 전시형으로 해석하는 iPad 우선 제품입니다.  
초기 세팅에서 개인 프로필과 기준 색상/기준 감정을 정하고, PencilKit 캔버스부터 온디바이스 분석, 감정 전시, 3D 분포, 로컬 아카이브까지 한 흐름으로 연결합니다.

> 최종 검증일: 2026-09-02 · 현재 단계: iPad 기능 프로토타입

## About Project

- **문제 정의**: 창작 과정에서 감정 상태를 정량화해 기록하기 어려운 문제 해결
- **핵심 아이디어**: 이미지의 주요 색상 분포와 감정 라벨의 연관 해석
- **활용 시나리오**: 개인 창작자의 감정 기록, 작품 회고, 개인 분포 확인

## Key Features

1. 첫 실행 개인 프로필과 기준 감정·색상 설정
2. PencilKit 드로잉과 기본 팔레트·도구 제어
3. 전경 픽셀 기반 대표 색상(K-means)과 최근접 감정 분석
4. 10개 감정 패밀리 집계와 SceneKit 3D RGB 분포
5. 감정 전시 카드의 로컬 저장과 재열람
6. Python KNN/RandomForest 모델 비교 및 데이터 보정
7. Node API, 메트릭, 기능 플래그, A/B, Canary와 CI/CD 검증

## Tech Stack

- **iPad**: Swift, SwiftUI, PencilKit, SceneKit, UIKit
- **On-device Analysis**: Swift K-means, CSV nearest-emotion mapping
- **Research**: Python, OpenCV, scikit-learn, pandas, numpy, matplotlib
- **API/Experiment**: Node.js, Jest, feature flags, A/B assignment
- **DevOps/Quality**: Playwright, Docker, Prometheus, Grafana, GitHub Actions

## Portfolio Highlights

- 드로잉부터 전시 카드 저장까지 iPad 로컬 흐름 구현
- 색상-감정 데이터를 10개 감정 패밀리로 확장하고 3D 분포에 통합
- KNN vs RandomForest 성능 비교 리포트 자동 생성
- CSV 데이터셋 버전 백업 + 업데이트 이력 관리
- API 관측성, 실험, DORA 지표 자동 수집 워크플로 구축

## Current Boundary

- **Implemented**: iPad 온보딩, 캔버스, 로컬 분석, 결과, 3D 분포, 로컬 아카이브
- **Prototype**: Node 팔레트 분석 API, Python 연구 파이프라인
- **Backlog**: 감정 수정·메모, 개인 학습 반영, 고급 색상 선택, 원격 동기화, iPhone 감상 앱

## Artifacts

- iPad 데모 앱: `app-development/iPadCanvasDemo/`
- 프로젝트 설명 문서: `Project_Descriptions/`
- 분석 코드: `test/main_.py`, `test/test_model_comparison.py`
- 실행 결과: `test/outputs/`
- 상세 포트폴리오: `Project_Descriptions/SentiVision_Portfolio.pdf`

## Contact

- GitHub: [acertainromance401/SentiVision](https://github.com/acertainromance401/SentiVision)
