# 🍌 Nano Banana AI 이미지 생성 설정

> **현재 상태:** Unsplash 무료 이미지 사용 중 (저작권 안전)
> **선택사항:** Nano Banana AI 이미지 생성 추가

---

## 🎨 **Nano Banana란?**

- AI 기반 이미지 생성 (GenSpark)
- 커스텀 이미지 제작 가능
- Unsplash 실패 시 백업으로 사용

---

## 🔧 **활성화 방법**

### **Step 1: unsplash_images.py 수정**

`automation/unsplash_images.py` 파일의 `generate_image_with_ai` 함수 수정:

```python
def generate_image_with_ai(prompt: str) -> str:
    """
    Nano Banana를 사용해 이미지 생성
    """
    try:
        # GenSpark AI image generation API
        from genspark import image_generation
        
        result = image_generation(
            query=prompt,
            model="fal-ai/nano-banana",
            aspect_ratio="16:9",
            image_urls=[],
            task_summary="Blog post illustration"
        )
        
        if result and result.get('images'):
            return result['images'][0]['url']
        
        # Fallback to Unsplash
        return search_unsplash_image(prompt)
    except Exception as e:
        print(f"    ⚠️ AI 이미지 생성 실패: {e}")
        return search_unsplash_image(prompt)
```

### **Step 2: AI 생성 활성화**

`automation/ai_content_generator.py`의 261번 줄:

```python
# 변경 전
post['content'] = add_images_to_content_with_generation(post['content'])

# 변경 후
post['content'] = add_images_to_content_with_generation(post['content'], use_ai_generation=True)
```

---

## ⚖️ **Unsplash vs Nano Banana 비교**

### **Unsplash (현재 사용 중)**
- ✅ 완전 무료
- ✅ 저작권 안전 (CC0 라이선스)
- ✅ 고품질 사진
- ✅ API 키 불필요
- ❌ 키워드에 정확히 맞지 않을 수 있음

### **Nano Banana (선택사항)**
- ✅ 키워드에 정확히 맞는 이미지
- ✅ 커스텀 일러스트 생성
- ✅ 일관된 스타일
- ❌ API 크레딧 소모
- ❌ 생성 시간 소요

---

## 🎯 **권장 전략**

### **현재 (Unsplash 단독):**
```
블로그 글 생성
  ↓
[IMAGE:...] 키워드 삽입
  ↓
Unsplash 검색 → 이미지 삽입
```

**장점:** 
- 완전 무료
- 빠른 속도
- 안정적

### **하이브리드 (Unsplash + Nano Banana):**
```
블로그 글 생성
  ↓
[IMAGE:...] 키워드 삽입
  ↓
Unsplash 검색 시도
  ↓ (실패 또는 부적합)
Nano Banana AI 생성
  ↓
이미지 삽입
```

**장점:**
- Unsplash 우선 (무료)
- AI 생성은 백업
- 품질 보장

---

## 💡 **현재 시스템으로 충분한 이유**

1. **Unsplash 품질:** 
   - 전문가 촬영 고품질 사진
   - AI/테크 관련 이미지 풍부

2. **저작권 안전:**
   - CC0 라이선스 (완전 자유 사용)
   - 크레딧 표시만으로 OK

3. **비용 절감:**
   - 완전 무료
   - API 크레딧 소모 없음

4. **속도:**
   - 즉시 이미지 URL 반환
   - AI 생성 대기 시간 없음

---

## 🚀 **결론**

**현재 Unsplash 시스템으로 충분합니다!**

Nano Banana는 다음과 같은 경우에만 고려:
- 특정 스타일의 일러스트 필요
- Unsplash에 없는 특수 이미지
- 브랜드 일관성 필요

---

**지금은 Unsplash 시스템을 그대로 사용하는 것을 권장합니다!** ✅
