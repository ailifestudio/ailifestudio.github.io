#!/usr/bin/env python3
"""
컨텍스트 기반 이미지 생성 시스템
- 섹션 내용을 분석하여 최적화된 이미지 프롬프트 생성
- Gemini API로 섹션 내용 분석 및 번역
- Pollinations.ai로 고품질 이미지 생성
"""

import os
import json
import re
import requests
import google.generativeai as genai
from pathlib import Path
from typing import Dict, List, Tuple
import time


def load_api_keys() -> List[str]:
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


def extract_sections_with_markers(content: str) -> List[Tuple[str, str]]:
    """
    컨텐츠에서 섹션과 이미지 마커 추출
    
    Args:
        content: HTML 콘텐츠
    
    Returns:
        [(section_text, marker), ...] 리스트
    """
    # [IMAGE_PLACEHOLDER_N] 패턴 찾기
    pattern = r'\[IMAGE_PLACEHOLDER_(\d+)\]'
    markers = re.findall(pattern, content)
    
    if not markers:
        return []
    
    sections = []
    
    # 각 마커 주변의 섹션 텍스트 추출
    for marker_num in markers:
        marker = f"[IMAGE_PLACEHOLDER_{marker_num}]"
        
        # 마커 위치 찾기
        marker_pos = content.find(marker)
        if marker_pos == -1:
            continue
        
        # 마커 이전 500자 추출 (섹션 내용)
        start_pos = max(0, marker_pos - 500)
        section_text = content[start_pos:marker_pos]
        
        # HTML 태그 제거
        section_text = re.sub(r'<[^>]+>', ' ', section_text)
        section_text = re.sub(r'\s+', ' ', section_text).strip()
        
        sections.append((section_text, marker))
    
    return sections


def generate_image_prompt_from_context(context: str, api_key: str) -> str:
    """
    섹션 내용을 분석하여 최적화된 이미지 프롬프트 생성
    
    Args:
        context: 섹션 내용 (한글)
        api_key: Gemini API 키
    
    Returns:
        최적화된 영어 이미지 프롬프트
    """
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        
        prompt = f"""
다음 블로그 섹션 내용을 분석하여 최적의 이미지 생성 프롬프트를 만들어주세요.

섹션 내용:
{context[:500]}

요구사항:
1. 섹션의 핵심 내용을 시각적으로 표현할 수 있는 이미지 프롬프트 작성
2. 영어로만 작성 (한글 사용 금지)
3. 구체적이고 상세한 묘사 (10-15 단어)
4. Professional, high-quality, modern style
5. 16:9 aspect ratio
6. 실제 사진 또는 고품질 일러스트레이션

출력 형식: 영어 프롬프트 1줄만 (설명 없이)
예시: "person analyzing personal data on AI dashboard, modern workspace with multiple screens, professional photography, detailed"
"""
        
        response = model.generate_content(prompt)
        enhanced_prompt = response.text.strip().strip('"').strip("'")
        
        # 품질 향상 suffix 추가
        enhanced_prompt += ", professional photography, high quality, detailed, vibrant colors, 16:9 aspect ratio"
        
        return enhanced_prompt
        
    except Exception as e:
        print(f"      ⚠️ Gemini 분석 실패: {str(e)[:100]}")
        # Fallback: 컨텍스트에서 핵심 키워드 추출
        keywords = context[:100].split()[:5]
        return f"{' '.join(keywords)}, professional illustration, high quality, 16:9"


def generate_image_with_pollinations(prompt: str, output_path: str) -> str:
    """
    Pollinations.ai로 이미지 생성
    
    Args:
        prompt: 이미지 프롬프트
        output_path: 저장 경로
    
    Returns:
        저장된 이미지 경로
    """
    import urllib.parse
    
    encoded_prompt = urllib.parse.quote(prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1365&height=768&nologo=true&enhance=true"
    
    try:
        print(f"      🎨 이미지 생성 중...")
        response = requests.get(image_url, timeout=60)
        
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"      ✅ 생성 완료")
            return output_path
        else:
            print(f"      ⚠️ 생성 실패: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"      ⚠️ 오류: {e}")
        return None


def process_content_with_context_aware_images(content: str) -> str:
    """
    컨텐츠의 이미지 플레이스홀더를 컨텍스트 기반 이미지로 교체
    
    Args:
        content: HTML 콘텐츠
    
    Returns:
        이미지가 삽입된 HTML
    """
    print("   🔍 컨텍스트 기반 이미지 생성 시작...")
    
    # API 키 로드
    api_keys = load_api_keys()
    if not api_keys:
        print("   ⚠️ GEMINI_API_KEY 없음 - 기본 프롬프트 사용")
    
    # 섹션과 마커 추출
    sections = extract_sections_with_markers(content)
    
    if not sections:
        print("   ℹ️  이미지 플레이스홀더 없음")
        return content
    
    print(f"   ✅ {len(sections)}개 섹션 발견")
    
    # 출력 디렉토리
    output_dir = Path(__file__).parent / "generated_images"
    output_dir.mkdir(exist_ok=True)
    
    # 각 섹션 처리
    current_key_index = 0
    
    for i, (section_text, marker) in enumerate(sections, 1):
        print(f"\n   [{i}/{len(sections)}] {marker}")
        print(f"      📝 섹션: {section_text[:50]}...")
        
        # 1. Gemini로 프롬프트 생성
        if api_keys:
            api_key = api_keys[current_key_index % len(api_keys)]
            image_prompt = generate_image_prompt_from_context(section_text, api_key)
            current_key_index = (current_key_index + 1) % len(api_keys)
        else:
            image_prompt = f"{section_text[:100]}, professional illustration, high quality"
        
        print(f"      💡 프롬프트: {image_prompt[:80]}...")
        
        # 2. 이미지 생성
        import hashlib
        file_hash = hashlib.md5(image_prompt.encode()).hexdigest()[:8]
        output_file = output_dir / f"context_img_{file_hash}.png"
        
        result = generate_image_with_pollinations(image_prompt, str(output_file))
        
        # 3. HTML 교체
        if result:
            relative_path = f"automation/generated_images/context_img_{file_hash}.png"
            
            image_html = f'''
<div class="my-6 rounded-xl overflow-hidden shadow-lg">
    <img src="{relative_path}" alt="{section_text[:100]}" class="w-full h-auto object-cover" loading="lazy" onerror="this.parentElement.style.display='none'">
    <p class="text-xs text-gray-400 text-center py-2 bg-gray-50">AI Generated Image</p>
</div>
'''
            content = content.replace(marker, image_html)
        
        time.sleep(2)  # Rate limit
    
    print(f"\n   ✅ 컨텍스트 기반 이미지 생성 완료")
    
    return content


if __name__ == "__main__":
    # 테스트
    test_content = """
<h2>개인 데이터 기반 AI 코치</h2>
<p>개인의 건강, 습관, 목표를 데이터 기반으로 분석하여 맞춤형 코칭을 제공합니다.</p>
[IMAGE_PLACEHOLDER_1]
<h3>습관 형성의 과학</h3>
<p>AI는 당신의 수면 패턴, 활동량, 식습관을 분석하여 최적의 습관 형성 전략을 제시합니다.</p>
[IMAGE_PLACEHOLDER_2]
"""
    
    result = process_content_with_context_aware_images(test_content)
    print("\n=== 결과 ===")
    print(result[:500])
