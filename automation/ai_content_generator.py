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
# Role Definition
당신은 월간 방문자 100만 명을 보유한 IT/Tech 전문 매거진의 **수석 편집장(Chief Editor)**입니다.
당신의 임무는 현재 시점에서 대중의 관심이 폭발하고 있지만, 아직 공급이 부족한 **'블루오션 키워드'**를 발굴하는 것입니다.

# Context Data
1. **Current Date**: {datetime.now().strftime('%Y-%m-%d')} (오늘 날짜를 반드시 인식할 것)
2. **Target Audience**: AI를 실무에 당장 적용하고 싶어 하는 3040 직장인 및 프리랜서.
3. **Existing Articles**: 아래 목록에 있는 주제는 **절대 중복 불가**. 유사한 소재라도 접근 방식(Angle)이 완전히 달라야 함.

{existing_titles_text}

# Task: Topic Selection & Title Engineering
다음 4단계 사고 과정(Chain of Thought)을 거쳐 **단 하나의 필승 주제**를 선정하시오.

**Step 1: 트렌드 스캐닝 (Trend Scanning)**
- 유튜브, 뉴스, 소셜 미디어에서 최근 1주일간 급상승한 'AI 활용' 키워드를 분석하십시오.
- 단순한 "AI란 무엇인가?" 류의 개론은 제외하십시오.

**Step 2: 네거티브 필터링 (Negative Filtering)**
- 다음 유형의 주제를 즉시 폐기하십시오:
  1. 부업, 돈 벌기, 수익화, 주식 자동매매 (신뢰도 하락 요인)
  2. 너무 뻔한 기초 사용법 (예: "ChatGPT 가입하는 법")
  3. 개발자 전용의 너무 어려운 코딩 주제
  4. **[Existing Articles]와 의미적으로 60% 이상 유사한 주제**

**Step 3: 앵글 구체화 (Angle Sharpening)**
- 선정된 주제를 "2025년 최신 트렌드"와 연결하십시오.
- 독자가 클릭할 수밖에 없는 '구체적인 효용(Benefit)'을 제목에 담으십시오.
- 과장된 낚시성 멘트(어그로) 대신, 신뢰감을 주는 숫자를 활용하십시오.

**Step 4: 제목 최적화 (Title SEO)**
- 제목 길이: 25~35자 이내 (모바일 가독성 최적화).
- 핵심 키워드는 제목 앞부분에 배치.
- 형식: [대상] + [도구/방법] + [구체적 결과/숫자]

# Output Format (최종 출력)
- 부가적인 설명이나 인사말, 따옴표("")를 모두 생략하고, **오직 완성된 제목 1줄만** 출력하시오.

# Example Output
DeepSeek vs ChatGPT: 2025년 무료 코딩 AI 성능 비교와 실무 활용팁
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
# Role Definition
당신은 대한민국 상위 1% IT/Tech 전문 블로거이자 SEO 전문가입니다.
독자가 글을 읽고 즉시 실행할 수 있는 실용적인 가이드를 제공하여 체류 시간을 극대화하는 것이 목표입니다.

# Task
주어진 주제에 대해 아래 [작성 규칙]을 엄격히 준수하여 블로그 포스팅을 작성하고, 마지막에 이미지 생성용 프롬프트를 제공하십시오.

# User Input (Topic)
주제: {주제}

# [작성 규칙] (엄격 준수)
1. **형식**: 오직 HTML 태그만 사용 (<h2>, <h3>, <p>, <ul>, <li>, <strong>, <mark>, <pre>, <br> 허용). <html>, <head>, <body> 태그는 제외.
2. **분량**: 공백 포함 1,500자 ~ 2,000자 이상.
3. **구성**:
   - 제목 (<h2>)
   - 서문 (인사말 생략, 페인포인트 자극 2-3문단)
   - 본문 (4~6개 섹션, <h3> 제목 + 설명)
   - 실무 활용 예시
   - 주의사항 또는 한계점
   - 정리 요약 (Call to Action 포함)
4. **이미지 플레이스홀더**:
   - 전체 글 내에 [IMAGE_PLACEHOLDER_1] ~ [IMAGE_PLACEHOLDER_5]를 최대 5개 배치.
   - [IMAGE_PLACEHOLDER_1]은 반드시 서론 직후(썸네일용)에 배치.
   - 나머지는 핵심 섹션 직후 배치.
   - ⚠️ 중요: 본문 안에는 **플레이스홀더만 삽입**하고, 영어 설명은 절대 넣지 마십시오.
5. **강조**: 핵심 문장은 <strong> 또는 <mark>로 강조.
6. **실무 팁 박스 스타일** (반드시 아래 코드 복사):
   <p style="border-left:4px solid #3b82f6; background:#f0f9ff; padding:15px; border-radius:4px; margin:15px 0;"><strong>💡 TIP:</strong> 내용</p>
