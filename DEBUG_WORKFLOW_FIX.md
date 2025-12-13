# 🔍 GitHub Secrets 디버깅 가이드

## 문제: GEMINI_API_KEYS가 비어있음

### 해결 방법 1: Secret 재등록

1. **GitHub Secrets 페이지:**
   ```
   https://github.com/ailifestudio/ailifestudio.github.io/settings/secrets/actions
   ```

2. **기존 GEMINI_API_KEYS 삭제**

3. **새로 등록:**
   - **Name:** `GEMINI_API_KEYS`
   - **Value:** (한 줄로, 공백 없이)
   ```
   ["AIzaSyC...키1","AIzaSyC...키2","AIzaSyC...키3","AIzaSyC...키4","AIzaSyC...키5"]
   ```

### 해결 방법 2: 워크플로우에 디버그 추가

GitHub 웹에서 워크플로우 파일 수정:
```
https://github.com/ailifestudio/ailifestudio.github.io/edit/main/.github/workflows/auto-update-ai.yml
```

**44-57번 줄 사이에 추가:**

```yaml
    - name: 🤖 블로그 자동 업데이트 (AI + RSS)
      env:
        GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        GEMINI_API_KEYS: ${{ secrets.GEMINI_API_KEYS }}
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
      run: |
        cd automation
        
        # 🔍 디버그: Secret 확인
        echo "🔍 디버그 정보:"
        if [ -n "$GEMINI_API_KEY" ]; then
          echo "✅ GEMINI_API_KEY 존재 (길이: ${#GEMINI_API_KEY})"
        else
          echo "❌ GEMINI_API_KEY 없음"
        fi
        
        if [ -n "$GEMINI_API_KEYS" ]; then
          echo "✅ GEMINI_API_KEYS 존재 (길이: ${#GEMINI_API_KEYS})"
          echo "📝 첫 20자: ${GEMINI_API_KEYS:0:20}..."
        else
          echo "❌ GEMINI_API_KEYS 없음"
        fi
        
        # AI 활성화 여부 확인
        ENABLE_AI="${{ github.event.inputs.enable_ai || 'true' }}"
        
        # GEMINI_API_KEY 또는 GEMINI_API_KEYS 중 하나라도 있으면 AI 활성화
        if [ "$ENABLE_AI" = "true" ] && { [ -n "$GEMINI_API_KEY" ] || [ -n "$GEMINI_API_KEYS" ]; }; then
          echo "🤖 AI 콘텐츠 생성 + RSS 크롤링 모드"
          python blog_automation.py --rss-config config_korean.json
        else
          echo "📰 RSS 크롤링만 실행"
          python blog_automation.py --rss-config config_korean.json --no-ai
        fi
```

### 해결 방법 3: 임시로 단일 키 사용

복수 키 대신 단일 키로 우선 테스트:

1. **GitHub Secrets:**
   - **Name:** `GEMINI_API_KEY` (단수)
   - **Value:** `AIzaSyC...` (키 1개)

2. **워크플로우 실행**

3. **성공하면:** 나중에 복수 키로 전환

---

## 📊 예상 로그 (성공 시)

```
🔍 디버그 정보:
✅ GEMINI_API_KEYS 존재 (길이: 395)
📝 첫 20자: ["AIzaSyC...

🤖 AI 콘텐츠 생성 + RSS 크롤링 모드

🔐 API 키 로테이션 시스템 초기화
✅ 5개 API 키 로드 완료
✅ API 키 #1 사용 시도...
✅ Gemini API 연결 성공
```

---

## 🎯 권장 순서

1. **단일 키로 테스트** (`GEMINI_API_KEY`)
2. **성공 확인**
3. **복수 키 추가** (`GEMINI_API_KEYS`)
4. **로테이션 시스템 확인**

---

## ❓ 자주 묻는 질문

**Q: 왜 GEMINI_API_KEYS가 비어있나요?**
A: Secret 값 형식 오류 또는 등록 실패일 가능성이 높습니다.

**Q: JSON 형식이 맞나요?**
A: 반드시 한 줄로, 공백 최소화:
```json
["key1","key2","key3"]
```

**Q: 줄바꿈하면 안 되나요?**
A: GitHub Secrets는 여러 줄 지원하지만, JSON 파싱 문제가 있을 수 있어 한 줄을 권장합니다.
