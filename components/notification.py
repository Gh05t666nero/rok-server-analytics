# components/notification.py
import streamlit as st
from utils.notification import NotificationManager
import json
import time
import datetime
import pytz
from config import TIME_CONFIG, NOTIFICATION_CONFIG


# Rate limiting untuk form submissions
def _is_rate_limited(key, limit_seconds=60):
    """Check if an action is rate limited."""
    current_time = time.time()

    # Get the last timestamp from session state
    last_time = st.session_state.get(f"last_{key}_time", 0)

    # Check if enough time has passed
    if current_time - last_time < limit_seconds:
        return True

    # Update the timestamp
    st.session_state[f"last_{key}_time"] = current_time
    return False


def render_notification_subscription():
    """Render form berlangganan notifikasi."""
    st.markdown('<div class="notification-section">', unsafe_allow_html=True)
    st.markdown("### 🔔 Berlangganan Notifikasi Server Baru")

    # Inisialisasi notification manager
    notification_manager = NotificationManager()

    # Tab untuk jenis langganan
    tab1, tab2 = st.tabs(["Notifikasi Email", "Notifikasi Telegram"])

    with tab1:
        # Form langganan email
        st.markdown("""
        Masukkan alamat email Anda untuk mendapatkan notifikasi saat server baru akan dibuka.
        Anda akan menerima email beberapa jam sebelum server dibuka.
        """)

        with st.form("email_subscription_form"):
            email = st.text_input("Alamat Email")
            submitted = st.form_submit_button("Berlangganan")

            if submitted:
                # Check for rate limiting
                if _is_rate_limited("email_subscription", 60):
                    st.error("Terlalu banyak permintaan. Silakan coba lagi setelah beberapa saat.")
                elif not email:
                    st.error("Harap masukkan alamat email.")
                else:
                    # Sanitasi input
                    email = email.strip().lower()
                    success = notification_manager.add_email_subscriber(email)
                    if success:
                        st.success(f"Berhasil berlangganan dengan email {email}!")
                    else:
                        st.error("Email tidak valid atau sudah berlangganan.")

        # Bagian berhenti berlangganan (bukan sebagai expander)
        st.markdown("#### Berhenti Berlangganan")
        with st.form("email_unsubscribe_form"):
            unsub_email = st.text_input("Alamat Email")
            unsub_submitted = st.form_submit_button("Berhenti Berlangganan")

            if unsub_submitted:
                # Check for rate limiting
                if _is_rate_limited("email_unsubscription", 60):
                    st.error("Terlalu banyak permintaan. Silakan coba lagi setelah beberapa saat.")
                elif not unsub_email:
                    st.error("Harap masukkan alamat email.")
                else:
                    # Sanitasi input
                    unsub_email = unsub_email.strip().lower()
                    success = notification_manager.remove_email_subscriber(unsub_email)
                    if success:
                        st.success(f"Berhasil berhenti berlangganan untuk {unsub_email}.")
                    else:
                        st.error("Email tidak ditemukan dalam daftar langganan.")

    with tab2:
        # Dapatkan telegram bot token yang terkonfigurasi
        telegram_token = NOTIFICATION_CONFIG.get("telegram_token")
        bot_username = "undefined_bot"

        # Coba dapatkan username bot dari token (hanya jika token tersedia)
        if telegram_token:
            try:
                # Ekstrak username bot dari token (opsional)
                bot_id = telegram_token.split(':')[0]
                # Gunakan placeholder username jika tidak bisa mendapatkan yang sebenarnya
                bot_username = f"rok_server_bot_{bot_id[-3:]}"
            except Exception:
                pass

        # Panduan langganan Telegram
        st.markdown(f"""
        ### Cara Berlangganan Notifikasi Telegram:

        1. Mulai obrolan dengan bot kami: [t.me/{bot_username}](https://t.me/{bot_username})
        2. Kirim perintah `/start` ke bot
        3. Kirim perintah `/subscribe` untuk berlangganan
        4. Kirim perintah `/unsubscribe` untuk berhenti berlangganan

        Anda akan menerima notifikasi Telegram saat server baru akan dibuka.
        """)

        # Tampilkan QR code dinamis jika checkbox dicentang
        if st.checkbox("Tampilkan QR Code"):
            st.markdown("""
            Pindai QR code ini dengan aplikasi Telegram Anda:
            """)
            qr_data = f"https://t.me/{bot_username}"
            qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={qr_data}"
            st.image(qr_url, width=200)

            # Tambahkan disclaimer
            st.info(
                "Catatan: Pastikan bot sudah dikonfigurasi dengan benar. Jika belum, silakan hubungi administrator.")

    st.markdown('</div>', unsafe_allow_html=True)


