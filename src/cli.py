import os
import sys
import json

# Add path to allow standalone execution
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.storage import get_pending_drafts, update_draft_status

def clear_screen():
    """Làm sạch màn hình cho dễ đọc."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_separator(char='-', length=80):
    print(char * length)

def review_drafts():
    """Vòng lặp tương tác CLI Menu duyệt bài nháp."""
    drafts = get_pending_drafts()
    
    if not drafts:
        print("🎉 Không có bản nháp nào đang chờ duyệt (Pending)!")
        return

    clear_screen()
    print(f"Bắt đầu duyệt bài. Tổng cộng có {len(drafts)} bản nháp chờ duyệt.\n")
    input("Nhấn Enter để bắt đầu...")
    
    for idx, draft in enumerate(drafts, 1):
        clear_screen()
        draft_id = draft['draft_id']
        title = draft['title']
        url = draft['original_url']
        raw_json = draft['gemini_content']
        
        print_separator('=')
        print(f"BẢN NHÁP [{idx}/{len(drafts)}] - ID: {draft_id}")
        print(f"Tiêu đề gốc: {title}")
        print(f"Nguồn:       {url}")
        print_separator('-')
        
        try:
            # Parse nội dung do AI sinh ra
            content = json.loads(raw_json)
            
            # In các thành phần ra màn hình
            if "caption_variant_1" in content:
                print("\n[Variant 1]:")
                print(content["caption_variant_1"])
            
            if "caption_variant_2" in content:
                print("\n[Variant 2]:")
                print(content["caption_variant_2"])
                
            if "hashtags" in content:
                print("\n[Hashtags]:")
                print(content["hashtags"])
                
            # Nếu AI trả về format không chuẩn nhưng vẫn là JSON
            if not any(k in content for k in ["caption_variant_1", "caption_variant_2", "hashtags"]):
                print("\n[JSON Content]:")
                print(json.dumps(content, indent=2, ensure_ascii=False))
                
        except json.JSONDecodeError:
            print("\n⚠️  [LỖI]: Nội dung AI trả về không phải là JSON hợp lệ.")
            print("Raw text:")
            print(raw_json)
            print("\nBạn nên REJECT bản nháp này để tránh lỗi khi đăng bài lên Fanpage.")
            
        print_separator('=')
        
        # Nhận input từ người dùng
        while True:
            choice = input("\nBạn muốn làm gì? [Y] Duyệt | [N] Từ chối | [S] Bỏ qua | [Q] Thoát : ").strip().lower()
            
            if choice == 'y':
                if update_draft_status(draft_id, 'approved'):
                    print("✅ Đã DUYỆT (Approved) thành công!")
                else:
                    print("❌ Lỗi khi cập nhật DB.")
                break
            elif choice == 'n':
                if update_draft_status(draft_id, 'rejected'):
                    print("⛔ Đã TỪ CHỐI (Rejected) bản nháp.")
                else:
                    print("❌ Lỗi khi cập nhật DB.")
                break
            elif choice == 's':
                print("⏭️ Đã BỎ QUA (Skip), giữ nguyên trạng thái pending.")
                break
            elif choice == 'q':
                print("👋 Đang thoát chương trình duyệt bài...")
                return
            else:
                print("Lựa chọn không hợp lệ. Vui lòng gõ Y, N, S hoặc Q.")
                
        # Nếu chưa phải bài cuối cùng và user không chọn Q, chờ 1 chút
        if idx < len(drafts):
            input("\nNhấn Enter để chuyển sang bài tiếp theo...")

    clear_screen()
    print("🎊 Bạn đã duyệt hết các bản nháp trong đợt này!")

if __name__ == "__main__":
    review_drafts()
