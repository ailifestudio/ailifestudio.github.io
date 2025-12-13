#!/usr/bin/env python3
"""
Unsplash API를 활용한 무료 이미지 검색
저작권 걱정 없는 고품질 이미지
"""

import requests
import urllib.parse


def load_generated_images():
    """Gemini로 생성된 이미지 맵 로드"""
    try:
        import json
        import os
        
        json_path = os.path.join(os.path.dirname(__file__), 'generated_images.json')
        
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                images = json.load(f)
                print(f"    ✅ Gemini 생성 이미지 {len(images)}개 로드됨")
                return images
        else:
            print(f"    ℹ️  generated_images.json 파일 없음")
            return {}
    except Exception as e:
        print(f"    ⚠️ 이미지 맵 로드 실패: {e}")
        return {}


def search_unsplash_image(keyword: str, access_key: str = None) -> str:
    """
    이미지 URL 검색 (Gemini 생성 이미지 우선)
    
    Args:
        keyword: 검색 키워드 (영어)
        access_key: API 키 (선택사항, 사용 안 함)
    
    Returns:
        이미지 URL (Gemini 생성 또는 플레이스홀더)
    """
    # 1순위: Gemini로 생성된 이미지 확인
    generated_images = load_generated_images()
    if keyword in generated_images:
        image_url = generated_images[keyword]
        print(f"    ✅ Gemini 이미지 사용: {keyword}")
        print(f"       → {image_url[:60]}...")
        return image_url
    
    # 2순위: 플레이스홀더 (이 키워드는 아직 생성 안 됨)
    print(f"    ⚠️ 이미지 없음: '{keyword}'")
    print(f"       → generated_images.json에 없는 새 키워드입니다")
    
    # 16:9 비율 플레이스홀더
    placeholder_url = f"https://via.placeholder.com/1280x720/1e293b/60a5fa?text={urllib.parse.quote(keyword[:30])}"
    
    print(f"    🔧 임시 Placeholder 사용: {placeholder_url[:70]}...")
    print(f"    💡 해결: 이 키워드로 이미지 생성 후 generated_images.json 업데이트 필요")
    
    return placeholder_url


def extract_keywords_from_content(content: str, max_images: int = 5) -> list:
    """
    콘텐츠에서 [IMAGE:...] 키워드 추출
    
    Args:
        content: HTML 콘텐츠
        max_images: 최대 이미지 개수 (기본: 5개)
    
    Returns:
        이미지 키워드 리스트 (최대 max_images개)
    """
    import re
    pattern = r'\[IMAGE:([^\]]+)\]'
    keywords = re.findall(pattern, content)
    keywords = [kw.strip() for kw in keywords]
    
    # 최대 개수 제한
    if len(keywords) > max_images:
        print(f"    ⚠️ 이미지 {len(keywords)}개 발견 → {max_images}개로 제한")
        keywords = keywords[:max_images]
    
    return keywords


def generate_image_with_nano_banana(prompt: str, aspect_ratio: str = "16:9") -> str:
    """
    Nano Banana Pro를 사용해 AI 이미지 생성
    
    Args:
        prompt: 이미지 생성 프롬프트 (영어)
        aspect_ratio: 이미지 비율 (기본: 16:9)
    
    Returns:
        생성된 이미지 AI Drive 경로 또는 URL (실패 시 None)
    """
    try:
        # GenSpark AI image_generation 도구 사용
        # 이 함수는 automation script에서 직접 호출되어야 함
        # Python 스크립트 내에서는 subprocess로 호출
        
        print(f"    🎨 Nano Banana Pro 이미지 생성 요청: {prompt[:50]}...")
        
        # 프롬프트 개선 (품질 향상)
        enhanced_prompt = f"{prompt}, high quality, professional photography, detailed, vibrant colors, clean composition"
        
        # 실제 구현: GenSpark image_generation API 호출
        # (이 부분은 외부 시스템에서 처리되어야 함)
        
        # 현재는 구현 불가 (Python 스크립트에서 직접 호출 불가)
        return None
        
    except Exception as e:
        print(f"    ⚠️ AI 이미지 생성 실패: {e}")
        return None


