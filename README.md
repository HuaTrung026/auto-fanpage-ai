# 🤖 Auto-Fanpage AI Assistant

[![English](https://img.shields.io/badge/Language-English-blue)](#english) [![Tiếng Việt](https://img.shields.io/badge/Language-Tiếng%20Việt-red)](#tiếng-việt)

---

## 🇬🇧 English

### Overview
**Auto-Fanpage AI Assistant** is an end-to-end, AI-powered system designed to automate Facebook Fanpage management. 
By integrating **FastAPI**, **APScheduler**, and **Google Gemini** (or compatible **Local LLMs**), the system autonomously aggregates news, generates engaging content, and schedules posts to your Facebook page.

### 🌟 Key Features
- **Automated News Scraping**: Continuously monitors RSS feeds to fetch the latest breaking news and relevant articles.
- **Multi-Provider AI Engine**: Leverages **Google Gemini** for high-quality content generation or connects seamlessly to **Local LLMs** (e.g., Ollama, LM Studio) for a cost-effective, self-hosted alternative.
- **Glassmorphism Web Dashboard**: Features a modern, aesthetically pleasing management interface with session-based authentication, allowing administrators to review and approve AI-generated posts effortlessly.
- **Smart Scheduling & Anti-Ban**: Implements a randomized "jitter" algorithm within configured timeframes to simulate human posting behavior and prevent Facebook API restrictions.
- **Dynamic Configuration**: Easily manage RSS sources and adjust AI System Prompts via the UI without any code modifications.

### 🚀 Quick Start

**1. Clone the repository & set up the environment:**
```bash
git clone https://github.com/HuaTrung026/auto-fanpage-ai.git
cd auto-fanpage-ai
python -m venv .venv

# Activate the virtual environment:
# Windows: .venv\Scripts\activate
# Mac/Linux: source .venv/bin/activate

pip install -r requirements.txt
```

**2. Security Configuration:**
Create an `.env` file from the provided template:
```bash
cp .env.example .env
```
Populate the `GEMINI_API_KEY` and `FB_PAGE_TOKEN` variables in the `.env` file. (Refer to `INSTRUCTIONS.md` for detailed steps on acquiring these credentials).

**3. Launch the System:**
```bash
python src/main.py
```
Access the dashboard via your browser: `http://localhost:8000` (Default Credentials - User: `admin` / Password: `admin123`).

### 📚 Documentation
- [**INSTRUCTIONS.md**](INSTRUCTIONS.md): Comprehensive user manual and configuration guide (For End Users).
- [**ARCHITECTURE.md**](ARCHITECTURE.md): System architecture, database schema, and data flow documentation (For Developers).

### 📝 License
This project is developed for personal and non-commercial use.

---

## 🇻🇳 Tiếng Việt

### Tổng Quan
**Auto-Fanpage AI Assistant** là hệ thống quản trị và tự động hóa Fanpage Facebook (End-to-End) ứng dụng Trí tuệ nhân tạo.
Dự án kết hợp **FastAPI**, **APScheduler**, và **Google Gemini** (hoặc các **Local LLMs**) nhằm tự động hóa quy trình thu thập tin tức, sáng tạo nội dung và đăng tải lên nền tảng Facebook.

### 🌟 Tính Năng Nổi Bật
- **Thu Thập Tin Tức Tự Động (Scraping)**: Theo dõi các nguồn RSS và tự động tổng hợp tin tức mới nhất theo định kỳ.
- **Tích Hợp AI Đa Nền Tảng**: Sáng tạo nội dung với **Google Gemini**, hoặc kết nối dễ dàng với các **Local LLM** (như Ollama, LM Studio) hoàn toàn miễn phí thông qua chuẩn giao tiếp tương thích.
- **Web Dashboard Hiện Đại**: Giao diện quản trị phong cách Glassmorphism trực quan, tích hợp hệ thống xác thực bảo mật Session-based, giúp quản trị viên duyệt và quản lý bài viết một cách hiệu quả.
- **Tự Động Đăng Bài & Chống Khóa (Anti-Ban)**: Lập lịch đăng bài thông minh kèm thuật toán độ trễ ngẫu nhiên (Jitter), giả lập hành vi người dùng thực tế nhằm tránh các giới hạn từ API của Facebook.
- **Quản Lý Linh Hoạt**: Giao diện thân thiện cho phép cấu hình nguồn tin RSS và điều chỉnh các câu lệnh AI (System Prompts) linh hoạt mà không yêu cầu can thiệp vào mã nguồn.

### 🚀 Cài Đặt Nhanh

**1. Clone dự án và thiết lập môi trường:**
```bash
git clone https://github.com/HuaTrung026/auto-fanpage-ai.git
cd auto-fanpage-ai
python -m venv .venv

# Kích hoạt môi trường ảo:
# Windows: .venv\Scripts\activate
# Mac/Linux: source .venv/bin/activate

pip install -r requirements.txt
```

**2. Cấu hình bảo mật:**
Tạo tệp `.env` từ tệp mẫu:
```bash
cp .env.example .env
```
Cập nhật biến `GEMINI_API_KEY` và `FB_PAGE_TOKEN` trong tệp `.env`. (Xem chi tiết cách lấy mã tại `INSTRUCTIONS.md`).

**3. Khởi động hệ thống:**
```bash
python src/main.py
```
Truy cập giao diện quản lý tại trình duyệt: `http://localhost:8000` (Tài khoản mặc định - User: `admin` / Password: `admin123`).

### 📚 Tài Liệu Kèm Theo
- [**INSTRUCTIONS.md**](INSTRUCTIONS.md): Sổ tay hướng dẫn sử dụng và cấu hình chi tiết (Dành cho Người Dùng).
- [**ARCHITECTURE.md**](ARCHITECTURE.md): Tài liệu thiết kế hệ thống, sơ đồ cơ sở dữ liệu và luồng xử lý (Dành cho Lập Trình Viên).

### 📝 Giấy Phép
Dự án được phát triển phục vụ mục đích cá nhân và phi thương mại.
