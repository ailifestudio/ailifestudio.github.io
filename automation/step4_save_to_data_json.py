#!/usr/bin/env python3
"""
Step 4: Save to data.json & Markdown (Clean Image Version)
- 이미지 캡션(설명글)을 화면에서 완전히 제거
- 한글 설명 -> Alt Text(SEO용)로 숨김
- 영어 프롬프트 -> HTML 주석(관리자용)으로 숨김
"""

import json
import os
from datetime import datetime
from pathlib import Path
import google.generativeai as genai
import time

class DataSaver:
    def __init__(self, config_path="config_ai.json"):
        self.output_dir = Path(__file__).parent.parent
        self.data_file = self.output_dir / 'data.json'
        self.contents_dir = self.output_dir / 'contents'
        self.contents_dir.mkdir(exist_ok=True)
        
        # 번역 설정
        self.config = {}
        if Path(config_path).exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        
        # API 키 로드
        self.api_key = os.getenv('GEMINI_API_KEY', self.config.get('gemini_api_key', ''))
        
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel("gemini-1.5-flash")
            print("   ✅ 번역용 Gemini API 연결 성공")
        else:
            print("   ⚠️ GEMINI_API_KEY 없음: 번역 기능 비활성화")
            self.model = None

    def load_validated_content(self, input_path="automation/intermediate_outputs/step3_validated_content.json"):
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("❌ Step 3 결과 파일이 없습니다.")
            return None

    def translate_descriptions(self, descriptions):
        """이미지 설명 한글 번역"""
        if not self.model or not descriptions:
            return descriptions

        print(f"   🌐 이미지 설명 {len(descriptions)}개 번역 시도...")
        prompt = "Translate the following image descriptions into natural Korean captions. Return ONLY the translated lines.\n\n"
        for desc in descriptions:
            prompt += f"- {desc}\n"
            
        try:
            response = self.model.generate_content(prompt)
            lines = [l.strip().replace('- ', '') for l in response.text.strip().split('\n') if l.strip()]
            if len(lines) == len(descriptions):
                return lines
            return descriptions
        except:
            return descriptions

    def create_markdown_content(self, data):
        """Markdown 변환 (이미지 캡션 제거됨)"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        today_date = datetime.now().strftime('%Y-%m-%d')
        
        md = "---\n"
        md += f"title: \"{data['title']}\"\n"
        md += f"date: {current_time}\n"
        md += f"layout: post\n"
        md += f"author: AI Editor\n"
        md += "category: ai\n"
        md += "---\n\n"

        sections = data.get('sections', [])
        
        # 이미지 번역 (Alt Text용)
        img_secs = [s for s in sections if s['type'] == 'image']
        eng_descs = [s['description'] for s in img_secs]
        kor_descs = self.translate_descriptions(eng_descs)
        desc_map = {eng: kor for eng, kor in zip(eng_descs, kor_descs)}

        for s in sections:
            sType = s['type']
            content = s.get('content', '')

            if sType in ['paragraph', 'text']:
                md += f"{content}\n\n"
            
            elif sType == 'heading':
                md += f"{'#' * s['level']} {content}\n\n"

            elif sType == 'list':
                for item in s['items']:
                    md += f"- {item}\n"
                md += "\n"
            
            elif sType in ['code_block', 'code']:
                lang = s.get('language', '')
                md += f"```{lang}\n{content}\n```\n\n"

            elif sType == 'tip_box':
                md += f"> 💡 **TIP:** {content}\n\n"

            elif sType == 'warning_box':
                md += f"> ⚠️ **주의:** {content}\n\n"

            elif sType == 'image':
                url = f"/{s['url']}"
                eng = s['description'].replace('"', "'")
                kor = desc_map.get(s['description'], eng)
                
                # [수정됨] 캡션(글자) 없는 순수 이미지 태그
                # - Alt Text: 한글 설명 (검색엔진용)
                # - HTML 주석: 영어 프롬프트 (관리자 참고용, 화면엔 안보임)
                md += f"![{kor}]({url})\n"
                md += f"\n\n"
        
        if 'summary' in data:
            md += "---\n## 📝 요약\n"
            md += f"{data['summary']}\n"

        return md, today_date

    def update_data_json(self, new_article):
        if self.data_file.exists():
            with open(self.data_file, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    articles = data.get('articles', []) if isinstance(data, dict) else data
                except:
                    articles = []
        else:
            articles = []

        articles = [a for a in articles if a['title'] != new_article['title']]
        articles.insert(0, new_article)
        articles = articles[:50]

        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump({"articles": articles}, f, ensure_ascii=False, indent=2)
        print(f"✅ data.json 업데이트 완료")

    def run(self):
        data = self.load_validated_content()
        if not data: return

        print("\n💾 Step 4: Markdown 변환 (Clean Image Version)")
        md_content, date_str = self.create_markdown_content(data)
        
        timestamp = datetime.now().strftime('%H%M%S')
        filename = f"{date_str}-{timestamp}-ai-article.md"
        file_path = self.contents_dir / filename

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"✅ Markdown 생성 완료: contents/{filename}")

        images = [s['url'] for s in data['sections'] if s['type'] == 'image']
        thumbnail = f"/{images[0]}" if images else "https://picsum.photos/800/400"
        
        article_entry = {
            "title": data['title'],
            "summary": data.get('summary', '')[:120] + "...",
            "date": date_str,
            "category": "ai",
            "image": thumbnail,
            "link": f"/contents/{filename.replace('.md', '.html')}",
            "tags": data.get('tags', []),
            "file_path": str(filename)
        }
        
        self.update_data_json(article_entry)

if __name__ == "__main__":
    saver = DataSaver()
    saver.run()
