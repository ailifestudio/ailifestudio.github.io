#!/usr/bin/env python3
"""
통합 블로그 자동화 시스템
- RSS 뉴스 크롤링 + AI 콘텐츠 생성
- data.json 통합 업데이트
"""

import json
import os
import sys
from datetime import datetime
from typing import List, Dict

# 기존 모듈
from news_crawler import NewsAutomation

# 새 모듈
try:
    from ai_content_generator import AIContentGenerator
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("⚠️ AI 콘텐츠 생성 모듈을 사용하려면 'pip install google-generativeai' 실행")


class BlogAutomation:
    def __init__(self, 
                 rss_config='config.json',
                 ai_config='config_ai.json',
                 enable_ai=True):
        """
        통합 블로그 자동화 초기화
        
        Args:
            rss_config: RSS 크롤링 설정 파일
            ai_config: AI 생성 설정 파일
            enable_ai: AI 콘텐츠 생성 활성화 여부
        """
        self.enable_ai = enable_ai and AI_AVAILABLE
        
        # RSS 크롤러 초기화
        self.news_automation = NewsAutomation(rss_config)
        
        # AI 생성기 초기화
        if self.enable_ai:
            try:
                self.ai_generator = AIContentGenerator(ai_config)
                print("✅ AI 콘텐츠 생성 활성화")
            except Exception as e:
                print(f"⚠️ AI 생성기 초기화 실패: {e}")
                self.enable_ai = False
        else:
            self.ai_generator = None
            print("ℹ️ AI 콘텐츠 생성 비활성화 (RSS만 사용)")
    
    def collect_rss_articles(self) -> List[Dict]:
        """RSS 피드에서 뉴스 수집"""
        print("\n" + "="*60)
        print("📰 RSS 뉴스 수집 시작")
        print("="*60)
        
        articles = self.news_automation.fetch_rss_feeds()
        
        if not articles:
            print("❌ 수집된 RSS 기사가 없습니다.")
            return []
        
        print(f"\n✅ 총 {len(articles)}개 RSS 기사 수집 완료")
        
        # AI 요약 적용
        processed = []
        for article in articles[:self.news_automation.config.get('max_articles', 20)]:
            if self.news_automation.config.get('use_ai_summary', False):
                article = self.news_automation.summarize_with_ai(article)
            else:
                article['summary'] = self.news_automation._clean_html(
                    article['summary']
                )[:200] + "..."
            
            processed.append({
                'title': article['title'],
                'source': article['source'],
                'time': self.news_automation.calculate_time_ago(
                    article.get('published', '')
                ),
                'summary': article['summary'],
                'link': article['link'],
                'image': article['image'],
                'category': 'AI/테크',  # 기본 카테고리
                'type': 'rss'
            })
        
        return processed
    
    def generate_ai_article(self) -> Dict:
        """AI로 콘텐츠 자동 생성"""
        if not self.enable_ai:
            return None
        
        print("\n" + "="*60)
        print("🤖 AI 콘텐츠 생성 시작")
        print("="*60)
        
        try:
            article = self.ai_generator.create_article_for_blog()
            if article:
                article['type'] = 'ai_generated'
                return article
        except Exception as e:
            print(f"❌ AI 콘텐츠 생성 실패: {e}")
            import traceback
            traceback.print_exc()
        
        return None
    
    def merge_articles(self, 
                      rss_articles: List[Dict], 
                      ai_article: Dict = None) -> List[Dict]:
        """RSS 뉴스와 AI 생성 글 통합"""
        all_articles = []
        
        # AI 생성 글을 맨 앞에 추가
        if ai_article:
            print(f"\n🎯 AI 생성 글 추가: {ai_article['title']}")
            all_articles.append(ai_article)
        
        # RSS 뉴스 추가
        all_articles.extend(rss_articles)
        
        print(f"\n📊 총 {len(all_articles)}개 아티클 (AI: {1 if ai_article else 0}, RSS: {len(rss_articles)})")
        
        return all_articles
    
    def create_data_json(self, articles: List[Dict]) -> Dict:
        """data.json 형식으로 변환"""
        return {
            'updatedAt': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'articles': articles
        }
    
    def save_data_json(self, data: Dict, output_path='data.json'):
        """data.json 저장"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 {output_path} 저장 완료!")
        print(f"   - 총 {len(data['articles'])}개 아티클")
        print(f"   - 업데이트: {data['updatedAt']}")
    
    def run(self, include_ai=True):
        """전체 자동화 프로세스 실행"""
        print("\n" + "="*60)
        print("🚀 통합 블로그 자동화 시작")
        print("="*60)
        print(f"모드: {'RSS + AI 생성' if include_ai and self.enable_ai else 'RSS만'}")
        
        # 1. RSS 뉴스 수집
        rss_articles = self.collect_rss_articles()
        
        # 2. AI 콘텐츠 생성 (옵션)
        ai_article = None
        if include_ai and self.enable_ai:
            ai_article = self.generate_ai_article()
        
        # 3. 통합
        all_articles = self.merge_articles(rss_articles, ai_article)
        
        if not all_articles:
            print("\n❌ 생성된 아티클이 없습니다.")
            return
        
        # 4. data.json 생성 및 저장
        data = self.create_data_json(all_articles)
        self.save_data_json(data)
        
        print("\n" + "="*60)
        print("🎉 자동화 완료!")
        print("="*60)
        
        # 미리보기
        print("\n📰 생성된 아티클 목록:")
        for i, article in enumerate(all_articles[:5], 1):
            article_type = "🤖 AI" if article.get('type') == 'ai_generated' else "📡 RSS"
            print(f"{i}. {article_type} | {article['title'][:50]}...")


def main():
    """메인 실행 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='통합 블로그 자동화')
    parser.add_argument('--rss-config', default='config.json', help='RSS 설정 파일')
    parser.add_argument('--ai-config', default='config_ai.json', help='AI 설정 파일')
    parser.add_argument('--no-ai', action='store_true', help='AI 생성 비활성화')
    parser.add_argument('--ai-only', action='store_true', help='AI 생성만 실행')
    
    args = parser.parse_args()
    
    try:
        automation = BlogAutomation(
            rss_config=args.rss_config,
            ai_config=args.ai_config,
            enable_ai=not args.no_ai
        )
        
        automation.run(include_ai=not args.no_ai)
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
