# components/time_analysis.py
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from utils.data_processor import prepare_time_series_data
from utils.time_series import perform_seasonal_decomposition, analyze_time_patterns
from plotly.subplots import make_subplots


def render_time_analysis_tab(filtered_df, color_scheme):
    """
    Render tab analisis waktu dengan visualisasi terkait waktu.

    Parameters:
        filtered_df (pandas.DataFrame): DataFrame yang sudah difilter
        color_scheme (list): Skema warna untuk visualisasi
    """
    st.markdown('<p class="sub-header">Analisis Waktu</p>', unsafe_allow_html=True)

    # Timeline pembukaan server
    st.markdown('<div class="insight-card">', unsafe_allow_html=True)
    with st.expander("### Timeline Pembukaan Server", expanded=True):
        render_timeline_analysis(filtered_df, color_scheme)
    st.markdown('</div>', unsafe_allow_html=True)

    # Analisis pola waktu
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown('<div class="insight-card">', unsafe_allow_html=True)
        with st.expander("### Pola Bulanan", expanded=True):
            render_monthly_pattern(filtered_df, color_scheme)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="insight-card">', unsafe_allow_html=True)
        with st.expander("### Ringkasan per Bulan", expanded=True):
            render_monthly_summary(filtered_df, color_scheme)
        st.markdown('</div>', unsafe_allow_html=True)

    # Pola hari dalam seminggu
    st.markdown('<div class="insight-card">', unsafe_allow_html=True)
    with st.expander("### Pola Hari dalam Seminggu", expanded=True):
        render_weekday_pattern(filtered_df, color_scheme)
    st.markdown('</div>', unsafe_allow_html=True)

    # Analisis jarak antar pembukaan server
    st.markdown('<div class="insight-card">', unsafe_allow_html=True)
    with st.expander("### Interval Antar Server", expanded=True):
        render_server_intervals(filtered_df, color_scheme)
    st.markdown('</div>', unsafe_allow_html=True)

    # Analisis musiman
    st.markdown('<div class="insight-card">', unsafe_allow_html=True)
    with st.expander("### Analisis Musiman", expanded=True):
        render_seasonal_analysis(filtered_df, color_scheme)
    st.markdown('</div>', unsafe_allow_html=True)


