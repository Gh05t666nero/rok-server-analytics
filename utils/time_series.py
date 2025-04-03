# utils/time_series.py
import pandas as pd
import numpy as np
import streamlit as st
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.arima.model import ARIMA
import warnings
import pytz
import logging
from config import TIME_CONFIG

# Suppress statsmodels warnings
warnings.filterwarnings("ignore")

# Setup logging
logger = logging.getLogger(__name__)


@st.cache_data(ttl=3600)
def perform_seasonal_decomposition(ts, period=12):
    """
    Melakukan dekomposisi time series menjadi komponen tren, musiman, dan residual.

    Parameters:
        ts (pandas.Series): Series time series dengan indeks datetime
        period (int): Periode musiman

    Returns:
        dict: Hasil dekomposisi dengan komponen 'trend', 'seasonal', 'resid', dan 'observed'
    """
    try:
        # Isi nilai yang hilang menggunakan interpolasi
        ts_filled = ts.interpolate(method='linear')

        # Dekomposisi time series
        decomposition = seasonal_decompose(ts_filled, model='additive', period=period)

        return {
            'trend': decomposition.trend,
            'seasonal': decomposition.seasonal,
            'resid': decomposition.resid,
            'observed': decomposition.observed
        }
    except Exception as e:
        logger.error(f"Error in time series decomposition: {e}")
        st.error(f"Error dalam dekomposisi time series: {str(e)}")
        return None


def forecast_with_arima(ts, periods=90, order=(1, 1, 0)):
    """
    Melakukan forecasting time series menggunakan model ARIMA.

    Parameters:
        ts (pandas.Series): Series time series dengan indeks datetime
        periods (int): Jumlah periode untuk forecast
        order (tuple): Parameter (p,d,q) untuk model ARIMA

    Returns:
        tuple: (forecast_values, forecast_dates) hasil prediksi
    """
    try:
        # Fit model ARIMA
        model = ARIMA(ts, order=order)
        model_fit = model.fit()

        # Membuat forecast
        forecast_values = model_fit.forecast(steps=periods)

        # Buat tanggal forecast
        last_date = ts.index[-1]
        forecast_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=periods)

        # Pastikan nilai forecast tidak negatif
        forecast_values = np.maximum(forecast_values, 0)

        return forecast_values, forecast_dates, model_fit
    except Exception as e:
        logger.error(f"Error in ARIMA forecasting: {e}")
        st.error(f"Error dalam forecasting ARIMA: {str(e)}")
        return None, None, None


def forecast_with_sarima(ts, periods=90):
    """
    Melakukan forecasting time series menggunakan model SARIMA
    (Seasonal ARIMA) yang menangkap pola musiman.

    Parameters:
        ts (pandas.Series): Series time series dengan indeks datetime
        periods (int): Jumlah periode untuk forecast

    Returns:
        tuple: (forecast_values, forecast_dates) hasil prediksi
    """
    try:
        # SARIMA dengan komponen musiman
        # order=(1,1,1) untuk komponen non-musiman (p,d,q)
        # seasonal_order=(1,1,0,12) untuk komponen musiman (P,D,Q,s) dengan periode 12
        model = SARIMAX(ts, order=(1, 1, 1), seasonal_order=(1, 1, 0, 12))
        model_fit = model.fit(disp=False)

        # Membuat forecast
        forecast_values = model_fit.forecast(steps=periods)

        # Buat tanggal forecast
        last_date = ts.index[-1]
        forecast_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=periods)

        # Pastikan nilai forecast tidak negatif
        forecast_values = np.maximum(forecast_values, 0)

        return forecast_values, forecast_dates, model_fit
    except Exception as e:
        logger.error(f"Error in SARIMA forecasting: {e}")
        st.error(f"Error dalam forecasting SARIMA: {str(e)}")
        return None, None, None


