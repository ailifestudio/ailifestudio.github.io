#!/usr/bin/env python3
"""
Step 1: Trend & Topic Agent
- 블루오션 키워드 발굴
- 네거티브 필터링 (중복, 저품질 주제 제외)
- SEO 최적화된 제목 생성
"""

import google.generativeai as genai
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List


class TopicAgent:
    def __init__(self, config_path="config_ai.json"):
        """Gemini API 초기화"""
        # config 파일은 선택사항 (환경변수 우선)
        self.config = {}
        if Path(config_path).exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        
        # API 키 로드
        self.api_keys = self._load_api_keys()
        self.current_key_index = 0
        
        if not self.api_keys:
            raise ValueError("❌ GEMINI_API_KEY가 설정되지 않았습니다.")
        
        genai.configure(api_key=self.api_keys[0])
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        
        print(f"✅ Gemini API 초기화 완료 (키: {len(self.api_keys)}개)")
    
    def _load_api_keys(self) -> List[str]:
        """API 키 로드 (복수 키 지원)"""
        keys_json = os.getenv('GEMINI_API_KEYS', '')
        if keys_json:
            try:
                keys = json.loads(keys_json)
                if isinstance(keys, list) and keys:
                    return keys
            except:
                pass
        
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
    
    def _generate_with_retry(self, prompt: str, max_retries: int = None) -> str:
        """할당량 초과 시 자동 재시도"""
        if max_retries is None:
            max_retries = len(self.api_keys)
        
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                return response.text
            except Exception as e:
                error_msg = str(e).lower()
                if 'quota' in error_msg or 'limit' in error_msg or '429' in error_msg:
                    print(f"⚠️ API 키 #{self.current_key_index + 1} 할당량 초과")
                    if attempt < max_retries - 1:
                        self._rotate_key()
                        continue
                    else:
                        raise Exception("모든 API 키의 할당량이 초과되었습니다.")
                else:
                    raise
        
        raise Exception("최대 재시도 횟수 초과")
    
    def get_existing_titles(self) -> List[str]:
        """기존 블로그 글 제목 목록 가져오기"""
        try:
            titles = []
            
            # data.json에서 제목 추출
            data_json = Path(__file__).parent.parent / 'data.json'
            if data_json.exists():
                with open(data_json, 'r', encoding='utf-8') as f:
                    data = json.load(f)
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
    
    def generate_topic(self) -> dict:
        """트렌드 분석 및 블루오션 주제 생성"""
        print("\n" + "="*60)
        print("🎯 Step 1: Trend & Topic Agent")
        print("   📁 automation/step1_topic_agent.py")
        print("   ⚙️  설정 위치: 라인 128-180 (토픽 생성 프롬프트)")
        print("="*60)
        
        existing_titles = self.get_existing_titles()
        existing_titles_text = '\n'.join(f"- {title}" for title in existing_titles[:20])
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        topic_prompt = f"""# Role Definition
당신은 대한민국 IT/Tech 트렌드 분석가입니다.
특히 **'김이솝', '알린', '닥또리', '소소한 AI 입문 노트'** 등 인기 테크 유튜버들이 다루는 **최신 AI 이슈**를 포착하여, 3040 직장인을 위한 실무 가이드로 재가공하는 능력이 탁월합니다.

# Task
현재 시점({current_date})을 기준으로, **나노바나나, 젠스파크, 제미나이**를 포함하여 **유튜브에서 가장 화제가 되고 있는 최신 AI 툴 중 하나**를 선정하고, 유튜버들의 스타일을 벤치마킹하여 **단 하나의 제목**을 작성하십시오.

# 🔥 Hot Trends Search Scope (검색 및 확장 범위)
**AI에게 지시: 아래 예시 국한되지 말고, 유사한 카테고리의 최신 'Rising Star' 툴을 적극적으로 포함하십시오.**

**1. [이미지/영상] 나노바나나 & Beyond**
   - *Core:* 구글 Nano Banana (캐릭터 일관성, 합성).
   - *Expand:* **Recraft V3** (벡터 생성), **Kling/Runway** (영상), **Midjourney** (최신).
   - *실무 포인트:* 돈 안 드는 룩북/상세페이지 제작, PPT용 고퀄리티 일러스트.

**2. [검색/에이전트] 젠스파크 & Beyond**
   - *Core:* GenSpark (AI 에이전트 검색).
   - *Expand:* **Perplexity** (Deep Research), **OpenAI Operator**, **Arc Search**.
   - *실무 포인트:* 시장 조사 자동화, 경쟁사 분석 리포트 3분 완성.

**3. [모델/생산성] 제미나이 & Beyond**
   - *Core:* Gemini 2.0 Flash Thinking (속도/추론).
   - *Expand:* **DeepSeek V3/R1** (가성비 코딩/글쓰기), **Claude 3.5** (Artifacts), **NotebookLM** (오디오 요약).
   - *실무 포인트:* 복잡한 엑셀 수식 해결, 논문 팟캐스트로 듣기, 앱 프로토타입.

**4. [시각화/문서] 오피스 꿀툴 (New)**
   - *Expand:* **Napkin AI** (텍스트 -> 다이어그램), **Gamma** (PPT 자동 생성).
   - *실무 포인트:* "글만 썼는데 도표가 뚝딱", "기획안 넣으니 PPT 완성".

# Filtering Rules
1. 기존 제목 중복 제외:
{existing_titles_text}

2. 선정 금지:
   - "돈 버는 법", "주식" 등 자극적 수익성 주제
   - "ChatGPT 가입법" 등 기초 내용
   - 개발자 전용 (Python 설치, API 키 발급 등)

# 🌟 벤치마킹 스타일 (YouTuber -> Blog)
유튜버들의 "이거 대박입니다"라는 텐션을 **"직장인의 퇴근 시간 단축"**으로 차분하고 실용적으로 변환하십시오.
**대상(직장인 등)을 제목 맨 앞에 쓰지 말고**, **도구명**이나 **해결책**을 강조하십시오.

**1. 김이솝 & 알린 스타일 (Trend & Review)**
   - *특징:* "나노바나나, 미드저니보다 좋은가?", "젠스파크로 구글링 끝"
   - *전략:* 신기술의 놀라움을 업무 효율로 연결.
   - *예시:* "Nano Banana, 똥손도 3분 만에 고정 캐릭터 만드는 법"

**2. 닥또리 & 소소한 AI 노트 스타일 (Tips & Tutorial)**
   - *특징:* "엑셀 노가다 이제 그만", "영어 공부 0원"
   - *전략:* Pain Point를 건드리고 구체적 툴로 해결.
   - *예시:* "논문 100장 읽기 지옥, NotebookLM으로 팟캐스트처럼 듣자"

# Output Format
- 부연 설명, 줄바꿈, 추가 제안 없이 **완성된 제목 딱 1줄**만 출력하십시오.
- 여러 개 제안하지 말고 **가장 좋은 제목 1개**만 선택하십시오.
- **다양성 필수:** 나노바나나, 젠스파크, 제미나이 외에도 DeepSeek, Napkin AI 등 **다양한 최신 툴을 로테이션하여 선정**하십시오.

# 예시 출력 (정확히 이런 형식):
Nano Banana로 광고용 캐릭터 룩북, 퇴근 전 뚝딱 만드는 비결
"""
        
        try:
            print("\n📊 트렌드 분석 중...")
            topic = self._generate_with_retry(topic_prompt)
            topic = topic.strip()
            
            # 검증: 제목이 너무 짧거나 길거나 여러 줄이면 재생성
            if len(topic) < 15 or len(topic) > 80 or '\n' in topic:
                print(f"  ⚠️ 제목 형식 부적절 ({len(topic)}자, 줄바꿈: {'\n' in topic}), 재생성 중...")
                topic = self._generate_with_retry(topic_prompt)
                topic = topic.strip()
            
            # 줄바꿈이 있으면 첫 번째 줄만 사용
            if '\n' in topic:
                topic = topic.split('\n')[0].strip()
                print(f"  ⚠️ 여러 줄 감지됨, 첫 번째 줄만 사용: {topic}")
            
            print(f"\n✅ 주제 생성 완료:")
            print(f"   📌 {topic}")
            
            result = {
                "title": topic,
                "generated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "agent": "step1_topic_agent"
            }
            
            return result
            
        except Exception as e:
            error_msg = str(e)
            print(f"\n❌ 주제 생성 실패: {error_msg}")
            
            # API 할당량 초과인 경우
            if '할당량' in error_msg or 'quota' in error_msg.lower():
                print("\n⏰ API 할당량이 초과되었습니다.")
                print("   - Gemini API는 분당/일일 할당량이 있습니다")
                print("   - 5~10분 후 재시도하거나 새 API 키를 추가하세요")
                print("   - 또는 Google AI Studio에서 유료 플랜 구독")
            
            # 실패 시 예외 발생 (폴백 데이터 반환하지 않음)
            raise Exception(f"주제 생성 실패: {error_msg}")
    
    def save_output(self, data: dict, output_path: str = "automation/intermediate_outputs/step1_topic.json"):
        """Step 1 출력 저장"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 출력 저장: {output_path}")
        print(f"   크기: {output_file.stat().st_size} bytes")


def main():
    """메인 실행 함수"""
    try:
        agent = TopicAgent()
        result = agent.generate_topic()
        
        # 검증: 실제 주제가 생성되었는지 확인
        if not result.get('title') or result.get('fallback'):
            raise Exception("유효한 주제가 생성되지 않았습니다")
        
        agent.save_output(result)
        
        print("\n" + "="*60)
        print("✅ Step 1 완료! (주제 생성 성공)")
        print("="*60)
        print(f"   📌 제목: {result['title']}")
        print(f"\n다음 단계: python automation/step2_writer_agent.py")
        
    except Exception as e:
        print("\n" + "="*60)
        print("❌ Step 1 실패!")
        print("="*60)
        print(f"   오류: {e}")
        print("\n💡 해결 방법:")
        print("   1. 5~10분 후 재시도")
        print("   2. 새 API 키 추가 (GEMINI_API_KEYS 환경변수)")
        print("   3. Google AI Studio에서 할당량 확인")
        
        import traceback
        print("\n🔍 상세 오류:")
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()
