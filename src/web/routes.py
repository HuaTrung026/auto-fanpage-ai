from fastapi import APIRouter, Request, HTTPException, Form, Depends, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import secrets
import os
import json
import yaml

from src.storage import get_pending_drafts, update_draft_status
from src.config import load_yaml_config, env_config
from src.scraper import run_scraper
from src.ai import process_pending_articles
from src.poster import run_poster
from src.utils.logger import logger

router = APIRouter()

# Setup templates
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
os.makedirs(templates_dir, exist_ok=True)
templates = Jinja2Templates(directory=templates_dir)

class NotAuthenticatedException(Exception):
    pass

# --- Session Authentication ---
def verify_auth(request: Request):
    if not request.session.get("authenticated"):
        raise NotAuthenticatedException()
    return True

# --- Helper logic for Masking ---
MASK_STRING = "••••••••••••••••••••••••••••••••"

def mask_key(key_value: str) -> str:
    return MASK_STRING if key_value else ""

# --- Manual Triggers ---
def job_crawl_and_ai():
    logger.info("=== MANUAL TRIGGER: CRAWL & AI ===")
    try:
        run_scraper()
        process_pending_articles()
    except Exception as e:
        logger.error(f"Manual trigger error (crawl): {e}")
    logger.info("=== END MANUAL TRIGGER ===")

def job_auto_post():
    logger.info("=== MANUAL TRIGGER: AUTO POST ===")
    try:
        run_poster()
    except Exception as e:
        logger.error(f"Manual trigger error (post): {e}")
    logger.info("=== END MANUAL TRIGGER ===")

@router.post("/api/trigger/crawl")
async def trigger_crawl(background_tasks: BackgroundTasks, _: bool = Depends(verify_auth)):
    background_tasks.add_task(job_crawl_and_ai)
    return {"status": "success", "message": "Đã gửi lệnh chạy ngầm Cào tin & AI. Vui lòng đợi một lát rồi F5."}

@router.post("/api/trigger/post")
async def trigger_post(background_tasks: BackgroundTasks, _: bool = Depends(verify_auth)):
    background_tasks.add_task(job_auto_post)
    return {"status": "success", "message": "Đã gửi lệnh Đăng bài ngầm. Kiểm tra Facebook sau ít phút."}

