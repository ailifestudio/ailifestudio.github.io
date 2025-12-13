#!/usr/bin/env python3
"""
이미지 생성 요청 처리 스크립트
- image_generation_requests.json 파일을 읽음
- GenSpark Assistant에게 Nano Banana 이미지 생성 요청
- 콘솔에 요청 정보 출력 (Assistant가 읽고 처리)
"""

import json
from pathlib import Path
from typing import Dict


def load_image_requests() -> Dict[str, str]:
    """이미지 생성 요청 로드"""
    json_path = Path(__file__).parent / "image_generation_requests.json"
    
    if not json_path.exists():
        return {}
    
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_generated_images() -> Dict[str, str]:
    """이미 생성된 이미지 로드"""
    json_path = Path(__file__).parent / "generated_images.json"
    
    if not json_path.exists():
        return {}
    
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def find_pending_requests() -> Dict[str, str]:
    """아직 생성되지 않은 이미지 요청 찾기"""
    requests = load_image_requests()
    generated = load_generated_images()
    
    pending = {}
    for keyword, prompt in requests.items():
        if keyword not in generated:
            pending[keyword] = prompt
    
    return pending


def display_image_generation_requests():
    """
    이미지 생성 요청을 콘솔에 출력
    GenSpark Assistant가 이를 읽고 Nano Banana로 이미지 생성
    """
    pending = find_pending_requests()
    
    if not pending:
        print("✅ 모든 이미지가 생성되었습니다!")
        return
    
    print("\n" + "="*70)
    print("🎨 이미지 생성 요청 (Nano Banana Pro)")
    print("="*70)
    print(f"\n📋 총 {len(pending)}개 이미지 생성 필요:\n")
    
    for i, (keyword, prompt) in enumerate(pending.items(), 1):
        print(f"[{i}/{len(pending)}] 키워드: {keyword}")
        print(f"프롬프트: {prompt}")
        print(f"모델: nano-banana-pro")
        print(f"비율: 16:9")
        print("-" * 70)
    
    print("\n" + "="*70)
    print("📝 GenSpark Assistant 작업:")
    print("="*70)
    print("""
1. 위의 각 프롬프트로 nano-banana-pro 이미지 생성
2. 생성된 이미지 URL 수집
3. 아래 형식으로 generated_images.json 업데이트:

{
  "키워드1": "https://www.genspark.ai/api/files/s/xxxxx",
  "키워드2": "https://www.genspark.ai/api/files/s/yyyyy",
  ...
}

4. image_generation_requests.json 파일 삭제 (완료 표시)
""")


if __name__ == "__main__":
    display_image_generation_requests()
