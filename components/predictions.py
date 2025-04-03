# components/predictions.py
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from utils.time_series import forecast_with_arima, forecast_with_sarima, predict_next_servers, \
    find_optimal_arima_params, analyze_time_patterns
from utils.data_processor import prepare_time_series_data


def render_prediction_tab(df, color_scheme):
    """
    Render tab prediksi dengan model time series dan prediksi server berikutnya.

    Parameters:
        df (pandas.DataFrame): DataFrame dengan data server
        color_scheme (list): Skema warna untuk visualisasi
    """
    st.markdown('<p class="sub-header">Prediksi Pembukaan Server</p>', unsafe_allow_html=True)

    # Agregasi bulanan untuk time series dengan visualisasi yang lebih baik
    st.markdown('<div class="insight-card">', unsafe_allow_html=True)
    st.markdown("### Data Historis Pembukaan Server Bulanan")
    render_historical_data(df, color_scheme)
    st.markdown('</div>', unsafe_allow_html=True)

    # Dekomposisi time series dengan tampilan yang lebih baik
    st.markdown('<div class="insight-card">', unsafe_allow_html=True)
    st.markdown("### Dekomposisi Time Series")
    render_time_series_decomposition(df)
    st.markdown('</div>', unsafe_allow_html=True)

    # Forecasting Sederhana dengan ARIMA
    st.markdown('<div class="insight-card">', unsafe_allow_html=True)
    st.markdown("### Prediksi dengan Model ARIMA/SARIMA")
    render_time_series_forecast(df, color_scheme)
    st.markdown('</div>', unsafe_allow_html=True)

    # Prediksi spesifik server berikutnya
    st.markdown('<div class="insight-card">', unsafe_allow_html=True)
    st.markdown("### Prediksi Server Berikutnya")
    render_next_server_predictions(df, color_scheme)
    st.markdown('</div>', unsafe_allow_html=True)


def render_historical_data(df, color_scheme):
    """Render data historis pembukaan server bulanan."""
    st.markdown("""
    Grafik ini menunjukkan jumlah server yang dibuka setiap bulan dalam data historis.
    Pola ini digunakan untuk memprediksi pembukaan server di masa depan.
    """)

    # Agregasi bulanan untuk time series
    monthly_servers = df.groupby(pd.Grouper(key='OpenDateTime', freq='MS')).size().reset_index(name='Count')
    monthly_servers.columns = ['OpenDateTime', 'Count']

    # Plot data bulanan historis
    fig = px.line(
        monthly_servers,
        x='OpenDateTime',
        y='Count',
        labels={'OpenDateTime': 'Tanggal', 'Count': 'Jumlah Server'},
        color_discrete_sequence=[color_scheme[2]]
    )

    fig.update_layout(
        template="plotly_dark",
        height=400,
        title='Pembukaan Server Bulanan',
        xaxis_title='Tanggal',
        yaxis_title='Jumlah Server'
    )

    fig.update_traces(
        hovertemplate='<b>%{x|%B %Y}</b><br>Jumlah server: %{y}'
    )

    st.plotly_chart(fig, use_container_width=True)

    # Tambahkan ringkasan statistik
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Rata-rata Server per Bulan", f"{monthly_servers['Count'].mean():.1f}")

    with col2:
        st.metric("Median Server per Bulan", f"{monthly_servers['Count'].median():.1f}")

    with col3:
        st.metric("Bulan Terakhir", monthly_servers['OpenDateTime'].max().strftime('%B %Y'))

    # Periksa musiman
    st.subheader("Analisis Musiman Bulanan")

    # Kelompokkan berdasarkan bulan
    monthly_servers['Month'] = monthly_servers['OpenDateTime'].dt.month
    monthly_servers['MonthName'] = monthly_servers['OpenDateTime'].dt.strftime('%B')
    monthly_pattern = monthly_servers.groupby('Month').agg({'Count': 'mean', 'MonthName': 'first'}).reset_index()
    monthly_pattern = monthly_pattern.sort_values('Month')

    fig = px.bar(
        monthly_pattern,
        x='MonthName',
        y='Count',
        title='Rata-rata Server per Bulan (Pola Musiman)',
        color='Count',
        color_continuous_scale=color_scheme
    )

    fig.update_layout(
        template="plotly_dark",
        height=300,
        xaxis_title='Bulan',
        yaxis_title='Rata-rata Jumlah Server',
        xaxis=dict(
            categoryorder='array',
            categoryarray=[
                'January', 'February', 'March', 'April', 'May', 'June',
                'July', 'August', 'September', 'October', 'November', 'December'
            ]
        ),
        coloraxis_showscale=False
    )

    st.plotly_chart(fig, use_container_width=True)


