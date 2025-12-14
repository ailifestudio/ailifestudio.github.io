# 🔧 GitHub Actions 워크플로우 업데이트 필요

**날짜**: 2025-12-14  
**상태**: ⚠️ **수동 업데이트 필요**

---

## ⚠️ **중요 공지**

**4단계 AI 파이프라인**이 구현되었지만, GitHub Actions 보안 정책으로 인해 워크플로우 파일을 자동으로 업데이트할 수 없습니다.

```
[remote rejected] refusing to allow a GitHub App to create or update 
workflow without `workflows` permission
```

**수동으로 워크플로우 파일을 업데이트해주세요.**

---

## 📝 **업데이트 방법**

### **1. GitHub 웹에서 수정 (가장 쉬움)**

1. GitHub 저장소 접속: https://github.com/ailifestudio/ailifestudio.github.io
2. 파일 열기: `.github/workflows/auto-update-ai.yml`
3. 우측 상단 ✏️ (Edit) 클릭
4. 아래 "신규 워크플로우" 섹션의 코드로 **전체 교체**
5. 커밋 메시지: `🔧 Update to 4-step AI pipeline`
6. "Commit changes" 클릭

---

## 💻 **신규 워크플로우 코드**

`.github/workflows/auto-update-ai.yml` 파일의 **39번 줄부터 57번 줄**을 아래 코드로 교체:

### **기존 코드 (삭제)**:
```yaml
    - name: 🤖 블로그 자동 업데이트 (AI + RSS)
      env:
        GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        GEMINI_API_KEYS: ${{ secrets.GEMINI_API_KEYS }}
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
      run: |
        cd automation
        
        # AI 활성화 여부 확인
        ENABLE_AI="${{ github.event.inputs.enable_ai || 'true' }}"
        
        if [ "$ENABLE_AI" = "true" ] && { [ -n "$GEMINI_API_KEY" ] || [ -n "$GEMINI_API_KEYS" ]; }; then
          echo "🤖 AI 콘텐츠 생성 + RSS 크롤링 모드"
          python blog_automation.py --rss-config config_korean.json
        else
          echo "📰 RSS 크롤링만 실행"
          python blog_automation.py --rss-config config_korean.json --no-ai
        fi
```

### **신규 코드 (추가)**:
```yaml
    - name: ✍️ Step 1 - 주제 선정
      if: ${{ github.event.inputs.enable_ai != 'false' }}
      env:
        GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        GEMINI_API_KEYS: ${{ secrets.GEMINI_API_KEYS }}
      run: |
        echo "🎯 Step 1: 블루오션 키워드 발굴 중..."
        python automation/step1_topic_agent.py
    
    - name: 📝 Step 2 - 글 작성
      if: ${{ github.event.inputs.enable_ai != 'false' }}
      env:
        GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        GEMINI_API_KEYS: ${{ secrets.GEMINI_API_KEYS }}
      run: |
        echo "📝 Step 2: 구조화된 콘텐츠 작성 중..."
        python automation/step2_writer_agent.py
    
    - name: 🎨 Step 3 - 이미지 생성 및 검수
      if: ${{ github.event.inputs.enable_ai != 'false' }}
      env:
        GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        GEMINI_API_KEYS: ${{ secrets.GEMINI_API_KEYS }}
      run: |
        echo "🎨 Step 3: 이미지 생성 및 Gemini Vision 검수 중..."
        python automation/step3_image_audit_agent.py
    
    - name: 💾 Step 4 - data.json 저장
      if: ${{ github.event.inputs.enable_ai != 'false' }}
      run: |
        echo "💾 Step 4: data.json 및 Markdown 파일 생성 중..."
        python automation/step4_save_to_data_json.py
```

---

## ✅ **업데이트 확인**

업데이트 후:
1. **Actions** 탭 클릭
2. "Auto Update Blog with AI" 선택
3. "Run workflow" 버튼 클릭 (수동 실행)
4. 로그에서 4단계 실행 확인:
   - ✅ Step 1: 주제 선정
   - ✅ Step 2: 글 작성
   - ✅ Step 3: 이미지 생성 및 검수
   - ✅ Step 4: data.json 저장

---

## 📊 **기대 효과**

### **Before (기존)**:
```
- name: 블로그 자동 업데이트
  run: python blog_automation.py
```
❌ 한 단계 실패 시 전체 실패  
❌ 디버깅 어려움  
❌ 이미지 품질 검증 없음

### **After (신규)**:
```
- Step 1: 주제 선정
- Step 2: 글 작성
- Step 3: 이미지 생성 및 검수
- Step 4: data.json 저장
```
✅ 각 단계 개별 실행  
✅ 상세한 로그  
✅ Gemini Vision 품질 검수  
✅ 비용 $0 (Pollinations.ai)

---

## 🔗 **관련 문서**

- `PIPELINE_ARCHITECTURE.md` - 전체 아키텍처
- `PIPELINE_IMPLEMENTATION_COMPLETE.md` - 구현 완료 보고서
- `TEST_RESULTS.md` - 테스트 결과

---

## 📞 **문제 해결**

### **Q: 워크플로우가 실행되지 않아요**
A: Actions 탭이 활성화되어 있는지 확인하세요.

### **Q: Step 실패 시 어떻게 하나요?**
A: 실패한 Step의 로그를 확인하고, 해당 스크립트를 로컬에서 개별 실행하여 디버깅하세요.

### **Q: 이미지가 생성되지 않아요**
A: Step 3 로그에서 Gemini Vision 검수 결과를 확인하세요. FAIL된 이미지는 자동 삭제됩니다.

---

**작성자**: AI Code Assistant  
**날짜**: 2025-12-14  
**상태**: ✅ 스크립트 준비 완료, ⚠️ 워크플로우 수동 업데이트 필요
