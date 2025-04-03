# components/overview.py
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from components.dashboard import render_server_growth_chart, render_recent_servers_table


def render_overview_tab(df, filtered_df, color_scheme):
    """
    Render tab ikhtisar dengan metrik dan visualisasi utama.

    Parameters:
        df (pandas.DataFrame): DataFrame lengkap dengan data server
        filtered_df (pandas.DataFrame): DataFrame yang sudah difilter
        color_scheme (list): Skema warna untuk visualisasi
    """
    st.markdown('<p class="sub-header">Ikhtisar Server</p>', unsafe_allow_html=True)

    # Tata letak dua kolom untuk ringkasan dan server terbaru
    col1, col2 = st.columns([1, 1])

    with col1:
        # Laju pembukaan server
        st.markdown('<div class="insight-card">', unsafe_allow_html=True)
        st.markdown("### Laju Pembukaan Server")
        st.markdown("Berikut adalah analisis kecepatan pembukaan server:")

        # Hitung statistik terkait waktu
        _render_time_metrics(df)

        # Distribusi jenis peta
        st.markdown("### Distribusi Server Berdasarkan Jenis Peta")
        _render_map_type_pie_chart(filtered_df, color_scheme)

        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        # Tabel server terbaru
        render_recent_servers_table(filtered_df)

    # Pertumbuhan server sepanjang waktu
    render_server_growth_chart(df, color_scheme)

    # Pola aktivitas server
    st.markdown('<div class="insight-card">', unsafe_allow_html=True)
    with st.expander("### Pola Aktivitas Server", expanded=True):
        _render_server_activity_patterns(filtered_df, color_scheme)
    st.markdown('</div>', unsafe_allow_html=True)


def _render_time_metrics(df):
    """Render metrik terkait waktu."""
    # Hitung hari sejak server pertama
    days_since_first = (df['OpenDateTime'].max() - df['OpenDateTime'].min()).days
    avg_days_per_server = days_since_first / len(df)

    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Hari Sejak Server Pertama", days_since_first)
    with col_b:
        st.metric("Rata-rata Hari Antar Server", round(avg_days_per_server, 1))


def _render_map_type_pie_chart(df, color_scheme):
    """Render diagram pie untuk distribusi jenis peta."""
    map_type_counts = df['MapType'].value_counts().reset_index()
    map_type_counts.columns = ['MapType', 'Count']

    fig = px.pie(
        map_type_counts,
        names='MapType',
        values='Count',
        hole=0.4,
        color_discrete_sequence=color_scheme
    )

    fig.update_layout(
        template="plotly_dark",
        height=300,
        margin=dict(l=10, r=10, t=30, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    fig.update_traces(
        hovertemplate='<b>%{label}</b><br>Jumlah: %{value} server<br>Persentase: %{percent}'
    )

    st.plotly_chart(fig, use_container_width=True)


def _render_server_activity_patterns(df, color_scheme):
    """Render pola aktivitas server."""
    st.markdown("""
    Visualisasi ini menunjukkan pola aktivitas pembukaan server berdasarkan waktu.
    """)

    # Pilih jenis pola yang akan ditampilkan
    pattern_type = st.radio(
        "Pilih Jenis Pola",
        ["Hari dalam Minggu", "Jam dalam Hari", "Bulan dalam Tahun"],
        horizontal=True
    )

    if pattern_type == "Hari dalam Minggu":
        _render_weekday_pattern(df, color_scheme)
    elif pattern_type == "Jam dalam Hari":
        _render_hour_pattern(df, color_scheme)
    else:
        _render_month_pattern(df, color_scheme)


def _render_weekday_pattern(df, color_scheme):
    """Render pola hari dalam seminggu untuk pembukaan server."""
    weekday_pattern = df.groupby('WeekDay').size().reset_index(name='Count')

    # Urutkan hari dalam seminggu dengan benar
    weekday_order = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
    english_weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    indo_weekdays = dict(zip(english_weekdays, weekday_order))

    weekday_pattern['WeekDayIndo'] = weekday_pattern['WeekDay'].map(indo_weekdays)
    weekday_pattern['DayOfWeek'] = weekday_pattern['WeekDay'].map(
        {'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3, 'Friday': 4, 'Saturday': 5, 'Sunday': 6}
    )

    weekday_pattern = weekday_pattern.sort_values('DayOfWeek')

    fig = px.bar(
        weekday_pattern,
        x='WeekDayIndo',
        y='Count',
        title='Pembukaan Server berdasarkan Hari dalam Seminggu',
        color='Count',
        color_continuous_scale=color_scheme
    )

    fig.update_layout(
        template="plotly_dark",
        height=350,
        xaxis_title='Hari',
        yaxis_title='Jumlah Server',
        xaxis=dict(categoryorder='array', categoryarray=weekday_order),
        coloraxis_showscale=False
    )

    fig.update_traces(
        hovertemplate='<b>%{x}</b><br>Jumlah server: %{y}'
    )

    st.plotly_chart(fig, use_container_width=True)


def _render_hour_pattern(df, color_scheme):
    """Render pola jam dalam hari untuk pembukaan server."""
    hour_pattern = df.groupby('Hour').size().reset_index(name='Count')
    hour_pattern = hour_pattern.sort_values('Hour')

    fig = px.bar(
        hour_pattern,
        x='Hour',
        y='Count',
        title='Pembukaan Server berdasarkan Jam dalam Hari',
        color='Count',
        color_continuous_scale=color_scheme
    )

    fig.update_layout(
        template="plotly_dark",
        height=350,
        xaxis_title='Jam (0-23)',
        yaxis_title='Jumlah Server',
        coloraxis_showscale=False
    )

    fig.update_traces(
        hovertemplate='<b>Jam %{x}:00</b><br>Jumlah server: %{y}'
    )

    st.plotly_chart(fig, use_container_width=True)


def _render_month_pattern(df, color_scheme):
    """Render pola bulan dalam tahun untuk pembukaan server."""
    month_pattern = df.groupby('Month').size().reset_index(name='Count')
    month_pattern = month_pattern.sort_values('Month')

    # Tambahkan nama bulan
    month_names = {
        1: 'Januari', 2: 'Februari', 3: 'Maret', 4: 'April', 5: 'Mei', 6: 'Juni',
        7: 'Juli', 8: 'Agustus', 9: 'September', 10: 'Oktober', 11: 'November', 12: 'Desember'
    }

    month_pattern['MonthName'] = month_pattern['Month'].map(month_names)

    fig = px.bar(
        month_pattern,
        x='MonthName',
        y='Count',
        title='Pembukaan Server berdasarkan Bulan dalam Tahun',
        color='Count',
        color_continuous_scale=color_scheme
    )

    fig.update_layout(
        template="plotly_dark",
        height=350,
        xaxis_title='Bulan',
        yaxis_title='Jumlah Server',
        xaxis=dict(categoryorder='array', categoryarray=list(month_names.values())),
        coloraxis_showscale=False
    )

    fig.update_traces(
        hovertemplate='<b>%{x}</b><br>Jumlah server: %{y}'
    )

    st.plotly_chart(fig, use_container_width=True)
