import json
import time
import sys
import os
from typing import Optional

# Thêm đường dẫn để chạy độc lập
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.config import env_config, app_config
    from src.storage import get_unprocessed_articles, save_draft
    from src.utils.logger import logger
except ImportError:
    from config import env_config, app_config
    from storage import get_unprocessed_articles, save_draft
    from utils.logger import logger

def generate_draft(article: dict) -> Optional[str]:
    """Gửi bài viết thô cho AI (Gemini hoặc Local LLM) để lấy caption dạng JSON."""
    if not app_config:
        logger.error("Configuration is missing.")
        return None
        
    provider = app_config.ai_settings.provider
    model_name = app_config.ai_settings.model
    temperature = app_config.ai_settings.temperature
    style = app_config.ai_settings.style

    prompt = f"""Bạn là một Admin Fanpage Facebook chuyên nghiệp, hài hước và bắt trend.
Dưới đây là một bài báo/tin tức thô:
---
Tiêu đề: {article.get('title', '')}
Nội dung: {article.get('raw_content', '')}
Nguồn: {article.get('original_url', '')}
---
Hãy viết lại nội dung trên thành một bài đăng Facebook Fanpage với các tiêu chí sau:
1. Văn phong: {style}. Đọc cuốn hút, tấu hài nhưng không phản cảm.
2. Không bịa đặt thông tin sai lệch so với bài gốc. Tóm tắt ngắn gọn ý chính.
3. Chèn emoji phù hợp để làm sinh động bài viết.
4. Thêm 3-5 hashtag liên quan ở cuối bài.
5. Luôn giữ lại link nguồn để trích dẫn.

Yêu cầu định dạng đầu ra: Hãy trả về định dạng JSON thuần túy (không bọc trong markdown code block) với cấu trúc sau:
{{
  "caption_variant_1": "Nội dung bài viết...",
  "caption_variant_2": "Nội dung bài viết cách diễn đạt khác...",
  "hashtags": "#tag1 #tag2"
}}"""

    try:
        logger.info(f"Sending prompt to {provider} ({model_name}) for article ID: {article['id']}")
        raw_text = ""
        
        if provider == "gemini":
            if not env_config.gemini_api_key:
                logger.error("GEMINI_API_KEY is missing. Cannot use Gemini.")
                return None
                
            from google import genai
            from google.genai import types
            
            client = genai.Client(api_key=env_config.gemini_api_key)
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=temperature
                )
            )
            raw_text = response.text
            
        elif provider == "local_llm":
            from openai import OpenAI
            base_url = app_config.ai_settings.base_url
            if not base_url:
                logger.error("Local LLM Base URL is missing in settings.")
                return None
                
            # Local endpoints like Ollama don't usually require an API key, but OpenAI SDK expects one
            client = OpenAI(base_url=base_url, api_key="sk-local-llm")
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that always responds in valid JSON format. Do not use markdown blocks."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature
            )
            raw_text = response.choices[0].message.content
        else:
            logger.error(f"Unsupported AI provider: {provider}")
            return None

        # Clean markdown if Local LLM returned ```json ... ```
        raw_text = raw_text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        elif raw_text.startswith("```"):
            raw_text = raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]

        # Parse JSON
        parsed_json = json.loads(raw_text.strip())
        return json.dumps(parsed_json, ensure_ascii=False)
        
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON from AI for article {article['id']}: {e}. Raw response: {raw_text}")
        return None
    except Exception as e:
        error_msg = str(e).lower()
        if '429' in error_msg or 'quota' in error_msg or 'rate limit' in error_msg:
            logger.error("Rate Limit (429) hit. Applying exponential backoff.")
            time.sleep(10)
        elif 'timeout' in error_msg or 'connection' in error_msg:
            logger.error(f"AI API Timeout or Connection Error for article {article['id']}: {e}")
        else:
            logger.error(f"Unexpected AI API error for article {article['id']}: {e}")
        return None

def process_pending_articles():
    """Lấy bài viết mới và sinh bản nháp."""
    articles = get_unprocessed_articles(limit=5)
    if not articles:
        logger.info("No unprocessed articles found for AI Engine.")
        return
        
    for article in articles:
        ai_content = generate_draft(article)
        if ai_content:
            draft_id = save_draft(article['id'], ai_content, status='pending')
            if draft_id:
                logger.info(f"Successfully generated and saved draft for article ID: {article['id']} (Draft ID: {draft_id})")
        else:
            logger.warning(f"Failed to generate draft for article ID: {article['id']}")
            
        time.sleep(2)

if __name__ == "__main__":
    logger.info("Starting AI Engine Test Run...")
    process_pending_articles()
    logger.info("AI Engine Test Run Completed.")
