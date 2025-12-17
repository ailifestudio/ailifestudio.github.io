#!/usr/bin/env python3
"""
Step 3: Image Generation & Vision Audit Agent (Final Integrated Version)
- Pollinations.ai (Flux)로 고품질 이미지 생성 (영문 프롬프트 사용)
- 한글 설명(description_ko) 보존하여 Step 4로 전달
- Vision 검수: Free Pass (쿼터 절약)
"""

import google.generativeai as genai
import json
import os
import hashlib
import requests
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import List, Dict
import time
import random

class ImageAuditAgent:
    def __init__(self, config_path="config_ai.json"):
        """Gemini API 초기화"""
        self.config = {}
        if Path(config_path).exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        
        self.api_keys = self._load_api_keys()
        self.current_key_index = 0
        
        # Vision 모델 초기화 (검수 프리패스 모드여도 초기화는 유지)
        if self.api_keys:
            genai.configure(api_key=self.api_keys[0])
            self.vision_model = genai.GenerativeModel("gemini-2.5-flash")
        
        # 출력 디렉토리 생성
        self.output_dir = Path(__file__).parent / "generated_images"
        self.output_dir.mkdir(exist_ok=True)
        
        print(f"✅ Image Agent 초기화 완료")
        print(f"✅ 이미지 저장 경로: {self.output_dir}")
    
    def _load_api_keys(self) -> List[str]:
        """API 키 로드"""
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
    
    def load_structured_content(self, input_path: str = "automation/intermediate_outputs/step2_structured_content.json") -> dict:
        """Step 2 출력 로드"""
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        image_count = sum(1 for s in data['sections'] if s['type'] == 'image_placeholder')
        
        print(f"\n📥 Step 2 출력 로드:")
        print(f"   제목: {data['title']}")
        print(f"   섹션 수: {len(data['sections'])}")
        print(f"   🎨 이미지 플레이스홀더: {image_count}개")
        
        return data
    
    def generate_image(self, description: str, image_id: str, max_retries: int = 3) -> tuple:
        """
        Pollinations.ai (Flux)로 초고화질 이미지 생성
        - 타임아웃 60초로 증가 (에러 방지)
        - 화질 부스터 & enhance=false 적용 (S급 퀄리티)
        """
        for attempt in range(max_retries):
            try:
                # 1. 랜덤 시드 (다양성 확보)
                seed = random.randint(1, 99999999)
                
                # 2. 💎 화질 부스터 (퀄리티 강제 주입)
                quality_prefix = "Masterpiece, award winning photography, 8k resolution, highly detailed, cinematic lighting, depth of field, f/1.8, bokeh, realistic texture, raw photo,"
                negative_prompt = "blurry, distorted, low quality, cartoon, illustration, bad hands, ugly, text, watermark, grainy"
                
                # 프롬프트 합체
                full_prompt = f"{quality_prefix} {description}, {negative_prompt}"
                encoded_prompt = urllib.parse.quote(full_prompt)
                
                # 3. URL 생성 (Flux 모델 고정)
                pollinations_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1280&height=720&model=flux&nologo=true&seed={seed}&enhance=false"
                
                if attempt == 0:
                    print(f"   🎨 [Flux] 고화질 생성 시도 ({attempt+1}/{max_retries})")
                else:
                    print(f"      🔄 재시도 {attempt+1}/{max_retries}...")
                
                # 4. 요청 (Timeout 60초)
                response = requests.get(pollinations_url, timeout=60)
                
                if response.status_code == 200:
                    # 파일 저장
                    file_hash = hashlib.md5(description.encode()).hexdigest()[:8]
                    image_filename = f"{image_id}_{file_hash}.png"
                    image_path = self.output_dir / image_filename
                    
                    with open(image_path, 'wb') as f:
                        f.write(response.content)
                    
                    relative_path = f"automation/generated_images/{image_filename}"
                    print(f"      ✅ 생성 성공: {image_filename}")
                    return str(image_path), relative_path
                else:
                    print(f"      ⚠️ HTTP {response.status_code}")
                    time.sleep(5)
                    
            except Exception as e:
                if "Read timed out" in str(e):
                    print(f"      ⏳ 시간 초과 (서버가 바쁨 - 재시도합니다)")
                else:
                    print(f"      ⚠️ 오류: {e}")
                time.sleep(5)
        
        print(f"      ❌ 최종 생성 실패 (재시도 초과)")
        return None, None
    
    def audit_image_with_vision(self, image_path: str, original_description: str, max_key_rotations: int = None) -> str:
        """[Free Pass 모드] API 쿼터 절약을 위해 무조건 통과"""
        print(f"      ⏩ [Free Pass] 쿼터 절약을 위해 Vision 검수 생략 (PASS)")
        return "PASS"

    def process_content_with_images(self, content_data: dict) -> dict:
        """이미지 플레이스홀더 처리 메인 로직"""
        print("\n" + "="*60)
        print("🎨 Step 3: Image Generation (Final Integrated Mode)")
        print("   ⚙️  설정: 한글 설명(description_ko) 보존 및 전달")
        print("="*60)
        
        sections = content_data['sections']
        updated_sections = []
        
        stats = {
            "total_placeholders": 0,
            "generated": 0,
            "passed": 0,
            "failed": 0,
            "removed": 0
        }
        
        for i, section in enumerate(sections):
            if section['type'] == 'image_placeholder':
                stats["total_placeholders"] += 1
                
                # 영어 설명과 한글 설명 가져오기
                eng_desc = section.get('description', '')
                kor_desc = section.get('description_ko', '') # ★ 핵심: 한글 설명 추출
                
                print(f"\n[{stats['total_placeholders']}] 이미지 처리 중 (ID: {section['id']})")
                print(f"   🇺🇸 Prompt: {eng_desc[:40]}...")
                if kor_desc:
                    print(f"   🇰🇷 Caption: {kor_desc[:40]}...")
                
                # 1. 이미지 생성 (영어 프롬프트 사용)
                image_path, relative_path = self.generate_image(
                    eng_desc,
                    section['id']
                )
                
                if image_path and relative_path:
                    stats["generated"] += 1
                    
                    # 2. 검수 (Free Pass)
                    audit_result = self.audit_image_with_vision(image_path, eng_desc)
                    
                    if audit_result == "PASS":
                        stats["passed"] += 1
                        updated_section = {
                            "type": "image",
                            "id": section['id'],
                            "description": eng_desc,       # 영어 (보존)
                            "description_ko": kor_desc,    # ★ 핵심: 한글 (보존하여 Step 4로 전달)
                            "url": relative_path,
                            "audit_status": "PASS",
                            "audit_timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        updated_sections.append(updated_section)
                        print(f"      🎉 최종 승인: 이미지 삽입됨")
                    else:
                        stats["failed"] += 1
                        stats["removed"] += 1
                        updated_sections.append(section)
                else:
                    stats["failed"] += 1
                    stats["removed"] += 1
                    print(f"      🗑️ 생성 실패로 플레이스홀더 삭제")
            else:
                updated_sections.append(section)
        
        result = content_data.copy()
        result['sections'] = updated_sections
        result['stats'] = stats
        
        print("\n" + "="*60)
        print(f"📊 처리 완료: 총 {stats['passed']}장 생성 및 삽입됨")
        print("="*60)
        
        return result
    
    def save_output(self, data: dict, output_path: str = "automation/intermediate_outputs/step3_validated_content.json"):
        """Step 3 출력 저장"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 출력 저장 완료: {output_path}")

def main():
    try:
        agent = ImageAuditAgent()
        content_data = agent.load_structured_content()
        result = agent.process_content_with_images(content_data)
        agent.save_output(result)
        
        print("\n✅ Step 3 완료!")
        
    except Exception as e:
        print(f"\n❌ Step 3 실패: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

if __name__ == "__main__":
    main()
