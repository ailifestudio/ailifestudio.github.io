# 🚀 빠른 시작 가이드

## 📋 목차
1. [즉시 실행하기](#즉시-실행하기)
2. [GitHub 배포하기](#github-배포하기)
3. [OpenAI API 설정 (선택)](#openai-api-설정)
4. [자동화 활성화](#자동화-활성화)
5. [커스터마이징](#커스터마이징)

---

## 🎯 즉시 실행하기

### 방법 1: 간편 스크립트 사용 (추천)

**영문 뉴스:**
```bash
./update_blog.sh
```

**한글 뉴스:**
```bash
./update_blog.sh config_korean.json
```

**Windows:**
```cmd
update_blog.bat config_korean.json
```

### 방법 2: 수동 실행

```bash
cd automation
python news_crawler.py config_korean.json
cp data.json ../data.json
```

---

## 📤 GitHub 배포하기

### 1단계: 로컬 변경사항 푸시

```bash
git add data.json
git commit -m "📰 뉴스 업데이트"
git push origin main
```

### 2단계: GitHub Pages 활성화

1. GitHub 저장소 페이지 접속
2. **Settings** 클릭
3. 왼쪽 메뉴에서 **Pages** 클릭
4. **Source**: `Deploy from a branch` 선택
5. **Branch**: `main` 선택, 폴더는 `/ (root)` 선택
6. **Save** 클릭

⏰ **5-10분 후** https://ailifestudio.github.io/ 접속 가능!

---

## 🤖 OpenAI API 설정 (선택)

AI 요약 기능을 사용하려면:

### 1단계: API 키 발급

1. https://platform.openai.com/ 접속
2. 회원가입/로그인
3. API keys 메뉴에서 새 키 생성
4. 키 복사 (한 번만 표시됨!)

### 2단계: GitHub Secrets 설정

1. 저장소 Settings → Secrets and variables → Actions
2. **New repository secret** 클릭
3. Name: `OPENAI_API_KEY`
4. Secret: 복사한 API 키 붙여넣기
5. **Add secret** 클릭

### 로컬 실행시 API 키 사용

```bash
export OPENAI_API_KEY="your-api-key-here"
./update_blog.sh
```

또는 `automation/config.json`에 직접 입력:
```json
{
  "openai_api_key": "your-api-key-here"
}
```

⚠️ **주의**: API 키를 config 파일에 직접 넣으면 Git에 노출될 수 있습니다. 환경 변수 사용을 권장합니다.

---

## ⏰ 자동화 활성화

GitHub Actions가 자동으로 활성화됩니다!

### 기본 스케줄
- 🌅 오전 9시 (KST)
- 🌞 오후 3시 (KST)
- 🌙 오후 9시 (KST)

### 수동 실행

1. GitHub 저장소 → **Actions** 탭
2. **Auto Update Blog** 선택
3. **Run workflow** 클릭
4. **Run workflow** 버튼 클릭

### 실행 로그 확인

Actions 탭에서 실행 내역 클릭하면 상세 로그 확인 가능

---

## 🎨 커스터마이징

### RSS 피드 변경

`automation/config.json` 편집:

```json
{
  "rss_feeds": [
    {
      "name": "내가 좋아하는 블로그",
      "url": "https://blog.example.com/rss",
      "max_items": 5
    }
  ]
}
```

### 업데이트 주기 변경

`.github/workflows/auto-update.yml` 편집:

```yaml
schedule:
  - cron: '0 */3 * * *'  # 3시간마다
  - cron: '0 9 * * 1'    # 매주 월요일 오전 9시
```

Cron 표현식 도움말: https://crontab.guru/

### 디자인 변경

`index.html` 파일의 Tailwind CSS 클래스 수정

**색상 변경:**
```html
<!-- 로고 색상 -->
<span class="text-blue-600">AI</span>
<!-- → -->
<span class="text-purple-600">AI</span>
```

**제목 변경:**
```html
<h1>Curator.<span class="text-blue-600">AI</span></h1>
```

---

## 🔍 문제 해결

### ❌ "No module named 'feedparser'"

```bash
pip install -r automation/requirements.txt
```

### ❌ GitHub Actions 실행 안 됨

1. Actions 탭에서 워크플로우가 활성화되어 있는지 확인
2. 저장소 Settings → Actions → General
3. "Allow all actions and reusable workflows" 선택

### ❌ 블로그가 안 보임

1. Settings → Pages에서 설정 확인
2. `index.html`이 루트 디렉토리에 있는지 확인
3. 5-10분 대기 후 재접속

### ❌ 한글이 깨짐

RSS 피드 URL이 올바른지, 해당 사이트의 RSS가 유효한지 확인

---

## 💡 유용한 팁

### 여러 설정 파일 관리

```bash
# 한글 IT 뉴스
./update_blog.sh config_korean.json

# 영문 AI 뉴스
./update_blog.sh config_ai_english.json

# 경제 뉴스
./update_blog.sh config_economy.json
```

### 로컬 미리보기

```bash
python -m http.server 8000
```

브라우저에서 http://localhost:8000 접속

### Git 자동 푸시 스크립트

`auto_push.sh` 생성:
```bash
#!/bin/bash
./update_blog.sh
git add data.json
git commit -m "📰 $(date +'%Y-%m-%d %H:%M') 뉴스 업데이트"
git push origin main
```

```bash
chmod +x auto_push.sh
./auto_push.sh
```

---

## 📚 더 알아보기

- [전체 README](README.md)
- [자동화 스크립트 상세 설명](automation/README.md)
- [GitHub Pages 공식 문서](https://docs.github.com/pages)
- [GitHub Actions 공식 문서](https://docs.github.com/actions)

---

**🎉 즐거운 블로깅 되세요!**
