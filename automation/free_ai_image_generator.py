#!/usr/bin/env python3
"""
완전 무료 AI 이미지 생성 시스템
- Hugging Face Inference API (무료)
- Stable Diffusion 3.5 Large
- Python에서 직접 실행 가능
"""

import os
import json
import requests
import base64
import time
from pathlib import Path
from typing import Dict, List, Optional


def generate_image_with_pollinations(prompt: str, output_path: str) -> Optional[str]:
    """
    Pollinations.ai API로 이미지 생성 (완전 무료, 제한 없음)
    
    Args:
        prompt: 이미지 생성 프롬프트 (영어)
        output_path: 이미지 저장 경로
    
    Returns:
        저장된 이미지 경로 또는 None
    """
    # Pollinations.ai (완전 무료, API 키 불필요, 제한 없음)
    import urllib.parse
    
    # 프롬프트 인코딩
    encoded_prompt = urllib.parse.quote(prompt)
    
    # Pollinations.ai URL (1365x768 = 16:9)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1365&height=768&nologo=true&enhance=true"
    
    try:
        print(f"      🎨 Pollinations.ai 생성 중...")
        response = requests.get(image_url, timeout=60)
        
        if response.status_code == 200:
            # 이미지 바이너리 데이터
            image_bytes = response.content
            
            # 파일로 저장
            with open(output_path, 'wb') as f:
                f.write(image_bytes)
            
            print(f"      ✅ 생성 완료: {output_path}")
            return output_path
        
        else:
            print(f"      ⚠️ Pollinations API 오류: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"      ⚠️ 이미지 생성 실패: {e}")
        return None


def generate_images_for_keywords(keywords: List[str], output_dir: str = "generated_images") -> Dict[str, str]:
    """
    여러 키워드에 대한 이미지 자동 생성
    
    Args:
        keywords: 이미지 키워드 리스트
        output_dir: 이미지 저장 디렉토리
    
    Returns:
        {keyword: image_path} 딕셔너리
    """
    # 출력 디렉토리 생성
    output_path = Path(__file__).parent / output_dir
    output_path.mkdir(exist_ok=True)
    
    images = {}
    
    # 기존 이미지 로드
    json_path = Path(__file__).parent / "generated_images.json"
    if json_path.exists():
        with open(json_path, 'r', encoding='utf-8') as f:
            existing_images = json.load(f)
        print(f"   📊 기존 이미지: {len(existing_images)}개")
    else:
        existing_images = {}
    
    for i, keyword in enumerate(keywords, 1):
        print(f"\n   [{i}/{len(keywords)}] '{keyword}'")
        
        # 이미 생성된 경우 스킵
        if keyword in existing_images:
            print(f"      ⏭️  이미 생성됨")
            images[keyword] = existing_images[keyword]
            continue
        
        # 프롬프트 향상
        enhanced_prompt = f"{keyword}, professional photography, high quality, detailed, vibrant colors, 16:9 aspect ratio, modern aesthetic, clean composition"
        
        # 파일명 생성
        import hashlib
        file_hash = hashlib.md5(keyword.encode()).hexdigest()[:8]
        output_file = output_path / f"ai_image_{file_hash}.png"
        
        # 이미지 생성
        result = generate_image_with_pollinations(enhanced_prompt, str(output_file))
        
        if result:
            # 상대 경로로 저장 (GitHub Pages에서 접근 가능)
            relative_path = f"automation/{output_dir}/ai_image_{file_hash}.png"
            images[keyword] = relative_path
        else:
            # Fallback: Unsplash
            keywords_clean = keyword.replace(' ', ',')
            fallback_url = f"https://source.unsplash.com/1280x720/?{keywords_clean}"
            images[keyword] = fallback_url
            print(f"      🔧 Fallback: Unsplash")
        
        # Rate limit 방지
        time.sleep(2)
    
    return images


def save_generated_images(images: Dict[str, str]):
    """생성된 이미지를 generated_images.json에 저장"""
    json_path = Path(__file__).parent / "generated_images.json"
    
    # 기존 이미지 로드
    existing = {}
    if json_path.exists():
        with open(json_path, 'r', encoding='utf-8') as f:
            existing = json.load(f)
    
    # 새 이미지 추가
    existing.update(images)
    
    # 저장
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
    
    print(f"\n   ✅ generated_images.json 업데이트 완료 (총 {len(existing)}개)")


if __name__ == "__main__":
    import sys
    
    # 테스트
    if len(sys.argv) > 1:
        test_keywords = sys.argv[1:]
    else:
        test_keywords = [
            "AI neural network visualization",
            "person working with AI tools"
        ]
    
    print("🎨 무료 AI 이미지 생성 시작 (Pollinations.ai)\n")
    print(f"📝 키워드: {len(test_keywords)}개")
    
    # 이미지 생성
    images = generate_images_for_keywords(test_keywords)
    
    # 저장
    if images:
        save_generated_images(images)
        
        print("\n" + "="*60)
        print("✅ 완료!")
        print("="*60)
        print("\n💰 비용: 0원 (완전 무료)")
    else:
        print("\n❌ 생성된 이미지가 없습니다")
