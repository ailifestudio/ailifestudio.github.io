# AI Life Studio Blog

자동화된 뉴스 큐레이션 블로그 시스템

## 🌟 주요 기능

- ✅ **완전 자동화**: GitHub Actions로 매일 3회 자동 업데이트
- 🤖 **AI 콘텐츠 생성**: Gemini API로 트렌드 기반 자동 글 생성 (NEW!)
- 🤖 **AI 요약**: OpenAI GPT를 활용한 자동 뉴스 요약
- 📰 **RSS 크롤링**: 여러 뉴스 소스에서 자동 수집
- 🎨 **반응형 디자인**: 모바일/데스크톱 최적화
- 💰 **완전 무료**: GitHub Pages + 무료 AI API

## 🚀 빠른 시작

### 1. 저장소 설정

```bash
# 저장소 클론
git clone https://github.com/ailifestudio/ailifestudio.github.io.git
cd ailifestudio.github.io

# 의존성 설치
pip install -r automation/requirements.txt
```

### 1-1. 간편 실행 (추천)

#### 🤖 AI 콘텐츠 생성 + RSS (신기능!)
```bash
./update_blog_ai.sh                 # AI 자동 생성 + 한글 뉴스
./update_blog_ai.sh --no-ai         # RSS만
./update_blog_ai.sh --ai-only       # AI만
```

#### 📰 RSS만 사용 (기존 방식)
```bash
./update_blog.sh                    # 영문 뉴스
./update_blog.sh config_korean.json # 한글 뉴스
```

**Windows:**
```cmd
update_blog.bat config_korean.json  # 한글 뉴스
```

### 2. API 키 설정 (선택사항)

#### 🤖 Gemini API (AI 콘텐츠 자동 생성용 - 무료!)

1. [Google AI Studio](https://aistudio.google.com/apikey)에서 API 키 발급
2. GitHub 저장소 Settings → Secrets and variables → Actions
3. `GEMINI_API_KEY` 시크릿 추가

#### 📝 OpenAI API (뉴스 요약용)

1. [OpenAI 플랫폼](https://platform.openai.com/)에서 API 키 발급
2. GitHub 저장소 Settings → Secrets and variables → Actions
3. `OPENAI_API_KEY` 시크릿 추가

> **참고**: API 키 없이도 작동합니다. AI 생성 및 요약 기능만 비활성화됩니다.
> 
> **🆕 상세 가이드**: [AI 콘텐츠 생성 가이드](AI_CONTENT_GUIDE.md) 참고

### 3. 뉴스 소스 설정

`automation/config.json` 파일을 편집하여 원하는 RSS 피드 추가:

```json
{
  "rss_feeds": [
    {
      "name": "원하는 블로그 이름",
      "url": "RSS 피드 URL",
      "max_items": 3
    }
  ],
  "max_articles": 20,
  "use_ai_summary": true
}
```

### 4. 로컬 테스트

```bash
cd automation
python news_crawler.py
```

### 5. 자동화 활성화

GitHub Actions가 자동으로 실행됩니다:
- 매일 오전 9시 (KST)
- 매일 오후 3시 (KST)
- 매일 오후 9시 (KST)

수동 실행: GitHub 저장소 → Actions → Auto Update Blog → Run workflow

## 📁 프로젝트 구조

```
ailifestudio.github.io/
├── index.html              # 메인 블로그 페이지
├── data.json              # 뉴스 데이터 (자동 생성)
├── automation/
│   ├── news_crawler.py    # 자동화 스크립트
│   ├── config.json        # 설정 파일
│   └── requirements.txt   # Python 의존성
└── .github/
    └── workflows/
        └── auto-update.yml # GitHub Actions 워크플로우
```

## 🛠️ 사용자 정의

### RSS 피드 추가

`automation/config.json`에 새로운 피드 추가:

```json
{
  "name": "내 블로그",
  "url": "https://myblog.com/rss",
  "max_items": 5
}
```

### 업데이트 주기 변경

`.github/workflows/auto-update.yml`의 cron 스케줄 수정:

```yaml
schedule:
  - cron: '0 */6 * * *'  # 6시간마다
```

### 디자인 커스터마이징

`index.html` 파일의 Tailwind CSS 클래스 수정

## 🔧 문제 해결

### Q: 자동 업데이트가 안 돼요
A: GitHub Actions 탭에서 워크플로우 실행 로그 확인

### Q: AI 요약이 작동하지 않아요
A: 
1. OpenAI API 키가 올바르게 설정되었는지 확인
2. API 크레딧 잔액 확인
3. `config.json`에서 `use_ai_summary: false`로 설정하여 비활성화 가능

### Q: RSS 피드가 수집되지 않아요
A:
1. RSS URL이 올바른지 확인
2. 해당 사이트가 RSS를 제공하는지 확인
3. 워크플로우 로그에서 오류 메시지 확인

## 📊 한국어 RSS 피드 추천

```json
{
  "rss_feeds": [
    {"name": "테크M", "url": "http://www.techm.kr/rss/allArticle.xml", "max_items": 3},
    {"name": "AI타임스", "url": "https://www.aitimes.com/rss/allArticle.xml", "max_items": 3},
    {"name": "블로터", "url": "https://www.bloter.net/feed", "max_items": 3}
  ]
}
```

## 📝 라이선스

MIT License - 자유롭게 사용, 수정, 배포 가능합니다.

## 🤝 기여

이슈와 PR은 언제나 환영합니다!

## 📮 문의

GitHub Issues를 통해 문의해주세요.

---

Made with ❤️ by AI Life Studio
