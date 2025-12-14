#!/usr/bin/env python3
"""
Step 2: Writer & Art Director Agent
- 구조화된 JSON 콘텐츠 생성 (HTML 아님!)
- 아트 디렉팅: 이미지 플레이스홀더 + 영어 설명
- 한국적 맥락 강제 (Korean professional, Seoul office 등)
"""

import google.generativeai as genai
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict


class WriterAgent:
    def __init__(self, config_path="config_ai.json"):
        """Gemini API 초기화"""
        # config 파일은 선택사항 (환경변수 우선)
        self.config = {}
        if Path(config_path).exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        
        self.api_keys = self._load_api_keys()
        self.current_key_index = 0
        
        if not self.api_keys:
            raise ValueError("❌ GEMINI_API_KEY가 설정되지 않았습니다.")
        
        genai.configure(api_key=self.api_keys[0])
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        
        print(f"✅ Gemini API 초기화 완료")
    
    def _load_api_keys(self) -> List[str]:
        """API 키 로드"""
        keys_json = os.getenv('GEMINI_API_KEYS', '')
        if keys_json:
            try:
                keys = json.loads(keys_json)
                if isinstance(keys, list) and keys:
                    return keys
            except:
                pass
        
        single_key = os.getenv('GEMINI_API_KEY', self.config.get('gemini_api_key', ''))
        if single_key:
            return [single_key]
        
        return []
    
    def _generate_with_retry(self, prompt: str) -> str:
        """API 호출 (재시도 포함)"""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"⚠️ API 호출 실패: {e}")
            raise
    
    def load_topic(self, input_path: str = "automation/intermediate_outputs/step1_topic.json") -> dict:
        """Step 1 출력 로드"""
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"\n📥 Step 1 출력 로드:")
        print(f"   제목: {data['title']}")
        
        return data
    
    def generate_structured_content(self, topic: str) -> dict:
        """구조화된 콘텐츠 생성 (JSON 형식)"""
        print("\n" + "="*60)
        print("📝 Step 2: Writer & Art Director Agent")
        print("="*60)
        
        # 프롬프트: 구조화된 JSON 출력 요청
        writer_prompt = f"""# Role Definition
당신은 대한민국 상위 1% IT/Tech 전문 블로거이자, 콘텐츠의 시각적 완성도를 책임지는 아트 디렉터(Art Director)입니다.

# Topic
주제: {topic}

# Task
위 주제에 대해 **구조화된 JSON 형식**으로 블로그 콘텐츠를 작성하십시오.

# JSON 구조 (반드시 이 형식으로 출력)
{{
  "sections": [
    {{"type": "heading", "level": 2, "content": "제목"}},
    {{"type": "paragraph", "content": "서론 내용 (인사말 생략, 페인포인트 자극 2-3문단)"}},
    {{"type": "image_placeholder", "id": "img_1", "description": "A confident Korean IT professional (age 30-40) sitting in a modern Seoul office with floor-to-ceiling windows showing Namsan Tower in the background, natural afternoon lighting, professional photography style, 8k quality", "position": "after_intro"}},
    {{"type": "heading", "level": 3, "content": "섹션 1 제목"}},
    {{"type": "paragraph", "content": "섹션 1 내용"}},
    {{"type": "tip_box", "content": "실무에서는..."}},
    {{"type": "image_placeholder", "id": "img_2", "description": "...", "position": "after_section_1"}},
    {{"type": "heading", "level": 3, "content": "섹션 2 제목"}},
    {{"type": "paragraph", "content": "섹션 2 내용"}},
    {{"type": "warning_box", "content": "주의: ..."}},
    {{"type": "code_block", "language": "python", "content": "코드 예시"}},
    {{"type": "paragraph", "content": "요약 및 CTA"}}
  ],
  "summary": "2-3문장 요약",
  "tags": ["AI", "업무자동화", "실전활용"]
}}

# Writing Rules
1. 분량: 전체 paragraph 내용 합계 1,500자 이상
2. 구조: 서론 → 본론(4-6개 섹션) → 실무 팁 → 주의사항 → 요약
3. 각 섹션은 반드시 독립된 객체로 작성
4. paragraph 타입: 한 문단당 하나의 객체
5. tip_box, warning_box는 최소 1개씩 포함

# 🎨 Image Art Directing Rules (매우 중요!)
**이미지 플레이스홀더 작성 시 필수 준수 사항:**

1. 위치: 
   - img_1은 서론 직후 필수 (썸네일용)
   - img_2~5는 핵심 섹션 직후 배치 (최대 5개)

2. description 작성 규칙:
   - 반드시 영어(English)로 작성
   - 한국적 맥락 필수 포함:
     * 인물: "Korean professional", "Asian ethnicity", "Korean business styling"
     * 배경: "Modern office in Seoul", "Han River view", "Gangnam city street"
     * UI: "Korean text interface (Hangul)", "KakaoTalk style UI"
   - 구체적 묘사: "A confident Korean IT professional (age 30-40) sitting..."
   - 품질 키워드: "professional photography", "8k quality", "natural lighting", "cinematic shot"

3. 나쁜 예시 (절대 금지):
   ❌ "description": "사람이 일하는 모습" (한글)
   ❌ "description": "office" (너무 간략)
   ❌ "description": "person working" (국적 불명)

4. 좋은 예시:
   ✅ "description": "A confident Korean IT professional (age 30-40) sitting in a modern Seoul office with floor-to-ceiling windows showing Namsan Tower in the background, typing on MacBook, natural afternoon lighting, professional photography style, 8k quality"
   ✅ "description": "Korean business team (3-4 people, mixed gender, professional attire) discussing AI strategy around a large monitor displaying Korean text dashboard, modern Gangnam office interior, warm collaborative atmosphere, cinematic wide shot"

# Output Format
- JSON 형식으로만 출력하십시오.
- 설명이나 주석은 절대 포함하지 마십시오.
- 유효한 JSON 문법을 준수하십시오.
"""
        
        try:
            print("\n✍️ 구조화된 콘텐츠 생성 중...")
            response = self._generate_with_retry(writer_prompt)
            
            # JSON 파싱
            # Gemini가 ```json ... ``` 형식으로 반환할 수 있으므로 정리
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:]
            if response.startswith('```'):
                response = response[3:]
            if response.endswith('```'):
                response = response[:-3]
            response = response.strip()
            
            content_data = json.loads(response)
            
            # 검증
            if 'sections' not in content_data:
                raise ValueError("sections 키가 없습니다.")
            
            # 통계
            total_paragraphs = sum(1 for s in content_data['sections'] if s['type'] == 'paragraph')
            total_images = sum(1 for s in content_data['sections'] if s['type'] == 'image_placeholder')
            total_chars = sum(len(s.get('content', '')) for s in content_data['sections'] if s['type'] == 'paragraph')
            
            print(f"\n✅ 콘텐츠 생성 완료:")
            print(f"   📊 섹션 수: {len(content_data['sections'])}")
            print(f"   📝 문단 수: {total_paragraphs}")
            print(f"   🎨 이미지 플레이스홀더: {total_images}개")
            print(f"   📏 총 글자 수: {total_chars}자")
            
            # 이미지 플레이스홀더 상세 정보
            print(f"\n🎨 아트 디렉팅 결과:")
            for section in content_data['sections']:
                if section['type'] == 'image_placeholder':
                    print(f"   • {section['id']}: {section['description'][:60]}...")
            
            result = {
                "title": topic,
                "sections": content_data['sections'],
                "summary": content_data.get('summary', ''),
                "tags": content_data.get('tags', []),
                "generated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "agent": "step2_writer_agent",
                "stats": {
                    "total_sections": len(content_data['sections']),
                    "total_paragraphs": total_paragraphs,
                    "total_images": total_images,
                    "total_chars": total_chars
                }
            }
            
            return result
            
        except json.JSONDecodeError as e:
            print(f"\n❌ JSON 파싱 실패: {e}")
            print(f"응답 내용:\n{response[:500]}...")
            raise
        except Exception as e:
            print(f"\n❌ 콘텐츠 생성 실패: {e}")
            raise
    
    def save_output(self, data: dict, output_path: str = "automation/intermediate_outputs/step2_structured_content.json"):
        """Step 2 출력 저장"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 출력 저장: {output_path}")
        print(f"   크기: {output_file.stat().st_size} bytes")


def main():
    """메인 실행 함수"""
    try:
        agent = WriterAgent()
        
        # Step 1 출력 로드
        topic_data = agent.load_topic()
        
        # 구조화된 콘텐츠 생성
        result = agent.generate_structured_content(topic_data['title'])
        
        # 출력 저장
        agent.save_output(result)
        
        print("\n" + "="*60)
        print("✅ Step 2 완료!")
        print("="*60)
        print(f"\n다음 단계: python automation/step3_image_audit_agent.py")
        
    except Exception as e:
        print(f"\n❌ Step 2 실패: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()
