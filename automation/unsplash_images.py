#!/usr/bin/env python3
"""
Unsplash API를 활용한 무료 이미지 검색
저작권 걱정 없는 고품질 이미지
"""

import requests
import urllib.parse


def search_unsplash_image(keyword: str, access_key: str = None) -> str:
    """
    Unsplash에서 키워드에 맞는 이미지 검색
    
    Args:
        keyword: 검색 키워드 (영어)
        access_key: Unsplash API 키 (없으면 기본 URL 반환)
    
    Returns:
        이미지 URL
    """
    # API 키가 없으면 Unsplash Source 사용 (무료, 키 불필요)
    if not access_key:
        # Unsplash Source API (랜덤 이미지)
        encoded_keyword = urllib.parse.quote(keyword)
        return f"https://source.unsplash.com/800x600/?{encoded_keyword}"
    
    # API 키가 있으면 공식 API 사용
    try:
        url = "https://api.unsplash.com/search/photos"
        params = {
            "query": keyword,
            "per_page": 1,
            "orientation": "landscape"
        }
        headers = {
            "Authorization": f"Client-ID {access_key}"
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data['results']:
                return data['results'][0]['urls']['regular']
    except Exception as e:
        print(f"  ⚠️ Unsplash API 오류: {e}")
    
    # 실패 시 기본 URL
    encoded_keyword = urllib.parse.quote(keyword)
    return f"https://source.unsplash.com/800x600/?{encoded_keyword}"


def extract_keywords_from_content(content: str) -> list:
    """
    콘텐츠에서 [IMAGE:...] 키워드 추출
    
    Args:
        content: HTML 콘텐츠
    
    Returns:
        이미지 키워드 리스트
    """
    import re
    pattern = r'\[IMAGE:([^\]]+)\]'
    keywords = re.findall(pattern, content)
    return [kw.strip() for kw in keywords]


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
    <img src="{image_url}" alt="{keyword}" class="w-full h-auto object-cover" loading="lazy">
    <p class="text-xs text-gray-400 text-center py-2 bg-gray-50">📷 Photo by <a href="https://unsplash.com" target="_blank" class="underline">Unsplash</a></p>
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
