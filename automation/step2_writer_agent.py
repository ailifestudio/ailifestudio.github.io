#!/usr/bin/env python3
"""
Step 2: Writer & Art Director Agent (Volume Booster V3)
- 모델: gemini-2.5-flash
- 수정 1: "각 섹션 최소 500자 이상 작성" 강제 (내용 증발 해결)
- 수정 2: "description_ko" 필드 누락 방지 (이미지 설명 한글화)
- 수정 3: 이미지 생성 시 '인물/손' 클로즈업 자제 요청 (기괴함 방지)
"""

import google.generativeai as genai
import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import List

class WriterAgent:
    def __init__(self, config_path="config_ai.json"):
        self.config = {}
        if Path(config_path).exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        
        self.api_keys = self._load_api_keys()
        self.current_key_index = 0
        
        if not self.api_keys:
            raise ValueError("❌ GEMINI_API_KEY가 설정되지 않았습니다.")
        
        genai.configure(api_key=self.api_keys[0])
        self.model_name = "gemini-2.5-flash"
        self.model = genai.GenerativeModel(self.model_name)
    
    def _load_api_keys(self) -> List[str]:
        keys_json = os.getenv('GEMINI_API_KEYS', '')
        if keys_json:
            try:
                keys = json.loads(keys_json)
                return keys if isinstance(keys, list) else []
            except: pass
        single_key = os.getenv('GEMINI_API_KEY', self.config.get('gemini_api_key', ''))
        return [single_key] if single_key else []
    
    def _generate_with_retry(self, prompt: str, max_key_rotations: int = None) -> str:
        if max_key_rotations is None: max_key_rotations = len(self.api_keys)
        
        for attempt in range(max_key_rotations):
            try:
                print(f"   🤖 시도: {self.model_name} (Key #{self.current_key_index + 1})")
                response = self.model.generate_content(
                    prompt,
                    generation_config={"response_mime_type": "application/json"}
                )
                return response.text
            except Exception as e:
                error_str = str(e)
                print(f"   ⚠️ 오류: {error_str.split('message')[0][:80]}...")
                if '429' in error_str or 'quota' in error_str.lower():
                    if self.current_key_index < len(self.api_keys) - 1:
                        self.current_key_index += 1
                        print(f"   🔄 쿼터 초과! Key #{self.current_key_index + 1}로 교체")
                        genai.configure(api_key=self.api_keys[self.current_key_index])
                        self.model = genai.GenerativeModel(self.model_name)
                        time.sleep(2)
                        continue
                    else: raise e
                time.sleep(5)
                if attempt == max_key_rotations - 1: raise e

    def load_topic(self, input_path: str = "automation/intermediate_outputs/step1_topic.json") -> dict:
        with open(input_path, 'r', encoding='utf-8') as f: return json.load(f)
    
    def generate_structured_content(self, topic: str) -> dict:
        print("\n" + "="*60)
        print("📝 Step 2: Writer Agent (Volume Booster V3)")
        print("   ⚙️  목표: 본문 내용 길게 쓰기 + 이미지 한글 설명 필수")
        print("="*60)
        
        writer_prompt = f"""
You are a professional IT Tech Editor.
**Topic:** {topic}

Your task is to write a high-quality blog post in **JSON format**.

### 🚨 CRITICAL RULES (Must Follow):
1.  **LENGTH (Very Important):**
    - Do NOT summarize. Write in full detail.
    - Each `paragraph` content MUST be at least **300~500 characters** (Korean).
    - Explain "Why", "How", "Example" in every section.

2.  **IMAGE DESCRIPTION:**
    - `description` (English): Cinematic lighting, wide shot, 8k resolution. **Avoid close-ups of hands or faces to prevent AI artifacts.**
    - `description_ko` (Korean): **REQUIRED.** Summarize the image description in Korean. (e.g., "사무실에서 일하는 남성")

3.  **NO CODE:** Use "Korean Prompts" instead of Python code.

### JSON Schema:
{{
  "title": "Title (Korean)",
  "sections": [
    {{ "type": "heading", "level": 2, "content": "Intro Title" }},
    {{ "type": "paragraph", "content": "Write a very long introduction (minimum 5 sentences)..." }},
    {{ 
      "type": "image_placeholder", 
      "id": "img_1", 
      "description": "Cinematic shot of [Subject], wide angle, soft lighting, 8k, photorealistic --no ugly hands", 
      "description_ko": "이미지에 대한 한글 설명 (필수 입력)",
      "position": "after_intro" 
    }},
    {{ "type": "heading", "level": 3, "content": "Section 1 Title" }},
    {{ "type": "paragraph", "content": "Write detailed content (minimum 500 characters)..." }},
    {{ "type": "tip_box", "content": "Useful tip..." }},
    {{ "type": "code_block", "language": "text", "content": "Korean Prompt Example" }},
    {{ "type": "warning_box", "content": "Warning note..." }},
    {{ "type": "paragraph", "content": "Conclusion..." }}
  ],
  "summary": "Short summary",
  "tags": ["Tag1", "Tag2"]
}}
"""
        try:
            print("\n✍️ 콘텐츠 생성 중 (장문 모드)...")
            response_text = self._generate_with_retry(writer_prompt)
            content_data = json.loads(response_text)
            
            # 결과 검증
            if len(content_data.get('sections', [])) > 0:
                first_p = next((s['content'] for s in content_data['sections'] if s['type'] == 'paragraph'), "")
                print(f"   ℹ️ 첫 문단 길이: {len(first_p)}자 (목표: 300자 이상)")

            return {
                "title": topic,
                "sections": content_data.get('sections', []),
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
        WriterAgent().save_output(WriterAgent().generate_structured_content(WriterAgent().load_topic()['title']))
        print("\n✅ Step 2 완료!")
    except Exception as e:
        print(f"\n❌ Step 2 실패: {e}")
        exit(1)

if __name__ == "__main__":
    main()
