import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger(name: str = "auto_fanpage", log_file: str = "logs/app.log", level: str = "INFO") -> logging.Logger:
    """
    Tạo và cấu hình logger với RotatingFileHandler và StreamHandler.
    """
    logger = logging.getLogger(name)
    
    # Tránh duplicate logs nếu hàm được gọi nhiều lần
    if logger.hasHandlers():
        return logger

    # Parse logging level string
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(numeric_level)

    # Định dạng log: Thời gian - Tên module - Mức độ log - Thông báo
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Đảm bảo thư mục logs tồn tại
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # File handler: tối đa 5MB mỗi file, giữ tối đa 3 file backup, hỗ trợ utf-8
    file_handler = RotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler: hiển thị log trên terminal
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

# Export một instance logger toàn cục để dùng chung
logger = setup_logger()
