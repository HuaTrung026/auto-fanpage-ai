# ARCHITECTURE.md

## 1. Executive Summary
Hệ thống "Trợ lý AI tự động vận hành Fanpage" (Auto-Fanpage AI Assistant) là một ứng dụng chạy nền (Background Service) được thiết kế để hoạt động độc lập trên Local Machine, VPS hoặc Raspberry Pi. Hệ thống chịu trách nhiệm tự động thu thập tin tức từ các nguồn công khai (RSS/Websites), sử dụng LLM (Gemini Flash) để biên tập lại nội dung theo văn phong được định cấu hình sẵn (ví dụ: tấu hài, giật gân), và đăng tải lên Facebook Fanpage thông qua Facebook Graph API chính thức. Phiên bản MVP sẽ áp dụng luồng duyệt bài thủ công (Draft Approval) trước khi tự động hóa hoàn toàn.

## 2. Goals and Non-Goals
**Goals (Mục tiêu):**
* Tự động cào tin tức từ các nguồn RSS feed và website public hợp lệ.
* Trích xuất nội dung chính và tóm tắt/viết lại bằng Gemini Flash API.
* Áp dụng văn phong được chỉ định, tự động đính kèm hashtag và biểu tượng cảm xúc (emoji).
* Lưu trữ trạng thái bài viết (Draft, Approved, Posted, Failed) bằng cơ sở dữ liệu cục bộ (SQLite).
* Đăng bài tự động lên Fanpage được cấp quyền qua Facebook Graph API.
* Có cơ chế kiểm duyệt nội dung (Review Draft) qua CLI trước khi đăng.

**Non-Goals (Những việc không làm):**
* KHÔNG tạo công cụ hack, lách luật, bypass màn hình đăng nhập của website nguồn.
* KHÔNG sử dụng tool automation (Puppeteer/Selenium) để giả lập user đăng bài Facebook hòng lách chính sách API.
* KHÔNG cào dữ liệu từ các trang web cấm bot (không tuân thủ robots.txt).
* KHÔNG đăng spam (giới hạn số lượng bài mỗi ngày, có cơ chế check trùng lặp dữ liệu khắt khe).

## 3. Recommended Tech Stack
**So sánh Python vs. Node.js:**
* **Node.js:** Mạnh về I/O bất đồng bộ, rất tốt cho việc cào dữ liệu đồng thời và xử lý API. Phù hợp nếu sau này muốn phát triển Dashboard bằng React/Vue tích hợp cùng hệ sinh thái JS.
* **Python:** Hệ sinh thái thư viện AI (Google Generative AI SDK), Data Processing và Scraping (BeautifulSoup, Feedparser) cực kỳ phong phú và dễ triển khai. Mã nguồn trực quan, dễ bảo trì, tiêu thụ RAM ổn định trên các thiết bị cấu hình thấp như Raspberry Pi.

**Lựa chọn:** Python 3.10+
**Lý do:** Phù hợp nhất cho việc xây dựng CLI tool tích hợp AI pipeline chạy nền. Tài nguyên trên Linux/Raspberry Pi được quản lý tốt.

**Thư viện đề xuất:**
* **Scraping:** `feedparser` (cho RSS), `requests`, `beautifulsoup4`.
* **AI:** `google-genai` (Gemini API).
* **Database:** `sqlite3` (tích hợp sẵn), SQLAlchemy (ORM nếu cần mở rộng) hoặc chỉ dùng raw SQL/dataclasses để giữ nhẹ hệ thống.
* **Facebook API:** `requests` (tương tác trực tiếp HTTP Graph API).
* **Scheduling:** `APScheduler`.
* **Config/Validation:** `pyyaml`, `pydantic`.

## 4. System Architecture Diagram

