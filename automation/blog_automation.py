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
        """AI로 콘텐츠 자동 생성 및 Markdown 파일 저장"""
        if not self.enable_ai:
            return None
        
        print("\n" + "="*60)
        print("🤖 AI 콘텐츠 생성 시작")
        print("="*60)
        
        try:
            article = self.ai_generator.create_article_for_blog()
            if article:
                article['type'] = 'ai_generated'
                
                # Markdown 파일로 저장
                self._save_ai_article_as_markdown(article)
                
                return article
        except Exception as e:
            print(f"❌ AI 콘텐츠 생성 실패: {e}")
            import traceback
            traceback.print_exc()
        
        return None
    
    def _save_ai_article_as_markdown(self, article: Dict):
        """AI 생성 글을 Markdown 파일로 저장"""
        import os
        from datetime import datetime
        import re
        
        # contents 디렉토리 확인 (절대 경로)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        contents_dir = os.path.join(project_root, 'contents')
        
        if not os.path.exists(contents_dir):
            os.makedirs(contents_dir)
        
        # 파일명 생성 (날짜-slug 형식)
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 영문 slug 생성
        title = article['title']
        
        # 1. 특수문자를 하이픈으로 변환
        title = title.replace('/', '-').replace(':', '-').replace('(', '').replace(')', '')
        
        # 2. 영문, 숫자, 공백, 하이픈만 남기고 제거
        title_slug = re.sub(r'[^a-zA-Z0-9\s-]', '', title)
        
        # 3. 여러 공백을 하나의 하이픈으로
        title_slug = re.sub(r'\s+', '-', title_slug.strip())
        
        # 4. 여러 하이픈을 하나로
        title_slug = re.sub(r'-+', '-', title_slug)
        
        # 5. 앞뒤 하이픈 제거
        title_slug = title_slug.strip('-').lower()
        
        # slug가 비어있거나 너무 짧으면 대체 slug 생성
        if not title_slug or len(title_slug) < 5:
            # 카테고리 + 타임스탬프 기반 slug
            category = article.get('category', 'ai')
            timestamp = datetime.now().strftime('%H%M%S')
            title_slug = f"{category}-article-{timestamp}"
        
        # 너무 길면 자르기 (최대 50자)
        title_slug = title_slug[:50].rstrip('-')
        
        filename = f"{today}-{title_slug}.md"
        filepath = os.path.join(contents_dir, filename)
        
        # Front Matter 생성
        front_matter = f"""---
title: "{article['title']}"
date: {article.get('created_at', datetime.now().strftime('%Y-%m-%d %H:%M'))}
category: ai
source: "AI/테크"
summary: "{article.get('summary', '')[:200]}"
image: {article.get('image', '')}
tags: [AI, 자동화, 생산성]
type: ai_generated
---

"""
        
        # Markdown 내용
        content = article.get('content', '')
        
        # 파일 저장
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(front_matter)
                f.write(content)
            
            print(f"  ✅ Markdown 파일 저장: {filename}")
            
            # 링크 업데이트
            article['link'] = f"/article.html?slug={today}-{title_slug}"
            
        except Exception as e:
            print(f"  ⚠️ Markdown 저장 실패: {e}")
            article['link'] = "#"
    
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
    
    def load_existing_articles(self, data_file='data.json') -> List[Dict]:
        """기존 data.json에서 기사 로드"""
        try:
            if os.path.exists(data_file):
                with open(data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('articles', [])
        except Exception as e:
            print(f"  ⚠️ 기존 데이터 로드 실패: {e}")
        return []
    
    def archive_old_articles(self, articles: List[Dict], threshold: int = 50):
        """
        오래된 글을 아카이브 파일로 이동
        
        Args:
            articles: 전체 기사 목록
            threshold: 메인 페이지 최대 기사 수
        
        Returns:
            (메인 기사 목록, 아카이브된 기사 수)
        """
        if len(articles) <= threshold:
            return articles, 0
        
        # 메인: 최신 50개
        main_articles = articles[:threshold]
        
        # 아카이브: 51번째부터
        archive_articles = articles[threshold:]
        
        # 아카이브 파일 로드 (기존 아카이브 + 새 아카이브)
        archive_path = 'archive.json'
        existing_archive = []
        
        try:
            if os.path.exists(archive_path):
                with open(archive_path, 'r', encoding='utf-8') as f:
                    archive_data = json.load(f)
                    existing_archive = archive_data.get('articles', [])
        except Exception as e:
            print(f"  ⚠️ 아카이브 로드 실패: {e}")
        
        # 중복 제거하고 아카이브에 추가
        archive_titles = {a['title'] for a in existing_archive}
        new_archived = 0
        
        for article in archive_articles:
            if article['title'] not in archive_titles:
                existing_archive.insert(0, article)  # 최신 순 유지
                new_archived += 1
        
        # 아카이브 파일 저장
        if new_archived > 0 or not os.path.exists(archive_path):
            archive_data = {
                'updatedAt': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'totalArticles': len(existing_archive),
                'articles': existing_archive
            }
            
            with open(archive_path, 'w', encoding='utf-8') as f:
                json.dump(archive_data, f, ensure_ascii=False, indent=2)
            
            print(f"📦 아카이브: {new_archived}개 새로 추가, 총 {len(existing_archive)}개 보관")
        
        return main_articles, len(archive_articles)
    
    def create_data_json(self, articles: List[Dict], max_articles: int = 50) -> Dict:
        """
        data.json 형식으로 변환 (아카이브 시스템 포함)
        
        Args:
            articles: 새로 추가할 기사 목록
            max_articles: 메인 페이지 최대 기사 수 (기본 50개)
        
        Notes:
            - 메인: 최신 50개 (빠른 로딩)
            - 아카이브: 51개부터 모두 보관 (archive.json)
            - 모든 글 영구 보존
        """
        # 1. 기존 기사 로드
        existing = self.load_existing_articles()
        print(f"\n📚 기존 메인 기사: {len(existing)}개")
        
        # 2. 새 기사 추가 (중복 제거)
        existing_titles = {article['title'] for article in existing}
        new_count = 0
        
        for article in articles:
            if article['title'] not in existing_titles:
                existing.insert(0, article)  # 최신 글을 맨 앞에 추가
                new_count += 1
        
        print(f"➕ 신규 기사: {new_count}개 추가")
        
        # 3. 아카이브 처리 (50개 초과 시)
        main_articles, archived_count = self.archive_old_articles(existing, max_articles)
        
        if archived_count > 0:
            print(f"📦 아카이브로 이동: {archived_count}개")
        
        print(f"📊 메인 페이지: {len(main_articles)}개 (로딩 최적화)")
        
        return {
            'updatedAt': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'totalArticles': len(main_articles),
            'hasArchive': archived_count > 0,
            'articles': main_articles
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
