# 📖 User Manual | Sổ Tay Hướng Dẫn Sử Dụng

[![English](https://img.shields.io/badge/Language-English-blue)](#english) [![Tiếng Việt](https://img.shields.io/badge/Language-Tiếng%20Việt-red)](#tiếng-việt)

---

## 🇬🇧 English

Welcome to the Auto-Fanpage AI Assistant! This system operates as an autonomous digital assistant that seamlessly handles your content pipeline:
- Scrapes and parses news articles via RSS feeds.
- Rewrites content intelligently using AI.
- Stages generated content on a Web Dashboard for your review.
- Automatically publishes approved posts to your Facebook Fanpage at optimal scheduled times.

Follow this comprehensive guide to set up and operate the system efficiently.

---

### STEP 1: PREREQUISITES (API KEY CONFIGURATION)

To initialize the system, two essential credentials are required:
1. **AI API Key (Gemini or Local LLM):** The core intelligence engine for natural language processing.
2. **Facebook Page Access Token:** The authorization token required to publish content to your Fanpage.

#### Acquiring the Google Gemini API Key (Free)
1. Navigate to [Google AI Studio](https://aistudio.google.com/) and sign in with your Google account.
2. Click on **Get API key** in the left navigation menu.
3. Select **Create API key**.
4. Copy the generated key and assign it to the `GEMINI_API_KEY` environment variable in your `.env` file.

*(Note: If you choose to utilize a Local LLM such as LM Studio or Ollama, this API key is not required. You only need to configure the Base URL within the Web Dashboard's settings).*

#### Acquiring the Facebook Page Access Token (Long-Lived)
1. Access [Meta for Developers](https://developers.facebook.com/), navigate to **My Apps**, and click **Create App** (Select the **Business** type).
2. Within the App Dashboard, locate the **Customize managing your Page** section. Expand it, scroll down to **Permissions**, click **Add**, and select the following three permissions: `pages_show_list`, `pages_read_engagement`, and `pages_manage_posts`.
3. In the top navigation bar, navigate to **Tools** -> **Graph API Explorer**.
4. Ensure the newly created Meta app is selected, click **Generate Access Token**, and authorize the connection with your target Fanpage.
5. In the "User or Page" dropdown menu, select **Get Page Access Token**, then select your specific Fanpage.
6. Copy the generated short-lived token. Click the **"i"** (Information) icon next to it -> **Open in Access Token Tool** -> **Extend Access Token**.
7. You now have the Long-Lived Token. Assign this value to the `FB_PAGE_TOKEN` environment variable in your `.env` file.

*(Tip: The default administrator credentials for the Dashboard are User: `admin`, Password: `admin123`. We strongly recommend updating these in the `.env` file).*

---

### STEP 2: SYSTEM INITIALIZATION

To initiate the automated processes, perform the following steps:
1. Open your Terminal or PowerShell within the root directory of the project.
2. Execute the start command:
   ```bash
   python src/main.py
   ```
3. Once the console indicates that the Dashboard is active, you may minimize the window (Do not close it). The system is now actively processing tasks in the background.

---

### STEP 3: ADMINISTRATION AND CONFIGURATION 👑

1. Launch your web browser, navigate to **`http://localhost:8000`**, and log in.
2. **Dashboard (Content Review)**: Here, you will find a queue of AI-generated posts derived from recent news. Click **Approve** (Duyệt Bài) to authorize publication, or **Reject** (Từ Chối) if the content is unsatisfactory. Approved posts will be automatically scheduled and published to your Fanpage.
3. **Sources & Prompts (Nguồn & Văn Phong)**: Manage your target RSS feeds and define system prompts to customize the AI's writing style (e.g., Professional, Gen-Z, Satirical).
4. **Settings (Cấu Hình)**: Configure advanced system parameters, including transitioning to a Local LLM (like LM Studio), adjusting posting schedules, and modifying delay (Jitter) settings. This section also provides *Manual Triggers* to force immediate news scraping or content publishing.

The system will now autonomously manage your Fanpage content.

---
---

## 🇻🇳 Tiếng Việt

Chào mừng bạn đến với Auto-Fanpage AI Assistant! Hệ thống này vận hành như một trợ lý tự động hóa quy trình nội dung của bạn một cách toàn diện:
- Tự động thu thập và trích xuất tin tức qua RSS.
- Biên tập và tái cấu trúc nội dung một cách thông minh bằng AI.
- Tổng hợp bài viết trên Web Dashboard để chờ phê duyệt.
- Tự động đăng tải bài viết đã duyệt lên Fanpage Facebook theo lịch trình tối ưu.

Vui lòng làm theo hướng dẫn chi tiết dưới đây để thiết lập và vận hành hệ thống hiệu quả.

---

### BƯỚC 1: ĐIỀU KIỆN TIÊN QUYẾT (CẤU HÌNH API KEY)

Để khởi tạo hệ thống, bạn cần chuẩn bị hai thông tin xác thực cốt lõi:
1. **AI API Key (Gemini hoặc Local LLM):** Đóng vai trò là trung tâm xử lý ngôn ngữ tự nhiên.
2. **Facebook Page Access Token:** Token ủy quyền cần thiết để đăng bài lên Fanpage.

#### Lấy Google Gemini API Key (Miễn phí)
1. Truy cập [Google AI Studio](https://aistudio.google.com/) và đăng nhập bằng tài khoản Google.
2. Nhấn vào **Get API key** tại menu điều hướng bên trái.
3. Chọn **Create API key**.
4. Sao chép chuỗi mã được tạo và gán vào biến `GEMINI_API_KEY` trong tệp `.env` của bạn.

*(Lưu ý: Nếu bạn chọn sử dụng Local LLM như LM Studio hoặc Ollama, khóa API này là không bắt buộc. Bạn chỉ cần cấu hình Base URL trong phần cài đặt của Web Dashboard).*

#### Lấy Facebook Page Access Token (Token Dài Hạn)
1. Truy cập [Meta for Developers](https://developers.facebook.com/), chuyển đến **Ứng dụng của tôi**, và nhấn **Tạo ứng dụng** (Chọn loại **Doanh nghiệp**).
2. Tại Bảng điều khiển ứng dụng, tìm phần **Tùy chỉnh trường hợp sử dụng Quản lý mọi thứ trên Trang**. Mở rộng phần này, cuộn xuống **Quyền**, nhấn **Thêm** và chọn ba quyền sau: `pages_show_list`, `pages_read_engagement`, `pages_manage_posts`.
3. Trên thanh công cụ trên cùng, điều hướng đến **Công cụ** -> **Trình khám phá Graph API**.
4. Đảm bảo ứng dụng Meta vừa tạo được chọn, nhấn **Tạo mã truy cập** và cấp quyền kết nối với Fanpage của bạn.
5. Tại menu thả xuống "Người dùng hoặc Trang", chọn **Nhận mã truy cập Trang**, sau đó chọn Fanpage mục tiêu.
6. Sao chép token ngắn hạn vừa được tạo. Nhấn vào biểu tượng **"i"** (Thông tin) bên cạnh token -> **Mở trong Công cụ mã truy cập** -> **Gia hạn mã truy cập**.
7. Bạn hiện đã có Token Dài Hạn. Hãy gán giá trị này vào biến `FB_PAGE_TOKEN` trong tệp `.env`.

*(Mẹo: Thông tin đăng nhập quản trị viên mặc định cho Dashboard là User: `admin`, Password: `admin123`. Khuyến nghị bạn nên thay đổi thông tin này trong tệp `.env`).*

---

### BƯỚC 2: KHỞI ĐỘNG HỆ THỐNG

Để kích hoạt các quy trình tự động, thực hiện các bước sau:
1. Mở Terminal hoặc PowerShell tại thư mục gốc của dự án.
2. Thực thi lệnh khởi động:
   ```bash
   python src/main.py
   ```
3. Khi giao diện console thông báo Dashboard đã hoạt động, bạn có thể thu nhỏ cửa sổ (Vui lòng không đóng cửa sổ này). Hệ thống hiện đang tích cực xử lý các tác vụ nền.

---

### BƯỚC 3: QUẢN TRỊ VÀ CẤU HÌNH 👑

1. Mở trình duyệt web, truy cập **`http://localhost:8000`**, và đăng nhập.
2. **Dashboard (Duyệt Bài)**: Tại đây, bạn sẽ thấy danh sách các bài đăng do AI tạo ra từ tin tức gần đây. Nhấn **Duyệt Bài** (Approve) để ủy quyền đăng tải, hoặc **Từ Chối** (Reject) nếu nội dung chưa đạt yêu cầu. Các bài đã duyệt sẽ được tự động xếp lịch và đăng lên Fanpage.
3. **Nguồn & Văn Phong (Sources & Prompts)**: Quản lý các luồng RSS mục tiêu và thiết lập "System prompts" để tùy chỉnh phong cách viết của AI (ví dụ: Chuyên nghiệp, Gen-Z, Châm biếm).
4. **Cấu Hình (Settings)**: Tùy chỉnh các thông số hệ thống nâng cao, bao gồm việc chuyển đổi sang Local LLM (như LM Studio), điều chỉnh lịch đăng bài, và sửa đổi độ trễ (Jitter). Phần này cũng cung cấp các nút *Thủ Công (Manual Triggers)* để ép buộc hệ thống thu thập tin tức hoặc đăng bài ngay lập tức.

Hệ thống sẽ bắt đầu tự động quản lý nội dung Fanpage của bạn một cách tối ưu.

---
