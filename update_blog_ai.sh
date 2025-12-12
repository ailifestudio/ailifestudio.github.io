#!/bin/bash

# AI 콘텐츠 생성 + RSS 크롤링 통합 스크립트
# 사용법: ./update_blog_ai.sh [--no-ai] [--ai-only]

echo "🚀 AI Life Studio 블로그 자동 업데이트 (AI + RSS)"
echo "=========================================="

cd automation

# 옵션 파싱
NO_AI=false
AI_ONLY=false

for arg in "$@"; do
    case $arg in
        --no-ai)
            NO_AI=true
            ;;
        --ai-only)
            AI_ONLY=true
            ;;
    esac
done

# 실행
if [ "$NO_AI" = true ]; then
    echo "📰 RSS만 실행 (AI 비활성화)"
    python blog_automation.py --rss-config config_korean.json --no-ai
elif [ "$AI_ONLY" = true ]; then
    echo "🤖 AI만 실행 (RSS 비활성화)"
    python ai_content_generator.py
else
    echo "🤖 AI 생성 + 📰 RSS 크롤링 (통합 모드)"
    python blog_automation.py --rss-config config_korean.json
fi

# data.json 복사
if [ -f "data.json" ]; then
    cp data.json ../data.json
    echo ""
    echo "✅ 블로그 업데이트 완료!"
    echo "📊 data.json 파일이 업데이트되었습니다."
    echo ""
    echo "다음 단계:"
    echo "  git add data.json"
    echo "  git commit -m '🤖 AI + RSS 업데이트'"
    echo "  git push"
else
    echo "❌ data.json 생성 실패"
    exit 1
fi
