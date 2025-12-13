#!/usr/bin/env python3
"""
이미지 키워드 자동 매칭 시스템
- 새로운 키워드를 기존 이미지와 자동 매칭
- 유사도 기반 fallback 제공
"""

import json
from pathlib import Path
from typing import Optional


# 키워드 패턴 매핑 (소문자로 변환 후 매칭)
KEYWORD_PATTERNS = {
    # AI 관련
    "ai": ["AI algorithm processing diverse data types", "futuristic AI assistant interface with personalized data"],
    "brain": ["AI brain generating creative ideas", "creative thought process with AI integration"],
    "creative": ["AI brain generating creative ideas", "creative thought process with AI integration"],
    "idea": ["AI brain generating creative ideas", "futuristic brainstorming session with holographic AI interface"],
    "brainstorm": ["futuristic brainstorming session with holographic AI interface", "diverse professionals using AI for problem solving"],
    "thinking": ["AI brain generating creative ideas", "creative thought process with AI integration"],
    
    # 업무/생산성
    "work": ["professional working on computer with AI assistant dashboard", "person using productivity tools on computer"],
    "productivity": ["person using productivity tools on computer", "professional working on computer with AI assistant dashboard"],
    "dashboard": ["data dashboard with automated report", "professional working on computer with AI assistant dashboard"],
    "report": ["data dashboard with automated report", "AI analyzing complex financial documents"],
    "document": ["AI analyzing complex financial documents", "person using productivity tools on computer"],
    
    # 기술/도구
    "tool": ["various AI tools icons on a digital screen", "person using productivity tools on computer"],
    "interface": ["futuristic AI assistant interface with personalized data", "smart home interface showing AI assistant controlling devices"],
    "chatbot": ["person typing complex prompt into an AI chatbot", "person typing detailed prompt into AI interface"],
    "assistant": ["futuristic AI assistant interface with personalized data", "professional working on computer with AI assistant dashboard"],
    
    # 협업/팀워크
    "team": ["diverse professionals using AI for problem solving", "futuristic brainstorming session with holographic AI interface"],
    "collaboration": ["diverse professionals using AI for problem solving", "product manager brainstorming app features with AI"],
    "professional": ["diverse professionals using AI for problem solving", "professional working on computer with AI assistant dashboard"],
    
    # 스마트홈/IoT
    "smart": ["smart home interface showing AI assistant controlling devices", "futuristic AI assistant interface with personalized data"],
    "home": ["smart home interface showing AI assistant controlling devices", "person using productivity tools on computer"],
    
    # 기타
    "warning": ["warning sign over AI robot head"],
    "synergy": ["synergy between human and AI intelligence", "diverse professionals using AI for problem solving"],
    "flowchart": ["flowchart illustrating AI-guided brainstorming steps", "data dashboard with automated report"],
}


def load_generated_images() -> dict:
    """생성된 이미지 맵 로드"""
    json_path = Path(__file__).parent / "generated_images.json"
    
    if json_path.exists():
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    return {}


def find_matching_image(keyword: str) -> Optional[str]:
    """
    키워드와 매칭되는 이미지 찾기
    
    Args:
        keyword: 검색 키워드
    
    Returns:
        매칭된 이미지 URL 또는 None
    """
    keyword_lower = keyword.lower()
    generated_images = load_generated_images()
    
    # 1순위: 정확히 일치
    if keyword in generated_images:
        return generated_images[keyword]
    
    # 2순위: 패턴 매칭 (키워드에 포함된 단어 찾기)
    for pattern_key, fallback_keywords in KEYWORD_PATTERNS.items():
        if pattern_key in keyword_lower:
            # 첫 번째 fallback 키워드 사용
            for fallback in fallback_keywords:
                if fallback in generated_images:
                    print(f"      📌 유사 이미지 사용: '{pattern_key}' → '{fallback}'")
                    return generated_images[fallback]
    
    # 3순위: 기본 AI 이미지
    default_key = "futuristic AI assistant interface with personalized data"
    if default_key in generated_images:
        print(f"      ⚠️ 기본 AI 이미지 사용")
        return generated_images[default_key]
    
    return None


def get_image_for_keyword(keyword: str) -> str:
    """
    키워드에 대한 이미지 URL 반환 (fallback 포함)
    
    Args:
        keyword: 검색 키워드
    
    Returns:
        이미지 URL (항상 반환)
    """
    # 매칭 시도
    image_url = find_matching_image(keyword)
    
    if image_url:
        return image_url
    
    # Fallback: Picsum.photos (키워드 기반 해시)
    import hashlib
    keyword_hash = hashlib.md5(keyword.lower().encode()).hexdigest()
    fallback_url = f"https://picsum.photos/seed/{keyword_hash[:16]}/1280/720"
    print(f"      🔧 Picsum fallback 사용")
    
    return fallback_url


if __name__ == "__main__":
    # 테스트
    test_keywords = [
        "AI brain generating creative ideas",
        "person working on laptop",
        "innovative technology concept",
        "data analysis dashboard"
    ]
    
    print("🧪 이미지 매칭 테스트:\n")
    for kw in test_keywords:
        url = get_image_for_keyword(kw)
        print(f"  '{kw}'")
        print(f"  → {url[:70]}...\n")
