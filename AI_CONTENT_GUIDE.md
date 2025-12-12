# 🤖 AI 콘텐츠 자동 생성 가이드

## 개요

Gemini API를 활용하여 트렌드 기반 AI 콘텐츠를 자동으로 생성하고, 기존 RSS 뉴스와 함께 블로그에 게시하는 시스템입니다.

## 🌟 주요 기능

### 1. **트렌드 분석 & 주제 생성**
- 유튜브, 네이버 블로그, X, 뉴스 등에서 트렌드 분석
- SEO 최적화된 제목 자동 생성
- 실전 활용 가능한 주제 추천

### 2. **AI 블로그 글 생성**
- 1500자 이상의 구조화된 콘텐츠
- HTML 포맷 (h2, h3, p, ul, li, strong, mark)
- 실무 팁, 주의사항, 코드 예시 포함
- 이미지 키워드 자동 생성

### 3. **RSS 뉴스 통합**
- AI 생성 글 + RSS 크롤링 뉴스를 하나의 블로그에 통합
- AI 글은 "AI/테크" 카테고리로 자동 분류
- 우선순위: AI 생성 글 > RSS 뉴스

---

## 🚀 빠른 시작

### 1. Gemini API 키 발급

1. https://aistudio.google.com/apikey 접속
2. Google 계정으로 로그인
3. **Get API Key** 클릭
4. API 키 복사 (무료 티어 사용 가능)

### 2. API 키 설정

#### 방법 A: 환경 변수 (권장)

```bash
export GEMINI_API_KEY="your-api-key-here"
./update_blog_ai.sh
```

#### 방법 B: 설정 파일 (로컬 테스트용)

`automation/config_ai.json` 편집:
```json
{
  "gemini_api_key": "your-api-key-here"
}
```

⚠️ **주의**: 설정 파일에 직접 입력하면 Git에 노출될 수 있습니다.

#### 방법 C: GitHub Secrets (자동화용)

1. GitHub 저장소 → Settings → Secrets and variables → Actions
2. **New repository secret** 클릭
3. Name: `GEMINI_API_KEY`
4. Secret: API 키 입력
5. **Add secret** 클릭

---

## 💻 사용 방법

### 로컬 실행

#### 1. AI + RSS 통합 모드 (추천)
```bash
./update_blog_ai.sh
```

#### 2. RSS만 실행 (AI 비활성화)
```bash
./update_blog_ai.sh --no-ai
```

#### 3. AI만 실행 (RSS 비활성화)
```bash
./update_blog_ai.sh --ai-only
```

#### 4. Python 직접 실행
```bash
cd automation

# AI + RSS 통합
python blog_automation.py --rss-config config_korean.json

# RSS만
python blog_automation.py --rss-config config_korean.json --no-ai

# AI만
python ai_content_generator.py
```

---

## ⚙️ 설정 커스터마이징

### config_ai.json 수정

```json
{
  "gemini_api_key": "",
  "generation_settings": {
    "topics_per_run": 1,              // 1회 실행당 생성할 글 개수
    "min_content_length": 1500,       // 최소 글자 수
    "max_content_length": 3000,       // 최대 글자 수
    "category": "AI/테크",            // 카테고리
    "language": "ko"                  // 언어
  },
  "trending_sources": [               // 트렌드 분석 소스
    "유튜브",
    "네이버 블로그",
    "카페",
    "뉴스",
    "X (트위터)"
  ],
  "excluded_keywords": [              // 제외할 키워드
    "부업",
    "수익",
    "돈벌기"
  ]
}
```

---

## 🤖 GitHub Actions 자동화

### 자동 실행 스케줄

- **오전 9시** (KST): AI 콘텐츠 + RSS 뉴스
- **오후 3시** (KST): RSS 뉴스만
- **오후 9시** (KST): RSS 뉴스만

### 수동 실행

1. GitHub 저장소 → **Actions** 탭
2. **Auto Update Blog with AI** 선택
3. **Run workflow** 클릭
4. AI 활성화 여부 선택:
   - `true`: AI 생성 + RSS
   - `false`: RSS만
5. **Run workflow** 버튼 클릭

### 워크플로우 파일

`.github/workflows/auto-update-ai.yml`

```yaml
on:
  schedule:
    - cron: '0 0,6,12 * * *'  # 매일 3회 실행
  workflow_dispatch:          # 수동 실행 가능
```

---

## 📊 생성 결과 구조