def render_notification_settings():
    """Render pengaturan notifikasi untuk admin."""
    if st.session_state.get('admin_mode', False):
        st.markdown("### Pengaturan Notifikasi")

        # Inisialisasi notification manager
        notification_manager = NotificationManager()

        # Tab untuk berbagai jenis pengaturan
        admin_tab1, admin_tab2, admin_tab3 = st.tabs(["Daftar Pelanggan", "Uji Notifikasi", "Log Aktivitas"])

        with admin_tab1:
            # Tampilkan daftar pelanggan
            st.markdown("#### Daftar Pelanggan Email")
            email_subscribers = notification_manager.subscribers.get("email", [])

            if email_subscribers:
                # Buat dataframe dengan informasi tambahan
                email_data = []
                for email in email_subscribers:
                    email_data.append({
                        "Email": email,
                        "Status": "Aktif",
                        "Tanggal Berlangganan": "N/A"  # Bisa diganti dengan tanggal sebenarnya jika disimpan
                    })

                st.dataframe(email_data)

                # Tambahkan opsi untuk expor data
                if st.button("Ekspor Data Pelanggan Email"):
                    # Check for rate limiting
                    if _is_rate_limited("export_subscribers", 300):  # 5 menit
                        st.error("Terlalu banyak permintaan. Silakan coba lagi setelah beberapa saat.")
                    else:
                        # Generate file JSON untuk diunduh
                        email_json = json.dumps({"email_subscribers": email_subscribers})
                        st.download_button(
                            label="Unduh Data (JSON)",
                            data=email_json,
                            file_name="email_subscribers.json",
                            mime="application/json"
                        )
            else:
                st.info("Belum ada pelanggan email.")

            st.markdown("#### Daftar Pelanggan Telegram")
            telegram_subscribers = notification_manager.subscribers.get("telegram", [])

            if telegram_subscribers:
                # Buat dataframe dengan informasi tambahan
                telegram_data = []
                for telegram_id in telegram_subscribers:
                    telegram_data.append({
                        "Telegram ID": telegram_id,
                        "Status": "Aktif",
                        "Tanggal Berlangganan": "N/A"
                    })

                st.dataframe(telegram_data)

                # Tambahkan opsi untuk expor data
                if st.button("Ekspor Data Pelanggan Telegram"):
                    # Check for rate limiting
                    if _is_rate_limited("export_subscribers", 300):  # 5 menit
                        st.error("Terlalu banyak permintaan. Silakan coba lagi setelah beberapa saat.")
                    else:
                        # Generate file JSON untuk diunduh
                        telegram_json = json.dumps({"telegram_subscribers": telegram_subscribers})
                        st.download_button(
                            label="Unduh Data (JSON)",
                            data=telegram_json,
                            file_name="telegram_subscribers.json",
                            mime="application/json"
                        )
            else:
                st.info("Belum ada pelanggan Telegram.")

        with admin_tab2:
            # Form ujicoba pengiriman notifikasi
            st.markdown("#### Uji Pengiriman Notifikasi")

            with st.form("test_notification_form"):
                test_server_id = st.number_input("ID Server", min_value=1, value=2000)
                test_date = st.date_input("Tanggal Pembukaan")
                test_time = st.time_input("Jam Pembukaan")
                test_map_type = st.selectbox("Jenis Peta", [
                    "Sever_Map_G1_1_v2",
                    "Sever_Map_G1_2_v2",
                    "Sever_Map_G1_3_v2",
                    "Sever_Map_G1_4_v2"
                ])
                test_district = st.number_input("ID District", min_value=1, value=250)

                submitted = st.form_submit_button("Kirim Notifikasi Uji")

                if submitted:
                    # Check for rate limiting (10 menit antara pengiriman)
                    if _is_rate_limited("test_notification", 600):
                        st.error("Terlalu banyak permintaan notifikasi uji. Harap tunggu beberapa saat.")
                    else:
                        # Format data server
                        server_data = {
                            "ServerId": int(test_server_id),
                            "Tanggal": test_date.strftime("%Y-%m-%d"),
                            "Jam": test_time.strftime("%H:%M:%S"),
                            "MapType": test_map_type,
                            "DistrictId": int(test_district),
                            "Estimasi": "Uji coba notifikasi"
                        }

                        # Kirim notifikasi
                        try:
                            success = notification_manager.notify_new_server(server_data)

                            if success:
                                st.success("Notifikasi uji berhasil dikirim!")
                            else:
                                st.error("Gagal mengirim notifikasi uji. Periksa pengaturan API.")
                        except Exception as e:
                            st.error(f"Error saat mengirim notifikasi: {str(e)}")

        with admin_tab3:
            # Panel log aktivitas sederhana
            st.markdown("#### Log Aktivitas Notifikasi")
            st.info(
                "Fitur log aktivitas akan tersedia dalam pembaruan mendatang. Silakan periksa log server untuk informasi lebih lanjut.")