def predict_next_servers(df, num_servers=5):
    """
    Memprediksi detail server berikutnya berdasarkan pola historis.

    Parameters:
        df (pandas.DataFrame): DataFrame dengan data server historis
        num_servers (int): Jumlah server berikutnya untuk diprediksi

    Returns:
        pandas.DataFrame: DataFrame dengan prediksi server berikutnya
    """
    try:
        # Ensure all numeric fields are properly typed
        df = df.copy()
        if 'ServerId' in df.columns:
            df['ServerId'] = pd.to_numeric(df['ServerId'], errors='coerce').fillna(0).astype(int)
        if 'DistrictId' in df.columns:
            df['DistrictId'] = pd.to_numeric(df['DistrictId'], errors='coerce').fillna(0).astype(int)

        # Gunakan 30 server terakhir untuk analisis pola
        recent_servers = df.sort_values('OpenDateTime').tail(30)

        # Hitung statistik penting
        # Gunakan median untuk ketahanan terhadap outlier
        time_deltas = recent_servers['OpenDateTime'].diff().dt.total_seconds() / 3600
        avg_hours_between_servers = time_deltas.dropna().median()

        # Analisis pola jam
        hour_counts = recent_servers['Hour'].value_counts()
        most_common_hour = hour_counts.idxmax()
        hour_consistency = hour_counts.max() / hour_counts.sum()

        # Analisis pola hari dalam seminggu
        day_counts = recent_servers['DayOfWeek'].value_counts()
        most_common_day = day_counts.idxmax()
        day_consistency = day_counts.max() / day_counts.sum()

        # Temukan server terakhir
        last_server_id = df['ServerId'].max()
        last_server = df[df['ServerId'] == last_server_id].iloc[0]
        last_open_date = last_server['OpenDateTime']
        last_district = last_server['DistrictId']

        # Analisis pola MapType
        map_type_pattern = df.sort_values('OpenDateTime').tail(20)['MapType'].tolist()
        # Deteksi pola dalam tipe peta
        map_types = _detect_map_pattern(map_type_pattern)

        # Prediksi server berikutnya
        next_servers = []

        # Dapatkan waktu sekarang di zona waktu WIB
        timezone = pytz.timezone(TIME_CONFIG["timezone"])
        current_time_wib = pd.Timestamp.now(tz=timezone)

        for i in range(1, num_servers + 1):
            next_server_id = last_server_id + i

            # Perhitungan waktu dasar
            hours_to_add = avg_hours_between_servers * i
            next_open_datetime = last_open_date + pd.Timedelta(hours=hours_to_add)

            # Sesuaikan waktu berdasarkan konsistensi pola
            if hour_consistency > 0.5:  # Pola jam yang konsisten
                next_open_datetime = next_open_datetime.replace(hour=most_common_hour, minute=0, second=0)

                if day_consistency > 0.5:  # Pola hari yang konsisten
                    days_to_add = (most_common_day - next_open_datetime.dayofweek) % 7
                    if days_to_add > 0:
                        next_open_datetime = next_open_datetime + pd.Timedelta(days=days_to_add)

            # Prediksi district ID
            district_increment = (next_server_id - last_server_id - 1) // 4
            next_district = last_district + district_increment

            # Prediksi jenis peta
            map_index = (next_server_id - 1) % len(map_types)
            next_map_type = map_types[map_index]

            # Hitung waktu hingga pembukaan menggunakan waktu WIB
            time_until_opening = next_open_datetime - current_time_wib
            days_until = time_until_opening.days
            hours_until = time_until_opening.seconds // 3600

            # Jika waktunya negatif (sudah lewat), sesuaikan estimasi
            if time_until_opening.total_seconds() < 0:
                estimate = "Seharusnya sudah dibuka"
            else:
                estimate = f"{days_until} hari {hours_until} jam lagi"

            next_servers.append({
                'ServerId': int(next_server_id),
                'Tanggal': next_open_datetime.strftime('%Y-%m-%d'),
                'Jam': next_open_datetime.strftime('%H:%M:%S'),
                'DistrictId': int(next_district),
                'MapType': next_map_type,
                'Estimasi': estimate
            })

        # Create DataFrame with explicit types for all columns
        next_servers_df = pd.DataFrame(next_servers)

        # Convert numeric columns to int explicitly (important for Arrow serialization)
        next_servers_df['ServerId'] = next_servers_df['ServerId'].astype(int)
        next_servers_df['DistrictId'] = next_servers_df['DistrictId'].astype(int)

        return next_servers_df

    except Exception as e:
        logger.error(f"Error predicting next servers: {e}", exc_info=True)
        st.error(f"Error dalam prediksi server berikutnya: {str(e)}")
        # Return empty DataFrame with the right structure
        return pd.DataFrame(columns=['ServerId', 'Tanggal', 'Jam', 'DistrictId', 'MapType', 'Estimasi'])


