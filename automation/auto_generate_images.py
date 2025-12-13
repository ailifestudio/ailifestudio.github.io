#!/usr/bin/env python3
"""
자동 이미지 생성 시스템
1. Gemini API로 이미지 프롬프트 생성
2. 프롬프트를 JSON 파일로 저장
3. GenSpark Assistant가 읽어서 Nano Banana로 이미지 생성
"""

import os
import json
import google.generativeai as genai
from pathlib import Path
from typing import List, Dict


def load_api_keys() -> list:
    """GEMINI_API_KEYS 환경변수에서 API 키 로드"""
    keys_json = os.getenv('GEMINI_API_KEYS', '')
    
    if keys_json:
        try:
            keys = json.loads(keys_json)
            if isinstance(keys, list):
                return keys
        except:
            pass
    
    # 단일 키
    single_key = os.getenv('GEMINI_API_KEY', '')
    if single_key:
        return [single_key]
    
    return []


def generate_image_prompt(keyword: str, api_key: str) -> str:
    """
    Gemini API로 이미지 생성 프롬프트 생성
    
    Args:
        keyword: 이미지 키워드 (예: "AI brain generating creative ideas")
        api_key: Gemini API 키
    
    Returns:
        Imagen/Nano Banana용 프롬프트 (영어)
    """
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash-exp")
    
    prompt = f"""
Create a detailed image generation prompt for: "{keyword}"

Requirements:
- Professional, high-quality, modern style
- 16:9 aspect ratio
- Suitable for tech/AI blog illustration
- No text overlays
- Realistic or clean illustration style
- Include specific visual details

Output only the English prompt (no explanations, 1-2 sentences).
"""
    
    try:
        response = model.generate_content(prompt)
        enhanced_prompt = response.text.strip()
        
        # 추가 품질 향상
        enhanced_prompt = f"{enhanced_prompt}, high quality, professional photography, 16:9 aspect ratio, detailed, vibrant colors"
        
        return enhanced_prompt
    except Exception as e:
        print(f"  ⚠️ Gemini API 실패: {e}")
        # Fallback: 키워드 그대로 사용
        return f"{keyword}, high quality professional photography, modern tech aesthetic, 16:9 aspect ratio"


def generate_prompts_for_keywords(keywords: List[str]) -> Dict[str, str]:
    """
    여러 키워드에 대한 이미지 프롬프트 생성
    
    Args:
        keywords: 이미지 키워드 리스트
    
    Returns:
        {keyword: prompt} 딕셔너리
    """
    api_keys = load_api_keys()
    
    if not api_keys:
        print("⚠️ GEMINI_API_KEY 환경변수가 설정되지 않았습니다")
        return {}
    
    prompts = {}
    current_key_index = 0
    
    for i, keyword in enumerate(keywords):
        print(f"\n[{i+1}/{len(keywords)}] '{keyword}'")
        
        # API 키 로테이션
        api_key = api_keys[current_key_index % len(api_keys)]
        
        try:
            prompt = generate_image_prompt(keyword, api_key)
            prompts[keyword] = prompt
            print(f"  ✅ 프롬프트 생성 완료")
            print(f"     → {prompt[:80]}...")
        except Exception as e:
            print(f"  ❌ 프롬프트 생성 실패: {e}")
            # 다음 키로 재시도
            current_key_index += 1
            if current_key_index < len(api_keys):
                try:
                    api_key = api_keys[current_key_index % len(api_keys)]
                    prompt = generate_image_prompt(keyword, api_key)
                    prompts[keyword] = prompt
                    print(f"  ✅ 재시도 성공 (키 #{current_key_index + 1})")
                except:
                    print(f"  ❌ 재시도 실패")
    
    return prompts


def save_prompts_to_file(prompts: Dict[str, str], output_file: str = "image_generation_requests.json"):
    """
    생성된 프롬프트를 JSON 파일로 저장
    
    Args:
        prompts: {keyword: prompt} 딕셔너리
        output_file: 출력 파일명
    """
    output_path = Path(__file__).parent / output_file
    
    # 기존 요청 로드
    existing = {}
    if output_path.exists():
        with open(output_path, 'r', encoding='utf-8') as f:
            existing = json.load(f)
    
    # 새 프롬프트 추가
    existing.update(prompts)
    
    # 저장
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ {len(prompts)}개 프롬프트 저장: {output_file}")
    print(f"   → GenSpark Assistant가 이 파일을 읽어 Nano Banana로 이미지 생성")


def extract_new_keywords_from_content(content: str) -> List[str]:
    """
    콘텐츠에서 [IMAGE:...] 키워드 추출 (generated_images.json에 없는 것만)
    
    Args:
        content: HTML 콘텐츠
    
    Returns:
        새 키워드 리스트
    """
    import re
    
    # 키워드 추출
    pattern = r'\[IMAGE:([^\]]+)\]'
    keywords = re.findall(pattern, content)
    keywords = [kw.strip() for kw in keywords]
    
    # 기존 이미지 확인
    json_path = Path(__file__).parent / "generated_images.json"
    existing_keywords = set()
    
    if json_path.exists():
        with open(json_path, 'r', encoding='utf-8') as f:
            existing_keywords = set(json.load(f).keys())
    
    # 새 키워드만 필터링
    new_keywords = [kw for kw in keywords if kw not in existing_keywords]
    
    return new_keywords


if __name__ == "__main__":
    import sys
    
    # 테스트: 커맨드라인에서 키워드 받기
    if len(sys.argv) > 1:
        test_keywords = sys.argv[1:]
    else:
        test_keywords = [
            "AI brain generating creative ideas",
            "modern workspace with laptop"
        ]
    
    print("🎨 자동 이미지 프롬프트 생성 시작\n")
    print(f"📝 키워드: {len(test_keywords)}개")
    
    # 프롬프트 생성
    prompts = generate_prompts_for_keywords(test_keywords)
    
    # 파일로 저장
    if prompts:
        save_prompts_to_file(prompts)
        
        print("\n" + "="*60)
        print("✅ 완료!")
        print("="*60)
        print("\n📋 다음 단계:")
        print("1. GenSpark Assistant가 image_generation_requests.json 읽기")
        print("2. Nano Banana Pro로 이미지 생성")
        print("3. generated_images.json 업데이트")
    else:
        print("\n❌ 생성된 프롬프트가 없습니다")