def render_timeline_analysis(df, color_scheme):
    """Render analisis timeline pembukaan server."""
    st.markdown("""
    Visualisasi ini menunjukkan pola pembukaan server berdasarkan waktu. 
    Anda dapat melihat periode di mana pembukaan server lebih sering atau lebih jarang terjadi.
    """)

    # Buat dataframe dengan hitungan berdasarkan tanggal
    timeline_data = df.groupby('OpenDate').size().reset_index(name='Count')
    timeline_data['OpenDate'] = pd.to_datetime(timeline_data['OpenDate'])

    # Hitungan kumulatif
    timeline_data['Cumulative'] = timeline_data['Count'].cumsum()

    # Tab timeline dengan ikon
    timeline_tab1, timeline_tab2, timeline_tab3 = st.tabs([
        "📊 Jumlah Harian",
        "📈 Pertumbuhan Kumulatif",
        "🔍 Analisis Moving Average"
    ])

    with timeline_tab1:
        fig = px.line(
            timeline_data,
            x='OpenDate',
            y='Count',
            title='Jumlah Server yang Dibuka Setiap Hari',
            color_discrete_sequence=[color_scheme[2]]
        )

        fig.update_layout(
            template="plotly_dark",
            height=400,
            xaxis_title='Tanggal',
            yaxis_title='Jumlah Server'
        )

        fig.update_traces(
            hovertemplate='<b>Tanggal: %{x|%d %b %Y}</b><br>Jumlah server: %{y}'
        )

        st.plotly_chart(fig, use_container_width=True)

    with timeline_tab2:
        fig = px.line(
            timeline_data,
            x='OpenDate',
            y='Cumulative',
            title='Pertumbuhan Kumulatif Server',
            color_discrete_sequence=[color_scheme[2]]
        )

        fig.update_layout(
            template="plotly_dark",
            height=400,
            xaxis_title='Tanggal',
            yaxis_title='Jumlah Kumulatif Server'
        )

        fig.update_traces(
            hovertemplate='<b>Tanggal: %{x|%d %b %Y}</b><br>Total server: %{y}'
        )

        st.plotly_chart(fig, use_container_width=True)

    with timeline_tab3:
        # Analisis moving average untuk melihat tren
        window_size = st.slider(
            "Pilih ukuran window untuk Moving Average",
            min_value=3,
            max_value=30,
            value=7,
            help="Semakin besar nilai, semakin halus kurva moving average"
        )

        # Isi nilai yang hilang dengan 0
        daily_complete = timeline_data.set_index('OpenDate').reindex(
            pd.date_range(start=timeline_data['OpenDate'].min(),
                          end=timeline_data['OpenDate'].max())
        ).fillna(0).reset_index()
        daily_complete.columns = ['OpenDate', 'Count', 'Cumulative']

        # Hitung moving average
        daily_complete['MA'] = daily_complete['Count'].rolling(window=window_size, center=True).mean()

        fig = go.Figure()

        # Plot data asli
        fig.add_trace(go.Scatter(
            x=daily_complete['OpenDate'],
            y=daily_complete['Count'],
            mode='lines',
            name='Data Asli',
            line=dict(color=color_scheme[2], width=1)
        ))

        # Plot moving average
        fig.add_trace(go.Scatter(
            x=daily_complete['OpenDate'],
            y=daily_complete['MA'],
            mode='lines',
            name=f'Moving Average ({window_size} hari)',
            line=dict(color=color_scheme[0], width=3)
        ))

        fig.update_layout(
            template="plotly_dark",
            height=400,
            xaxis_title='Tanggal',
            yaxis_title='Jumlah Server',
            title=f'Analisis Tren dengan Moving Average ({window_size} hari)'
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("""
        **Interpretasi Moving Average:**

        Moving average membantu mengidentifikasi tren dengan mengurangi fluktuasi harian. 
        Kenaikan kurva menunjukkan peningkatan frekuensi pembukaan server, 
        sedangkan penurunan menunjukkan perlambatan.
        """)


def render_monthly_pattern(df, color_scheme):
    """Render pola bulanan pembukaan server."""
    st.markdown("""
    Grafik ini menunjukkan berapa banyak server dibuka setiap bulan. 
    Perhatikan apakah ada bulan tertentu dengan lebih banyak pembukaan server.
    """)

    # Kelompokkan berdasarkan tahun dan bulan
    monthly_data = df.groupby(['Year', 'Month']).size().reset_index(name='Count')
    monthly_data['YearMonth'] = monthly_data['Year'].astype(str) + '-' + monthly_data['Month'].astype(str).str.zfill(2)

    # Urutkan berdasarkan tahun dan bulan
    monthly_data = monthly_data.sort_values(['Year', 'Month'])

    fig = px.bar(
        monthly_data,
        x='YearMonth',
        y='Count',
        title='Pembukaan Server per Bulan',
        color_discrete_sequence=[color_scheme[2]]
    )

    fig.update_layout(
        template="plotly_dark",
        height=300,
        xaxis_title='Tahun-Bulan',
        yaxis_title='Jumlah Server',
        xaxis=dict(tickangle=45)
    )

    fig.update_traces(
        hovertemplate='<b>%{x}</b><br>Jumlah server: %{y}'
    )

    st.plotly_chart(fig, use_container_width=True)

    # Tambahkan analisis tren YoY jika data cukup
    years = df['Year'].unique()
    if len(years) > 1:
        st.subheader("Analisis Year-over-Year")

        # Hitung jumlah server per bulan per tahun
        pivot_monthly = pd.pivot_table(
            monthly_data,
            values='Count',
            index='Month',
            columns='Year',
            aggfunc='sum'
        ).fillna(0)

        # Hitung perubahan persentase YoY untuk setiap bulan
        for year in range(int(min(years)) + 1, int(max(years)) + 1):
            if year - 1 in pivot_monthly.columns and year in pivot_monthly.columns:
                pivot_monthly[f'YoY {year - 1}-{year}'] = (
                            (pivot_monthly[year] - pivot_monthly[year - 1]) / pivot_monthly[year - 1] * 100).replace(
                    [np.inf, -np.inf], np.nan)

        st.dataframe(pivot_monthly)


def render_monthly_summary(df, color_scheme):
    """Render ringkasan bulanan pembukaan server."""
    st.markdown("""
    Grafik ini menunjukkan total server yang dibuka di setiap bulan sepanjang tahun.
    Ini membantu mengidentifikasi bulan-bulan paling aktif untuk pembukaan server.
    """)

    # Ringkasan bulan (tanpa memperhatikan tahun)
    monthly_pattern = df.groupby('Month').size().reset_index(name='Count')
    monthly_pattern = monthly_pattern.sort_values('Month')

    # Tambahkan nama bulan
    month_names = {
        1: 'Januari', 2: 'Februari', 3: 'Maret', 4: 'April', 5: 'Mei', 6: 'Juni',
        7: 'Juli', 8: 'Agustus', 9: 'September', 10: 'Oktober', 11: 'November', 12: 'Desember'
    }

    monthly_pattern['MonthName'] = monthly_pattern['Month'].map(month_names)

    fig = px.bar(
        monthly_pattern,
        x='MonthName',
        y='Count',
        title='Total Pembukaan Server per Bulan',
        color_discrete_sequence=[color_scheme[2]]
    )

    fig.update_layout(
        template="plotly_dark",
        height=300,
        xaxis_title='Bulan',
        yaxis_title='Jumlah Server',
        xaxis=dict(categoryorder='array', categoryarray=list(month_names.values()))
    )

    fig.update_traces(
        hovertemplate='<b>%{x}</b><br>Jumlah server: %{y}'
    )

    st.plotly_chart(fig, use_container_width=True)

    # Tambahkan insight tentang musim
    st.markdown("### Analisis Musiman")

    # Kelompokkan bulan berdasarkan musim (untuk contoh global)
    spring = monthly_pattern[monthly_pattern['Month'].isin([3, 4, 5])]['Count'].sum()
    summer = monthly_pattern[monthly_pattern['Month'].isin([6, 7, 8])]['Count'].sum()
    fall = monthly_pattern[monthly_pattern['Month'].isin([9, 10, 11])]['Count'].sum()
    winter = monthly_pattern[monthly_pattern['Month'].isin([12, 1, 2])]['Count'].sum()

    seasons_data = pd.DataFrame({
        'Musim': ['Musim Semi (Mar-Mei)', 'Musim Panas (Jun-Agu)', 'Musim Gugur (Sep-Nov)', 'Musim Dingin (Des-Feb)'],
        'Jumlah': [spring, summer, fall, winter]
    })

    fig = px.bar(
        seasons_data,
        x='Musim',
        y='Jumlah',
        title='Pembukaan Server per Musim',
        color='Jumlah',
        color_continuous_scale=color_scheme
    )

    fig.update_layout(
        template="plotly_dark",
        height=300,
        xaxis_title='Musim',
        yaxis_title='Jumlah Server',
        coloraxis_showscale=False
    )

    st.plotly_chart(fig, use_container_width=True)


def render_weekday_pattern(df, color_scheme):
    """Render pola hari dalam seminggu untuk pembukaan server."""
    st.markdown("""
    Grafik ini menunjukkan pada hari apa dalam seminggu server biasanya dibuka.
    Hari tertentu mungkin lebih sering digunakan untuk pembukaan server baru.
    """)

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

    # Tambahkan kategori weekday vs weekend
    weekday_pattern['IsWeekend'] = weekday_pattern['DayOfWeek'].isin([5, 6])
    weekday_pattern['DayType'] = weekday_pattern['IsWeekend'].map({True: 'Akhir Pekan', False: 'Hari Kerja'})

    # Tab untuk dua jenis visualisasi
    tab1, tab2 = st.tabs(["Hari dalam Seminggu", "Hari Kerja vs Akhir Pekan"])

    with tab1:
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

    with tab2:
        # Hitung total per kategori
        weekday_vs_weekend = weekday_pattern.groupby('DayType')['Count'].sum().reset_index()

        fig = px.pie(
            weekday_vs_weekend,
            names='DayType',
            values='Count',
            title='Pembukaan Server: Hari Kerja vs Akhir Pekan',
            color_discrete_sequence=color_scheme
        )

        fig.update_layout(
            template="plotly_dark",
            height=350
        )

        fig.update_traces(
            hovertemplate='<b>%{label}</b><br>Jumlah server: %{value}<br>Persentase: %{percent}'
        )

        st.plotly_chart(fig, use_container_width=True)

        # Tambahkan insight
        weekday_total = weekday_vs_weekend[weekday_vs_weekend['DayType'] == 'Hari Kerja']['Count'].sum()
        weekend_total = weekday_vs_weekend[weekday_vs_weekend['DayType'] == 'Akhir Pekan']['Count'].sum()
        weekday_avg = weekday_total / 5  # 5 hari kerja
        weekend_avg = weekend_total / 2  # 2 hari akhir pekan

        st.markdown(f"""
        ### Insight Hari Kerja vs Akhir Pekan

        - Rata-rata pembukaan server per hari kerja: **{weekday_avg:.1f}**
        - Rata-rata pembukaan server per hari akhir pekan: **{weekend_avg:.1f}**
        - Rasio akhir pekan/hari kerja: **{(weekend_avg / weekday_avg):.2f}**

        {'Server lebih sering dibuka pada akhir pekan (per harinya).' if weekend_avg > weekday_avg else 'Server lebih sering dibuka pada hari kerja (per harinya).'}
        """)


def render_server_intervals(df, color_scheme):
    """Render analisis interval waktu antar pembukaan server."""
    st.markdown("""
    Grafik ini menunjukkan distribusi interval waktu antar pembukaan server.
    Ini membantu mengidentifikasi apakah ada pola konsisten dalam waktu antar pembukaan server.
    """)

    # Urutkan berdasarkan waktu pembukaan
    df_sorted = df.sort_values('OpenDateTime').reset_index(drop=True)

    # Hitung selisih waktu dalam jam
    df_sorted['TimeDelta'] = df_sorted['OpenDateTime'].diff().dt.total_seconds() / 3600

    # Hilangkan nilai pertama yang NaN
    time_deltas = df_sorted['TimeDelta'].dropna()

    # Statistik dasar
    mean_delta = time_deltas.mean()
    median_delta = time_deltas.median()

    # Histogram interval waktu
    fig = px.histogram(
        time_deltas,
        title='Distribusi Interval Waktu Antar Pembukaan Server',
        labels={'value': 'Interval (jam)'},
        color_discrete_sequence=[color_scheme[2]]
    )

    fig.update_layout(
        template="plotly_dark",
        height=300,
        xaxis_title='Interval Waktu (jam)',
        yaxis_title='Frekuensi'
    )

    # Tambahkan garis untuk rata-rata dan median
    fig.add_vline(x=mean_delta, line_dash="dash", line_color=color_scheme[4],
                  annotation_text=f"Rata-rata: {mean_delta:.1f} jam")
    fig.add_vline(x=median_delta, line_dash="dot", line_color=color_scheme[5],
                  annotation_text=f"Median: {median_delta:.1f} jam")

    st.plotly_chart(fig, use_container_width=True)

    # Tambahkan insight dan interpretasi
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Statistik Interval")
        st.markdown(f"""
        - **Rata-rata**: {mean_delta:.1f} jam ({mean_delta / 24:.1f} hari)
        - **Median**: {median_delta:.1f} jam ({median_delta / 24:.1f} hari)
        - **Minimum**: {time_deltas.min():.1f} jam
        - **Maksimum**: {time_deltas.max():.1f} jam
        """)

    with col2:
        st.subheader("Interpretasi")

        # Berikan interpretasi berdasarkan data
        if median_delta < 24:
            interpretation = "Pembukaan server cenderung terjadi **beberapa kali sehari**."
        elif median_delta < 48:
            interpretation = "Pembukaan server cenderung terjadi **setiap hari**."
        elif median_delta < 168:
            interpretation = "Pembukaan server cenderung terjadi **beberapa kali seminggu**."
        else:
            interpretation = "Pembukaan server cenderung terjadi **lebih jarang** dari sekali seminggu."

        st.markdown(f"""
        {interpretation}

        Perbedaan antara rata-rata dan median mengindikasikan adanya periode tidak biasa saat interval waktu sangat panjang atau sangat pendek.
        """)

    # Plot interval waktu antar server
    st.subheader("Interval Waktu Antar Server")

    fig = px.line(
        df_sorted,
        x='OpenDateTime',
        y='TimeDelta',
        title='Interval Waktu Antar Pembukaan Server',
        color_discrete_sequence=[color_scheme[3]]
    )

    fig.update_layout(
        template="plotly_dark",
        height=300,
        xaxis_title='Tanggal',
        yaxis_title='Interval (jam)'
    )

    fig.update_traces(
        hovertemplate='<b>Tanggal: %{x|%d %b %Y}</b><br>Interval: %{y:.1f} jam'
    )

    st.plotly_chart(fig, use_container_width=True)


def render_seasonal_analysis(df, color_scheme):
    """Render analisis musiman pembukaan server."""
    st.markdown("""
    Analisis musiman membantu mengidentifikasi pola berulang dalam data pembukaan server.
    Dekomposisi memisahkan data menjadi komponen tren, musiman, dan residual.
    """)

    # Persiapkan data time series
    daily_data, monthly_data = prepare_time_series_data(df)

    # Pilihan periode untuk analisis musiman
    period_options = {
        "Tahunan (12 bulan)": 12,
        "Kuartalan (3 bulan)": 3,
        "Mingguan (7 hari)": 7
    }

    selected_period = st.selectbox(
        "Pilih periode untuk analisis musiman:",
        list(period_options.keys())
    )

    period = period_options[selected_period]

    # Gunakan data bulanan untuk analisis tahunan/kuartalan
    if period in (3, 12):
        # Set index untuk time series
        monthly_ts = monthly_data.set_index('Date')['Count']

        # Pastikan data cukup untuk dekomposisi
        if len(monthly_ts) >= 2 * period:
            decomposition = perform_seasonal_decomposition(monthly_ts, period=period)

            if decomposition:
                render_decomposition_plot(decomposition, color_scheme)
            else:
                st.warning("Tidak dapat melakukan dekomposisi musiman. Pastikan data cukup panjang.")
        else:
            st.warning(
                f"Data tidak cukup untuk analisis musiman dengan periode {period}. Diperlukan minimal {2 * period} bulan data.")

    # Gunakan data harian untuk analisis mingguan
    else:
        # Set index untuk time series
        daily_ts = daily_data.set_index('Date')['Count']

        # Pastikan data cukup untuk dekomposisi
        if len(daily_ts) >= 2 * period:
            decomposition = perform_seasonal_decomposition(daily_ts, period=period)

            if decomposition:
                render_decomposition_plot(decomposition, color_scheme)
            else:
                st.warning("Tidak dapat melakukan dekomposisi musiman. Pastikan data cukup panjang.")
        else:
            st.warning(
                f"Data tidak cukup untuk analisis musiman dengan periode {period}. Diperlukan minimal {2 * period} hari data.")


def render_decomposition_plot(decomposition, color_scheme):
    """Render plot dekomposisi musiman."""
    # Plot dekomposisi
    fig = make_subplots(
        rows=4,
        cols=1,
        subplot_titles=('Data Asli', 'Tren', 'Musiman', 'Residu')
    )

    fig.add_trace(
        go.Scatter(
            x=decomposition['observed'].index,
            y=decomposition['observed'],
            mode='lines',
            name='Data Asli',
            line=dict(color=color_scheme[1])
        ),
        row=1,
        col=1
    )

    fig.add_trace(
        go.Scatter(
            x=decomposition['trend'].index,
            y=decomposition['trend'],
            mode='lines',
            name='Tren',
            line=dict(color=color_scheme[2])
        ),
        row=2,
        col=1
    )

    fig.add_trace(
        go.Scatter(
            x=decomposition['seasonal'].index,
            y=decomposition['seasonal'],
            mode='lines',
            name='Musiman',
            line=dict(color=color_scheme[3])
        ),
        row=3,
        col=1
    )

    fig.add_trace(
        go.Scatter(
            x=decomposition['resid'].index,
            y=decomposition['resid'],
            mode='lines',
            name='Residu',
            line=dict(color=color_scheme[4])
        ),
        row=4,
        col=1
    )

    fig.update_layout(
        template="plotly_dark",
        height=800,
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

    # Tambahkan penjelasan komponen
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Tren**")
        st.markdown("""
        Menunjukkan arah jangka panjang dalam pembukaan server.
        Tren naik berarti lebih banyak server dibuka seiring waktu.
        """)

    with col2:
        st.markdown("**Musiman**")
        st.markdown("""
        Menunjukkan pola berulang, seperti musiman tahunan. 
        Puncak menunjukkan bulan dengan pembukaan server tertinggi.
        """)

    with col3:
        st.markdown("**Residu**")
        st.markdown("""
        Variasi acak yang tidak dapat dijelaskan oleh tren atau musiman.
        Penyimpangan besar menunjukkan peristiwa tidak biasa.
        """)