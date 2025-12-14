#!/usr/bin/env python3
"""
Step 4: Save to data.json
- Step 3의 검증된 콘텐츠를 data.json에 저장
- Markdown 파일 생성 (contents/*.md)
- 썸네일 이미지 생성
"""

import json
import os
import hashlib
import requests
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import Dict


class DataJsonSaver:
    def __init__(self):
        """초기화"""
        self.output_dir = Path(__file__).parent / "generated_images"
        self.output_dir.mkdir(exist_ok=True)
        print("✅ DataJsonSaver 초기화 완료")
    
    def load_validated_content(self, input_path: str = "automation/intermediate_outputs/step3_validated_content.json") -> dict:
        """Step 3 출력 로드"""
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        image_count = sum(1 for s in data['sections'] if s['type'] == 'image')
        
        print(f"\n📥 Step 3 출력 로드:")
        print(f"   제목: {data['title']}")
        print(f"   섹션 수: {len(data['sections'])}")
        print(f"   ✅ 검증된 이미지: {image_count}개")
        
        return data
    
    def generate_thumbnail(self, topic: str) -> str:
        """
        Pollinations.ai로 썸네일 생성
        
        Returns:
            상대 경로 (예: "automation/generated_images/thumbnail_abc123.png")
        """
        try:
            thumbnail_prompt = f"{topic}, professional blog thumbnail, modern design, tech aesthetic, high quality, 16:9, Korean style"
            encoded_prompt = urllib.parse.quote(thumbnail_prompt)
            thumbnail_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1280&height=720&nologo=true&enhance=true"
            
            print(f"\n🎨 썸네일 생성 중...")
            print(f"   프롬프트: {thumbnail_prompt[:60]}...")
            
            response = requests.get(thumbnail_url, timeout=60)
            
            if response.status_code == 200:
                file_hash = hashlib.md5(topic.encode()).hexdigest()[:8]
                thumbnail_filename = f"thumbnail_{file_hash}.png"
                thumbnail_path = self.output_dir / thumbnail_filename
                
                with open(thumbnail_path, 'wb') as f:
                    f.write(response.content)
                
                relative_path = f"automation/generated_images/{thumbnail_filename}"
                print(f"   ✅ 썸네일 생성 완료: {thumbnail_filename}")
                return relative_path
            else:
                print(f"   ⚠️ 썸네일 생성 실패, 기본 이미지 사용")
                return "https://picsum.photos/seed/ai-tech/1280/720"
                
        except Exception as e:
            print(f"   ⚠️ 썸네일 생성 오류: {e}")
            return "https://picsum.photos/seed/ai-tech/1280/720"
    
    def sections_to_html(self, sections: list) -> str:
        """
        구조화된 sections를 HTML로 변환
        (블로그 빌드 시 사용할 HTML)
        """
        html_parts = []
        
        for section in sections:
            section_type = section['type']
            
            if section_type == 'heading':
                level = section['level']
                content = section['content']
                html_parts.append(f"<h{level}>{content}</h{level}>")
                
            elif section_type == 'paragraph':
                content = section['content']
                html_parts.append(f"<p>{content}</p>")
                
            elif section_type == 'image':
                url = section['url']
                # GitHub Pages에서 작동하도록 절대 경로로 변환
                if url.startswith('automation/'):
                    url = f'/{url}'
                description = section.get('description', '')[:50]
                html_parts.append(f'<img src="{url}" alt="{description}..." style="max-width:100%; height:auto; margin:20px 0;" />')
                
            elif section_type == 'tip_box':
                content = section['content']
                html_parts.append(
                    f'<p style="border-left:4px solid #3b82f6; background:#f0f9ff; '
                    f'padding:15px; border-radius:4px; margin:15px 0;">'
                    f'<strong>💡 TIP:</strong> {content}</p>'
                )
                
            elif section_type == 'warning_box':
                content = section['content']
                html_parts.append(
                    f'<p style="border-left:4px solid #ef4444; background:#fef2f2; '
                    f'padding:15px; border-radius:4px; margin:15px 0;">'
                    f'<strong>⚠️ 주의:</strong> {content}</p>'
                )
                
            elif section_type == 'code_block':
                language = section.get('language', '')
                content = section['content']
                html_parts.append(
                    f'<pre style="background:#1e293b; color:#e2e8f0; padding:15px; '
                    f'border-radius:8px; white-space:pre-wrap; word-wrap:break-word; '
                    f'line-height:1.6; border:1px solid #334155; margin:15px 0;">'
                    f'<code class="language-{language}">{content}</code></pre>'
                )
        
        return '\n'.join(html_parts)
    
    def create_markdown_file(self, validated_data: dict, thumbnail_url: str):
        """
        Markdown 파일 생성 (contents/*.md)
        """
        try:
            # 파일명 생성
            timestamp = datetime.now().strftime('%Y-%m-%d-%H%M%S')
            filename = f"{timestamp}-ai-article.md"
            contents_dir = Path(__file__).parent.parent / 'contents'
            contents_dir.mkdir(exist_ok=True)
            filepath = contents_dir / filename
            
            # HTML 변환
            html_content = self.sections_to_html(validated_data['sections'])
            
            # Markdown 작성 (이미지 경로 절대 경로로 변환)
            if thumbnail_url.startswith('automation/'):
                thumbnail_url = f'/{thumbnail_url}'
            
            markdown_content = f"""---
title: "{validated_data['title']}"
date: {datetime.now().strftime('%Y-%m-%d')}
category: ai
tags: {', '.join(validated_data.get('tags', []))}
image: {thumbnail_url}
---

{html_content}
"""
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            print(f"\n📄 Markdown 파일 생성:")
            print(f"   파일명: {filename}")
            print(f"   경로: {filepath}")
            
            return str(filepath)
            
        except Exception as e:
            print(f"\n❌ Markdown 파일 생성 실패: {e}")
            return None
    
    def update_data_json(self, validated_data: dict, thumbnail_url: str):
        """
        data.json 업데이트
        """
        try:
            data_json_path = Path(__file__).parent.parent / 'data.json'
            
            # 기존 data.json 로드
            if data_json_path.exists():
                with open(data_json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {"articles": []}
            
            # 기존 형식에 맞춰 article 생성
            article = {
                "title": validated_data['title'],
                "source": "AI/테크",
                "time": "방금 전",
                "summary": validated_data.get('summary', '')[:200],
                "link": "#",
                "image": thumbnail_url,
                "category": "ai",
                "type": "ai_generated",
                "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "data": {
                    "sections": validated_data['sections'],
                    "tags": validated_data.get('tags', []),
                    "stats": validated_data.get('stats', {})
                }
            }
            
            # articles 배열에 추가 (맨 앞에)
            if 'articles' not in data:
                data['articles'] = []
            
            data['articles'].insert(0, article)
            
            # 최대 50개까지만 유지
            if len(data['articles']) > 50:
                data['articles'] = data['articles'][:50]
            
            # 저장
            with open(data_json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 data.json 업데이트 완료:")
            print(f"   경로: {data_json_path}")
            print(f"   총 articles: {len(data['articles'])}개")
            
            return True
            
        except Exception as e:
            print(f"\n❌ data.json 업데이트 실패: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def process(self):
        """전체 처리 프로세스"""
        print("\n" + "="*60)
        print("💾 Step 4: Save to data.json")
        print("="*60)
        
        # Step 3 출력 로드
        validated_data = self.load_validated_content()
        
        # 썸네일 생성
        thumbnail_url = self.generate_thumbnail(validated_data['title'])
        
        # Markdown 파일 생성
        markdown_file = self.create_markdown_file(validated_data, thumbnail_url)
        
        # data.json 업데이트
        success = self.update_data_json(validated_data, thumbnail_url)
        
        if success:
            print("\n" + "="*60)
            print("✅ Step 4 완료!")
            print("="*60)
            print(f"\n생성된 파일:")
            print(f"   • data.json (업데이트됨)")
            if markdown_file:
                print(f"   • {markdown_file}")
            print(f"   • {thumbnail_url}")
            
            # 이미지 파일 목록
            image_count = sum(1 for s in validated_data['sections'] if s['type'] == 'image')
            if image_count > 0:
                print(f"\n생성된 이미지: {image_count}개")
                for section in validated_data['sections']:
                    if section['type'] == 'image':
                        print(f"   • {section['url']}")
        else:
            print("\n⚠️ Step 4 일부 실패")


def main():
    """메인 실행 함수"""
    try:
        saver = DataJsonSaver()
        saver.process()
        
        print("\n" + "="*60)
        print("🎉 전체 파이프라인 완료!")
        print("="*60)
        print("\n다음 단계:")
        print("   1. Git 커밋 & 푸시")
        print("   2. GitHub Pages 자동 배포")
        print("   3. 블로그에서 확인")
        
    except Exception as e:
        print(f"\n❌ Step 4 실패: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()
