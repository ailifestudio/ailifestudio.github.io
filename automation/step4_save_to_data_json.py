#!/usr/bin/env python3
"""
Step 4: Save to data.json & Markdown (Final Polish)
- 기능 1: 가로 스크롤 방지 (Code Block -> 인용구/팁박스 변환)
- 기능 2: 썸네일 자동 등록 (Front Matter에 image 필드 추가)
- 기능 3: 불필요한 번역 호출 제거 (Step 2 데이터 활용)
"""

import json
import os
from datetime import datetime
from pathlib import Path
import re

class DataSaver:
    def __init__(self):
        self.output_dir = Path(__file__).parent.parent
        self.data_file = self.output_dir / 'data.json'
        self.contents_dir = self.output_dir / 'contents'
        self.contents_dir.mkdir(exist_ok=True)

    def load_validated_content(self, input_path="automation/intermediate_outputs/step3_validated_content.json"):
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("❌ Step 3 결과 파일이 없습니다.")
            return None

    def clean_markdown_syntax(self, text):
        """본문 내에 숨어있는 코드블록 문법(```) 제거"""
        if not text: return ""
        text = re.sub(r'```\w*\n', '', text) 
        text = text.replace('```', '')
        return text

    def create_markdown_content(self, data):
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        today_date = datetime.now().strftime('%Y-%m-%d')
        
        # [1] 썸네일 찾기 (첫 번째 이미지 URL 추출)
        sections = data.get('sections', [])
        images = [s for s in sections if s['type'] == 'image']
        thumbnail_url = ""
        if images:
            url = images[0]['url']
            # URL이 /로 시작하지 않으면 붙여줌 (절대 경로)
            thumbnail_url = f"/{url}" if not url.startswith('/') else url

        # [2] Front Matter (머리말) 작성
        md = "---\n"
        md += f"title: \"{data['title']}\"\n"
        md += f"date: {current_time}\n"
        md += f"layout: post\n"
        md += f"author: AI Editor\n"
        md += "category: ai\n"
        # 🌟 대시보드 썸네일용 코드 추가
        if thumbnail_url:
            md += f"image: \"{thumbnail_url}\"\n"
        md += "---\n\n"

        # [3] 본문 작성
        for s in sections:
            sType = s['type']
            content = s.get('content', '')

            if sType in ['paragraph', 'text']:
                md += f"{self.clean_markdown_syntax(content)}\n\n"
            elif sType == 'heading':
                md += f"{'#' * s['level']} {content}\n\n"
            elif sType == 'list':
                for item in s['items']: md += f"- {item}\n"
                md += "\n"
            
            # [핵심] 코드블록 -> 인용구 변환 (스크롤 방지)
            elif sType in ['code_block', 'code']:
                md += f"> 💬 **AI 프롬프트 예시:**\n>\n"
                clean_code = self.clean_markdown_syntax(content).strip()
                # 줄바꿈이 깨지지 않도록 인용구 기호(>)를 줄마다 붙임
                formatted_content = clean_code.replace("\n", "\n> ")
                md += f"> {formatted_content}\n\n"
            
            elif sType == 'tip_box':
                md += f"> 💡 **TIP:** {content}\n\n"
            elif sType == 'warning_box':
                md += f"> ⚠️ **주의:** {content}\n\n"
            
            # [이미지] 화면엔 사진만 깔끔하게 표시
            elif sType == 'image':
                url = f"/{s['url']}" if not s['url'].startswith('/') else s['url']
                kor = s.get('description_ko', '')
                md += f"![{kor}]({url})\n\n"
        
        if 'summary' in data:
            md += "---\n## 📝 요약\n"
            md += f"{data['summary']}\n"

        return md, today_date, thumbnail_url

    def update_data_json(self, new_article):
        if self.data_file.exists():
            with open(self.data_file, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    articles = data.get('articles', []) if isinstance(data, dict) else data
                except: articles = []
        else: articles = []

        articles = [a for a in articles if a['title'] != new_article['title']]
        articles.insert(0, new_article)
        articles = articles[:50]

        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump({"articles": articles}, f, ensure_ascii=False, indent=2)

    def run(self):
        data = self.load_validated_content()
        if not data: return
        print("\n💾 Step 4: Markdown 변환 (Final Polish)")
        
        # Markdown 생성 및 썸네일 URL 획득
        md_content, date_str, thumbnail_url = self.create_markdown_content(data)
        
        timestamp = datetime.now().strftime('%H%M%S')
        filename = f"{date_str}-{timestamp}-ai-article.md"
        file_path = self.contents_dir / filename

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        # 썸네일 없으면 기본 이미지 사용
        final_image = thumbnail_url if thumbnail_url else "https://picsum.photos/800/400"
        
        self.update_data_json({
            "title": data['title'],
            "summary": data.get('summary', '')[:120] + "...",
            "date": date_str,
            "category": "ai",
            "image": final_image, # data.json에도 이미지 경로 저장
            "link": f"/contents/{filename.replace('.md', '.html')}",
            "tags": data.get('tags', []),
            "file_path": str(filename)
        })
        print(f"✅ 저장 완료: contents/{filename}")

if __name__ == "__main__":
    DataSaver().run()
