#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""main_.py와 test_model_comparison.py를 한 번에 실행한다."""

import os
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MAIN_SCRIPT = BASE_DIR / 'main_.py'
COMPARE_SCRIPT = BASE_DIR / 'test_model_comparison.py'


def run_script(script_path, input_text):
    """서브 스크립트를 입력값과 함께 실행한다."""
    print(f"\n[실행] {script_path.name}")
    result = subprocess.run(
        [sys.executable, str(script_path)],
        input=input_text,
        text=True,
        capture_output=True,
        cwd=str(BASE_DIR.parent),
    )
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    if result.returncode != 0:
        print(f"[오류] {script_path.name} 종료 코드: {result.returncode}")
        return False
    return True


def main():
    """이미지 경로를 받아 두 분석 스크립트를 순차 실행한다."""
    if len(sys.argv) > 1:
        image_path = sys.argv[1].strip()
    else:
        image_path = input("분석할 이미지 파일 경로를 입력하세요: ").strip()

    if not image_path:
        print("이미지 경로가 비어 있습니다.")
        sys.exit(1)

    if not os.path.exists(image_path):
        print(f"이미지 파일을 찾을 수 없습니다: {image_path}")
        sys.exit(1)

    # main_.py는 이미지 경로 입력 후 색상 개수만큼 피드백 입력을 받으므로
    # 빈 줄을 여유 있게 제공해 기본(yes) 동작으로 진행한다.
    main_input = image_path + "\n" + ("\n" * 10)
    compare_input = image_path + "\n"

    ok_main = run_script(MAIN_SCRIPT, main_input)
    ok_compare = run_script(COMPARE_SCRIPT, compare_input)

    if ok_main and ok_compare:
        print("\n[완료] main + comparison 분석이 모두 끝났습니다.")
    else:
        print("\n[완료(부분)] 일부 스크립트 실행에 실패했습니다. 로그를 확인하세요.")
        sys.exit(1)


if __name__ == '__main__':
    main()
