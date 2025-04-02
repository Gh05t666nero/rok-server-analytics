# utils/data_processor.py
import pandas as pd
import numpy as np
import streamlit as st


@st.cache_data(ttl=1800)  # Cache untuk 30 menit
def process_server_data(data):
    """
    Memproses data server mentah dari API menjadi DataFrame yang siap untuk analisis.

    Parameters:
        data (dict): Data server mentah dari API

    Returns:
        pandas.DataFrame: DataFrame yang telah diproses, atau None jika data tidak valid
    """
    if not _validate_data_structure(data):
        st.error("Struktur data tidak valid. Mohon coba lagi nanti.")
        return None

    servers = data["1"]["Servers"]
    df = pd.DataFrame(servers)

    # Validasi kolom yang dibutuhkan
    required_columns = ['ServerId', 'OpenTime', 'MapType', 'DistrictId']
    if not all(col in df.columns for col in required_columns):
        st.error("Data tidak memiliki semua kolom yang diperlukan")
        return None

    # Konversi dan ekstraksi data waktu
    df = _process_time_data(df)

    # Bersihkan dan standarisasi data
    df = _clean_data(df)

    # Tambahkan kolom turunan untuk analisis
    df = _add_derived_features(df)

    return df


def _validate_data_structure(data):
    """Validasi struktur dasar data API."""
    return (
            data is not None and
            isinstance(data, dict) and
            "1" in data and
            "Servers" in data["1"] and
            isinstance(data["1"]["Servers"], list) and
            len(data["1"]["Servers"]) > 0
    )


def _process_time_data(df):
    """Proses data waktu dan tambahkan kolom waktu yang relevan."""
    # Konversi OpenTime ke datetime
    df['OpenDateTime'] = pd.to_datetime(df['OpenTime'], unit='s')

    # Ekstrak komponen tanggal
    df['OpenDate'] = df['OpenDateTime'].dt.date
    df['Year'] = df['OpenDateTime'].dt.year
    df['Month'] = df['OpenDateTime'].dt.month
    df['MonthName'] = df['OpenDateTime'].dt.strftime('%B')
    df['MonthYear'] = df['OpenDateTime'].dt.strftime('%Y-%m')
    df['WeekDay'] = df['OpenDateTime'].dt.day_name()
    df['DayOfWeek'] = df['OpenDateTime'].dt.dayofweek
    df['Quarter'] = df['OpenDateTime'].dt.quarter
    df['Hour'] = df['OpenDateTime'].dt.hour

    return df


def _clean_data(df):
    """Bersihkan dan standarisasi data."""
    # Tangani nilai yang hilang
    if 'MapType' in df.columns and df['MapType'].isnull().any():
        # Isi nilai MapType yang hilang dengan 'Unknown'
        df['MapType'] = df['MapType'].fillna('Unknown')

    # Pastikan tipe data yang konsisten
    if 'ServerId' in df.columns:
        df['ServerId'] = df['ServerId'].astype(int)

    if 'DistrictId' in df.columns:
        df['DistrictId'] = df['DistrictId'].astype(int)

    return df


def _add_derived_features(df):
    """Tambahkan fitur turunan untuk analisis lanjutan."""
    # Hitung hari sejak server pertama dibuka
    if 'OpenDateTime' in df.columns:
        first_server_date = df['OpenDateTime'].min()
        df['DaysSinceFirstServer'] = (df['OpenDateTime'] - first_server_date).dt.days

    # Kelompokkan server berdasarkan tahun dan bulan pembukaan
    df['YearMonthGroup'] = df['Year'].astype(str) + '-' + df['Month'].astype(str).str.zfill(2)

    # Kategorikan jenis peta untuk analisis yang lebih mudah
    if 'MapType' in df.columns:
        # Ekstrak nomor versi peta dari nama lengkap
        df['MapVersion'] = df['MapType'].str.extract(r'G1_(\d+)')

    return df


