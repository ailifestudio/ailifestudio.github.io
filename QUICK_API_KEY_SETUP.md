# 🔑 5개 API 키 빠른 생성 가이드

## 📋 단계별 가이드

### 1️⃣ 각 프로젝트에서 API 키 생성 (5개)

아래 링크를 **하나씩** 클릭해서 API 키를 생성하세요:

#### 프로젝트 1: gen-lang-client-0496487695
🔗 https://console.cloud.google.com/apis/credentials?project=gen-lang-client-0496487695

1. "**사용자 인증 정보 만들기**" 클릭
2. "**API 키**" 선택
3. 생성된 키 복사 → **메모장에 저장**
   - 예: `AIzaSyCBq3X7Ym8Kp2RtNvLwHj9Fd5Ge6Ua1Zc8`

---

#### 프로젝트 2: gen-lang-client-0535136181
🔗 https://console.cloud.google.com/apis/credentials?project=gen-lang-client-0535136181

동일한 방법으로 키 생성 → 메모장에 추가

---

#### 프로젝트 3: gen-lang-client-0459365803
🔗 https://console.cloud.google.com/apis/credentials?project=gen-lang-client-0459365803

동일한 방법으로 키 생성 → 메모장에 추가

---

#### 프로젝트 4: gen-lang-client-0491854348
🔗 https://console.cloud.google.com/apis/credentials?project=gen-lang-client-0491854348

동일한 방법으로 키 생성 → 메모장에 추가

---

#### 프로젝트 5: gen-lang-client-0703890354
🔗 https://console.cloud.google.com/apis/credentials?project=gen-lang-client-0703890354

동일한 방법으로 키 생성 → 메모장에 추가

---

### 2️⃣ GitHub Secrets에 5개 키 등록

🔗 https://github.com/ailifestudio/ailifestudio.github.io/settings/secrets/actions

1. "**New repository secret**" 클릭
2. **Name**: `GEMINI_API_KEYS` (복수형 주의!)
3. **Secret** 입력 (아래 형식 참고):

```json
["AIzaSyC키1xxxxx","AIzaSyC키2xxxxx","AIzaSyC키3xxxxx","AIzaSyC키4xxxxx","AIzaSyC키5xxxxx"]
```

⚠️ **중요**:
- 대괄호 `[]` 필수
- 쌍따옴표 `""` 필수
- 키 사이에 쉼표 `,` 필수
- **한 줄로 입력** (줄바꿈 없이)
- 공백 최소화

#### ✅ 올바른 예시:
```json
["AIzaSyCBq3X7Ym8K","AIzaSyCDf4Y9Zn2M","AIzaSyCEg5Z1Ao3N","AIzaSyCFh6A2Bp4O","AIzaSyCGi7B3Cq5P"]
```

#### ❌ 잘못된 예시:
```json
# 줄바꿈 있음 (X)
[
  "AIzaSyCBq3X7Ym8K",
  "AIzaSyCDf4Y9Zn2M"
]

# 대괄호 없음 (X)
"AIzaSyCBq3X7Ym8K","AIzaSyCDf4Y9Zn2M"

# 따옴표 없음 (X)
[AIzaSyCBq3X7Ym8K,AIzaSyCDf4Y9Zn2M]
```

4. "**Add secret**" 클릭

---

### 3️⃣ 기존 단일 키 삭제 (선택)

로테이션 시스템은 `GEMINI_API_KEYS` (복수)를 우선 사용하므로, 기존 `GEMINI_API_KEY` (단수)는 삭제해도 됩니다.

---

### 4️⃣ 워크플로우 실행 및 확인

🔗 https://github.com/ailifestudio/ailifestudio.github.io/actions

1. "**Auto Update Blog with AI**" 클릭
2. "**Run workflow**" 버튼 클릭
3. 로그에서 확인:

```
✅ Gemini API 초기화 완료 (5개 키, 모델: gemini-2.5-flash)
✅ API 키 로테이션 시스템 초기화
```

---

## 📊 예상 결과

### ✅ 성공 시 로그:
```
🤖 AI 콘텐츠 생성 + RSS 크롤링 모드
✅ Gemini API 초기화 완료 (5개 키, 모델: gemini-2.5-flash)
✅ API 키 로테이션 시스템 초기화
【1단계】 트렌드 분석 중...
  ✅ 주제 생성 완료: [제목]
【2단계】 블로그 글 생성 중...
  ✅ 글 생성 완료 (1,542자)
  ✅ Markdown 파일 저장: 2025-12-13-제목.md
🔨 build_blog.py 실행 중...
✅ 블로그 빌드 완료
✅ 블로그 업데이트 완료!
```

### 📈 할당량:
- **일일 총 할당량**: 7,500회
- **분당 제한**: 75 RPM (5개 × 15 RPM)
- **자동 로테이션**: ✅

---

## 🆘 트러블슈팅

### Q1: "API key not valid" 오류
**원인**: 키가 잘못 입력됨  
**해결**: 
1. AI Studio에서 키 재확인: https://aistudio.google.com/app/apikey
2. GitHub Secrets에서 `GEMINI_API_KEYS` 삭제 후 재등록
3. 각 키를 AI Studio Chat에서 테스트

### Q2: "모든 API 키 할당량 초과"
**원인**: 5개 키 모두 할당량 소진  
**해결**: 
1. 내일 09:00 KST까지 대기 (자동 리셋)
2. 또는 프로젝트 추가 생성 (최대 10개까지 권장)

### Q3: JSON 형식 오류
**해결**: 아래 형식 그대로 사용
```json
["키1","키2","키3","키4","키5"]
```

---

## ✅ 체크리스트

- [ ] 프로젝트 1에서 API 키 생성
- [ ] 프로젝트 2에서 API 키 생성
- [ ] 프로젝트 3에서 API 키 생성
- [ ] 프로젝트 4에서 API 키 생성
- [ ] 프로젝트 5에서 API 키 생성
- [ ] GitHub Secrets에 `GEMINI_API_KEYS` 등록
- [ ] 워크플로우 실행 및 로그 확인
- [ ] 블로그에서 AI 생성 글 확인

---

**🎉 설정 완료 후 7,500회/일 사용 가능!**