7. **주의사항 박스 스타일** (반드시 아래 코드 복사):
   <p style="border-left:4px solid #ef4444; background:#fef2f2; padding:15px; border-radius:4px; margin:15px 0;"><strong>⚠️ 주의:</strong> 구체적인 위험/비용/제약 사항 내용</p>
8. **코드/명령어 박스 스타일** (반드시 아래 코드 복사):
   <pre style="background:#1e293b; color:#e2e8f0; padding:15px; border-radius:8px; white-space:pre-wrap; word-wrap:break-word; line-height:1.6; border:1px solid #334155; margin:15px 0;">코드 내용</pre>

---

# [Step-by-Step 실행 지침]

**Step 1: 구조 설계 (Internal Monologue)**
- 출력하지 말고 혼자 생각하십시오. 주제를 분석하여 가장 논리적인 목차를 구성합니다.

**Step 2: 콘텐츠 작성 (HTML Output)**
- 위 [작성 규칙]에 맞춰 고품질의 HTML 글을 작성하십시오.
- 스타일(CSS)을 정확하게 적용하십시오.

**Step 3: 이미지 프롬프트 생성 (List Output)**
- ⚠️ 글 작성이 끝난 후, 맨 마지막에 `<hr>` 태그로 구분선을 넣고 그 아래에 작성하십시오.
- 각 플레이스홀더 번호에 맞춰, '고품질 AI 이미지 생성용 영어 프롬프트'를 작성하십시오.
- 이 부분은 블로그 발행 시 관리자가 참고하여 삭제할 부분입니다.
- **형식**:
| ID | Context | English Prompt for AI Image Generation |
|:--|:--|:--|
| [IMAGE_PLACEHOLDER_1] | (메인 주제) | (Cinematic, Detailed, 8k, Description...) |
| [IMAGE_PLACEHOLDER_2] | (섹션 1 요약) | (Futuristic, UI Design, Description...) |
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
        """[IMAGE_PLACEHOLDER_N] 형식의 플레이스홀더 개수 추출"""
        pattern = r'\[IMAGE_PLACEHOLDER_(\d+)\]'
        matches = re.findall(pattern, html)
        
        if matches:
            # 플레이스홀더 번호를 정렬하여 순서대로 처리
            placeholder_numbers = sorted([int(m) for m in matches])
            print(f"  ℹ️  이미지 플레이스홀더 {len(placeholder_numbers)}개 발견: {placeholder_numbers}")
            
            # 최대 개수 제한
            if len(placeholder_numbers) > max_images:
                print(f"  ⚠️ 플레이스홀더 {len(placeholder_numbers)}개 → {max_images}개로 제한")
                placeholder_numbers = placeholder_numbers[:max_images]
            
            # 플레이스홀더를 문자열로 반환 (예: ['1', '2', '3'])
            return [str(n) for n in placeholder_numbers]
        
        return []
    
    def generate_summary(self, content: str, max_length: int = 200) -> str:
        """요약문 생성"""
        # HTML 태그 제거
        text = re.sub(r'<[^>]+>', '', content)
        # 이미지 플레이스홀더 제거
        text = re.sub(r'\[IMAGE_PLACEHOLDER_\d+\]', '', text)
        
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
        
        # 5. 썸네일 생성 (컨텍스트 기반 생성)
        print("\n[5단계] 썸네일 이미지 설정 중...")
        
        # 썸네일은 주제 기반으로 Pollinations.ai에서 생성
        try:
            import hashlib
            import requests
            import urllib.parse
            from pathlib import Path
            
            # 주제 기반 프롬프트 생성
            thumbnail_prompt = f"{topic}, professional blog thumbnail, modern design, tech aesthetic, high quality, 16:9"
            encoded_prompt = urllib.parse.quote(thumbnail_prompt)
            thumbnail_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1280&height=720&nologo=true&enhance=true"
            
            # 썸네일 로컬 저장
            output_dir = Path(__file__).parent / "generated_images"
            output_dir.mkdir(exist_ok=True)
            
            file_hash = hashlib.md5(topic.encode()).hexdigest()[:8]
            thumbnail_path = output_dir / f"thumbnail_{file_hash}.png"
            
            response = requests.get(thumbnail_url, timeout=30)
            if response.status_code == 200:
                with open(thumbnail_path, 'wb') as f:
                    f.write(response.content)
                thumbnail_url = f"automation/generated_images/thumbnail_{file_hash}.png"
                print(f"  ✅ 썸네일 생성 완료")
            else:
                thumbnail_url = 'https://picsum.photos/seed/ai-tech/1280/720'
                print(f"  ⚠️ 썸네일 생성 실패, 기본 이미지 사용")
        except Exception as e:
            thumbnail_url = 'https://picsum.photos/seed/ai-tech/1280/720'
            print(f"  ⚠️ 썸네일 생성 오류: {e}")
        
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