def generate_image_with_ai(prompt: str) -> str:
    """
    Nano Banana를 사용해 이미지 생성 (레거시 함수, 호환성 유지)
    
    Args:
        prompt: 이미지 생성 프롬프트 (영어)
    
    Returns:
        생성된 이미지 URL (실패 시 Picsum fallback)
    """
    # Nano Banana 시도
    result = generate_image_with_nano_banana(prompt)
    if result:
        return result
    
    # Fallback: Picsum 사용
    import hashlib
    keyword_hash = hashlib.md5(prompt.lower().encode()).hexdigest()
    fallback_url = f"https://picsum.photos/seed/{keyword_hash[:16]}/1280/720"
    print(f"    ⚠️ Fallback 이미지: {fallback_url}")
    return fallback_url


def add_images_to_content(content: str, unsplash_key: str = None) -> str:
    """
    [IMAGE:...] 키워드를 실제 이미지로 변환
    
    Args:
        content: HTML 콘텐츠
        unsplash_key: Unsplash API 키 (선택)
    
    Returns:
        이미지가 삽입된 HTML
    """
    import re
    
    def replace_image(match):
        keyword = match.group(1).strip()
        image_url = search_unsplash_image(keyword, unsplash_key)
        
        # 이미지 HTML 생성
        return f'''
<div class="my-6 rounded-xl overflow-hidden shadow-lg">
    <img src="{image_url}" alt="{keyword}" class="w-full h-auto object-cover" loading="lazy" onerror="this.parentElement.style.display='none'">
    <p class="text-xs text-gray-400 text-center py-2 bg-gray-50">Photo by Unsplash</p>
</div>
'''
    
    # [IMAGE:...] 패턴을 이미지 태그로 교체
    pattern = r'\[IMAGE:([^\]]+)\]'
    result = re.sub(pattern, replace_image, content)
    
    return result


def add_images_to_content_with_generation(content: str, use_ai_generation: bool = True) -> str:
    """
    [IMAGE:...] 키워드를 이미지로 변환 (Unsplash 우선, 실패 시 AI 생성)
    
    Args:
        content: HTML 콘텐츠
        use_ai_generation: AI 이미지 생성 사용 여부
    
    Returns:
        이미지가 삽입된 HTML
    """
    import re
    
    def replace_image(match):
        keyword = match.group(1).strip()
        
        # 한글 키워드 검증 및 경고
        if any('\uac00' <= char <= '\ud7a3' for char in keyword):
            print(f"    ⚠️ 한글 키워드 발견: {keyword}")
            # 기본 영어 키워드로 대체
            keyword = "modern technology workspace"
        
        # 키워드 정제 (영어로 확인)
        print(f"    🔍 이미지 검색: {keyword}")
        
        # 1차: Unsplash 시도
        image_url = search_unsplash_image(keyword)
        source_text = "Photo by Unsplash"
        
        # 2차: AI 생성 시도 (선택적)
        # 현재는 Unsplash만 사용 (안정성)
        
        # 이미지 HTML 생성
        return f'''
<div class="my-6 rounded-xl overflow-hidden shadow-lg">
    <img src="{image_url}" alt="{keyword}" class="w-full h-auto object-cover" loading="lazy" onerror="this.parentElement.style.display='none'">
    <p class="text-xs text-gray-400 text-center py-2 bg-gray-50">{source_text}</p>
</div>
'''
    
    # [IMAGE:...] 패턴을 이미지 태그로 교체
    pattern = r'\[IMAGE:([^\]]+)\]'
    result = re.sub(pattern, replace_image, content)
    
    return result


if __name__ == "__main__":
    # 테스트
    test_keywords = [
        "modern workspace with laptop",
        "artificial intelligence concept",
        "productivity tools",
        "ChatGPT interface"
    ]
    
    print("🖼️ Unsplash 이미지 검색 테스트\n")
    
    for keyword in test_keywords:
        url = search_unsplash_image(keyword)
        print(f"✅ {keyword}")
        print(f"   → {url}\n")
