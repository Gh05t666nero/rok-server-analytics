# utils/data_loader.py
import os
import json
import requests
import streamlit as st
from config import API_CONFIG, DATA_CONFIG, TIME_CONFIG
import pandas as pd
from datetime import datetime
import pytz
import logging

# Configure logging
logger = logging.getLogger(__name__)


@st.cache_data(ttl=DATA_CONFIG["cache_ttl"])
def load_data_from_api():
    """
    Memuat data dari API Rise of Kingdoms dengan kredensial yang aman.

    Returns:
        dict: Data server yang dimuat dari API atau data fallback jika gagal.
    """
    endpoint = API_CONFIG["endpoint"]
    params = {
        "app_uid": API_CONFIG["app_uid"],
        "app_token": API_CONFIG["app_token"],
        "app_id": API_CONFIG["app_id"],
        "lg_channel": API_CONFIG["lg_channel"],
        "sdk_type": API_CONFIG["sdk_type"],
        "ip": API_CONFIG["ip"],
        "udid": API_CONFIG["udid"],
        "lang": API_CONFIG["lang"],
        "platform": API_CONFIG["platform"]
    }

    try:
        with st.spinner("Sedang mengambil data terbaru..."):
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Ensure data has the expected structure
            if not isinstance(data, dict) or "1" not in data or "Servers" not in data["1"]:
                logger.error("Invalid data structure from API")
                return load_fallback_data()

            # Pre-process numeric and boolean fields in the raw data
            for server in data["1"]["Servers"]:
                # Convert numeric fields to integers
                for field in ['ServerId', 'DistrictId', 'OpenTime', 'ContinentId', 'IsNew', 'Status']:
                    if field in server:
                        try:
                            server[field] = int(server[field])
                        except (ValueError, TypeError):
                            server[field] = 0

                # Convert boolean fields to true booleans
                for field in ['IsVisible', 'CanRelocate', 'AllowLifeRelocate', 'FogOpen']:
                    if field in server:
                        if isinstance(server[field], str):
                            server[field] = server[field].lower() in ('true', 'yes', '1')
                        else:
                            server[field] = bool(server[field])

            # Simpan salinan data untuk fallback
            save_fallback_data(data)

            return data
    except requests.exceptions.RequestException as e:
        st.error(f"Gagal mengambil data dari API: {e}")
        logger.error(f"API request failed: {e}")
        return load_fallback_data()
    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
        logger.error(f"Unexpected error loading data: {e}")
        return load_fallback_data()


