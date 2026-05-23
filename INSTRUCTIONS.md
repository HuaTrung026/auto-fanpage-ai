# 📖 Sổ Tay Hướng Dẫn Sử Dụng Auto-Fanpage AI

Chào mừng bạn đến với kỷ nguyên rảnh tay! Hệ thống này đóng vai trò như một "nhân viên thực tập" mẫn cán:
- Tự động quét và đọc báo (Cào tin RSS).
- Tự động viết content (Sử dụng AI để xào nấu lại).
- Tự động đẩy lên Web Dashboard để bạn duyệt.
- Tự động đăng lên Fanpage theo khung giờ vàng đã hẹn.

Dưới đây là hướng dẫn từ A đến Z, đảm bảo **ai cũng làm được**.

---

## BƯỚC 1: CHUẨN BỊ ĐỒ NGHỀ (THIẾT LẬP API KEY)

Để hệ thống hoạt động, bạn cần 2 chiếc chìa khóa cốt lõi:
1. **AI API Key (Gemini/Local LLM):** "Bộ não" xử lý ngôn ngữ.
2. **Facebook Page Access Token:** "Cánh tay" đăng bài lên Fanpage.

### Lấy Google Gemini API Key (Miễn phí)
1. Truy cập [Google AI Studio](https://aistudio.google.com/) và đăng nhập bằng Gmail.
2. Bấm vào nút **Get API key** ở menu bên trái.
3. Bấm **Create API key**.
4. Sao chép (Copy) chuỗi mã hiện ra và dán vào biến `GEMINI_API_KEY` trong file `.env`.

*(Lưu ý: Nếu sử dụng Local LLM như LM Studio/Ollama, bạn không cần nhập mã này mà chỉ cần cấu hình Base URL trên giao diện Web).*

### Lấy Facebook Page Access Token (Token Dài Hạn)
1. Truy cập [Meta for Developers](https://developers.facebook.com/) -> **Ứng dụng của tôi** -> **Tạo ứng dụng** (Loại hình: Doanh nghiệp).
2. Tại Bảng điều khiển ứng dụng, cuộn xuống phần **Tùy chỉnh trường hợp sử dụng Quản lý mọi thứ trên Trang**. Bấm vào để mở rộng, kéo xuống phần **Quyền**, bấm **Thêm** và chọn 3 quyền: `pages_show_list`, `pages_read_engagement`, `pages_manage_posts`.
3. Lên thanh menu trên cùng, chọn **Công cụ** -> **Trình khám phá Graph API**.
4. Chọn đúng ứng dụng Meta vừa tạo, nhấn **Tạo mã truy cập** và cấp quyền kết nối với Fanpage của bạn.
5. Ở ô "Người dùng hoặc Trang", bấm xổ xuống và chọn **Nhận mã truy cập Trang** -> Chọn Fanpage của bạn.
6. Copy mã ngắn hạn vừa xuất hiện. Bấm vào nút **"i"** (Thông tin) cạnh đó -> **Mở trong Công cụ mã truy cập** -> **Gia hạn mã truy cập**.
7. BÙM! Bạn đã có Token Dài Hạn. Hãy dán nó vào biến `FB_PAGE_TOKEN` trong file `.env`.

*(Mẹo: Admin đăng nhập mặc định của Dashboard là User: `admin`, Pass: `admin123`. Bạn có thể đổi lại trong file `.env`).*

---

## BƯỚC 2: KHỞI ĐỘNG HỆ THỐNG ("BẬT CÔNG TẮC")

Việc duy nhất bạn cần làm mỗi ngày để hệ thống chạy là:
1. Mở Terminal / PowerShell tại thư mục dự án.
2. Gõ lệnh:
   ```bash
   python src/main.py
   ```
3. Khi thấy báo hiệu Dashboard đã mở, bạn có thể thu nhỏ cửa sổ này xuống (Tuyệt đối không tắt nó). Hệ thống đã bắt đầu làm việc ngầm.

---

## BƯỚC 3: LÀM "SẾP" DUYỆT BÀI VÀ CẤU HÌNH 👑

1. Mở trình duyệt web, truy cập: **`http://localhost:8000`** và đăng nhập.
2. Tại **Dashboard (Duyệt Bài)**: Bạn sẽ thấy danh sách các bài báo mà AI đã đọc và chế thành Content + Hashtag. Bấm **Duyệt Bài** nếu thấy ưng ý, hoặc **Từ Chối** nếu nội dung chưa phù hợp. Bài đã duyệt sẽ nằm chờ tự động đăng lên Fanpage.
3. Tại trang **Nguồn & Văn Phong**: Quản lý các Link RSS muốn cào, và tự do nhập "Thần chú" (Prompt) để ép AI viết bài theo phong cách (Gen Z, Châm biếm, Góc nhìn chuyên gia...).
4. Tại trang **Cấu Hình (Settings)**: Quản lý cấu hình nâng cao như Đổi AI Provider sang Local LLM (LM Studio), thay đổi khung giờ đăng, độ trễ (Jitter). Bạn cũng có thêm các nút bấm *Thủ Công (Manual Triggers)* để ép bot đi cào tin hoặc ép đăng ngay lập tức.

Hãy đi nhâm nhi tách cà phê, hệ thống sẽ tự động chăm sóc Fanpage cho bạn! ☕
