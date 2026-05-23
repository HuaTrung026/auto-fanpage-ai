import os
import yaml
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional

class SystemSettings(BaseModel):
    log_level: str = "INFO"
    max_posts_per_day: int = 5

class RssSource(BaseModel):
    name: str
    url: str
    category: str

class SourcesSettings(BaseModel):
    rss: List[RssSource]

class AiSettings(BaseModel):
    provider: str = "gemini"
    base_url: str = "http://localhost:11434/v1"
    model: str = "gemini-1.5-flash"
    temperature: float = 0.7
    style: str = "hài hước, giật gân nhẹ, ngôn ngữ gen z"

class PostingSchedule(BaseModel):
    time_slots: List[str]
    jitter_minutes: int

class FacebookSettings(BaseModel):
    page_id: str
    posting_schedule: PostingSchedule

class AppConfig(BaseModel):
    system: SystemSettings
    sources: SourcesSettings
    ai_settings: AiSettings
    facebook: FacebookSettings

class EnvConfig(BaseSettings):
    db_path: str = "data/database.sqlite"
    fb_page_token: str = ""
    gemini_api_key: str = ""
    web_username: str = "admin"
    web_password: str = "admin123"

    # Load environment variables from .env file
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

def load_yaml_config(filepath: str = "config/settings.yaml") -> Optional[AppConfig]:
    if not os.path.exists(filepath):
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return AppConfig(**data)

# Singleton instances for easy access
env_config = EnvConfig()
app_config = load_yaml_config()