def schedule_notification_check(df, notification_manager):
    """
    Memeriksa apakah perlu mengirim notifikasi untuk server yang akan dibuka.

    Parameters:
        df (pandas.DataFrame): DataFrame dengan data server
        notification_manager (NotificationManager): Instance dari NotificationManager
    """
    try:
        # Hanya jalankan jika fitur ini tidak di-rate-limit
        if _is_rate_limited("notification_check", 3600):  # 1 jam
            return

        import datetime
        import pytz
        from config import TIME_CONFIG, NOTIFICATION_CONFIG
        from utils.time_series import predict_next_servers

        # Dapatkan waktu sekarang di zona waktu yang dikonfigurasi
        timezone = pytz.timezone(TIME_CONFIG["timezone"])
        now = datetime.datetime.now(timezone)

        # Prediksi server berikutnya (maksimal 3 untuk efisiensi)
        next_servers = predict_next_servers(df, num_servers=3)

        if not next_servers.empty:
            for _, server in next_servers.iterrows():
                try:
                    # Konversi string tanggal dan waktu ke datetime
                    server_datetime_str = f"{server['Tanggal']} {server['Jam']}"
                    server_datetime = datetime.datetime.strptime(server_datetime_str, "%Y-%m-%d %H:%M:%S")

                    # Tambahkan timezone
                    server_datetime = timezone.localize(server_datetime)

                    # Hitung selisih waktu dalam jam
                    time_diff = (server_datetime - now).total_seconds() / 3600

                    # Jika waktu pembukaan dalam interval notifikasi (default 24 jam)
                    notification_interval = NOTIFICATION_CONFIG.get("notification_interval", 24)

                    # Cek jika dalam interval notifikasi (misalnya 24-28 jam sebelum pembukaan)
                    # Gunakan rentang untuk menghindari notifikasi duplikat
                    if notification_interval <= time_diff <= (notification_interval + 4):
                        # Simpan server_id terakhir yang dinotifikasikan di session state
                        last_notified = st.session_state.get('last_notified_server_id', 0)

                        # Pastikan tidak mengirim notifikasi yang sama dua kali
                        if server['ServerId'] != last_notified:
                            # Kirim notifikasi
                            notification_manager.notify_new_server(server.to_dict())

                            # Update server_id terakhir
                            st.session_state['last_notified_server_id'] = server['ServerId']
                except Exception as e:
                    # Log error tapi jangan crash aplikasi
                    import logging
                    logging.getLogger("notification_scheduler").error(f"Error scheduling notification: {e}")
    except Exception as e:
        # Tangkap semua exception untuk mencegah dashboard crash
        import logging
        logging.getLogger("notification_scheduler").error(f"Fatal error in notification scheduler: {e}")