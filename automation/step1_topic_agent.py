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
        print("="*60)
        
        existing_titles = self.get_existing_titles()
        existing_titles_text = '\n'.join(f"- {title}" for title in existing_titles[:20])
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        topic_prompt = f"""# Role Definition
당신은 대한민국 IT/Tech 트렌드 분석가이자 '블루오션 키워드' 발굴 전문가입니다.

# Task
현재 시점({current_date})을 기준으로, 30-40대 직장인을 위한 실용적인 AI/Tech 주제를 선정하여 출력하십시오.

# Filtering Rules (네거티브 필터링)
1. 기존 작성된 글 제목과 중복되는 주제는 제외하십시오:
{existing_titles_text}

2. 다음 주제는 절대 선정하지 마십시오:
   - "돈 버는 법", "주식", "부업" 등 수익성 강조 주제
   - "ChatGPT 가입법" 등 너무 기초적인 내용
   - "Python 설치" 등 개발자 전용 내용

3. 다음 주제 선정은 괜찮습니다 (단, 유튜브 등 참고하여 활용법 위주):
   - 젠스파크 활용법
   - 제미나이 활용법
   - 챗GPT 활용법
   - 기타 AI 활용법

# Selection Criteria (선정 기준)
1. 대상: 비개발자 직장인, 프리랜서
2. 효용: 업무 효율화, 시간 단축, 자동화 등 즉각적인 이득
3. 트렌드: 2025년 이후 최신 트렌드 (AI 에이전트, 멀티모달 등) 반영

# Output Format
- 부연 설명 없이 완성된 제목 1줄만 출력하십시오.
- 형식: [타겟] + [도구/방법] + [구체적 결과/숫자]
- 예시: "직장인 회의록, AI 에이전트로 5분 만에 자동 정리"
"""
        
        try:
            print("\n📊 트렌드 분석 중...")
            topic = self._generate_with_retry(topic_prompt)
            topic = topic.strip()
            
            # 검증: 제목이 너무 짧거나 길면 재생성
            if len(topic) < 15 or len(topic) > 50:
                print(f"  ⚠️ 제목 길이 부적절 ({len(topic)}자), 재생성 중...")
                topic = self._generate_with_retry(topic_prompt)
                topic = topic.strip()
            
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
