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
        """설정 파일 로드 및 Gemini API 초기화"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        # API 키 로드 (환경 변수 우선)
        api_key = os.getenv('GEMINI_API_KEY', self.config.get('gemini_api_key', ''))
        
        if not api_key:
            raise ValueError("❌ GEMINI_API_KEY가 설정되지 않았습니다.")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        
        print(f"✅ Gemini API 초기화 완료 (모델: gemini-2.5-flash)")
    
    def generate_trending_topic(self) -> str:
        """트렌드 기반 AI 주제 자동 생성"""
        print("\n[1단계] 트렌드 분석 중...")
        
        topic_prompt = """
유튜브, 네이버 블로그, 카페, 뉴스, X(트위터)에서
최근 1주일간 가장 많이 언급되며 조회수와 검색량이 높은
AI 실전 활용 주제 1개를 추천해줘.

조건:
- 바로 써먹을 수 있는 실전 주제
- 수익/부업 주제 제외
- SEO 최적화된 제목
- 클릭을 유도하되 과장 없는 제목
- 2024-2025년 최신 트렌드 반영

결과는 제목 1줄만 출력 (예: "ChatGPT로 업무 자동화하는 5가지 방법")
"""
        
        try:
            response = self.model.generate_content(topic_prompt)
            topic = response.text.strip()
            print(f"  ✅ 주제 생성 완료: {topic}")
            return topic
        except Exception as e:
            print(f"  ❌ 주제 생성 실패: {e}")
            return "AI 실전 활용 가이드"
    
    def generate_blog_post(self, topic: str) -> Dict[str, str]:
        """블로그 글 자동 생성"""
        print(f"\n[2단계] 블로그 글 생성 중...")
        
        post_prompt = f"""
당신은 친근하고 공감 능력이 뛰어난 AI/테크 블로거입니다.
독자가 쉽게 이해하고 바로 실천할 수 있는 실용적인 글을 작성해주세요.

[작성 톤]
- 친근하고 대화하듯 자연스럽게
- "~해요", "~니다" 혼용 (너무 딱딱하지 않게)
- 이모지 적절히 활용 (💡, ✨, 🎯, 💪 등)
- 독자에게 직접 말 거는 느낌

[글 구조]
1. <h2>제목</h2> (이모지 포함)

2. 도입부 (2-3문장)
   - 독자의 고민/문제점 공감
   - "이런 경험 있으시죠?"

3. 본문 (필수 4-6개 섹션)
   각 섹션마다:
   - [IMAGE:구체적인 이미지 설명] (영어로, 예: modern ai workspace with laptop)
   - <h3>섹션 제목</h3>
   - 설명 (<p>) 또는 리스트 (<ul><li>)
   - 💡 TIP 박스 (선택):
     <p style="border-left:4px solid #3b82f6; padding-left:10px; background:#f0f9ff; padding:10px;">
     <strong>💡 꿀팁:</strong> 실전 팁
     </p>

4. 마무리
   - 핵심 요약
   - 행동 유도 ("오늘부터 바로 써보세요!")

[중요 규칙]
- 2000자 이상 작성
- 각 섹션 앞에 [IMAGE:...] 필수 (4-6개)
- 이미지 키워드는 영어로, 구체적으로 (예: "ChatGPT interface on laptop screen")
- <strong>, <mark> 적극 활용
- 실제 사용 가능한 구체적 예시 포함
- 코드 예시는 <pre> 태그

주제: {topic}

지금 바로 독자가 따라할 수 있는 실전 가이드를 작성해주세요!
"""
        
        try:
            response = self.model.generate_content(post_prompt)
            html_content = response.text.strip()
            
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
                'category': 'AI/테크'
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
    
    def _extract_image_keywords(self, html: str) -> List[str]:
        """[IMAGE:...] 형식의 이미지 키워드 추출"""
        pattern = r'\[IMAGE:([^\]]+)\]'
        keywords = re.findall(pattern, html)
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
            response = self.model.generate_content(summary_prompt)
            return response.text.strip()
        except:
            return text[:max_length] + "..."
    
    def generate_thumbnail_prompt(self, topic: str) -> str:
        """썸네일 이미지 생성용 프롬프트 생성"""
        prompt_request = f"""
"{topic}" 주제에 어울리는 블로그 썸네일 이미지를 생성하기 위한
DALL-E 또는 Midjourney 프롬프트를 영어로 작성해줘.

조건:
- 깔끔하고 모던한 스타일
- 기술/AI 느낌
- 텍스트는 포함하지 않음
- 16:9 비율

프롬프트만 출력 (설명 없이)
"""
        
        try:
            response = self.model.generate_content(prompt_request)
            return response.text.strip()
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
        
        # 3. 이미지 자동 삽입
        print("\n[3단계] 이미지 자동 삽입 중...")
        try:
            from unsplash_images import add_images_to_content, extract_keywords_from_content
            
            # 이미지 키워드 확인
            keywords = extract_keywords_from_content(post['content'])
            print(f"  ✅ {len(keywords)}개 이미지 키워드 발견")
            
            # 이미지 자동 삽입
            post['content'] = add_images_to_content(post['content'])
            print(f"  ✅ 이미지 삽입 완료")
        except Exception as e:
            print(f"  ⚠️ 이미지 삽입 실패: {e}")
        
        # 4. 요약문 생성
        print("\n[4단계] 요약문 생성 중...")
        summary = self.generate_summary(post['content'])
        print(f"  ✅ 요약 완료")
        
        # 5. 썸네일 생성 (첫 번째 이미지 키워드 사용)
        print("\n[5단계] 썸네일 이미지 설정 중...")
        thumbnail_url = 'https://source.unsplash.com/800x600/?artificial-intelligence,technology'
        
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
            'category': 'AI/테크',
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