```mermaid
flowchart TD
    subgraph Sources
        RSS(RSS Feeds)
        Web(Public Websites)
    end

    subgraph Data Acquisition
        Scraper[Scraper / RSS Reader]
        Filter[Content Filter & Deduplication]
    end

    subgraph AI Processing
        Gemini[Gemini Flash API]
        Rewriter[AI Rewriter]
    end

    subgraph Storage
        SQLite[(SQLite Database)]
    end

    subgraph Output & Control
        CLI[CLI Dashboard / Approver]
        Scheduler[APScheduler]
        FBPoster[Facebook Graph API Poster]
    end
    
    subgraph Fanpage
        FB(Facebook Page)
    end

    RSS --> Scraper
    Web --> Scraper
    Scraper --> Filter
    Filter -- Check DB --> SQLite
    Filter -- New Articles --> Rewriter
    Rewriter <--> Gemini
    Rewriter -- Save Drafts --> SQLite
    SQLite <--> CLI
    CLI -- Approve/Reject --> SQLite
    Scheduler -- Fetch Approved --> SQLite
    Scheduler --> FBPoster
    FBPoster --> FB
    FBPoster -- Log Status --> SQLite
5. Module Breakdown
Hệ thống được chia thành các module độc lập sau:
config_manager: Quản lý đọc/ghi file .yaml và .env. Cung cấp interface để lấy API Key, Page Token, danh sách RSS.
feed_reader:
Nhiệm vụ: Đọc RSS feed hoặc parse website.
Input: URL nguồn.
Output: Danh sách các object RawArticle (title, link, description, pub_date).
content_filter:
Nhiệm vụ: Lọc rác, loại bỏ bài trùng (dựa trên URL hoặc Title băm), check độ trễ bài.
Interface: is_duplicate(article) -> bool.
ai_rewriter:
Nhiệm vụ: Gửi raw text tới Gemini Flash và nhận về caption Facebook.
Input: RawArticle, PromptStyle.
Output: DraftContent (JSON object).
Lỗi cần xử lý: Quota limit, Timeout, Content Safety Violation.
storage:
Nhiệm vụ: Tương tác với SQLite (CRUD operations).
Interface: save_raw_article(), save_draft(), get_pending_drafts(), update_post_status().
cli:
Nhiệm vụ: Cung cấp giao diện dòng lệnh cho user xem log, duyệt draft, kích hoạt đăng tay.
facebook_poster:
Nhiệm vụ: Gọi FB Graph API endpoint /page_id/feed.
Input: ApprovedDraft (text, link).
Output: PostID hoặc Error Message.
scheduler:
Nhiệm vụ: Định tuyến thời gian chạy feed_reader (ví dụ: 1h/lần) và thời gian đăng bài (các khung giờ vàng).
logger: Ghi log ra file cục bộ với cơ chế xoay vòng (RotatingFileHandler).
## 6. Folder Structure 
project-root/
├── .env                 # API Keys, Tokens (Git ignored)
├── .env.example         # Template cho .env
├── .gitignore
├── README.md
├── ARCHITECTURE.md
├── requirements.txt
├── config/
│   └── settings.yaml    # Cấu hình Feed, Khung giờ, Prompt settings
├── data/
│   └── database.sqlite  # SQLite DB file (Git ignored)
├── logs/
│   └── app.log          # System logs (Git ignored)
├── src/
│   ├── __init__.py
│   ├── main.py          # Entry point & Scheduler setup
│   ├── config.py        # Module đọc settings.yaml và .env
│   ├── storage.py       # Tương tác SQLite
│   ├── scraper.py       # RSS/Web parser
│   ├── ai.py            # Tích hợp Gemini API
│   ├── poster.py        # Tích hợp Facebook Graph API
│   ├── utils.py         # Helper functions (Hash, Logger init)
│   └── cli.py           # Command Line Interface menu
└── tests/               # Unit tests
7. Database Design
Sử dụng SQLite. Lược đồ cơ sở dữ liệu:
sources: id, name, url, type (rss/web), is_active, last_fetched_at.
articles: id, source_id, original_url (UNIQUE), title, raw_content, published_at, created_at.
post_drafts: id, article_id, gemini_content (JSON/Text), status (pending/approved/rejected/posted), created_at, scheduled_for.
post_history: id, draft_id, fb_post_id, posted_at, status_code, response_log.
8. Configuration Design
File config/settings.yaml mẫu:
system:
  log_level: "INFO"
  max_posts_per_day: 5

sources:
  rss:
    - name: "Tinhte Tech"
      url: "[https://tinhte.vn/rss](https://tinhte.vn/rss)"
      category: "technology"

ai_settings:
  model: "gemini-2.0-flash"
  temperature: 0.7
  style: "hài hước, giật gân nhẹ, ngôn ngữ gen z"

facebook:
  page_id: "YOUR_PAGE_ID"
  # token được đọc từ .env (FB_PAGE_TOKEN)
  posting_schedule:
    time_slots:
      - "08:00"
      - "12:00"
      - "19:00"
    jitter_minutes: 15 # Đăng lệch ngẫu nhiên 1-15 phút để tránh bot pattern
9. AI Prompt Design
Mẫu Prompt gửi cho Gemini Flash:
Bạn là một Admin Fanpage Facebook chuyên nghiệp, hài hước và bắt trend.
Dưới đây là một bài báo/tin tức thô:
---
Tiêu đề: {title}
Nội dung: {raw_content}
Nguồn: {url}
---
Hãy viết lại nội dung trên thành một bài đăng Facebook Fanpage với các tiêu chí sau:
1. Văn phong: {style_from_config}. Đọc cuốn hút, tấu hài nhưng không phản cảm.
2. Không bịa đặt thông tin sai lệch so với bài gốc. Tóm tắt ngắn gọn ý chính.
3. Chèn emoji phù hợp để làm sinh động bài viết.
4. Thêm 3-5 hashtag liên quan ở cuối bài.
5. Luôn giữ lại link nguồn để trích dẫn.

Yêu cầu định dạng đầu ra: Hãy trả về định dạng JSON thuần túy (không bọc trong markdown code block) với cấu trúc sau:
{
  "caption_variant_1": "Nội dung bài viết...",
  "caption_variant_2": "Nội dung bài viết cách diễn đạt khác...",
  "hashtags": "#tag1 #tag2"
}
10. Facebook Posting Strategy
Giao thức: Sử dụng Facebook Graph API phiên bản mới nhất (v19.0+).
Authentication: Yêu cầu Page Access Token (Lấy từ Facebook Developer App, phân quyền pages_manage_posts, pages_read_engagement). Token cần được cấu hình dạng Long-lived token.
Endpoint: POST https://graph.facebook.com/v19.0/{page_id}/feed
Payload: {"message": "Nội dung caption", "link": "URL nguồn"}
Kiểm soát an toàn: API call chỉ được thực hiện đối với các post_drafts có status là approved. Nếu API trả về lỗi Token Expiration, ngắt luồng auto-post và bắn log cảnh báo hệ thống.
11. Scheduling Strategy
Công cụ: APScheduler (BackgroundScheduler).
Task 1 (Crawl & Draft): Chạy định kỳ mỗi 1-2 giờ. Lấy tin -> Lọc trùng -> Chạy Gemini -> Lưu Database với trạng thái pending.
Task 2 (Auto Post): Cấu hình cron-job dựa trên time_slots trong YAML. Tại mỗi khung giờ, query DB lấy 1 bản ghi approved cũ nhất.
Tính tự nhiên (Jitter): Áp dụng random trễ từ 1 đến jitter_minutes để thời gian đăng không cố định đúng số 00, mô phỏng hành vi người dùng thật.
12. Error Handling and Logging
Scraper: Lỗi HTTP timeout/403 -> Bỏ qua, thử lại ở cron cycle tiếp theo. Ghi log WARNING.
Gemini API: Bắt lỗi Rate Limit (429) hoặc API Unavailable. Áp dụng Exponential Backoff chờ 10s-30s. Nếu lỗi Safety Block (nội dung nhạy cảm), đánh dấu bài đó là rejected trong DB.
Facebook API: Bắt HTTP Error. Log lại toàn bộ JSON response của FB. Nếu lỗi 400 (Bad request), đánh dấu failed. Nếu 401 (Auth), dừng toàn bộ Scheduler và alert.
Logging: Dùng thư viện logging của Python. Ghi log vào file logs/app.log với max size 5MB, rotate 3 files.
13. Security and Compliance
.env tuyệt đối không được đưa lên VCS (Git).
Thêm time.sleep(2) giữa các request cào tin để không tạo DOS lên website nguồn.
Custom User-Agent hợp lệ khi crawl (VD: AutoFanpage-Bot/1.0).
MVP bắt buộc duy trì trạng thái Review Draft: Tránh việc AI sinh nội dung nhạy cảm hoặc sai lệch (Hallucination) gây khủng hoảng truyền thông cho Page.
14. Step-by-Step Implementation Plan
Phase 1: Foundation.
Mục tiêu: Set up cấu trúc thư mục, đọc config .yaml, .env, thiết lập Logger và khởi tạo SQLite schema.
Phase 2: Data Acquisition.
Mục tiêu: Viết module scraper.py. Đọc RSS feed thành công, lưu bài thô vào database, xử lý được logic trùng lặp (is_duplicate).
Phase 3: AI Engine.
Mục tiêu: Tích hợp Gemini SDK. Truyền bài thô vào AI và nhận về JSON chứa caption. Lưu thành công vào bảng post_drafts với status pending.
Phase 4: The Approver CLI (MVP Core).
Mục tiêu: Tạo CLI menu bằng Python. Hiển thị danh sách pending drafts. Cho phép user gõ "Y" để duyệt (chuyển sang approved), "N" để từ chối.
Phase 5: Facebook Integration.
Mục tiêu: Viết hàm post_to_facebook(draft_id). Test gửi thử một draft đã duyệt lên Fanpage thử nghiệm.
Phase 6: Scheduler & Automation.
Mục tiêu: Tích hợp APScheduler. Móc nối mọi thứ thành 2 job chạy nền độc lập: Fetcher Job và Poster Job.
Phase 7: Polish & Document.
Mục tiêu: Viết file requirements.txt, hướng dẫn cấu hình Crontab/Systemd cho Linux/Pi.
15. MVP Scope
Bản MVP tối giản nhất sẽ bao gồm:
Nguồn: Chỉ lấy từ RSS Feeds (không parse HTML phức tạp).
AI: Sử dụng prompt cố định, sinh ra 1 caption.
Kiểm duyệt: Hoàn toàn thủ công. Hệ thống tự cào và soạn sẵn bài, nhưng user phải dùng CLI để duyệt (status = approved).
Đăng bài: Tool tự động bốc bài đã approved đăng theo khung giờ cài sẵn.
16. Future Improvements
Phát triển Web Dashboard UI (dùng FastAPI/Flask + Vue/React) thay cho CLI.
Tích hợp Text-to-Image AI (Stable Diffusion/Midjourney/DALL-E) để tự tạo hình ảnh minh họa thay vì dùng ảnh nguồn.
Tích hợp bắn thông báo (Notification) qua Telegram/Discord mỗi khi có bài Draft mới chờ duyệt hoặc khi bài bị lỗi đăng tải.
A/B Testing caption dựa trên lượt reach sau 24h.

