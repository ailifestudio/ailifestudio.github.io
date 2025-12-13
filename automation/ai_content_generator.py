#!/usr/bin/env python3
"""
AI 콘텐츠 자동 생성기
- Gemini API를 활용한 트렌드 주제 분석
- 자동 블로그 글 생성
- GitHub 블로그 자동 업로드
"""

import google.generativeai as genai
import json
import os
from datetime import datetime
import re
from typing import Dict, List


class AIContentGenerator:
    def __init__(self, config_path="config_ai.json"):
        """설정 파일 로드 및 Gemini API 초기화 (로테이션 지원)"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        # API 키 로드 (복수 키 지원)
        self.api_keys = self._load_api_keys()
        self.current_key_index = 0
        
        if not self.api_keys:
            raise ValueError("❌ GEMINI_API_KEY가 설정되지 않았습니다.")
        
        # 첫 번째 키로 초기화
        genai.configure(api_key=self.api_keys[0])
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        
        print(f"✅ Gemini API 초기화 완료 ({len(self.api_keys)}개 키, 모델: gemini-2.5-flash)")
    
    def _load_api_keys(self):
        """API 키 로드 (단일/복수 지원)"""
        # 방법 1: 복수 키 (JSON 배열)
        keys_json = os.getenv('GEMINI_API_KEYS', '')
        print(f"🔍 DEBUG: GEMINI_API_KEYS 환경변수 = {keys_json[:50] if keys_json else '(없음)'}...")
        if keys_json:
            try:
                keys = json.loads(keys_json)
                if isinstance(keys, list) and keys:
                    print(f"✅ DEBUG: {len(keys)}개 키 로드 성공")
                    return keys
            except Exception as e:
                print(f"❌ DEBUG: JSON 파싱 실패 - {e}")
        
        # 방법 2: 단일 키
        single_key = os.getenv('GEMINI_API_KEY', self.config.get('gemini_api_key', ''))
        if single_key:
            return [single_key]
        
        return []
    
    def _rotate_key(self):
        """다음 API 키로 전환"""
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        new_key = self.api_keys[self.current_key_index]
        genai.configure(api_key=new_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        print(f"🔄 API 키 #{self.current_key_index + 1}로 전환")
    
    def _generate_with_retry(self, prompt, max_retries=None):
        """할당량 초과 시 자동으로 다음 키로 재시도"""
        if max_retries is None:
            max_retries = len(self.api_keys)
        
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                return response.text
            except Exception as e:
                error_msg = str(e).lower()
                
                # 할당량 초과 감지
                if 'quota' in error_msg or 'limit' in error_msg or '429' in error_msg:
                    print(f"⚠️ API 키 #{self.current_key_index + 1} 할당량 초과")
                    
                    if attempt < max_retries - 1:
                        self._rotate_key()
                        continue
                    else:
                        print("❌ 모든 API 키 할당량 초과")
                        raise Exception("모든 API 키의 할당량이 초과되었습니다. 24시간 후 재시도하세요.")
                else:
                    raise
        
        raise Exception("최대 재시도 횟수 초과")
    
    def get_existing_titles(self) -> list:
        """기존 블로그 글 제목 목록 가져오기"""
        try:
            import json
            import os
            from pathlib import Path
            
            titles = []
            
            # data.json에서 제목 추출
            data_json = Path(__file__).parent.parent / 'data.json'
            if data_json.exists():
                with open(data_json, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # data.json이 articles 배열을 가진 객체인 경우
                    articles = data.get('articles', data) if isinstance(data, dict) else data
                    for item in articles:
                        if 'title' in item:
                            titles.append(item['title'].lower())
            
            # contents/*.md 파일에서 제목 추출
            contents_dir = Path(__file__).parent.parent / 'contents'
            if contents_dir.exists():
                for md_file in contents_dir.glob('*.md'):
                    with open(md_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.startswith('title:'):
                                title = line.replace('title:', '').strip().strip('"\'')
                                titles.append(title.lower())
                                break
            
            print(f"  ℹ️  기존 글 {len(titles)}개 확인")
            return titles
        except Exception as e:
            print(f"  ⚠️ 기존 글 확인 실패: {e}")
            return []
    
    def generate_trending_topic(self) -> str:
        """트렌드 기반 AI 주제 자동 생성 (중복 체크)"""
        print("\n[1단계] 트렌드 분석 중...")
        
        # 기존 제목 가져오기
        existing_titles = self.get_existing_titles()
        existing_titles_text = '\n'.join(f"- {title}" for title in existing_titles[:20])  # 최근 20개만
        
        topic_prompt = f"""
유튜브, 네이버 블로그, 카페, 뉴스, X(트위터)에서
최근 1주일간 가장 많이 언급되며 조회수와 검색량이 높은
AI 실전 활용 주제 1개를 추천해줘.

조건:
- 바로 써먹을 수 있는 실전 주제
- 수익/부업 주제 제외
- SEO 최적화된 제목
- 클릭을 유도하되 과장 없는 제목
- 2025년 최신 트렌드 반영

