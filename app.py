# app.py
import streamlit as st

# IMPORTANT: st.set_page_config must be the first st.* command used
st.set_page_config(
    page_title="Analisis Server Rise of Kingdoms",
    layout="wide",
    initial_sidebar_state="expanded"
)

from datetime import datetime
import pandas as pd
import pytz
import logging
import time
import os

# Konfigurasi logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("app")

# Import config terlebih dahulu untuk mengatur environment
from config import TIME_CONFIG, APP_CONFIG, NOTIFICATION_CONFIG

# Import modul kustom
from utils.data_loader import load_data_from_api
from utils.data_processor import process_server_data, filter_dataframe
from utils.time_series import perform_seasonal_decomposition, forecast_with_arima, predict_next_servers
from utils.notification import NotificationManager

# Import komponen UI
from components.overview import render_overview_tab
from components.time_analysis import render_time_analysis_tab
from components.map_analysis import render_map_analysis_tab
from components.predictions import render_prediction_tab
from components.notification import render_notification_subscription, render_notification_settings, \
    schedule_notification_check
from styles.custom_styles import apply_custom_styles

# Pastikan direktori data ada
os.makedirs('data', exist_ok=True)

# Terapkan custom CSS
apply_custom_styles()

# Inisialisasi session state
if 'admin_mode' not in st.session_state:
    st.session_state.admin_mode = False

if 'last_notification_check' not in st.session_state:
    st.session_state.last_notification_check = 0

if 'last_notified_server_id' not in st.session_state:
    st.session_state.last_notified_server_id = 0

# Header aplikasi
st.markdown(f'<p class="main-header">{APP_CONFIG["title"]}</p>', unsafe_allow_html=True)

# Dapatkan waktu sekarang di zona waktu WIB
try:
    wib_timezone = pytz.timezone(TIME_CONFIG["timezone"])
    current_time_wib = datetime.now(wib_timezone)
except Exception as e:
    logger.error(f"Error setting timezone: {e}")
    # Fallback ke UTC jika timezone error
    current_time_wib = datetime.now()

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
        <span style="color: #E0E0E0;">{current_time_wib.strftime(TIME_CONFIG['datetime_format'])}</span>
    </div>
