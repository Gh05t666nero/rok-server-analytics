# app.py
import streamlit as st
from datetime import datetime
import pandas as pd

# Import modul kustom
from utils.data_loader import load_data_from_api
from utils.data_processor import process_server_data, filter_dataframe
from utils.time_series import perform_seasonal_decomposition, forecast_with_arima, predict_next_servers

# Import komponen UI
from components.overview import render_overview_tab
from components.time_analysis import render_time_analysis_tab
from components.map_analysis import render_map_analysis_tab
from components.predictions import render_prediction_tab
from styles.custom_styles import apply_custom_styles

# Konfigurasi halaman
st.set_page_config(
    page_title="Analisis Server Rise of Kingdoms",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Terapkan custom CSS
apply_custom_styles()

# Header aplikasi
st.markdown('<p class="main-header">Analisis Server Rise of Kingdoms</p>', unsafe_allow_html=True)

# Navigasi dengan penjelasan
st.markdown("<div class='nav-section'>", unsafe_allow_html=True)
st.markdown(f"""
<div style="display: flex; align-items: center; justify-content: space-between;">
    <div>
        <h2 style="margin: 0; color: #BB86FC; font-size: 1.3rem;">📊 Dashboard Analisis Server</h2>
        <p style="margin: 8px 0 0 0;">Dashboard ini menyediakan analisis dan prediksi untuk data server game Rise of Kingdoms. Gunakan tab di bawah untuk menjelajahi berbagai jenis analisis.</p>
    </div>
    <div style="background-color: rgba(0,0,0,0.2); padding: 8px 16px; border-radius: 8px; display: inline-block;">
        <span style="color: #03DAC6; font-weight: 500;">Update terakhir:</span> 
        <span style="color: #E0E0E0;">{datetime.now().strftime('%d %b %Y %H:%M')}</span>
    </div>
</div>
""", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)


# Fungsi utama
def main():
    # Memuat data saat aplikasi dimulai
    with st.spinner("Mengambil data dari API..."):
        data = load_data_from_api()
        df = process_server_data(data)

    if df is not None and not df.empty:
        # Tampilkan statistik cepat dalam baris di bagian atas
        display_key_metrics(df)

        # Sidebar untuk filter
        filters = create_sidebar_filters(df)

        # Terapkan filter
        filtered_df = filter_dataframe(df, filters)

        # Tampilkan informasi filter
        st.sidebar.success(f"Menampilkan {len(filtered_df)} dari {len(df)} server")

        # Pilih tema warna
        chart_theme = select_color_theme()

        # Definisikan palet warna berdasarkan tema
        color_scheme = get_color_scheme(chart_theme)

        # Buat tab utama
        create_main_tabs(df, filtered_df, color_scheme)

        # Footer
        display_footer()
    else:
        st.error("Gagal memuat atau memproses data. Silakan periksa koneksi internet Anda dan coba lagi.")

        # Tambahkan tombol coba lagi
        if st.button("Coba Lagi"):
            st.experimental_rerun()


def display_key_metrics(df):
    """Menampilkan metrik utama di bagian atas dashboard."""
    st.markdown('<div class="metric-section">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Server", len(df))
        st.markdown('<p class="card-explanation">Jumlah total server game yang tersedia</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Server Pertama", df['OpenDateTime'].min().strftime('%Y-%m-%d'))
        st.markdown('<p class="card-explanation">Tanggal server pertama dibuka</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Server Terbaru", df['OpenDateTime'].max().strftime('%Y-%m-%d'))
        st.markdown('<p class="card-explanation">Tanggal server terbaru dibuka</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Jenis Peta", df['MapType'].nunique())
        st.markdown('<p class="card-explanation">Jumlah jenis peta yang berbeda</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


def create_sidebar_filters(df):
    """Membuat filter di sidebar dan mengembalikan konfigurasi filter."""
    st.sidebar.markdown('<p class="sub-header">Filter & Pengaturan</p>', unsafe_allow_html=True)

    # Bagian filter
    st.sidebar.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.sidebar.markdown("### Filter Data")
    st.sidebar.markdown("Gunakan filter berikut untuk menyaring data server yang ditampilkan:")

    # Filter jenis peta
    all_map_types = ['Semua'] + sorted(df['MapType'].unique().tolist())
    selected_map_type = st.sidebar.selectbox("Pilih Jenis Peta", all_map_types)

    # Filter tahun
    all_years = ['Semua'] + sorted(df['Year'].unique().tolist(), reverse=True)
    selected_year = st.sidebar.selectbox("Pilih Tahun", all_years)

    # Filter rentang tanggal
    min_date = df['OpenDateTime'].min().date()
    max_date = df['OpenDateTime'].max().date()
    date_range = st.sidebar.date_input(
        "Rentang Tanggal",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    # Filter preset waktu
    time_preset = st.sidebar.radio(
        "Filter Waktu Cepat",
        ["Semua Waktu", "30 Hari Terakhir", "90 Hari Terakhir", "1 Tahun Terakhir"]
    )
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

    # Tambahkan opsi ekspor di sidebar
    st.sidebar.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.sidebar.markdown("### Ekspor Data")
    add_export_options(df)
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

    # Tambahkan bantuan cepat di sidebar
    st.sidebar.markdown('<div class="filter-section">', unsafe_allow_html=True)
    with st.sidebar.expander("💡 Tips Penggunaan"):
        st.markdown("""
        **Panduan Singkat Dashboard:**

        1. **Filter Data**: Gunakan bagian filter di atas untuk memilih server mana yang ingin ditampilkan.

        2. **Tab**: Klik tab di bawah untuk melihat analisis berbeda.
           - **Ikhtisar**: Melihat ringkasan data server
           - **Analisis Waktu**: Melihat pola pembukaan server berdasarkan waktu
           - **Analisis Peta**: Melihat distribusi tipe peta
           - **Prediksi**: Melihat perkiraan pembukaan server berikutnya

        3. **Interaksi Grafik**: Pada sebagian besar grafik, Anda dapat:
           - Perbesar dengan menyeret area
           - Klik legenda untuk menyembunyikan/menampilkan data
           - Gerakkan kursor ke grafik untuk detail
        """)
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

    # Kumpulkan semua filter ke dalam dictionary
    return {
        'map_type': selected_map_type,
        'year': selected_year,
        'date_range': date_range,
        'time_preset': time_preset
    }


def add_export_options(df):
    """Menambahkan opsi ekspor data."""
    st.sidebar.markdown("Unduh data yang ditampilkan:")

    export_format = st.sidebar.selectbox(
        "Format Ekspor",
        ["CSV", "Excel", "JSON"]
    )

    if st.sidebar.button("Ekspor Data"):
        if export_format == "CSV":
            csv = df.to_csv(index=False).encode('utf-8')
            st.sidebar.download_button(
                label="Unduh CSV",
                data=csv,
                file_name='data_server_rok.csv',
                mime='text/csv',
            )
        elif export_format == "Excel":
            # Menggunakan BytesIO untuk Excel
            import io
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='ServerData')
            excel_data = buffer.getvalue()
            st.sidebar.download_button(
                label="Unduh Excel",
                data=excel_data,
                file_name='data_server_rok.xlsx',
                mime='application/vnd.ms-excel',
            )
        elif export_format == "JSON":
            json_data = df.to_json(orient='records', date_format='iso')
            st.sidebar.download_button(
                label="Unduh JSON",
                data=json_data,
                file_name='data_server_rok.json',
                mime='application/json',
            )


def select_color_theme():
    """Membuat selector tema warna di sidebar."""
    st.sidebar.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.sidebar.markdown("### Pengaturan Tampilan")
    st.sidebar.markdown("Ubah tampilan grafik sesuai preferensi:")

    chart_theme = st.sidebar.select_slider(
        "Tema Warna Grafik",
        options=["Biru Gelap", "Ungu", "Teal", "Magenta"],
        value="Biru Gelap"
    )

    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    return chart_theme


def get_color_scheme(chart_theme):
    """Mengambil skema warna berdasarkan tema yang dipilih."""
    import plotly.express as px

    if chart_theme == "Biru Gelap":
        return px.colors.sequential.Blues_r
    elif chart_theme == "Ungu":
        return px.colors.sequential.Purples_r
    elif chart_theme == "Teal":
        return px.colors.sequential.Teal_r
    else:  # Magenta
        return px.colors.sequential.Magenta_r


def create_main_tabs(df, filtered_df, color_scheme):
    """Membuat tab utama aplikasi."""
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Ikhtisar", "🕒 Analisis Waktu", "🗺️ Analisis Peta", "📈 Prediksi"])

    with tab1:
        render_overview_tab(df, filtered_df, color_scheme)

    with tab2:
        render_time_analysis_tab(filtered_df, color_scheme)

    with tab3:
        render_map_analysis_tab(filtered_df, color_scheme)

    with tab4:
        render_prediction_tab(df, color_scheme)


def display_footer():
    """Menampilkan footer aplikasi."""
    st.markdown('<div class="footer">', unsafe_allow_html=True)
    st.markdown("""
    <div style="display: flex; flex-direction: column; align-items: center; gap: 8px;">
        <div style="font-weight: 500; color: #BB86FC;">Dashboard Analisis Server Rise of Kingdoms</div>
        <div style="display: flex; align-items: center; gap: 16px; margin: 8px 0;">
            <div style="display: flex; align-items: center; gap: 4px;">
                <span style="color: #03DAC6;">💻</span> Dibuat dengan Streamlit
            </div>
            <div style="display: flex; align-items: center; gap: 4px;">
                <span style="color: #03DAC6;">📊</span> Visualisasi dengan Plotly
            </div>
            <div style="display: flex; align-items: center; gap: 4px;">
                <span style="color: #03DAC6;">🔍</span> Data dari API Game
            </div>
        </div>
        <div>© 2025 - Semua Hak Dilindungi</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()