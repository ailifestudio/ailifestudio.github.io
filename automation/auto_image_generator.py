#!/usr/bin/env python3
"""
완전 자동 이미지 생성 시스템
- Gemini API로 고품질 프롬프트 생성
- Replicate API로 Stable Diffusion 이미지 생성
- generated_images.json 자동 업데이트
"""

import os
import json
import google.generativeai as genai
from pathlib import Path
from typing import Dict, List, Optional
import time
import hashlib


def load_gemini_api_keys() -> List[str]:
    """GEMINI_API_KEYS 환경변수에서 API 키 로드"""
    keys_json = os.getenv('GEMINI_API_KEYS', '')
    
    if keys_json:
        try:
            keys = json.loads(keys_json)
            if isinstance(keys, list):
                return keys
        except:
            pass
    
    single_key = os.getenv('GEMINI_API_KEY', '')
    if single_key:
        return [single_key]
    
    return []


def generate_enhanced_prompt_with_gemini(keyword: str, api_key: str) -> str:
    """
    Gemini API로 이미지 생성 프롬프트 생성
    
    Args:
        keyword: 이미지 키워드
        api_key: Gemini API 키
    
    Returns:
        향상된 영어 프롬프트
    """
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        
        prompt = f"""
Create a detailed Stable Diffusion image generation prompt for: "{keyword}"

Requirements:
- Professional, high-quality, modern style
- 16:9 aspect ratio suitable for blog header
- Tech/AI blog illustration aesthetic
- Realistic photography or clean illustration
- No text overlays, no UI elements
- Include specific visual details, lighting, composition

Output ONLY the English prompt (1-2 sentences, no explanations).
Example format: "Professional photo of [subject], [setting], [lighting], [mood], high quality, detailed"
"""
        
        response = model.generate_content(prompt)
        enhanced = response.text.strip().strip('"').strip("'")
        
        # 품질 향상 suffix 추가
        enhanced += ", professional photography, 16:9 aspect ratio, high quality, detailed, vibrant colors, modern aesthetic"
        
        return enhanced
        
    except Exception as e:
        print(f"      ⚠️ Gemini API 실패: {str(e)[:100]}")
        # Fallback: 키워드 그대로 사용
        return f"{keyword}, professional photography, high quality, 16:9 aspect ratio, modern tech aesthetic, detailed"


def generate_image_with_sdxl(prompt: str) -> str:
    """
    무료 이미지 생성 (Unsplash Source API 사용)
    
    Args:
        prompt: 이미지 프롬프트
    
    Returns:
        이미지 URL
    """
    # Unsplash Source API (무료, API 키 불필요)
    # 키워드에서 핵심 단어 추출
    keywords = prompt.split(',')[0].strip()
    keywords = keywords.replace(' ', ',')
    
    # 시드 생성 (같은 키워드는 같은 이미지)
    seed = hashlib.md5(prompt.encode()).hexdigest()[:8]
    
    # Unsplash 1280x720 이미지 (16:9)
    image_url = f"https://source.unsplash.com/1280x720/?{keywords}"
    
    return image_url


def generate_images_for_keywords(keywords: List[str]) -> Dict[str, str]:
    """
    여러 키워드에 대한 이미지 자동 생성
    
    Args:
        keywords: 이미지 키워드 리스트
    
    Returns:
        {keyword: image_url} 딕셔너리
    """
    api_keys = load_gemini_api_keys()
    
    if not api_keys:
        print("   ⚠️ GEMINI_API_KEY 없음 - 기본 프롬프트 사용")
    
    images = {}
    current_key_index = 0
    
    # 기존 이미지 로드
    json_path = Path(__file__).parent / "generated_images.json"
    existing_images = {}
    
    if json_path.exists():
        with open(json_path, 'r', encoding='utf-8') as f:
            existing_images = json.load(f)
    
    print(f"   📊 기존 이미지: {len(existing_images)}개")
    
    for i, keyword in enumerate(keywords, 1):
        print(f"\n   [{i}/{len(keywords)}] '{keyword}'")
        
        # 이미 생성된 경우 → 새 스타일로 재생성
        if keyword in existing_images:
            print(f"      🔄 중복 키워드 → 다른 스타일로 재생성")
            # 프롬프트에 변형 추가
            variation_suffix = f"_v{len([k for k in existing_images.keys() if keyword in k]) + 1}"
            keyword_with_variation = keyword + variation_suffix
        else:
            keyword_with_variation = keyword
        
        # 1단계: Gemini로 프롬프트 생성
        if api_keys:
            api_key = api_keys[current_key_index % len(api_keys)]
            enhanced_prompt = generate_enhanced_prompt_with_gemini(keyword, api_key)
            print(f"      ✅ 프롬프트: {enhanced_prompt[:80]}...")
            current_key_index = (current_key_index + 1) % len(api_keys)
        else:
            enhanced_prompt = f"{keyword}, professional photography, high quality, 16:9"
        
        # 2단계: 이미지 생성
        print(f"      🎨 이미지 생성 중...")
        image_url = generate_image_with_sdxl(enhanced_prompt)
        
        images[keyword] = image_url
        print(f"      ✅ 생성 완료: {image_url[:60]}...")
        
        time.sleep(0.5)  # Rate limit 방지
    
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


def extract_new_keywords_from_content(content: str) -> List[str]:
    """
    콘텐츠에서 [IMAGE:...] 키워드 추출
    
    Args:
        content: HTML 콘텐츠
    
    Returns:
        모든 키워드 리스트 (중복 포함, 각각 다른 스타일로 생성)
    """
    import re
    
    # 키워드 추출
    pattern = r'\[IMAGE:([^\]]+)\]'
    keywords = re.findall(pattern, content)
    keywords = [kw.strip() for kw in keywords]
    
    # 모든 키워드 반환 (중복도 다른 스타일로 생성)
    return keywords


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        test_keywords = sys.argv[1:]
    else:
        test_keywords = [
            "AI brain processing information with data streams",
            "person interacting with AI chatbot on screen",
            "mind map generated by AI showing connections"
        ]
    
    print("🎨 완전 자동 이미지 생성 시작\n")
    print(f"📝 키워드: {len(test_keywords)}개")
    
    # 이미지 생성
    images = generate_images_for_keywords(test_keywords)
    
    # 저장
    if images:
        save_generated_images(images)
        
        print("\n" + "="*60)
        print("✅ 완료!")
        print("="*60)
    else:
        print("\n❌ 생성된 이미지가 없습니다")
