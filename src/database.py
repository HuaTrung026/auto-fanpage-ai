import sqlite3
import os
import logging
from typing import Optional

# Setup basic log if run independently
logger = logging.getLogger("auto_fanpage")
if not logger.hasHandlers():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Database:
    def __init__(self, db_path: str = "data/database.sqlite"):
        self.db_path = db_path
        self._ensure_dir()
        self.conn: Optional[sqlite3.Connection] = None

    def _ensure_dir(self):
        """Đảm bảo thư mục chứa file db tồn tại."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def connect(self):
        """Kết nối tới SQLite DB."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # Trả về row như dictionary
            logger.info(f"Connected to database at {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Error connecting to database: {e}")
            raise

    def close(self):
        """Đóng kết nối cơ sở dữ liệu."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed.")

    def init_schema(self):
        """Tạo lược đồ CSDL lần đầu nếu chưa có."""
        if not self.conn:
            self.connect()
        
        schema = """
        -- Bảng sources (Nguồn cấp dữ liệu)
        CREATE TABLE IF NOT EXISTS sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            url TEXT NOT NULL,
            type TEXT NOT NULL DEFAULT 'rss',
            is_active BOOLEAN NOT NULL DEFAULT 1,
            last_fetched_at DATETIME
        );

        -- Bảng articles (Bài viết thô)
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id INTEGER NOT NULL,
            original_url TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            raw_content TEXT,
            published_at DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (source_id) REFERENCES sources (id)
        );

        -- Bảng post_drafts (Bản nháp AI tạo ra)
        CREATE TABLE IF NOT EXISTS post_drafts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article_id INTEGER NOT NULL,
            gemini_content TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending', -- pending/approved/rejected/posted
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            scheduled_for DATETIME,
            FOREIGN KEY (article_id) REFERENCES articles (id)
        );

        -- Bảng post_history (Lịch sử đăng bài)
        CREATE TABLE IF NOT EXISTS post_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            draft_id INTEGER NOT NULL,
            fb_post_id TEXT,
            posted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            status_code INTEGER,
            response_log TEXT,
            FOREIGN KEY (draft_id) REFERENCES post_drafts (id)
        );
        """
        try:
            self.conn.executescript(schema)
            self.conn.commit()
            logger.info("Database schema initialized successfully.")
        except sqlite3.Error as e:
            logger.error(f"Error initializing schema: {e}")
            self.conn.rollback()
            raise

def get_connection(db_path: str = None) -> sqlite3.Connection:
    """Helper để lấy connection nhanh từ bên ngoài."""
    if db_path is None:
        try:
            from config import env_config
            db_path = env_config.db_path
        except ImportError:
            db_path = "data/database.sqlite"
    db = Database(db_path)
    db.connect()
    return db.conn

if __name__ == "__main__":
    # Test/Khởi tạo database khi chạy trực tiếp file script này
    try:
        from config import env_config
        db_path = env_config.db_path
    except ImportError:
        # Nếu chạy không có module config, dùng path mặc định
        db_path = "data/database.sqlite"
        
    db = Database(db_path)
    db.init_schema()
    db.close()
    print(f"Database setup complete at {db_path}")
