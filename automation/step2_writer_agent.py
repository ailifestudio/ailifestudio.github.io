#!/usr/bin/env python3
"""
Step 2: Writer & Art Director Agent (Final)
- 기능: 에디터 모드 & 창작 모드
- 필수 1: "Intro:" 접두사 절대 금지 (자연스러운 한글 소제목)
- 필수 2: 썸네일(img_1) 포함 이미지 3~5장 필수 생성
- 필수 3: 스크롤 방지 (Tip Box 사용)
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
        manual_content = os.getenv('MANUAL_CONTENT', '').strip()
        
        # [공통 규칙]
        common_rules = """
        ### 🚨 CRITICAL RULES (Must Follow):
        1. **NO "Intro:" Prefix:** The first heading MUST be a natural Korean title (e.g., "업무 효율이 고민이신가요?"), **NEVER** start with "Intro:" or "서론:".
        2. **IMAGE COUNT:** You MUST include **3 to 5 images** in total.
        3. **THUMBNAIL (Important):** The first image (`img_1`) is the **Blog Thumbnail**. It must be the most representative and high-quality wide shot.
        4. **SCROLL FIX:** NEVER use `code_block` (```). Use `tip_box` for prompts.
        """
        
        if manual_content:
            print("\n" + "="*60)
            print("📝 Step 2: Editor Mode (수동 본문 정리)")
            print("="*60)
            
            writer_prompt = f"""
You are a professional Editor.
**Topic:** {topic}
**User's Draft:**
{manual_content}

**Task:**
1. Organize the draft into a structured blog post (JSON).
2. **Expand content:** Min 300 chars/paragraph.
3. **Insert Images:** Add 3~5 images (First one is thumbnail).

{common_rules}

**JSON Schema Example:**
{{
  "title": "{topic}",
  "sections": [
    {{ "type": "heading", "level": 2, "content": "독자를 사로잡는 첫 소제목 (Intro X)" }},
    {{ "type": "paragraph", "content": "..." }},
    {{ 
      "type": "image_placeholder", 
      "id": "img_1", 
      "description": "Thumbnail shot, cinematic, wide angle, 8k, --no ugly hands", 
      "description_ko": "썸네일용 대표 이미지 설명 (필수)",
      "position": "after_intro" 
    }},
    {{ "type": "heading", "level": 3, "content": "..." }},
    {{ "type": "paragraph", "content": "..." }},
    {{ 
      "type": "image_placeholder", 
      "id": "img_2", 
      "description": "...", 
      "description_ko": "...",
      "position": "middle" 
    }},
    {{ "type": "tip_box", "content": "Korean Prompt Example (No code_block)" }}
  ],
  "summary": "Summary",
  "tags": ["Tag1"]
}}
"""
        else:
            print("\n" + "="*60)
            print("📝 Step 2: Creator Mode (AI 창작)")
            print("="*60)
            
            writer_prompt = f"""
You are a professional IT Tech Editor.
**Topic:** {topic}
**Task:** Write a high-quality blog post in **JSON format**.

**Rules:**
1. **Length:** Minimum 300~500 characters per paragraph.
2. **Content:** Rich details, Why/How/Examples.
3. **Images:** 3~5 images required. 50+ words description. Avoid close-ups.

{common_rules}

**JSON Schema Example:**
{{
  "title": "{topic}",
  "sections": [
    {{ "type": "heading", "level": 2, "content": "흥미로운 도입부 소제목 (Intro 절대 금지)" }},
    {{ "type": "paragraph", "content": "Write very long intro..." }},
    {{ 
      "type": "image_placeholder", 
      "id": "img_1", 
      "description": "Best quality thumbnail shot, cinematic lighting, wide angle, 8k", 
      "description_ko": "블로그 썸네일용 이미지 설명 (필수)",
      "position": "after_intro" 
    }},
    {{ "type": "heading", "level": 3, "content": "Section 1" }},
    {{ "type": "paragraph", "content": "Write detailed content..." }},
    {{ 
      "type": "image_placeholder", 
      "id": "img_2", 
      "description": "...", 
      "description_ko": "...",
      "position": "middle" 
    }},
    {{ "type": "tip_box", "content": "Useful tip (No ```)" }},
    {{ "type": "paragraph", "content": "..." }},
    {{ 
      "type": "image_placeholder", 
      "id": "img_3", 
      "description": "...", 
      "description_ko": "...",
      "position": "end" 
    }}
  ],
  "summary": "Summary",
  "tags": ["Tag1"]
}}
"""

        try:
            print("\n✍️ 콘텐츠 생성/정리 중...")
            response_text = self._generate_with_retry(writer_prompt)
            clean_text = response_text.strip()
            if clean_text.startswith('```json'): clean_text = clean_text[7:]
            if clean_text.startswith('```'): clean_text = clean_text[3:]
            if clean_text.endswith('```'): clean_text = clean_text[:-3]
            content_data = json.loads(clean_text.strip())
            
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
        agent = WriterAgent()
        topic = agent.load_topic()
        result = agent.generate_structured_content(topic['title'])
        agent.save_output(result)
        print("\n✅ Step 2 완료!")
    except Exception as e:
        print(f"\n❌ Step 2 실패: {e}")
        exit(1)

if __name__ == "__main__":
    main()