def save_fallback_data(data):
    """
    Menyimpan data sebagai fallback jika API tidak tersedia di masa mendatang.

    Parameters:
        data (dict): Data server untuk disimpan.
    """
    try:
        # Buat direktori jika belum ada
        os.makedirs(os.path.dirname(DATA_CONFIG["fallback_path"]), exist_ok=True)

        # Dapatkan waktu saat ini dalam WIB
        wib_timezone = pytz.timezone(TIME_CONFIG["timezone"])
        current_time_wib = datetime.now(wib_timezone)

        # Simpan data dengan timestamp
        with open(DATA_CONFIG["fallback_path"], 'w', encoding='utf-8') as f:
            json.dump({
                "data": data,
                "timestamp": current_time_wib.isoformat()
            }, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.error(f"Could not save fallback data: {e}")
        st.warning(f"Tidak dapat menyimpan data fallback: {e}")


def load_fallback_data():
    """
    Memuat data fallback jika API tidak tersedia.

    Returns:
        dict: Data server dari fallback atau data contoh jika fallback tidak tersedia.
    """
    try:
        if os.path.exists(DATA_CONFIG["fallback_path"]):
            with open(DATA_CONFIG["fallback_path"], 'r', encoding='utf-8') as f:
                fallback = json.load(f)
                st.info(f"Menggunakan data cache dari {fallback['timestamp']}")
                return fallback["data"]
    except Exception as e:
        logger.error(f"Could not load fallback data: {e}")
        st.warning(f"Tidak dapat memuat data fallback: {e}")

    # Jika fallback tidak tersedia, gunakan data contoh
    return get_sample_data()


def get_sample_data():
    """
    Menyediakan data contoh jika API dan fallback tidak tersedia.

    Returns:
        dict: Data contoh.
    """
    st.warning("Menggunakan data contoh. Fitur akan terbatas.")
    return {
        "1": {
            "Servers": [
                {"ServerId": 1121, "ServerName": "S", "IsNew": 0, "Status": 4, "MapType": "Sever_Map_G1_1_v2",
                 "OpenTime": 1605526068, "DistrictId": 141, "ContinentId": 1, "IsVisible": True,
                 "CanRelocate": True, "AllowLifeRelocate": False, "FogOpen": True},
                {"ServerId": 1441, "ServerName": "S", "IsNew": 0, "Status": 4, "MapType": "Sever_Map_G1_2_v2",
                 "OpenTime": 1632662260, "DistrictId": 181, "ContinentId": 1, "IsVisible": True,
                 "CanRelocate": True, "AllowLifeRelocate": False, "FogOpen": True},
                {"ServerId": 1313, "ServerName": "S", "IsNew": 0, "Status": 4, "MapType": "Sever_Map_G1_3_v2",
                 "OpenTime": 1622358503, "DistrictId": 165, "ContinentId": 1, "IsVisible": True,
                 "CanRelocate": True, "AllowLifeRelocate": False, "FogOpen": True},
                {"ServerId": 1522, "ServerName": "S", "IsNew": 0, "Status": 4, "MapType": "Sever_Map_G1_4_v2",
                 "OpenTime": 1642358503, "DistrictId": 190, "ContinentId": 1, "IsVisible": True,
                 "CanRelocate": True, "AllowLifeRelocate": False, "FogOpen": True},
                {"ServerId": 1621, "ServerName": "S", "IsNew": 0, "Status": 4, "MapType": "Sever_Map_G1_1_v2",
                 "OpenTime": 1652358503, "DistrictId": 200, "ContinentId": 1, "IsVisible": True,
                 "CanRelocate": True, "AllowLifeRelocate": False, "FogOpen": True},
                {"ServerId": 1701, "ServerName": "S", "IsNew": 0, "Status": 4, "MapType": "Sever_Map_G1_2_v2",
                 "OpenTime": 1662358503, "DistrictId": 210, "ContinentId": 1, "IsVisible": True,
                 "CanRelocate": True, "AllowLifeRelocate": False, "FogOpen": True},
                {"ServerId": 1801, "ServerName": "S", "IsNew": 1, "Status": 4, "MapType": "Sever_Map_G1_3_v2",
                 "OpenTime": 1672358503, "DistrictId": 220, "ContinentId": 1, "IsVisible": True,
                 "CanRelocate": True, "AllowLifeRelocate": False, "FogOpen": True}
            ]
        }
    }


@st.cache_data(ttl=3600)
def load_data_from_csv(filepath):
    """
    Memuat data dari file CSV lokal.

    Parameters:
        filepath (str): Path ke file CSV.

    Returns:
        pandas.DataFrame: Data yang dimuat dari CSV atau None jika gagal.
    """
    try:
        # Convert columns to proper types during load
        dtype_dict = {
            'ServerId': 'int64',
            'DistrictId': 'int64',
            'ContinentId': 'int64',
            'IsNew': 'int64',
            'Status': 'int64'
        }

        df = pd.read_csv(filepath, dtype=dtype_dict)

        # Convert boolean columns
        bool_columns = ['IsVisible', 'CanRelocate', 'AllowLifeRelocate', 'FogOpen']
        for col in bool_columns:
            if col in df.columns:
                df[col] = df[col].astype(bool)

        return df
    except Exception as e:
        logger.error(f"Failed to load data from CSV: {e}")
        st.error(f"Gagal memuat data dari CSV: {e}")
        return None