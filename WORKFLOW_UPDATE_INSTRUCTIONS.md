# 🔧 워크플로우 업데이트 필요

## 문제
AI 생성 글이 `data.json`에는 있지만 메인 페이지에 표시되지 않습니다.

## 원인
- `blog_automation.py`는 `data.json`만 업데이트
- `build_blog.py`가 실행되지 않음
- `dashboard_summary.json`이 업데이트되지 않음

## 해결책

GitHub 웹에서 워크플로우 파일을 다음과 같이 수정하세요:

### URL:
```
https://github.com/ailifestudio/ailifestudio.github.io/edit/main/.github/workflows/auto-update-ai.yml
```

### 57번 줄 다음에 추가:

```yaml
    - name: 🔨 블로그 빌드 (Markdown → HTML)
      run: |
        echo "🔨 build_blog.py 실행 중..."
        python automation/build_blog.py
        echo "✅ 블로그 빌드 완료"
        
```

### 78번 줄 수정:

**기존:**
```yaml
        git add data.json
```

**변경:**
```yaml
        # AI 생성 Markdown, data.json, data/, feed/, contents/ 모두 추가
        git add data.json data/ feed/ contents/
```

## 수정 후 예상 결과

```
✅ AI 글 생성
✅ Markdown 파일 저장 (contents/)
✅ build_blog.py 실행
✅ dashboard_summary.json 업데이트
✅ 메인 페이지에 표시
```

## 전체 워크플로우 코드

또는 아래 전체 코드를 복사해서 붙여넣으세요:
name: Auto Update Blog with AI

on:
  schedule:
    # 매일 오전 9시, 오후 3시, 오후 9시 (KST = UTC+9)
    - cron: '0 0,6,12 * * *'  # UTC 0시, 6시, 12시 = KST 9시, 15시, 21시
  workflow_dispatch:  # 수동 실행 가능
    inputs:
      enable_ai:
        description: 'AI 콘텐츠 생성 활성화'
        required: false
        default: 'true'
        type: choice
        options:
          - 'true'
          - 'false'

permissions:
  contents: write        # ← 이 부분 추가!

jobs:
  update-blog:
    runs-on: ubuntu-latest
    
    steps:
    - name: 📥 체크아웃
      uses: actions/checkout@v4
      
    - name: 🐍 Python 설정
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
        
    - name: 📦 의존성 설치
      run: |
        cd automation
        pip install -r requirements.txt
        
    - name: 🤖 블로그 자동 업데이트 (AI + RSS)
      env:
        GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
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
        
    - name: 🔨 블로그 빌드 (Markdown → HTML)
      run: |
        echo "🔨 build_blog.py 실행 중..."
        python automation/build_blog.py
        echo "✅ 블로그 빌드 완료"
        
    - name: 📊 data.json 이동
      run: |
        if [ -f automation/data.json ]; then
          cp automation/data.json data.json
          echo "✅ data.json 업데이트 완료"
        else
          echo "❌ data.json 생성 실패"
          exit 1
        fi
        
    - name: 📤 변경사항 커밋 및 푸시
      run: |
        git config --local user.email "github-actions[bot]@users.noreply.github.com"
        git config --local user.name "github-actions[bot]"
        
        # AI 생성 Markdown, data.json, data/, feed/, contents/ 모두 추가
        git add data.json data/ feed/ contents/
        
        # 변경사항이 있을 때만 커밋
        if ! git diff --staged --quiet; then
          # AI 생성 여부에 따라 커밋 메시지 변경
          if [ -n "${{ secrets.GEMINI_API_KEY }}" ] || [ -n "${{ secrets.GEMINI_API_KEYS }}" ]; then
            git commit -m "🤖 자동 업데이트 (AI + RSS): $(date +'%Y-%m-%d %H:%M')"
          else
            git commit -m "📰 자동 업데이트 (RSS): $(date +'%Y-%m-%d %H:%M')"
          fi
          
          git push
          echo "✅ 블로그 업데이트 완료!"
        else
          echo "ℹ️ 변경사항 없음"
        fi