# --- Login Routes ---
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Trang giao diện đăng nhập."""
    if request.session.get("authenticated"):
        return RedirectResponse(url="/")
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def process_login(request: Request, username: str = Form(...), password: str = Form(...)):
    from src.config import env_config
    is_user_ok = secrets.compare_digest(username.encode("utf8"), env_config.web_username.encode("utf8"))
    is_pass_ok = secrets.compare_digest(password.encode("utf8"), env_config.web_password.encode("utf8"))
    
    if is_user_ok and is_pass_ok:
        request.session["authenticated"] = True
        return RedirectResponse(url="/", status_code=303)
        
    # Return to login with error
    return templates.TemplateResponse("login.html", {"request": request, "error": "Sai thông tin đăng nhập! / Invalid credentials!"})

@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login")

# --- Protected Routes ---
@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, _: bool = Depends(verify_auth)):
    """Trang chủ hiển thị danh sách bài nháp."""
    drafts_raw = get_pending_drafts()
    drafts = []
    
    for draft in drafts_raw:
        try:
            content = json.loads(draft['gemini_content'])
            draft['parsed_content'] = content
            draft['has_error'] = False
        except Exception:
            draft['parsed_content'] = {}
            draft['has_error'] = True
            
        drafts.append(draft)
        
    return templates.TemplateResponse("dashboard.html", {"request": request, "drafts": drafts})

@router.post("/api/drafts/{draft_id}/approve")
async def approve_draft(draft_id: int, _: bool = Depends(verify_auth)):
    success = update_draft_status(draft_id, 'approved')
    if success:
        return {"status": "success", "message": "Đã duyệt bài thành công."}
    raise HTTPException(status_code=500, detail="Không thể cập nhật CSDL.")

@router.post("/api/drafts/{draft_id}/reject")
async def reject_draft(draft_id: int, _: bool = Depends(verify_auth)):
    success = update_draft_status(draft_id, 'rejected')
    if success:
        return {"status": "success", "message": "Đã từ chối bài."}
    raise HTTPException(status_code=500, detail="Không thể cập nhật CSDL.")

@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request, _: bool = Depends(verify_auth)):
    """Trang giao diện chỉnh sửa config."""
    current_config = load_yaml_config()
    
    from src.config import env_config
    env_data = {
        "gemini_key": mask_key(env_config.gemini_api_key),
        "fb_token": mask_key(env_config.fb_page_token),
        "web_user": env_config.web_username,
        "web_pass": mask_key(env_config.web_password)
    }
    
    return templates.TemplateResponse("settings.html", {"request": request, "config": current_config, "env_data": env_data})

@router.post("/api/settings")
async def save_settings(
    provider: str = Form(...),
    base_url: str = Form(""),
    model: str = Form(...),
    temperature: float = Form(...),
    time_slots: str = Form(...),
    jitter_minutes: int = Form(...),
    max_posts: int = Form(...),
    gemini_key: str = Form(""),
    fb_token: str = Form(""),
    web_user: str = Form(""),
    web_pass: str = Form(""),
    _: bool = Depends(verify_auth)
):
    """Lưu thay đổi vào settings.yaml và .env"""
    config_path = "config/settings.yaml"
    env_path = ".env"
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            
        data['ai_settings']['provider'] = provider
        data['ai_settings']['base_url'] = base_url
        data['ai_settings']['model'] = model
        data['ai_settings']['temperature'] = temperature
        
        slots = [s.strip() for s in time_slots.split(',') if s.strip()]
        data['facebook']['posting_schedule']['time_slots'] = slots
        data['facebook']['posting_schedule']['jitter_minutes'] = jitter_minutes
        data['system']['max_posts_per_day'] = max_posts
        
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
            
        from src.config import env_config
        new_gemini = env_config.gemini_api_key
        new_fb = env_config.fb_page_token
        new_web_user = env_config.web_username
        new_web_pass = env_config.web_password
        
        is_env_changed = False
        
        if gemini_key and gemini_key != MASK_STRING:
            new_gemini = gemini_key
            is_env_changed = True
            
        if fb_token and fb_token != MASK_STRING:
            new_fb = fb_token
            is_env_changed = True
            
        if web_user and web_user != new_web_user:
            new_web_user = web_user
            is_env_changed = True
            
        if web_pass and web_pass != MASK_STRING:
            new_web_pass = web_pass
            is_env_changed = True
            
        if is_env_changed:
            env_content = f"GEMINI_API_KEY={new_gemini}\nFB_PAGE_TOKEN={new_fb}\nWEB_USERNAME={new_web_user}\nWEB_PASSWORD={new_web_pass}\n"
            with open(env_path, "w", encoding="utf-8") as f:
                f.write(env_content)
                
            os.environ['GEMINI_API_KEY'] = new_gemini
            os.environ['FB_PAGE_TOKEN'] = new_fb
            os.environ['WEB_USERNAME'] = new_web_user
            os.environ['WEB_PASSWORD'] = new_web_pass
            
            env_config.gemini_api_key = new_gemini
            env_config.fb_page_token = new_fb
            env_config.web_username = new_web_user
            env_config.web_password = new_web_pass
            
        return {"status": "success", "message": "Đã lưu cài đặt thành công."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lưu cài đặt: {e}")

# --- Content Settings Routes ---
@router.get("/content", response_class=HTMLResponse)
async def content_settings_page(request: Request, _: bool = Depends(verify_auth)):
    current_config = load_yaml_config()
    return templates.TemplateResponse("content_settings.html", {"request": request, "config": current_config})

@router.post("/api/content/style")
async def update_style(request: Request, style: str = Form(...), _: bool = Depends(verify_auth)):
    config_path = "config/settings.yaml"
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        data['ai_settings']['style'] = style
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
        return {"status": "success", "message": "Đã lưu văn phong mới thành công."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/content/sources/add")
async def add_source(request: Request, name: str = Form(...), category: str = Form(...), url: str = Form(...), _: bool = Depends(verify_auth)):
    config_path = "config/settings.yaml"
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        if 'sources' not in data:
            data['sources'] = {'rss': []}
        if 'rss' not in data['sources']:
            data['sources']['rss'] = []
            
        data['sources']['rss'].append({
            "name": name,
            "category": category,
            "url": url
        })
        
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
        return {"status": "success", "message": "Đã thêm nguồn báo thành công."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/content/sources/delete")
async def delete_source(request: Request, index: int = Form(...), _: bool = Depends(verify_auth)):
    config_path = "config/settings.yaml"
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            
        rss_list = data.get('sources', {}).get('rss', [])
        if 0 <= index < len(rss_list):
            rss_list.pop(index)
            
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
        return {"status": "success", "message": "Đã xóa nguồn báo."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
