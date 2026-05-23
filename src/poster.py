import os
import sys
import json
import requests
from typing import Tuple, Optional

# Add path to allow standalone execution
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.config import env_config, app_config
    from src.storage import get_next_approved_draft, save_post_history, update_draft_status
    from src.utils.logger import logger
except ImportError:
    from config import env_config, app_config
    from storage import get_next_approved_draft, save_post_history, update_draft_status
    from utils.logger import logger

def post_to_facebook(message: str, link: str) -> Tuple[Optional[str], Optional[int], str]:
    """Gọi HTTP POST đến Facebook Graph API để đăng bài."""
    if not app_config:
        return None, None, "App Config not loaded."
        
    page_id = app_config.facebook.page_id
    fb_page_token = env_config.fb_page_token
    
    if not fb_page_token or fb_page_token == "your_facebook_page_token_here":
        logger.error("Facebook Page Token is missing or invalid in .env")
        return None, None, "Invalid Facebook Page Token"
        
    url = f"https://graph.facebook.com/v19.0/{page_id}/feed"
    payload = {
        "message": message,
        "link": link,
        "access_token": fb_page_token
    }
    
    logger.info(f"Posting to Facebook Page ID: {page_id}")
    try:
        response = requests.post(url, data=payload, timeout=15)
        status_code = response.status_code
        response_text = response.text
        
        if status_code == 200:
            res_json = response.json()
            fb_post_id = res_json.get("id")
            logger.info(f"Successfully posted to Facebook. Post ID: {fb_post_id}")
            return fb_post_id, status_code, response_text
        else:
            logger.error(f"Facebook API Error ({status_code}): {response_text}")
            return None, status_code, response_text
            
    except requests.RequestException as e:
        logger.error(f"HTTP Error during Facebook POST: {e}")
        return None, None, str(e)

def run_poster():
    """Lấy bản nháp đã duyệt cũ nhất và đăng lên Fanpage."""
    logger.info("Checking for approved drafts to post...")
    draft = get_next_approved_draft()
    
    if not draft:
        logger.info("No approved drafts waiting to be posted.")
        return
        
    draft_id = draft['draft_id']
    original_url = draft['original_url']
    raw_json = draft['gemini_content']
    
    try:
        content = json.loads(raw_json)
        # Ưu tiên lấy variant 1, nếu không có thì lấy string rỗng
        caption = content.get("caption_variant_1", "")
        hashtags = content.get("hashtags", "")
        
        if not caption:
            logger.warning(f"Draft ID {draft_id} missing caption_variant_1. Attempting variant_2.")
            caption = content.get("caption_variant_2", "Nội dung bài viết đang được cập nhật.")
            
        message = f"{caption}\n\n{hashtags}".strip()
        
    except json.JSONDecodeError:
        logger.error(f"Failed to parse JSON for Draft ID {draft_id}. Raw: {raw_json}")
        # Nếu không parse được, chuyển trạng thái sang failed để không bị lặp lại mãi khi chạy cron
        update_draft_status(draft_id, 'failed')
        return

    logger.info(f"Attempting to post Draft ID {draft_id}...")
    fb_post_id, status_code, response_text = post_to_facebook(message=message, link=original_url)
    
    # Lưu vào lịch sử post
    save_post_history(
        draft_id=draft_id,
        fb_post_id=fb_post_id,
        status_code=status_code,
        response_log=response_text
    )
    
    # Cập nhật status của draft
    if status_code == 200 and fb_post_id:
        update_draft_status(draft_id, 'posted')
        logger.info(f"Draft ID {draft_id} marked as 'posted'.")
    else:
        update_draft_status(draft_id, 'failed')
        logger.error(f"Draft ID {draft_id} marked as 'failed' due to API error.")

if __name__ == "__main__":
    logger.info("Starting Poster Test Run...")
    run_poster()
    logger.info("Poster Test Run Completed.")
