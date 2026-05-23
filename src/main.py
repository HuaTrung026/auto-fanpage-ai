import os
import sys
import uvicorn
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

# Add root directory to path to allow clean imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.logger import logger
from src.config import app_config
from src.scraper import run_scraper
from src.ai import process_pending_articles
from src.poster import run_poster

def job_crawl_and_ai():
    """Job 1: Cào tin tức mới và sử dụng AI để sinh bản nháp."""
    logger.info("=== BẮT ĐẦU JOB: CRAWL & AI ===")
    try:
        run_scraper()
        process_pending_articles()
    except Exception as e:
        logger.error(f"Lỗi trong quá trình chạy Crawl & AI: {e}")
    logger.info("=== KẾT THÚC JOB: CRAWL & AI ===")

def job_auto_post():
    """Job 2: Đăng các bản nháp đã được duyệt lên Fanpage."""
    logger.info("=== BẮT ĐẦU JOB: AUTO POST ===")
    try:
        run_poster()
    except Exception as e:
        logger.error(f"Lỗi trong quá trình Auto Post: {e}")
    logger.info("=== KẾT THÚC JOB: AUTO POST ===")

def start_scheduler():
    if not app_config:
        return None
        
    scheduler = BackgroundScheduler()

    scheduler.add_job(job_crawl_and_ai, 'interval', hours=2, id='job_crawl_and_ai')
    logger.info("✅ Đã lên lịch Job 1: Thu thập & Sinh nháp (mỗi 2 giờ).")

    time_slots = app_config.facebook.posting_schedule.time_slots
    jitter_minutes = app_config.facebook.posting_schedule.jitter_minutes
    jitter_seconds = jitter_minutes * 60

    for slot in time_slots:
        try:
            hour, minute = slot.split(':')
            trigger = CronTrigger(hour=int(hour), minute=int(minute), jitter=jitter_seconds)
            scheduler.add_job(job_auto_post, trigger, id=f'job_auto_post_{hour}_{minute}')
            logger.info(f"✅ Đã lên lịch Job 2: Auto Post lúc {slot} (Jitter ngẫu nhiên: {jitter_minutes} phút).")
        except ValueError:
            logger.error(f"Khung giờ cấu hình không hợp lệ: {slot}.")

    scheduler.start()
    return scheduler

def main():
    logger.info("🚀 Khởi động hệ thống Auto-Fanpage AI Assistant...")
    
    if not app_config:
        logger.error("Không thể tải cấu hình từ settings.yaml. Hệ thống dừng hoạt động.")
        return

    # Khởi chạy Scheduler ở chế độ Background (chạy ngầm, không block)
    scheduler = start_scheduler()
    
    # Khởi chạy Web Server bằng Uvicorn trên luồng chính
    logger.info("🌐 Bắt đầu khởi chạy Web Dashboard tại http://localhost:8000")
    try:
        uvicorn.run("src.web.app:app", host="0.0.0.0", port=8000, reload=False, log_level="warning")
    except (KeyboardInterrupt, SystemExit):
        logger.info("🛑 Nhận tín hiệu dừng từ người dùng. Đang tắt hệ thống...")
    finally:
        if scheduler:
            scheduler.shutdown(wait=False)
        logger.info("👋 Hệ thống đã dừng hoàn toàn.")

if __name__ == "__main__":
    main()
