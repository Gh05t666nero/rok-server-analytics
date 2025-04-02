# config.py
import os
import streamlit as st
from dotenv import load_dotenv

# Muat variabel lingkungan dari file .env
load_dotenv()

# Coba akses dari streamlit secrets jika berjalan di cloud, fallback ke env vars
def get_config_value(key, default=None):
    """Ambil nilai konfigurasi dari Streamlit secrets atau variabel lingkungan"""
    try:
        return st.secrets.get(key, os.getenv(key, default))
    except:
        return os.getenv(key, default)

# Konfigurasi API
API_CONFIG = {
    "endpoint": get_config_value("ROK_API_ENDPOINT", "https://rocdir.lilithgame.com/get/roles"),
    "app_uid": get_config_value("ROK_APP_UID"),
    "app_token": get_config_value("ROK_APP_TOKEN"),
    "app_id": get_config_value("ROK_APP_ID"),
    "lg_channel": get_config_value("ROK_LG_CHANNEL", "and"),
    "sdk_type": get_config_value("ROK_SDK_TYPE", "1"),
    "ip": get_config_value("ROK_IP", "3.128.191.232"),
    "udid": get_config_value("ROK_UDID"),
    "lang": get_config_value("ROK_LANG", "en"),
    "platform": get_config_value("ROK_PLATFORM", "android")
}

# Data config
DATA_CONFIG = {
    "cache_ttl": 3600,  # Waktu cache dalam detik (1 jam)
    "fallback_path": "data/fallback_data.json"  # Path untuk data fallback
}

# Konfigurasi zona waktu
TIME_CONFIG = {
    "timezone": "Asia/Jakarta",  # Zona waktu WIB
    "datetime_format": "%d %b %Y %H:%M"  # Format tanggal dan waktu
}

# App config
APP_CONFIG = {
    "title": "Analisis Server Rise of Kingdoms",
    "description": "Dashboard analisis dan prediksi untuk data server game Rise of Kingdoms",
    "author": "Nama Anda",
    "version": "1.0.0"
}

# Theme config
THEME_CONFIG = {
    "primary_color": "#BB86FC",
    "secondary_color": "#03DAC6",
    "background_color": "#121212",
    "text_color": "#E0E0E0"
}

# Color schemes
COLOR_SCHEMES = {
    "Biru Gelap": "Blues_r",
    "Ungu": "Purples_r",
    "Teal": "Teal_r",
    "Magenta": "Magenta_r"
}