def render_time_series_decomposition(df):
    """Render dekomposisi time series."""
    st.markdown("""
    Dekomposisi time series membagi pola pembukaan server menjadi tiga komponen:
    - **Tren**: Perubahan jangka panjang
    - **Musiman**: Pola yang berulang (misalnya bulanan atau tahunan)
    - **Residu**: Fluktuasi acak yang tidak dapat dijelaskan oleh tren atau musiman
    """)

    # Siapkan data time series
    daily_data, monthly_data = prepare_time_series_data(df)

    # Pilihan periode untuk dekomposisi
    period_options = {
        "Tahunan (12 bulan)": 12,
        "Kuartalan (3 bulan)": 3,
        "Mingguan (7 hari)": 7
    }

    selected_period = st.selectbox(
        "Pilih periode untuk dekomposisi:",
        list(period_options.keys()),
        index=0
    )

    period = period_options[selected_period]

    # Hanya lanjutkan jika kita memiliki cukup data
    if selected_period.startswith("Tahunan") or selected_period.startswith("Kuartalan"):
        # Gunakan data bulanan
        min_length = 2 * period

        if len(monthly_data) >= min_length:
            # Atur indeks series ke datetime untuk dekomposisi
            ts = monthly_data.set_index('Date')['Count']

            # Informasi jumlah data
            st.info(f"Menggunakan {len(ts)} bulan data untuk dekomposisi dengan periode {period} bulan.")

            from utils.time_series import perform_seasonal_decomposition
            decomposition = perform_seasonal_decomposition(ts, period=period)

            if decomposition:
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
                        name='Data Asli'
                    ),
                    row=1,
                    col=1
                )

                fig.add_trace(
                    go.Scatter(
                        x=decomposition['trend'].index,
                        y=decomposition['trend'],
                        mode='lines',
                        name='Tren'
                    ),
                    row=2,
                    col=1
                )

                fig.add_trace(
                    go.Scatter(
                        x=decomposition['seasonal'].index,
                        y=decomposition['seasonal'],
                        mode='lines',
                        name='Musiman'
                    ),
                    row=3,
                    col=1
                )

                fig.add_trace(
                    go.Scatter(
                        x=decomposition['resid'].index,
                        y=decomposition['resid'],
                        mode='lines',
                        name='Residu'
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

                    # Tentukan arah tren
                    trend_start = decomposition['trend'].dropna().iloc[0]
                    trend_end = decomposition['trend'].dropna().iloc[-1]
                    trend_direction = "naik" if trend_end > trend_start else "turun" if trend_end < trend_start else "stabil"

                    st.markdown(f"""
                    Tren {trend_direction}, menunjukkan pola jangka panjang dalam pembukaan server.
                    Tren naik berarti lebih banyak server dibuka seiring waktu.
                    """)

                with col2:
                    st.markdown("**Musiman**")

                    # Temukan bulan dengan pembukaan tertinggi
                    seasonal = decomposition['seasonal'].dropna()
                    if len(seasonal) >= 12:
                        monthly_seasonal = seasonal.groupby(seasonal.index.month).mean()
                        peak_month = monthly_seasonal.idxmax()
                        peak_month_name = pd.Timestamp(year=2020, month=peak_month, day=1).strftime('%B')

                        st.markdown(f"""
                        Menunjukkan pola berulang tahunan. 
                        Puncak terjadi di bulan **{peak_month_name}**, 
                        menunjukkan bulan dengan pembukaan server tertinggi.
                        """)
                    else:
                        st.markdown("""
                        Menunjukkan pola berulang. 
                        Puncak menunjukkan periode dengan pembukaan server tertinggi.
                        """)

                with col3:
                    st.markdown("**Residu**")

                    # Hitung statistik residual
                    resid = decomposition['resid'].dropna()
                    resid_std = resid.std()

                    st.markdown(f"""
                    Variasi acak (std: {resid_std:.2f}) yang tidak dapat dijelaskan oleh tren atau musiman.
                    Penyimpangan besar menunjukkan peristiwa tidak biasa dalam pembukaan server.
                    """)
            else:
                st.error("Dekomposisi time series gagal. Coba periode yang berbeda.")
        else:
            st.warning(
                f"Tidak cukup data untuk dekomposisi time series dengan periode {period}. Diperlukan minimal {min_length} bulan data.")
    else:
        # Gunakan data harian
        min_length = 2 * period

        if len(daily_data) >= min_length:
            # Atur indeks series ke datetime untuk dekomposisi
            ts = daily_data.set_index('Date')['Count']

            # Informasi jumlah data
            st.info(f"Menggunakan {len(ts)} hari data untuk dekomposisi dengan periode {period} hari.")

            from utils.time_series import perform_seasonal_decomposition
            decomposition = perform_seasonal_decomposition(ts, period=period)

            if decomposition:
                # Plot dekomposisi (sama seperti kode di atas)
                # ...
                pass
            else:
                st.error("Dekomposisi time series gagal. Coba periode yang berbeda.")
        else:
            st.warning(
                f"Tidak cukup data untuk dekomposisi time series dengan periode {period}. Diperlukan minimal {min_length} hari data.")


def render_time_series_forecast(df, color_scheme):
    """Render prediksi time series menggunakan ARIMA/SARIMA."""
    st.markdown("""
    ARIMA (AutoRegressive Integrated Moving Average) adalah model statistik untuk
    memprediksi nilai di masa depan berdasarkan pola dalam data historis.

    SARIMA (Seasonal ARIMA) adalah ekstensi ARIMA yang juga memperhitungkan pola musiman.
    """)

    # Siapkan data time series
    daily_data, monthly_data = prepare_time_series_data(df)

    # Pilihan periode forecast
    forecast_period = st.slider(
        "Periode Prediksi (hari)",
        min_value=30,
        max_value=365,
        value=90,
        step=30,
        help="Pilih berapa hari ke depan yang ingin Anda prediksi"
    )

    # Pilihan model
    model_type = st.radio(
        "Pilih Model Prediksi",
        ["ARIMA (Auto-tuned)", "SARIMA (Seasonal)"],
        horizontal=True
    )

    # Pilihan data untuk prediksi
    data_type = st.radio(
        "Pilih Jenis Data",
        ["Data Harian", "Data Bulanan"],
        horizontal=True
    )

    # Persiapkan data yang sesuai
    if data_type == "Data Harian":
        ts_data = daily_data.set_index('Date')['Count']
    else:
        ts_data = monthly_data.set_index('Date')['Count']

    # Tampilkan informasi data
    st.info(f"Menggunakan {len(ts_data)} titik data untuk prediksi {forecast_period} hari ke depan.")

    # Fit model dan prediksi
    try:
        if model_type == "ARIMA (Auto-tuned)":
            # Temukan parameter ARIMA optimal
            optimal_params = find_optimal_arima_params(ts_data)
            st.markdown(
                f"Parameter ARIMA optimal yang ditemukan: p={optimal_params[0]}, d={optimal_params[1]}, q={optimal_params[2]}")

            # Prediksi dengan ARIMA
            forecast_values, forecast_dates, model_fit = forecast_with_arima(
                ts_data,
                periods=forecast_period // (30 if data_type == "Data Bulanan" else 1),
                order=optimal_params
            )
        else:  # SARIMA
            # Prediksi dengan SARIMA
            forecast_values, forecast_dates, model_fit = forecast_with_sarima(
                ts_data,
                periods=forecast_period // (30 if data_type == "Data Bulanan" else 1)
            )

        if forecast_values is not None and len(forecast_values) > 0:
            # Plot forecast
            fig = go.Figure()

            # Data historis
            fig.add_trace(
                go.Scatter(
                    x=ts_data.index,
                    y=ts_data.values,
                    mode='lines',
                    name='Data Historis',
                    line=dict(color=color_scheme[1])
                )
            )

            # Forecast
            fig.add_trace(
                go.Scatter(
                    x=forecast_dates,
                    y=forecast_values,
                    mode='lines',
                    name='Prediksi',
                    line=dict(color=color_scheme[3], dash='dash')
                )
            )

            # Tambahkan interval kepercayaan jika tersedia
            if hasattr(model_fit, 'get_forecast') and model_type == "ARIMA (Auto-tuned)":
                forecast_obj = model_fit.get_forecast(steps=len(forecast_values))
                conf_int = forecast_obj.conf_int()

                fig.add_trace(
                    go.Scatter(
                        x=forecast_dates,
                        y=conf_int.iloc[:, 0],
                        mode='lines',
                        line=dict(width=0),
                        showlegend=False
                    )
                )

                fig.add_trace(
                    go.Scatter(
                        x=forecast_dates,
                        y=conf_int.iloc[:, 1],
                        mode='lines',
                        fill='tonexty',
                        fillcolor='rgba(255, 255, 255, 0.1)',
                        line=dict(width=0),
                        name='Interval Kepercayaan 95%'
                    )
                )

            fig.update_layout(
                template="plotly_dark",
                title=f'Prediksi Pembukaan Server ({model_type})',
                xaxis_title='Tanggal',
                yaxis_title='Jumlah Server',
                legend=dict(x=0, y=1, traceorder='normal'),
                height=500
            )

            fig.update_traces(
                hovertemplate='<b>%{x|%d %b %Y}</b><br>%{y:.1f} server'
            )

            st.plotly_chart(fig, use_container_width=True)

            # Tampilkan ringkasan forecast pembukaan server di masa depan
            st.subheader("Ringkasan Prediksi Pembukaan Server")

            # Buat summary berdasarkan tipe data
            if data_type == "Data Bulanan":
                forecast_df = pd.DataFrame({
                    'Date': forecast_dates,
                    'Forecast': forecast_values
                })

                forecast_df['Month'] = forecast_df['Date'].dt.strftime('%Y-%m')
                monthly_forecast = forecast_df.groupby('Month')['Forecast'].sum().reset_index()
                monthly_forecast['Forecast'] = monthly_forecast['Forecast'].round(1)
                monthly_forecast.columns = ['Bulan', 'Perkiraan Jumlah Server']

                st.dataframe(monthly_forecast, use_container_width=True)
            else:
                # Kelompokkan data harian berdasarkan bulan dan minggu
                forecast_df = pd.DataFrame({
                    'Date': forecast_dates,
                    'Forecast': forecast_values
                })

                forecast_df['Month'] = forecast_df['Date'].dt.strftime('%Y-%m')
                forecast_df['Week'] = forecast_df['Date'].dt.strftime('%Y-W%U')

                # Summary bulanan
                monthly_forecast = forecast_df.groupby('Month')['Forecast'].sum().reset_index()
                monthly_forecast['Forecast'] = monthly_forecast['Forecast'].round(1)
                monthly_forecast.columns = ['Bulan', 'Perkiraan Jumlah Server']

                # Summary mingguan
                weekly_forecast = forecast_df.groupby('Week')['Forecast'].sum().reset_index()
                weekly_forecast['Forecast'] = weekly_forecast['Forecast'].round(1)
                weekly_forecast.columns = ['Minggu', 'Perkiraan Jumlah Server']

                tab1, tab2 = st.tabs(["Prediksi Bulanan", "Prediksi Mingguan"])

                with tab1:
                    st.dataframe(monthly_forecast, use_container_width=True)

                with tab2:
                    st.dataframe(weekly_forecast, use_container_width=True)
        else:
            st.error("Forecasting gagal. Coba model atau parameter lain.")
    except Exception as e:
        st.error(f"Error dalam prediksi: {e}")
        st.info("Coba gunakan model atau data lain untuk prediksi.")


def render_next_server_predictions(df, color_scheme):
    """Render prediksi spesifik untuk 5 server berikutnya."""
    st.markdown("""
    Berdasarkan analisis pola pembukaan server sebelumnya, berikut adalah prediksi detail
    untuk server berikutnya yang mungkin akan dibuka.
    """)

    # Pilihan jumlah server untuk diprediksi
    num_servers = st.slider(
        "Jumlah Server yang Diprediksi",
        min_value=3,
        max_value=10,
        value=5,
        help="Berapa banyak server berikutnya yang ingin diprediksi"
    )

    # Prediksi server berikutnya
    next_servers = predict_next_servers(df, num_servers=num_servers)

    if not next_servers.empty:
        # Menampilkan prediksi
        st.success(f"Prediksi Pembukaan {num_servers} Server Berikutnya:")

        # Pastikan kolom ditampilkan dalam urutan yang benar
        column_order = ['ServerId', 'Tanggal', 'Jam', 'DistrictId', 'MapType', 'Estimasi']
        if all(col in next_servers.columns for col in column_order):
            display_servers = next_servers[column_order].copy()

            # Format tanggal untuk membuatnya lebih mudah dibaca
            display_servers['Tanggal'] = pd.to_datetime(display_servers['Tanggal']).dt.strftime('%d %b %Y')

            st.dataframe(display_servers, use_container_width=True)
        else:
            st.dataframe(next_servers, use_container_width=True)

        # Analisis pola waktu untuk pola waktu
        time_patterns = analyze_time_patterns(df)

        # Tata letak dua kolom untuk prediksi server dan pola waktu
        col1, col2 = st.columns([2, 1])

        with col1:
            # Visualisasi prediksi
            st.subheader("Visualisasi Pembukaan Server Berikutnya")
    
            # Buat data gabungan untuk visualisasi
            df_sorted = df.sort_values('OpenDateTime')
    
            # Ambil 30 server terakhir
            recent_servers = df_sorted.tail(30).copy()
            recent_servers['Type'] = 'Historis'
    
            # Siapkan data prediksi
            pred_servers = next_servers.copy()
            pred_servers['OpenDateTime'] = pd.to_datetime(pred_servers['Tanggal'] + ' ' + pred_servers['Jam'])
            
            # PERBAIKAN: Pastikan keduanya memiliki status timezone yang sama
            # Jika df historis memiliki timezone, tambahkan timezone yang sama ke prediksi
            if hasattr(recent_servers['OpenDateTime'].iloc[0], 'tz') and recent_servers['OpenDateTime'].iloc[0].tz is not None:
                # Ambil timezone dari data historis
                hist_tz = recent_servers['OpenDateTime'].iloc[0].tz
                # Terapkan ke data prediksi
                pred_servers['OpenDateTime'] = pred_servers['OpenDateTime'].dt.tz_localize(hist_tz)
            # Jika df historis tidak memiliki timezone, hapus timezone dari prediksi jika ada
            else:
                # Pastikan data historis tidak memiliki timezone
                recent_servers['OpenDateTime'] = recent_servers['OpenDateTime'].dt.tz_localize(None)
                # Pastikan data prediksi juga tidak memiliki timezone
                if hasattr(pred_servers['OpenDateTime'].iloc[0], 'tz') and pred_servers['OpenDateTime'].iloc[0].tz is not None:
                    pred_servers['OpenDateTime'] = pred_servers['OpenDateTime'].dt.tz_localize(None)
                    
            pred_servers['Type'] = 'Prediksi'
    
            # Gabungkan data (sekarang timezone sudah konsisten)
            vis_data = pd.concat([
                recent_servers[['ServerId', 'OpenDateTime', 'Type']],
                pred_servers[['ServerId', 'OpenDateTime', 'Type']]
            ]).sort_values('OpenDateTime')

            # Plot timeline
            fig = px.scatter(
                vis_data,
                x='OpenDateTime',
                y=[1] * len(vis_data),  # Semua pada tinggi yang sama
                color='Type',
                size=[10 if t == 'Prediksi' else 7 for t in vis_data['Type']],
                hover_data={'ServerId': True, 'OpenDateTime': True, 'Type': True},
                color_discrete_map={'Historis': color_scheme[1], 'Prediksi': color_scheme[4]},
                title='Timeline Pembukaan Server'
            )

            # Hilangkan label y
            fig.update_layout(
                template="plotly_dark",
                height=300,
                xaxis_title='Tanggal',
                yaxis_title='',
                yaxis=dict(showticklabels=False),
                showlegend=True
            )

            # Tambahkan notasi untuk server ID
            for i, row in vis_data.iterrows():
                if row['Type'] == 'Prediksi':
                    fig.add_annotation(
                        x=row['OpenDateTime'],
                        y=1,
                        text=str(row['ServerId']),
                        showarrow=True,
                        arrowhead=1,
                        arrowsize=1,
                        arrowwidth=1,
                        arrowcolor=color_scheme[4]
                    )

            st.plotly_chart(fig, use_container_width=True)

            # Metodologi prediksi
            with st.expander("ℹ️ Cara Perhitungan Prediksi", expanded=False):
                st.markdown("""
                **Metodologi Prediksi Server:**

                1. **Interval Waktu**: Dihitung dari interval rata-rata antara pembukaan server terakhir

                2. **Jam Pembukaan**: Didasarkan pada jam pembukaan yang paling umum dari 30 server terakhir

                3. **Hari dalam Minggu**: Disesuaikan dengan hari dalam seminggu yang paling sering digunakan untuk pembukaan server

                4. **Jenis Peta**: Mengikuti pola bergantian antara jenis peta yang diidentifikasi dari data historis

                5. **District ID**: Dihitung berdasarkan peningkatan dari server terakhir

                Prediksi ini merupakan estimasi terbaik berdasarkan pola historis, namun jadwal pembukaan server yang sebenarnya mungkin bervariasi.
                """)

        with col2:
            # Tampilkan analisis pola waktu
            st.markdown("### Analisis Pola Waktu")
            st.markdown("Pola waktu yang digunakan untuk prediksi:")

            # Buat kartu metrik yang lebih menarik untuk pola waktu
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Jam Pembukaan Umum", f"{time_patterns['most_common_hour']}:00")
            st.markdown('<p class="card-explanation">Jam di mana server paling sering dibuka</p>',
                        unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Interval Antar Server (jam)", f"{time_patterns['median_hours_between_servers']:.1f}")
            st.markdown('<p class="card-explanation">Rata-rata waktu antara pembukaan server baru</p>',
                        unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            days = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Hari Pembukaan Umum", time_patterns['most_common_day'])
            st.markdown(
                '<p class="card-explanation">Hari dalam seminggu yang paling sering digunakan untuk pembukaan server</p>',
                unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Tampilkan grafik pola hari dalam minggu
            st.markdown("### Pola Hari (30 Server Terakhir)")

            # Persiapkan data untuk grafik
            day_counts = pd.DataFrame(list(time_patterns['weekday_counts'].items()), columns=['Day', 'Count'])

            # Tetapkan urutan hari
            day_order = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
            day_counts = day_counts.set_index('Day').reindex(day_order).reset_index()

            fig = px.bar(
                day_counts,
                x='Day',
                y='Count',
                title='Pola Hari (30 Server Terakhir)',
                color='Count',
                color_continuous_scale=color_scheme
            )

            fig.update_layout(
                template="plotly_dark",
                height=250,
                xaxis_title='',
                yaxis_title='Jumlah Server',
                coloraxis_showscale=False
            )

            st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Prediksi server berikutnya gagal. Silakan coba lagi dengan data lebih banyak.")
