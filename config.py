# config.py
import os
import streamlit as st
from dotenv import load_dotenv
import logging

# Konfigurasi logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("config")

# Muat variabel lingkungan dari file .env
try:
    load_dotenv()
    logger.info("Environment variables loaded from .env file")
except Exception as e:
    logger.warning(f"Could not load .env file: {e}")


# Coba akses dari streamlit secrets jika berjalan di cloud, fallback ke env vars
def get_config_value(key, default=None):
    """Ambil nilai konfigurasi dari Streamlit secrets atau variabel lingkungan"""
    try:
        # Coba dapatkan dari streamlit secrets
        return st.secrets.get(key, os.getenv(key, default))
    except Exception:
        # Fallback ke environment variable jika secrets tidak tersedia
        return os.getenv(key, default)


# Fungsi validasi URL
def _validate_url(url):
    """Validate URL format"""
    if not url:
        return False

    try:
        # Simple validation
        return url.startswith(('http://', 'https://'))
    except:
        return False


# Konfigurasi API dengan validasi
api_endpoint = get_config_value("ROK_API_ENDPOINT", "https://rocdir.lilithgame.com/get/roles")
if not _validate_url(api_endpoint):
    logger.warning(f"Invalid API endpoint URL: {api_endpoint}, using default")
    api_endpoint = "https://rocdir.lilithgame.com/get/roles"

API_CONFIG = {
    "endpoint": api_endpoint,
    "app_uid": get_config_value("ROK_APP_UID", ""),
    "app_token": get_config_value("ROK_APP_TOKEN", ""),
    "app_id": get_config_value("ROK_APP_ID", ""),
    "lg_channel": get_config_value("ROK_LG_CHANNEL", "and"),
    "sdk_type": get_config_value("ROK_SDK_TYPE", "1"),
    "ip": get_config_value("ROK_IP", "3.128.191.232"),
    "udid": get_config_value("ROK_UDID", ""),
    "lang": get_config_value("ROK_LANG", "en"),
    "platform": get_config_value("ROK_PLATFORM", "android")
}

# Data config
DATA_CONFIG = {
    "cache_ttl": int(get_config_value("CACHE_TTL", "3600")),  # Waktu cache dalam detik (1 jam)
    "fallback_path": get_config_value("FALLBACK_PATH", "data/fallback_data.json")  # Path untuk data fallback
}

# Konfigurasi zona waktu
TIME_CONFIG = {
    "timezone": get_config_value("TIMEZONE", "Asia/Jakarta"),  # Zona waktu WIB
    "datetime_format": get_config_value("DATETIME_FORMAT", "%d %b %Y %H:%M")  # Format tanggal dan waktu
}

# Konfigurasi notifikasi (Baru)
notification_interval = get_config_value("NOTIFICATION_INTERVAL", "24")
try:
    notification_interval = int(notification_interval)
    # Pastikan nilai dalam rentang yang masuk akal
    if notification_interval < 1:
        notification_interval = 24
except (ValueError, TypeError):
    logger.warning(f"Invalid notification interval: {notification_interval}, using default (24)")
    notification_interval = 24

NOTIFICATION_CONFIG = {
    "subscribers_file": get_config_value("SUBSCRIBERS_FILE", "data/subscribers.json"),
    "sendgrid_api_key": get_config_value("SENDGRID_API_KEY", ""),
    "sender_email": get_config_value("SENDER_EMAIL", "noreply@example.com"),
    "sender_name": get_config_value("SENDER_NAME", "ROK Server Analytics"),
    "telegram_token": get_config_value("TELEGRAM_BOT_TOKEN", ""),
    "telegram_channel_id": get_config_value("TELEGRAM_CHANNEL_ID", ""),
    "notification_interval": notification_interval,  # Jam
    # Batas untuk rate limiting
    "rate_limits": {
        "email_subscribe": 86400,  # 24 jam
        "telegram_subscribe": 86400,  # 24 jam
        "notification_send": 3600,  # 1 jam
        "admin_actions": 300  # 5 menit
    }
}

# App config
APP_CONFIG = {
    "title": get_config_value("APP_TITLE", "Analisis Server Rise of Kingdoms"),
    "description": get_config_value("APP_DESCRIPTION",
                                    "Dashboard analisis dan prediksi untuk data server game Rise of Kingdoms"),
    "author": get_config_value("APP_AUTHOR", "ROK Analytics Team"),
    "version": get_config_value("APP_VERSION", "1.1.0"),
    "admin_password": get_config_value("ADMIN_PASSWORD", ""),  # Hindari hardcoding password
    "debug_mode": get_config_value("DEBUG_MODE", "False").lower() in ('true', '1', 't')
}

# Theme config
THEME_CONFIG = {
    "primary_color": get_config_value("PRIMARY_COLOR", "#BB86FC"),
    "secondary_color": get_config_value("SECONDARY_COLOR", "#03DAC6"),
    "background_color": get_config_value("BACKGROUND_COLOR", "#121212"),
    "text_color": get_config_value("TEXT_COLOR", "#E0E0E0")
}

# Color schemes
COLOR_SCHEMES = {
    "Biru Gelap": "Blues_r",
    "Ungu": "Purples_r",
    "Teal": "Teal_r",
    "Magenta": "Magenta_r"
}

# Log konfigurasi yang dimuat
logger.info(f"Application configured: {APP_CONFIG['title']} version {APP_CONFIG['version']}")