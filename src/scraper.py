import time
import requests
import feedparser
import logging
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import html
import sys
import os

# Thêm đường dẫn để chạy độc lập dễ dàng
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.config import app_config
    from src.storage import get_or_create_source, is_article_exists, save_raw_article
    from src.utils.logger import logger
except ImportError:
    from config import app_config
    from storage import get_or_create_source, is_article_exists, save_raw_article
    from utils.logger import logger

HEADERS = {'User-Agent': 'AutoFanpage-Bot/1.0'}
TIMEOUT = 10

def clean_html(raw_html: str) -> str:
    """Dùng BeautifulSoup loại bỏ thẻ HTML rác và trả về text thuần."""
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    # Lấy text thuần túy
    text = soup.get_text(separator=' ', strip=True)
    # Xử lý các entity HTML (VD: &amp; -> &)
    return html.unescape(text)

def fetch_rss(url: str) -> List[Dict[str, Any]]:
    """Tải và parse RSS feed từ URL."""
    logger.info(f"Fetching RSS: {url}")
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()
        
        feed = feedparser.parse(response.content)
        articles = []
        for entry in feed.entries:
            title = entry.get('title', '')
            link = entry.get('link', '')
            
            # Ưu tiên lấy content đầy đủ, nếu không có lấy summary
            content = ''
            if 'content' in entry and len(entry.content) > 0:
                content = entry.content[0].value
            elif 'summary' in entry:
                content = entry.summary
            elif 'description' in entry:
                content = entry.description
            
            published = entry.get('published', '') or entry.get('updated', '')
            
            articles.append({
                'title': title,
                'link': link,
                'raw_content': clean_html(content),
                'published_at': published
            })
        return articles
    except requests.RequestException as e:
        logger.error(f"HTTP Error fetching {url}: {e}")
        return []
    except Exception as e:
        logger.error(f"Error parsing RSS {url}: {e}")
        return []

def run_scraper():
    """Load danh sách RSS từ config, duyệt từng link, cào bài và lưu DB."""
    if not app_config or not app_config.sources.rss:
        logger.warning("No RSS sources found in config.")
        return

    for source in app_config.sources.rss:
        name = source.name
        url = source.url
        
        logger.info(f"Processing source: {name} ({url})")
        
        # 1. Lấy hoặc tạo source_id
        source_id = get_or_create_source(name, url, 'rss')
        
        # 2. Cào bài viết
        articles = fetch_rss(url)
        new_count = 0
        
        for article in articles:
            link = article['link']
            
            # 3. Check xem URL bài viết đã tồn tại chưa
            if is_article_exists(link):
                continue
                
            # 4. Lưu bài mới
            saved_id = save_raw_article(
                source_id=source_id,
                original_url=link,
                title=article['title'],
                raw_content=article['raw_content'],
                published_at=article['published_at']
            )
            
            if saved_id:
                new_count += 1
                logger.info(f"Saved new article: {article['title']}")
                
        logger.info(f"Finished {name}. Saved {new_count} new articles.")
        
        # 5. DOS prevention - time.sleep(2)
        logger.info("Sleeping for 2 seconds to prevent DOS...")
        time.sleep(2)

if __name__ == "__main__":
    logger.info("Starting Scraper Test Run...")
    run_scraper()
    logger.info("Scraper Test Run Completed.")