⚠️ 중요: 아래 기존 블로그 글과 유사하거나 중복되는 주제는 절대 제외!
기존 블로그 글 제목:
{existing_titles_text}

결과는 제목 1줄만 출력 (예: "ChatGPT로 업무 자동화하는 5가지 방법")
"""
        
        try:
            topic = self._generate_with_retry(topic_prompt)
            topic = topic.strip()
            print(f"  ✅ 주제 생성 완료: {topic}")
            return topic
        except Exception as e:
            print(f"  ❌ 주제 생성 실패: {e}")
            return "AI 실전 활용 가이드"
    
    def generate_blog_post(self, topic: str) -> Dict[str, str]:
        """블로그 글 자동 생성"""
        print(f"\n[2단계] 블로그 글 생성 중...")
        
        post_prompt = f"""
[작성 규칙]
0. 제목은 반드시 <h2> 태그 사용, 중요 키워드는 <strong> 또는 <mark>로 강조
1. 인사말 없이 글 바로 시작
2. 1500자 이상 작성
3. 구성:
   - 제목 (<h2>)
   - 서문 2-3문단 (<p>)
   - 본문 4~6개 섹션 (<h3> 제목 + <p> 설명 또는 <ul><li> 리스트)
   - 실무 활용 예시
   - 주의사항 또는 한계점
   - 정리 요약
4. ⚠️ 이미지 플레이스홀더는 전체 글에 최대 3~5개만 삽입 (매우 중요!)
   형식: [IMAGE_PLACEHOLDER_1], [IMAGE_PLACEHOLDER_2], ...
   
   ⚠️ 필수 규칙:
   - **플레이스홀더만 삽입** (영어 설명 넣지 말 것!)
   - 순서대로 번호 매기기: 1, 2, 3, 4, 5
   - 최대 5개까지만 삽입
   - 핵심 섹션 바로 아래에 배치
   - 예시:
     <h3>AI 활용 전략</h3>
     <p>AI를 활용하여...</p>
     [IMAGE_PLACEHOLDER_1]
   
   ⚠️ 중요: 이미지는 나중에 섹션 내용을 분석하여 자동 생성됩니다!
5. HTML 태그만 사용 (허용: <h2>, <h3>, <p>, <ul>, <li>, <strong>, <mark>, <pre>, <br>)
6. 중요 문장은 <strong> 또는 <mark>로 강조
7. 실무 팁은 아래 스타일 박스 사용 (일반 텍스트용):

<p style="border-left:4px solid #3b82f6; background:#f0f9ff; padding:15px; border-radius:4px; margin:15px 0;">
<strong>💡 TIP:</strong> 내용
</p>

8. 코드·명령어·프롬프트 예시는 반드시 아래 <pre> 태그를 **정확히** 복사해서 사용:

<pre style="background:#1e293b; color:#e2e8f0; padding:15px; border-radius:8px; white-space:pre-wrap; word-wrap:break-word; line-height:1.6; border:1px solid #334155; margin:15px 0;">
코드나 명령어 또는 프롬프트 예시
(여러 줄 가능, 자동 줄바꿈 적용됨)
</pre>

⚠️ 주의: style 속성을 정확히 복사하세요! white-space 오타 금지!

9. ⚠️ 주의사항·경고 박스는 **반드시 의미 있는 내용 포함** (필수!):

<p style="border-left:4px solid #ef4444; background:#fef2f2; padding:15px; border-radius:4px; margin:15px 0;">
<strong>⚠️ 주의:</strong> 실제 주의해야 할 내용을 구체적으로 작성 (예: 개인정보 유출 위험, 과도한 의존 주의, 비용 발생 가능성 등)
</p>

⚠️ 중요: 주의사항 박스는 비워두거나 형식적인 내용 금지! 
실제로 사용자가 주의해야 할 구체적인 내용을 반드시 작성하세요.

주제: {topic}

실제 사용 가능한 구체적인 내용으로 작성해주세요. 이모지는 사용하지 마세요.
"""
        
        try:
            content = self._generate_with_retry(post_prompt)
            html_content = content.strip()
            
            # HTML 태그 정리
            html_content = self._clean_html(html_content)
            
            print(f"  ✅ 글 생성 완료 (길이: {len(html_content)}자)")
            
            # 이미지 키워드 추출
            image_keywords = self._extract_image_keywords(html_content)
            
            return {
                'title': topic,
                'content': html_content,
                'image_keywords': image_keywords,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'category': 'ai'
            }
        except Exception as e:
            print(f"  ❌ 글 생성 실패: {e}")
            return None
    
    def _clean_html(self, html: str) -> str:
        """HTML 정리 (불필요한 마크다운 제거)"""
        # ```html, ``` 제거
        html = re.sub(r'```html\s*', '', html)
        html = re.sub(r'```\s*$', '', html)
        html = html.strip()
        return html
    
    def _extract_image_keywords(self, html: str, max_images: int = 5) -> List[str]:
        """[IMAGE:...] 형식의 이미지 키워드 추출 (최대 5개 제한)"""
        pattern = r'\[IMAGE:([^\]]+)\]'
        keywords = re.findall(pattern, html)
        
        # 최대 개수 제한
        if len(keywords) > max_images:
            print(f"  ⚠️ 이미지 {len(keywords)}개 발견 → {max_images}개로 제한")
            keywords = keywords[:max_images]
        
        return keywords
    
    def generate_summary(self, content: str, max_length: int = 200) -> str:
        """요약문 생성"""
        # HTML 태그 제거
        text = re.sub(r'<[^>]+>', '', content)
        # 이미지 키워드 제거
        text = re.sub(r'\[IMAGE:[^\]]+\]', '', text)
        
        if len(text) <= max_length:
            return text
        
        # AI로 요약
        try:
            summary_prompt = f"다음 글을 2-3문장으로 요약해줘:\n\n{text[:1000]}"
            text = self._generate_with_retry(summary_prompt)
            return text.strip()
        except:
            return text[:max_length] + "..."
    
    def generate_thumbnail_prompt(self, topic: str) -> str:
        """썸네일 이미지 생성용 프롬프트 생성 (16:9 비율)"""
        prompt_request = f"""
