#!/usr/bin/env python3
"""
블로그 자동화 스크립트
- RSS 피드에서 뉴스 수집
- AI로 자동 요약
- data.json 자동 업데이트
"""

import feedparser
import json
import os
from datetime import datetime
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
import time


class NewsAutomation:
    def __init__(self, config_path="config.json"):
        """설정 파일 로드"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.openai_api_key = os.getenv('OPENAI_API_KEY', self.config.get('openai_api_key', ''))
        
    def fetch_rss_feeds(self) -> List[Dict]:
        """RSS 피드에서 뉴스 수집"""
        articles = []
        
        for feed_info in self.config['rss_feeds']:
            print(f"📡 {feed_info['name']} 피드 수집 중...")
            
            try:
                feed = feedparser.parse(feed_info['url'])
                
                for entry in feed.entries[:feed_info.get('max_items', 3)]:
                    article = {
                        'title': entry.get('title', '제목 없음'),
                        'source': feed_info['name'],
                        'link': entry.get('link', '#'),
                        'published': entry.get('published', ''),
                        'summary': entry.get('summary', entry.get('description', '')),
                        'image': self._extract_image(entry)
                    }
                    articles.append(article)
                    
                print(f"  ✅ {len(feed.entries[:feed_info.get('max_items', 3)])}개 기사 수집 완료")
                
            except Exception as e:
                print(f"  ❌ 오류 발생: {e}")
                
        return articles
    
    def _extract_image(self, entry) -> str:
        """RSS 엔트리에서 이미지 URL 추출"""
        # 1. media:content 태그에서 찾기
        if hasattr(entry, 'media_content'):
            for media in entry.media_content:
                if 'url' in media:
                    return media['url']
        
        # 2. enclosures에서 찾기
        if hasattr(entry, 'enclosures'):
            for enc in entry.enclosures:
                if enc.get('type', '').startswith('image/'):
                    return enc.get('href', '')
        
        # 3. summary에서 img 태그 찾기
        if hasattr(entry, 'summary'):
            soup = BeautifulSoup(entry.summary, 'html.parser')
            img = soup.find('img')
            if img and img.get('src'):
                return img['src']
        
        # 4. 기본 이미지 (Unsplash random)
        return "https://images.unsplash.com/photo-1504711434969-e33886168f5c?auto=format&fit=crop&w=800&q=80"
    
    def summarize_with_ai(self, article: Dict) -> Dict:
        """AI로 기사 요약 (OpenAI API 사용)"""
        if not self.openai_api_key:
            print("  ⚠️ OpenAI API 키가 없어 원본 요약 사용")
            article['summary'] = self._clean_html(article['summary'])[:200] + "..."
            return article
        
        try:
            # HTML 태그 제거
            clean_summary = self._clean_html(article['summary'])
            
            # API 요청
            headers = {
                'Authorization': f'Bearer {self.openai_api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'gpt-3.5-turbo',
                'messages': [
                    {'role': 'system', 'content': '당신은 뉴스 기사를 간결하고 명확하게 요약하는 전문가입니다. 2-3문장으로 핵심만 요약해주세요.'},
                    {'role': 'user', 'content': f"다음 기사를 요약해주세요:\n\n제목: {article['title']}\n\n내용: {clean_summary[:1000]}"}
                ],
                'max_tokens': 150,
                'temperature': 0.7
            }
            
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                article['summary'] = result['choices'][0]['message']['content'].strip()
                print(f"  🤖 AI 요약 완료: {article['title'][:30]}...")
            else:
                print(f"  ⚠️ API 오류 (상태 코드: {response.status_code}), 원본 사용")
                article['summary'] = clean_summary[:200] + "..."
                
        except Exception as e:
            print(f"  ❌ AI 요약 실패: {e}, 원본 사용")
            article['summary'] = self._clean_html(article['summary'])[:200] + "..."
        
        return article
    
    def _clean_html(self, text: str) -> str:
        """HTML 태그 제거"""
        soup = BeautifulSoup(text, 'html.parser')
        return soup.get_text(strip=True)
    
    def calculate_time_ago(self, published_str: str) -> str:
        """게시 시간을 '몇 시간 전' 형식으로 변환"""
        try:
            from dateutil import parser
            pub_date = parser.parse(published_str)
            now = datetime.now(pub_date.tzinfo)
            diff = now - pub_date
            
            if diff.days > 0:
                return f"{diff.days}일 전"
            elif diff.seconds >= 3600:
                return f"{diff.seconds // 3600}시간 전"
            elif diff.seconds >= 60:
                return f"{diff.seconds // 60}분 전"
            else:
                return "방금 전"
        except:
            return "최근"
    
    def generate_data_json(self, articles: List[Dict]) -> Dict:
        """data.json 형식으로 변환"""
        processed_articles = []
        
        for article in articles[:self.config.get('max_articles', 20)]:
            # AI 요약 적용
            if self.config.get('use_ai_summary', False):
                article = self.summarize_with_ai(article)
                time.sleep(1)  # API 요청 간격
            else:
                article['summary'] = self._clean_html(article['summary'])[:200] + "..."
            
            processed_articles.append({
                'title': article['title'],
                'source': article['source'],
                'time': self.calculate_time_ago(article.get('published', '')),
                'summary': article['summary'],
                'link': article['link'],
                'image': article['image']
            })
        
        return {
            'updatedAt': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'articles': processed_articles
        }
    
    def save_data_json(self, data: Dict, output_path='data.json'):
        """data.json 저장"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n✅ {output_path} 저장 완료! ({len(data['articles'])}개 기사)")
    
    def run(self):
        """전체 자동화 프로세스 실행"""
        print("=" * 50)
        print("🚀 블로그 자동화 시작")
        print("=" * 50)
        
        # 1. RSS 피드 수집
        print("\n[1단계] RSS 피드 수집")
        articles = self.fetch_rss_feeds()
        
        if not articles:
            print("❌ 수집된 기사가 없습니다.")
            return
        
        print(f"\n총 {len(articles)}개 기사 수집됨")
        
        # 2. 데이터 가공 & AI 요약
        print("\n[2단계] 데이터 가공 및 AI 요약")
        data = self.generate_data_json(articles)
        
        # 3. data.json 저장
        print("\n[3단계] 파일 저장")
        self.save_data_json(data)
        
        print("\n" + "=" * 50)
        print("🎉 자동화 완료!")
        print("=" * 50)


def main():
    """메인 실행 함수"""
    automation = NewsAutomation()
    automation.run()


if __name__ == "__main__":
    main()