### AI 생성 아티클 형식

```json
{
  "title": "AI 트렌드 주제",
  "source": "AI 자동 생성",
  "time": "방금 전",
  "summary": "2-3문장 요약...",
  "link": "#",
  "image": "https://...",
  "content": "<h2>제목</h2><p>내용...</p>",
  "category": "AI/테크",
  "type": "ai_generated",
  "created_at": "2025-12-12 15:00",
  "thumbnail_prompt": "modern AI workspace...",
  "image_keywords": ["ChatGPT 화면", "AI 자동화"]
}
```

---

## 🎨 HTML 콘텐츠 스타일

### 기본 태그
- `<h2>` - 메인 제목
- `<h3>` - 섹션 제목
- `<p>` - 본문
- `<ul><li>` - 리스트
- `<strong>` - 강조
- `<mark>` - 하이라이트

### 특수 스타일

#### 💡 TIP 박스
```html
<p style="border-left:4px solid #3b82f6; padding-left:10px; background:#f0f9ff; padding:10px;">
<strong>💡 TIP:</strong> 내용
</p>
```

#### 코드 블록
```html
<pre style="background:#1e293b; color:#e2e8f0; padding:15px; border-radius:8px;">
코드 예시
</pre>
```

#### 이미지 키워드
```
[IMAGE:ChatGPT 업무 자동화 화면]
```

---

## 🔧 문제 해결

### Q: AI 생성이 너무 느려요
A: 
- Gemini API는 처음 실행 시 30초~2분 소요 가능
- 무료 티어는 분당 요청 제한이 있음
- 워크플로우는 자동으로 재시도 포함

### Q: API 쿼터 초과 오류
A:
- 무료 티어: 분당 15개 요청, 일일 1500개 요청
- 24시간 후 자동 리셋
- 또는 유료 플랜으로 업그레이드

### Q: 생성된 글 품질이 낮아요
A:
- `config_ai.json`의 `min_content_length` 증가
- 프롬프트 수정 (`ai_content_generator.py`)
- 다른 모델 시도 (gemini-2.5-pro)

### Q: AI 없이 RSS만 사용하고 싶어요
A:
```bash
./update_blog_ai.sh --no-ai
```

---

## 📈 무료 티어 제한

### Gemini API (무료)
- **분당**: 15개 요청
- **일일**: 1500개 요청
- **토큰**: 분당 100만 토큰

### 권장 사용 패턴
- **하루 1회 AI 생성** (오전 9시)
- **나머지는 RSS만** (오후 3시, 9시)
- 수동 실행은 필요시에만

---

## 🎯 실전 활용 예시

### 예시 1: 매일 아침 AI 트렌드 글
```bash
# Cron 설정 (매일 오전 9시)
0 9 * * * cd /path/to/webapp && ./update_blog_ai.sh && git add . && git commit -m "AI 업데이트" && git push
```

### 예시 2: 주간 요약 콘텐츠
```bash
# 매주 일요일 오후 6시
0 18 * * 0 cd /path/to/webapp && ./update_blog_ai.sh
```

### 예시 3: 특정 주제 지정
`ai_content_generator.py` 수정:
```python
topic_prompt = """
최근 ChatGPT 업데이트 중 가장 실용적인 기능 1개를 추천해줘.
"""
```

---

## 💡 고급 활용

### 커스텀 프롬프트 작성

`automation/ai_content_generator.py`의 `post_prompt` 수정:

```python
post_prompt = f"""
[작성 규칙]
- 개발자를 위한 실전 코드 포함
- GitHub 예제 링크 추가
- 단계별 튜토리얼 형식

주제: {topic}
"""
```

### 다중 언어 지원

`config_ai.json`:
```json
{
  "language": "en"  // 영문 콘텐츠 생성
}
```

### 여러 주제 동시 생성

```python
# blog_automation.py 수정
for _ in range(3):  # 3개 주제 생성
    ai_article = self.generate_ai_article()
```

---

## 📚 관련 문서

- [메인 README](README.md)
- [빠른 시작 가이드](QUICKSTART.md)
- [아키텍처 문서](ARCHITECTURE.md)
- [Gemini API 공식 문서](https://ai.google.dev/gemini-api/docs)

---

## 🤝 기여

AI 프롬프트 개선, 새로운 기능 제안은 언제나 환영합니다!

---

**🎉 AI 자동화로 더 스마트한 블로그 운영을 시작하세요!**
