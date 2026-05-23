# 🤖 Auto-Fanpage AI Assistant

Hệ thống quản trị và tự động hóa Fanpage Facebook (End-to-End) ứng dụng Trí tuệ nhân tạo.
Project kết hợp **FastAPI**, **APScheduler**, **Google Gemini** (hoặc **Local LLMs**) để tự động thu thập tin tức, sinh bài đăng và đăng bài lên Facebook.

## 🌟 Tính Năng Nổi Bật
- **Cào Tin Tự Động (Scraping)**: Theo dõi các nguồn RSS và tự động lấy tin tức nóng hổi định kỳ.
- **AI Đa Nền Tảng (Multi-Provider AI)**: Xào nấu nội dung cực đỉnh với **Google Gemini**, hoặc kết nối không giới hạn với các **Local LLM** (Ollama, LM Studio) hoàn toàn miễn phí qua chuẩn giao tiếp tương thích.
- **Glassmorphism Web Dashboard**: Giao diện quản lý cực đẹp mắt, cho phép bạn vào vai "Sếp" duyệt bài chỉ bằng một cú click. Có xác thực bảo mật Session-based Auth.
- **Auto Post & Anti-Ban**: Tự động đăng bài theo "Giờ vàng" kèm thuật toán Jitter (độ trễ ngẫu nhiên) giúp chống bị Facebook nhận diện bot.
- **Quản lý linh hoạt**: Giao diện cho phép thêm/xóa nguồn báo (RSS) và thay đổi "Thần chú Văn phong" (System Prompts) nhanh chóng mà không cần đụng đến Code.

## 🚀 Cài Đặt Nhanh

**1. Clone kho lưu trữ & cài đặt môi trường:**
```bash
git clone https://github.com/your-username/auto-fanpage-ai.git
cd auto-fanpage-ai
python -m venv .venv
# Kích hoạt môi trường ảo:
# Windows: .venv\Scripts\activate
# Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

**2. Cấu hình bảo mật:**
Tạo file `.env` từ file mẫu:
```bash
cp .env.example .env
```
Điền `GEMINI_API_KEY` và `FB_PAGE_TOKEN` vào file `.env`. (Xem chi tiết cách lấy key tại `INSTRUCTIONS.md`).

**3. Khởi động hệ thống:**
```bash
python src/main.py
```
Mở trình duyệt: `http://localhost:8000` (User: `admin` / Pass: `admin123`).

## 📚 Tài Liệu Kèm Theo
- [**INSTRUCTIONS.md**](INSTRUCTIONS.md): Sổ tay hướng dẫn sử dụng và cách cấu hình chi tiết (Dành cho Người Dùng Cuối).
- [**ARCHITECTURE.md**](ARCHITECTURE.md): Bản vẽ kiến trúc hệ thống, Database Schema và kỹ thuật luồng dữ liệu (Dành cho Developer).

## 📝 Giấy Phép (License)
Dự án được xây dựng phục vụ mục đích cá nhân và phi thương mại.
