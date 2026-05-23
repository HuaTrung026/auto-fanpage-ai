import sqlite3
import logging
from typing import Optional
from database import get_connection

logger = logging.getLogger("auto_fanpage")

def get_or_create_source(name: str, url: str, type_src: str = 'rss') -> int:
    """Lấy ID nguồn tin, chưa có thì insert mới."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM sources WHERE url = ?", (url,))
        row = cursor.fetchone()
        if row:
            return row['id']
        
        cursor.execute(
            "INSERT INTO sources (name, url, type) VALUES (?, ?, ?)",
            (name, url, type_src)
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        logger.error(f"Error in get_or_create_source: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def is_article_exists(url: str) -> bool:
    """Check xem URL bài viết đã tồn tại trong bảng articles chưa."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM articles WHERE original_url = ?", (url,))
        row = cursor.fetchone()
        return bool(row)
    except sqlite3.Error as e:
        logger.error(f"Error checking if article exists: {e}")
        return False
    finally:
        conn.close()

def save_raw_article(source_id: int, original_url: str, title: str, raw_content: str, published_at: str) -> Optional[int]:
    """Lưu bài viết thô vào database. Bắt lỗi IntegrityError nếu trùng khóa."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO articles (source_id, original_url, title, raw_content, published_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (source_id, original_url, title, raw_content, published_at)
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        logger.warning(f"Article already exists (IntegrityError): {original_url}")
        conn.rollback()
        return None
    except sqlite3.Error as e:
        logger.error(f"Error saving raw article: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()

def get_unprocessed_articles(limit: int = 10) -> list:
    """Lấy danh sách các bài viết chưa được tạo bản nháp."""
    conn = get_connection()
    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT a.id, a.title, a.raw_content, a.original_url
            FROM articles a
            LEFT JOIN post_drafts p ON a.id = p.article_id
            WHERE p.id IS NULL
            ORDER BY a.created_at ASC
            LIMIT ?
            """,
            (limit,)
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as e:
        logger.error(f"Error fetching unprocessed articles: {e}")
        return []
    finally:
        conn.close()

def save_draft(article_id: int, gemini_content: str, status: str = 'pending') -> Optional[int]:
    """Lưu bản nháp do AI tạo ra vào CSDL."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO post_drafts (article_id, gemini_content, status)
            VALUES (?, ?, ?)
            """,
            (article_id, gemini_content, status)
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        logger.error(f"Error saving post draft: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()

def get_pending_drafts() -> list:
    """Truy vấn các bản nháp đang chờ duyệt."""
    conn = get_connection()
    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT p.id as draft_id, a.title, a.original_url, p.gemini_content
            FROM post_drafts p
            JOIN articles a ON p.article_id = a.id
            WHERE p.status = 'pending'
            ORDER BY p.created_at ASC
            """
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as e:
        logger.error(f"Error fetching pending drafts: {e}")
        return []
    finally:
        conn.close()

def update_draft_status(draft_id: int, status: str) -> bool:
    """Cập nhật trạng thái của bản nháp."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE post_drafts SET status = ? WHERE id = ?",
            (status, draft_id)
        )
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        logger.error(f"Error updating draft status: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def get_next_approved_draft() -> Optional[dict]:
    """Lấy 1 bản ghi cũ nhất đã được approve để chuẩn bị đăng."""
    conn = get_connection()
    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT p.id as draft_id, a.original_url, p.gemini_content
            FROM post_drafts p
            JOIN articles a ON p.article_id = a.id
            WHERE p.status = 'approved'
            ORDER BY p.created_at ASC
            LIMIT 1
            """
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    except sqlite3.Error as e:
        logger.error(f"Error fetching approved draft: {e}")
        return None
    finally:
        conn.close()

def save_post_history(draft_id: int, fb_post_id: Optional[str], status_code: Optional[int], response_log: str):
    """Lưu lịch sử đăng bài vào bảng post_history."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO post_history (draft_id, fb_post_id, status_code, response_log)
            VALUES (?, ?, ?, ?)
            """,
            (draft_id, fb_post_id, status_code, response_log)
        )
        conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Error saving post history: {e}")
        conn.rollback()
    finally:
        conn.close()