</div>
""", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)


# Fungsi utama
def main():
    # Batasi data fetching dengan caching
    @st.cache_data(ttl=600)  # Cache untuk 10 menit
    def fetch_and_process_data():
        with st.spinner("Mengambil data dari API..."):
            try:
                data = load_data_from_api()
                return process_server_data(data)
            except Exception as e:
                logger.error(f"Error loading data: {e}")
                return None

    # Memuat data saat aplikasi dimulai
    df = fetch_and_process_data()

    # Tampilkan pesan debugging jika mode debug aktif
    if APP_CONFIG.get("debug_mode", False):
        st.sidebar.info(f"Debug Mode: Active")
        if df is not None:
            st.sidebar.text(f"Data loaded: {len(df)} records")

    if df is not None and not df.empty:
        # Buat instance notification manager
        notification_manager = NotificationManager()

        # Jadwalkan pemeriksaan notifikasi (dengan batasan waktu)
        current_time = time.time()
        if current_time - st.session_state.last_notification_check > 3600:  # Cek setiap jam
            try:
                schedule_notification_check(df, notification_manager)
                st.session_state.last_notification_check = current_time
            except Exception as e:
                logger.error(f"Error checking notifications: {e}")

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

        # Tampilkan bagian notifikasi
        try:
            render_notification_subscription()
        except Exception as e:
            logger.error(f"Error rendering notification subscription: {e}")
            st.error("Terjadi kesalahan saat memuat formulir notifikasi. Silakan coba lagi nanti.")

        # Tampilkan pengaturan admin jika mode admin aktif
        if st.session_state.admin_mode:
            try:
                render_notification_settings()
            except Exception as e:
                logger.error(f"Error rendering notification settings: {e}")
                st.error("Terjadi kesalahan saat memuat pengaturan admin. Silakan coba lagi nanti.")

        # Footer
        display_footer()
    else:
        st.error("Gagal memuat atau memproses data. Silakan periksa koneksi internet Anda dan coba lagi.")

        # Tambahkan tombol coba lagi
        if st.button("Coba Lagi"):
            # Clear cache dan refresh
            st.cache_data.clear()
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

    # Mode Admin (gunakan password dari konfigurasi)
    admin_password = APP_CONFIG.get("admin_password", "")
    if admin_password:  # Hanya tampilkan jika password dikonfigurasi
        entered_password = st.sidebar.text_input("Admin", type="password")

        # Gunakan constant-time comparison untuk menghindari timing attacks
        if entered_password and admin_password and compare_digest(entered_password, admin_password):
            st.session_state.admin_mode = True
            st.sidebar.success("Mode Admin Aktif")
        elif entered_password:  # Hanya tampilkan error jika ada input
            # Hindari mengkonfirmasi password yang benar/salah
            time.sleep(0.5)  # Delay kecil untuk mencegah brute force
            st.session_state.admin_mode = False

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

        3. **Notifikasi**: Berlangganan untuk mendapatkan pemberitahuan saat server baru akan dibuka.

        4. **Interaksi Grafik**: Pada sebagian besar grafik, Anda dapat:
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


def compare_digest(a, b):
    """
    Constant-time string comparison to prevent timing attacks.
    """
    try:
        from hmac import compare_digest as hmac_compare
        return hmac_compare(a, b)
    except ImportError:
        # Fallback implementation if hmac.compare_digest is not available
        if len(a) != len(b):
            return False
        result = 0
        for x, y in zip(a, b):
            result |= ord(x) ^ ord(y)
        return result == 0


def add_export_options(df):
    """Menambahkan opsi ekspor data."""
    st.sidebar.markdown("Unduh data yang ditampilkan:")

    export_format = st.sidebar.selectbox(
        "Format Ekspor",
        ["CSV", "Excel", "JSON"]
    )

    if st.sidebar.button("Ekspor Data"):
        # Check for rate limiting (maksimal 1 ekspor per menit)
        current_time = time.time()
        last_export_time = st.session_state.get('last_export_time', 0)

        if current_time - last_export_time < 60:
            st.sidebar.error("Terlalu banyak ekspor. Harap tunggu beberapa saat.")
            return

        st.session_state['last_export_time'] = current_time

        # Batasi ukuran ekspor untuk keamanan
        if len(df) > 10000:
            export_df = df.head(10000)
            st.sidebar.warning("Ekspor dibatasi untuk 10.000 baris pertama.")
        else:
            export_df = df

        try:
            if export_format == "CSV":
                csv = export_df.to_csv(index=False).encode('utf-8')
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
                    export_df.to_excel(writer, index=False, sheet_name='ServerData')
                excel_data = buffer.getvalue()
                st.sidebar.download_button(
                    label="Unduh Excel",
                    data=excel_data,
                    file_name='data_server_rok.xlsx',
                    mime='application/vnd.ms-excel',
                )
            elif export_format == "JSON":
                json_data = export_df.to_json(orient='records', date_format='iso')
                st.sidebar.download_button(
                    label="Unduh JSON",
                    data=json_data,
                    file_name='data_server_rok.json',
                    mime='application/json',
                )
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            st.sidebar.error("Gagal mengekspor data. Silakan coba lagi nanti.")


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
        try:
            render_overview_tab(df, filtered_df, color_scheme)
        except Exception as e:
            logger.error(f"Error rendering overview tab: {e}")
            st.error("Terjadi kesalahan saat memuat tab ikhtisar. Silakan coba lagi nanti.")

    with tab2:
        try:
            render_time_analysis_tab(filtered_df, color_scheme)
        except Exception as e:
            logger.error(f"Error rendering time analysis tab: {e}")
            st.error("Terjadi kesalahan saat memuat tab analisis waktu. Silakan coba lagi nanti.")

    with tab3:
        try:
            render_map_analysis_tab(filtered_df, color_scheme)
        except Exception as e:
            logger.error(f"Error rendering map analysis tab: {e}")
            st.error("Terjadi kesalahan saat memuat tab analisis peta. Silakan coba lagi nanti.")

    with tab4:
        try:
            render_prediction_tab(df, color_scheme)
        except Exception as e:
            logger.error(f"Error rendering prediction tab: {e}")
            st.error("Terjadi kesalahan saat memuat tab prediksi. Silakan coba lagi nanti.")


def display_footer():
    """Menampilkan footer aplikasi."""
    # Dapatkan waktu sekarang di zona waktu WIB
    try:
        wib_timezone = pytz.timezone(TIME_CONFIG["timezone"])
        current_time_wib = datetime.now(wib_timezone)
    except:
        # Fallback ke UTC jika timezone error
        current_time_wib = datetime.now()

    st.markdown('<div class="footer">', unsafe_allow_html=True)
    st.markdown(f"""
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
        <div style="margin-top: 8px;">
            <a href="https://github.com/Gh05t666nero/rok-server-analytics" target="_blank" style="color: #03DAC6; text-decoration: none; margin: 0 8px;">
                <span>GitHub</span>
            </a>
            <span style="color: #666;">|</span>
            <a href="#" id="privacyLink" style="color: #03DAC6; text-decoration: none; margin: 0 8px;">
                <span>Kebijakan Privasi</span>
            </a>
        </div>
        <div>© {current_time_wib.year} - Semua Hak Dilindungi</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Tampilkan kebijakan privasi saat tombol diklik
    if st.button("Lihat Kebijakan Privasi", key="privacy_policy_button"):
        st.info("""
        **Kebijakan Privasi**

        Kami hanya mengumpulkan alamat email atau ID Telegram untuk tujuan pengiriman notifikasi saat server baru dibuka.

        Data ini tidak akan dibagikan dengan pihak ketiga dan hanya digunakan untuk tujuan notifikasi.

        Anda dapat berhenti berlangganan kapan saja melalui formulir di halaman ini.
        """)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Unhandled exception in main app: {e}", exc_info=True)
        st.error("Terjadi kesalahan yang tidak terduga. Silakan muat ulang halaman.")

        if APP_CONFIG.get("debug_mode", False):
            st.exception(e)