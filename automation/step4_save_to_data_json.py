#!/usr/bin/env python3
"""
Step 4: Save to data.json & Markdown (Translator Edition)
- Step 3에서 검증된 콘텐츠를 최종 블로그 포맷으로 변환
- 영어 이미지 프롬프트를 '한글'로 자동 번역하여 캡션에 사용
- Markdown 파일 생성 (Jekyll/Github Pages용)
"""

import json
import os
from datetime import datetime
from pathlib import Path
import google.generativeai as genai
import time
import re

class DataSaver:
    def __init__(self, config_path="config_ai.json"):
        self.output_dir = Path(__file__).parent.parent
        self.data_file = self.output_dir / 'data.json'
        self.contents_dir = self.output_dir / 'contents'
        self.contents_dir.mkdir(exist_ok=True)
        self.image_dir = Path(__file__).parent / "generated_images" # 썸네일 확인용
        
        # 번역을 위한 Gemini 초기화
        self.config = {}
        if Path(config_path).exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        
        # 환경변수 우선, 없으면 config 파일 사용
        self.api_key = os.getenv('GEMINI_API_KEY', self.config.get('gemini_api_key', ''))
        
        if self.api_key:
            genai.configure(api_key=self.api_key)
            # 번역은 가볍고 빠른 1.5-flash 모델 사용
            self.model = genai.GenerativeModel("gemini-1.5-flash")
        else:
            print("⚠️ GEMINI_API_KEY가 없습니다. 번역 기능이 비활성화됩니다.")
            self.model = None

    def load_validated_content(self, input_path="automation/intermediate_outputs/step3_validated_content.json"):
        """Step 3 결과 로드"""
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("❌ Step 3 결과 파일이 없습니다.")
            return None

    def translate_descriptions(self, descriptions):
        """
        영어 설명 리스트를 한글로 일괄 번역 (API 1회 호출로 절약)
        """
        if not self.model or not descriptions:
            return descriptions # 키 없거나 데이터 없으면 원본 반환

        print(f"   🌐 이미지 설명 {len(descriptions)}개 한글로 번역 중...")
        
        # 프롬프트 구성
        prompt = "Translate the following image descriptions into natural Korean captions for a blog post. Return ONLY the translated lines in order, one per line.\n\n"
        for desc in descriptions:
            prompt += f"- {desc}\n"
            
        try:
            response = self.model.generate_content(prompt)
            # 결과 파싱 (줄바꿈으로 분리 및 불필요한 기호 제거)
            translated_lines = [line.strip().replace('- ', '') for line in response.text.strip().split('\n') if line.strip()]
            
            # 개수가 맞으면 반환, 아니면 원본 반환 (안전장치)
            if len(translated_lines) == len(descriptions):
                return translated_lines
            else:
                print("   ⚠️ 번역 개수 불일치로 원본 사용")
                return descriptions
        except Exception as e:
            print(f"   ⚠️ 번역 실패: {e}")
            return descriptions

    def create_markdown_content(self, data):
        """
        JSON -> Markdown 변환 (한글 캡션 + 영어 프롬프트 툴팁)
        """
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        today_date = datetime.now().strftime('%Y-%m-%d')
        
        md_content = "---\n"
        md_content += f"title: \"{data['title']}\"\n"
        md_content += f"date: {current_time}\n"
        md_content += f"layout: post\n"
        md_content += f"author: AI Editor\n"
        md_content += "category: ai\n"
        md_content += "---\n\n"

        sections = data.get('sections', [])
        
        # 1. 이미지 섹션만 모아서 번역 준비
        image_sections = [s for s in sections if s['type'] == 'image']
        english_descs = [s['description'] for s in image_sections]
        
        # 번역 실행
        korean_descs = self.translate_descriptions(english_descs)
        
        # 매핑용 딕셔너리 생성 (영어 -> 한글)
        desc_map = {eng: kor for eng, kor in zip(english_descs, korean_descs)}

        # 2. 본문 작성 Loop
        for section in sections:
            if section['type'] == 'text':
                md_content += f"{section['content']}\n\n"
            
            elif section['type'] == 'heading':
                md_content += f"{'#' * section['level']} {section['content']}\n\n"

            elif section['type'] == 'list':
                for item in section['items']:
                    md_content += f"- {item}\n"
                md_content += "\n"
            
            elif section['type'] == 'code':
                md_content += f"```python\n{section['content']}\n```\n\n"

            elif section['type'] == 'image':
                image_url = f"/{section['url']}" # 절대 경로
                eng_desc = section['description'].replace('"', "'") # 따옴표 충돌 방지
                kor_desc = desc_map.get(section['description'], eng_desc) # 번역본 가져오기 (없으면 영어)
                
                # HTML 구조 개선:
                # - alt: 한글 설명 (검색엔진 최적화)
                # - figcaption: 한글 설명 (진하게) + 영어 프롬프트 (작게)
                img_tag = f"""
<figure style="text-align:center; margin: 30px 0;">
  <img src="{image_url}" alt="{kor_desc}" style="max-width:100%; height:auto; border-radius:8px; box-shadow:0 4px 6px rgba(0,0,0,0.1);">
  <figcaption style="margin-top:10px; text-align: center;">
    <div style="color:#555; font-size:0.95em; font-weight:bold; margin-bottom:5px;">{kor_desc}</div>
    <div style="color:#aaa; font-size:0.8em; font-family:monospace; background:#f5f5f5; padding:4px 8px; border-radius:4px; display:inline-block;">Prompt: {eng_desc}</div>
  </figcaption>
</figure>
"""
                md_content += img_tag + "\n\n"
        
        # 3. 요약 추가
        if 'summary' in data:
            md_content += "---\n## 📝 요약\n"
            md_content += f"{data['summary']}\n"

        return md_content, today_date

    def update_data_json(self, new_article):
        """data.json 업데이트 (프론트엔드용)"""
        # 기존 파일 로드
        if self.data_file.exists():
            with open(self.data_file, 'r', encoding='utf-8') as f:
                try:
                    current_data = json.load(f)
                    if isinstance(current_data, dict) and 'articles' in current_data:
                        articles = current_data['articles']
                    else:
                        articles = current_data if isinstance(current_data, list) else []
                except json.JSONDecodeError:
                    articles = []
        else:
            articles = []

        # 중복 방지 (제목 기준 삭제 후 재삽입)
        articles = [a for a in articles if a['title'] != new_article['title']]
        
        # 최신 글을 맨 위로
        articles.insert(0, new_article)
        
        # 최대 50개 유지
        if len(articles) > 50:
            articles = articles[:50]

        # 저장
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump({"articles": articles}, f, ensure_ascii=False, indent=2)
        print(f"✅ data.json 업데이트 완료 ({len(articles)}개 글)")

    def run(self):
        data = self.load_validated_content()
        if not data: return

        print("\n💾 Step 4: Markdown 변환 및 저장 (번역 포함)")
        
        # Markdown 내용 생성
        md_content, date_str = self.create_markdown_content(data)
        
        # 파일명 생성
        timestamp = datetime.now().strftime('%H%M%S')
        filename = f"{date_str}-{timestamp}-ai-article.md"
        file_path = self.contents_dir / filename

        # .md 파일 저장
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"✅ Markdown 생성 완료: contents/{filename}")

        # 썸네일 이미지 찾기 (첫 번째 이미지 or 기본값)
        images = [s['url'] for s in data['sections'] if s['type'] == 'image']
        thumbnail = f"/{images[0]}" if images else "https://picsum.photos/800/400"
        
        # data.json 업데이트용 객체
        article_entry = {
            "title": data['title'],
            "summary": data.get('summary', '')[:120] + "...",
            "date": date_str,
            "category": "ai",
            "image": thumbnail,
            "link": f"/contents/{filename.replace('.md', '.html')}", # 링크 주소
            "tags": data.get('tags', []),
            "file_path": str(filename) # 나중에 찾기 쉽게
        }
        
        self.update_data_json(article_entry)

if __name__ == "__main__":
    saver = DataSaver()
    saver.run()