def _detect_map_pattern(map_types):
    """
    Mendeteksi pola tipe peta dari data historis.

    Parameters:
        map_types (list): Daftar tipe peta dari server terakhir

    Returns:
        list: Pola tipe peta yang terdeteksi
    """
    # Default pattern jika tidak bisa mendeteksi pola
    default_pattern = ['Sever_Map_G1_1_v2', 'Sever_Map_G1_2_v2', 'Sever_Map_G1_3_v2', 'Sever_Map_G1_4_v2']

    if len(map_types) < 4:
        return default_pattern

    # Coba deteksi pola berulang
    for pattern_length in range(2, 5):
        # Ambil pattern_length terakhir sebagai pola potensial
        potential_pattern = map_types[-pattern_length:]

        # Cek apakah pola ini berulang dalam daftar
        matches = 0
        for i in range(len(map_types) - pattern_length):
            if map_types[i:i + pattern_length] == potential_pattern:
                matches += 1

        # Jika pola muncul setidaknya 2 kali, kita anggap itu pola yang valid
        if matches >= 2:
            return potential_pattern

    # Jika tidak mendeteksi pola, gunakan 4 tipe peta terakhir
    if len(map_types) >= 4:
        return map_types[-4:]

    return default_pattern


def find_optimal_arima_params(ts):
    """
    Menemukan parameter optimal untuk model ARIMA.

    Parameters:
        ts (pandas.Series): Series time series dengan indeks datetime

    Returns:
        tuple: Parameter optimal (p,d,q) untuk model ARIMA
    """
    try:
        best_aic = float("inf")
        best_params = None

        # Grid search sederhana untuk parameter
        p_values = range(0, 3)
        d_values = range(0, 2)
        q_values = range(0, 3)

        for p in p_values:
            for d in d_values:
                for q in q_values:
                    try:
                        # Skip kombinasi yang tidak valid atau terlalu kompleks
                        if p + d + q > 4:
                            continue

                        model = ARIMA(ts, order=(p, d, q))
                        model_fit = model.fit()

                        if model_fit.aic < best_aic:
                            best_aic = model_fit.aic
                            best_params = (p, d, q)
                    except:
                        continue

        if best_params is None:
            # Jika tidak menemukan parameter yang cocok, gunakan default
            return (1, 1, 0)

        return best_params

    except Exception as e:
        logger.warning(f"Could not find optimal ARIMA parameters: {e}")
        # Kembalikan parameter default
        return (1, 1, 0)


def analyze_time_patterns(df):
    """
    Analisis pola waktu dalam data untuk insight.

    Parameters:
        df (pandas.DataFrame): DataFrame dengan data server

    Returns:
        dict: Hasil analisis pola waktu
    """
    try:
        patterns = {}

        # Analisis pola hari dalam seminggu
        weekday_counts = df['DayOfWeek'].value_counts().sort_index()
        weekday_names = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
        patterns['weekday_counts'] = {weekday_names[i]: count for i, count in enumerate(weekday_counts)}
        patterns['most_common_day'] = weekday_names[weekday_counts.idxmax()]
        patterns['weekday_consistency'] = weekday_counts.max() / weekday_counts.sum()

        # Analisis pola jam
        hour_counts = df['Hour'].value_counts().sort_index()
        patterns['hour_counts'] = hour_counts.to_dict()
        patterns['most_common_hour'] = hour_counts.idxmax()
        patterns['hour_consistency'] = hour_counts.max() / hour_counts.sum()

        # Analisis interval pembukaan server
        df_sorted = df.sort_values('OpenDateTime')
        time_diffs = df_sorted['OpenDateTime'].diff().dt.total_seconds() / 3600  # dalam jam
        patterns['avg_hours_between_servers'] = time_diffs.mean()
        patterns['median_hours_between_servers'] = time_diffs.median()

        # Analisis pola musiman bulanan
        month_counts = df.groupby('Month').size()
        patterns['month_counts'] = month_counts.to_dict()
        patterns['most_common_month'] = month_counts.idxmax()
        patterns['monthly_consistency'] = month_counts.max() / month_counts.sum()

        return patterns
    except Exception as e:
        logger.error(f"Error analyzing time patterns: {e}")
        # Return default patterns
        return {
            'weekday_counts': {"Senin": 0, "Selasa": 0, "Rabu": 0, "Kamis": 0, "Jumat": 0, "Sabtu": 0, "Minggu": 0},
            'most_common_day': "Senin",
            'weekday_consistency': 0,
            'hour_counts': {0: 0},
            'most_common_hour': 12,
            'hour_consistency': 0,
            'avg_hours_between_servers': 24,
            'median_hours_between_servers': 24,
            'month_counts': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0},
            'most_common_month': 1,
            'monthly_consistency': 0
        }