def filter_dataframe(df, filters):
    """
    Filter DataFrame berdasarkan kriteria yang diberikan

    Parameters:
        df (pandas.DataFrame): DataFrame yang akan difilter
        filters (dict): Kriteria filter

    Returns:
        pandas.DataFrame: DataFrame yang telah difilter
    """
    filtered_df = df.copy()

    # Filter jenis peta
    if 'map_type' in filters and filters['map_type'] != 'Semua':
        filtered_df = filtered_df[filtered_df['MapType'] == filters['map_type']]

    # Filter tahun
    if 'year' in filters and filters['year'] != 'Semua':
        filtered_df = filtered_df[filtered_df['Year'] == filters['year']]

    # Filter rentang tanggal
    if 'date_range' in filters and isinstance(filters['date_range'], tuple) and len(filters['date_range']) == 2:
        start_date, end_date = filters['date_range']
        filtered_df = filtered_df[(filtered_df['OpenDate'] >= start_date) &
                                  (filtered_df['OpenDate'] <= end_date)]

    # Filter preset waktu
    if 'time_preset' in filters and filters['time_preset'] != "Semua Waktu":
        current_date = pd.Timestamp.now()
        if filters['time_preset'] == "30 Hari Terakhir":
            start_date = current_date - pd.Timedelta(days=30)
            filtered_df = filtered_df[filtered_df['OpenDateTime'] >= start_date]
        elif filters['time_preset'] == "90 Hari Terakhir":
            start_date = current_date - pd.Timedelta(days=90)
            filtered_df = filtered_df[filtered_df['OpenDateTime'] >= start_date]
        elif filters['time_preset'] == "1 Tahun Terakhir":
            start_date = current_date - pd.Timedelta(days=365)
            filtered_df = filtered_df[filtered_df['OpenDateTime'] >= start_date]

    return filtered_df


def prepare_time_series_data(df):
    """
    Menyiapkan data untuk analisis time series

    Parameters:
        df (pandas.DataFrame): DataFrame dengan data server

    Returns:
        tuple: (daily_data, monthly_data) untuk analisis time series
    """
    # Data harian
    daily = df.groupby('OpenDate').size().reset_index(name='Count')
    daily.columns = ['Date', 'Count']
    daily['Date'] = pd.to_datetime(daily['Date'])

    # Isi hari yang hilang dengan nol
    date_range = pd.date_range(start=daily['Date'].min(), end=daily['Date'].max())
    date_df = pd.DataFrame({'Date': date_range})
    daily_complete = pd.merge(date_df, daily, on='Date', how='left').fillna(0)

    # Data bulanan
    monthly = df.groupby(pd.Grouper(key='OpenDateTime', freq='MS')).size().reset_index(name='Count')
    monthly.columns = ['Date', 'Count']

    # Isi bulan yang hilang
    month_range = pd.date_range(start=monthly['Date'].min(), end=monthly['Date'].max(), freq='MS')
    month_df = pd.DataFrame({'Date': month_range})
    monthly_complete = pd.merge(month_df, monthly, on='Date', how='left').fillna(0)

    return daily_complete, monthly_complete


def calculate_statistics(df):
    """
    Menghitung statistik penting untuk dashboard

    Parameters:
        df (pandas.DataFrame): DataFrame dengan data server

    Returns:
        dict: Statistik penting
    """
    stats = {}

    # Total server
    stats['total_servers'] = len(df)

    # Tanggal server pertama dan terakhir
    stats['first_server_date'] = df['OpenDateTime'].min()
    stats['last_server_date'] = df['OpenDateTime'].max()

    # Hari sejak server pertama
    days_since_first = (df['OpenDateTime'].max() - df['OpenDateTime'].min()).days
    stats['days_since_first'] = days_since_first

    # Rata-rata hari antar server
    stats['avg_days_per_server'] = days_since_first / len(df) if len(df) > 1 else 0

    # Jumlah jenis peta
    stats['map_types_count'] = df['MapType'].nunique()

    # Jenis peta paling umum
    stats['most_common_map'] = df['MapType'].value_counts().idxmax()

    # Hari paling umum untuk pembukaan server
    stats['most_common_day'] = df['WeekDay'].value_counts().idxmax()

    # Statistik pembukaan bulanan
    monthly_counts = df.groupby(['Year', 'Month']).size()
    stats['max_monthly_servers'] = monthly_counts.max()
    stats['avg_monthly_servers'] = monthly_counts.mean()

    return stats