Create an English image prompt for a blog thumbnail about "{topic}".

Requirements:
- Clean and modern style
- Tech/AI aesthetic
- NO text overlays
- 16:9 aspect ratio (1280x720 or 1920x1080)
- Professional and appealing design
- High quality, photorealistic or minimalist illustration

Output only the prompt in English (no explanations).
"""
        
        try:
            text = self._generate_with_retry(prompt_request)
            return text.strip()
        except:
            return "modern AI technology workspace, clean design, blue gradient, tech illustration"
    
    def create_article_for_blog(self) -> Dict:
        """블로그용 아티클 생성 (data.json 형식)"""
        print("\n" + "="*50)
        print("🤖 AI 콘텐츠 자동 생성 시작")
        print("="*50)
        
        # 1. 트렌드 주제 생성
        topic = self.generate_trending_topic()
        
        # 2. 블로그 글 생성
        post = self.generate_blog_post(topic)
        
        if not post:
            print("❌ 글 생성 실패")
            return None
        
        # 3. 컨텍스트 기반 이미지 자동 생성 및 삽입
        print("\n[3단계] 컨텍스트 기반 이미지 생성 및 삽입 중...")
        try:
            from context_aware_image_generator import process_content_with_context_aware_images
            
            # 컨텍스트 기반 이미지 생성
            print(f"  🎨 섹션 내용 분석 및 최적화된 이미지 생성 중...")
            print(f"     ├─ Gemini API: 섹션 내용 분석 & 프롬프트 최적화")
            print(f"     └─ Pollinations.ai: 고품질 AI 이미지 생성 (무료)")
            
            post['content'] = process_content_with_context_aware_images(post['content'])
            print(f"  ✅ 이미지 생성 및 삽입 완료")
            
        except Exception as e:
            print(f"  ⚠️ 이미지 처리 실패: {e}")
            import traceback
            traceback.print_exc()
            # 실패해도 계속 진행 (이미지 없이)
            pass
        
        # 4. 요약문 생성
        print("\n[4단계] 요약문 생성 중...")
        summary = self.generate_summary(post['content'])
        print(f"  ✅ 요약 완료")
        
        # 5. 썸네일 생성 (첫 번째 이미지 키워드 사용)
        print("\n[5단계] 썸네일 이미지 설정 중...")
        # 16:9 비율 (1280x720) 사용
        thumbnail_url = 'https://picsum.photos/seed/ai-tech/1280/720'
        
        if post['image_keywords']:
            first_keyword = post['image_keywords'][0]
            from unsplash_images import search_unsplash_image
            thumbnail_url = search_unsplash_image(first_keyword)
            print(f"  ✅ 썸네일: {first_keyword}")
        
        # 6. data.json 형식으로 변환
        article = {
            'title': post['title'],
            'source': 'AI/테크',  # "AI 자동 생성" 대신 카테고리명 사용
            'time': '방금 전',
            'summary': summary,
            'link': '#',
            'image': thumbnail_url,
            'content': post['content'],
            'category': 'ai',
            'type': 'ai_generated',  # 내부적으로만 사용
            'created_at': post['created_at'],
            'image_keywords': post['image_keywords']
        }
        
        print("\n" + "="*50)
        print("✅ AI 콘텐츠 생성 완료!")
        print("="*50)
        
        return article
    
    def save_to_json(self, article: Dict, output_path='ai_article.json'):
        """생성된 아티클 JSON 저장"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(article, f, ensure_ascii=False, indent=2)
        print(f"\n💾 {output_path} 저장 완료")


def main():
    """메인 실행 함수"""
    import sys
    
    config_path = "config_ai.json"
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    
    try:
        generator = AIContentGenerator(config_path)
        article = generator.create_article_for_blog()
        
        if article:
            generator.save_to_json(article)
            
            # 미리보기
            print("\n📰 생성된 아티클 미리보기:")
            print(f"제목: {article['title']}")
            print(f"요약: {article['summary'][:100]}...")
            print(f"카테고리: {article['category']}")
            print(f"생성 시간: {article['created_at']}")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
