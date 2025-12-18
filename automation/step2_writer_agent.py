#!/usr/bin/env python3
"""
Step 2: Writer & Art Director Agent (Return of 2.5 Flash)
- 전략: 쿼터 초기화를 기대하며 '유일하게 인식된 모델'인 2.5-flash 사용
- 설정: 코딩 금지 + 이미지 묘사 이중화
"""

import google.generativeai as genai
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict
import time

class WriterAgent:
    def __init__(self, config_path="config_ai.json"):
        """Gemini API 초기화"""
        self.config = {}
        if Path(config_path).exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        
        self.api_keys = self._load_api_keys()
        self.current_key_index = 0
        
        if not self.api_keys:
            raise ValueError("❌ GEMINI_API_KEY가 설정되지 않았습니다.")
        
        genai.configure(api_key=self.api_keys[0])
        
        # [수정] 로그에서 유일하게 '존재함(404 아님)'이 확인된 모델
        self.model_name = "gemini-2.5-flash"
        self.model = genai.GenerativeModel(self.model_name)
    
    def _load_api_keys(self) -> List[str]:
        keys_json = os.getenv('GEMINI_API_KEYS', '')
        if keys_json:
            try:
                keys = json.loads(keys_json)
                return keys if isinstance(keys, list) else []
            except:
                pass
        single_key = os.getenv('GEMINI_API_KEY', self.config.get('gemini_api_key', ''))
        return [single_key] if single_key else []
    
    def _generate_with_retry(self, prompt: str, max_key_rotations: int = None) -> str:
        if max_key_rotations is None:
            max_key_rotations = len(self.api_keys)
        
        for attempt in range(max_key_rotations):
            try:
                print(f"   🤖 시도: {self.model_name} (Key #{self.current_key_index + 1})")
                response = self.model.generate_content(prompt)
                return response.text
            except Exception as e:
                error_str = str(e)
                print(f"   ⚠️ 오류: {error_str.split('message')[0][:80]}...")
                
                # 429 (쿼터 초과) 발생 시 키 교체
                if '429' in error_str or 'quota' in error_str.lower():
                    if self.current_key_index < len(self.api_keys) - 1:
                        self.current_key_index += 1
                        print(f"   🔄 쿼터 초과! Key #{self.current_key_index + 1}로 교체하여 재시도")
                        genai.configure(api_key=self.api_keys[self.current_key_index])
                        self.model = genai.GenerativeModel(self.model_name)
                        time.sleep(2)
                        continue
                    else:
                        print("❌ 모든 키의 쿼터가 소진되었습니다.")
                        raise e
                
                # 그 외 오류 (404 등)
                time.sleep(5)
                if attempt == max_key_rotations - 1:
                    raise e
    
    def load_topic(self, input_path: str = "automation/intermediate_outputs/step1_topic.json") -> dict:
        with open(input_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def generate_structured_content(self, topic: str) -> dict:
        print("\n" + "="*60)
        print("📝 Step 2: Writer Agent (Retry 2.5 Flash)")
        print(f"   ⚙️  모델: {self.model_name} (쿼터 리셋 기대)")
        print("   ⚙️  설정: 코딩 금지 + 이미지 묘사 이중화")
        print("="*60)
        
        writer_prompt = f"""# Role Definition
당신은 IT 비전공자도 쉽게 이해할 수 있는 콘텐츠를 만드는 '친절한 IT 에디터'이자, 시각적 완성도를 책임지는 '아트 디렉터'입니다.

# Topic
주제: {topic}

# Task
위 주제에 대해 **구조화된 JSON 형식**으로 블로그 콘텐츠를 작성하십시오.

# Target Audience
- 코딩을 전혀 모르는 일반 직장인
- AI 툴을 업무에 바로 활용하고 싶어하는 비개발자

# Writing Rules (매우 중요)
1. **쉬운 용어:** 전문 용어는 피하거나 쉽게 풀어서 설명하세요.
2. **코딩 금지:** Python, API, JSON 등 프로그래밍 코드는 **절대 작성하지 마십시오.**
3. **실전 활용:** 이론보다는 "당장 내일 써먹을 수 있는 방법"을 알려주세요.

# ★ 'code_block' 작성 규칙 (엄격 준수):
`code_block`에는 프로그래밍 코드 대신, **독자가 AI 채팅창에 복사해서 붙여넣을 수 있는 '한글 지시문(Prompt)'**을 넣으세요.
- ❌ Bad (작성 금지): `import requests`
- ⭕ Good (작성 권장): "신규 입사자를 위한 온보딩 매뉴얼 목차를 짜줘."

# ★ [매우 중요] Image Art Directing Rules (Flux Model Optimized)
이미지 퀄리티를 높이기 위해 `description`을 **최대한 길고, 구체적이고, 묘사적으로(Descriptive)** 작성하세요.

1. **`description` (영어 - 생성용)**:
   - 50단어 이상의 영어 문장. 조명, 구도, 인물 묘사, 8k, photorealistic 키워드 포함.
2. **`description_ko` (한글 - 관리용)**:
   - 위 내용을 요약한 한글 설명.

# JSON Structure
{{
  "sections": [
    {{"type": "heading", "level": 2, "content": "제목"}},
    {{"type": "paragraph", "content": "서론..."}},
    {{
      "type": "image_placeholder", 
      "id": "img_1", 
      "description": "Long English description...", 
      "description_ko": "한글 설명...",
      "position": "after_intro"
    }},
    {{"type": "heading", "level": 3, "content": "섹션 1"}},
    {{"type": "paragraph", "content": "내용..."}},
    {{"type": "tip_box", "content": "꿀팁..."}},
    {{"type": "code_block", "language": "text", "content": "한글 예시"}},
    {{"type": "warning_box", "content": "주의사항..."}},
    {{"type": "paragraph", "content": "결론"}}
  ],
  "summary": "요약",
  "tags": ["AI", "활용팁"]
}}

# Output Format
- JSON 형식으로만 출력하십시오.
"""
        
        try:
            print("\n✍️ 콘텐츠 생성 중...")
            response = self._generate_with_retry(writer_prompt)
            
            # JSON 파싱
            response = response.strip()
            if response.startswith('```json'): response = response[7:]
            if response.startswith('```'): response = response[3:]
            if response.endswith('```'): response = response[:-3]
            
            content_data = json.loads(response.strip())
            return {
                "title": topic,
                "sections": content_data['sections'],
                "summary": content_data.get('summary', ''),
                "tags": content_data.get('tags', []),
                "generated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            print(f"\n❌ 실패: {e}")
            raise

    def save_output(self, data: dict, output_path: str = "automation/intermediate_outputs/step2_structured_content.json"):
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"💾 저장 완료: {output_path}")

def main():
    try:
        agent = WriterAgent()
        topic = agent.load_topic()
        result = agent.generate_structured_content(topic['title'])
        agent.save_output(result)
        print("\n✅ Step 2 완료! (Gemini 2.5 Flash)")
    except Exception as e:
        print(f"\n❌ Step 2 실패: {e}")
        exit(1)

if __name__ == "__main__":
    main()
