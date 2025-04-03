# components/dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.data_processor import calculate_statistics


def render_dashboard_header():
    """Render header dashboard dengan navigasi."""
    # Tombol bantuan di pojok kanan atas
    st.markdown("""
    <div id="helpButton" class="help-button" onclick="toggleHelp()">?</div>
    <div id="helpPanel" class="help-panel" style="display: none;">
        <h3>Bantuan Dashboard</h3>
        <p>Dashboard ini menampilkan analisis dan prediksi server game Rise of Kingdoms.</p>
        <ul>
            <li><b>Ikhtisar</b>: Ringkasan visual dan statistik server</li>
            <li><b>Analisis Waktu</b>: Pola pembukaan server berdasarkan waktu</li>
            <li><b>Analisis Peta</b>: Distribusi dan karakteristik tipe peta</li>
            <li><b>Prediksi</b>: Perkiraan pembukaan server berikutnya</li>
        </ul>
        <p>Gunakan filter di sidebar untuk menyaring data berdasarkan:</p>
        <ul>
            <li>Jenis Peta</li>
            <li>Tahun</li>
            <li>Rentang Tanggal</li>
            <li>Periode Waktu</li>
        </ul>
        <p>Klik ekspander pada setiap bagian untuk melihat detail lebih lanjut.</p>
    </div>

    <script>
    function toggleHelp() {
        var panel = document.getElementById("helpPanel");
        var button = document.getElementById("helpButton");

        if (panel.style.display === "none") {
            panel.style.display = "block";
            panel.style.animation = "fadeIn 0.3s";
            button.style.backgroundColor = "#03DAC6";
        } else {
            panel.style.animation = "fadeOut 0.3s";
            setTimeout(function() {
                panel.style.display = "none";
                button.style.backgroundColor = "#BB86FC";
            }, 280);
        }
    }

    document.addEventListener("DOMContentLoaded", function() {
        // Add animations
        var style = document.createElement('style');
        style.textContent = `
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(-10px); }
                to { opacity: 1; transform: translateY(0); }
            }

            @keyframes fadeOut {
                from { opacity: 1; transform: translateY(0); }
                to { opacity: 0; transform: translateY(-10px); }
            }
        `;
        document.head.appendChild(style);
    });
    </script>
    """, unsafe_allow_html=True)


def render_stat_cards(df):
    """Render kartu statistik utama."""
    stats = calculate_statistics(df)

    st.markdown('<div class="metric-section">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Server", stats['total_servers'])
        st.markdown('<p class="card-explanation">Jumlah total server game yang tersedia</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Server Pertama", stats['first_server_date'].strftime('%Y-%m-%d'))
        st.markdown('<p class="card-explanation">Tanggal server pertama dibuka</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Server Terbaru", stats['last_server_date'].strftime('%Y-%m-%d'))
        st.markdown('<p class="card-explanation">Tanggal server terbaru dibuka</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Hari Antar Server", f"{stats['avg_days_per_server']:.1f}")
        st.markdown('<p class="card-explanation">Rata-rata hari antara pembukaan server</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


def render_server_growth_chart(df, color_scheme):
    """Render grafik pertumbuhan server sepanjang waktu."""
    st.markdown('<div class="insight-card">', unsafe_allow_html=True)
    with st.expander("### Pertumbuhan Server Sepanjang Waktu", expanded=True):
        st.markdown("Grafik berikut menunjukkan pertambahan jumlah server sepanjang waktu:")

        # Buat hitungan kumulatif berdasarkan tanggal
        server_growth = df.sort_values('OpenDateTime')
        server_growth['Counter'] = range(1, len(server_growth) + 1)

        fig = px.line(
            server_growth,
            x='OpenDateTime',
            y='Counter',
            color_discrete_sequence=[color_scheme[2]]
        )

        fig.update_layout(
            template="plotly_dark",
            height=350,
            xaxis_title="Tanggal",
            yaxis_title="Total Server",
            margin=dict(l=10, r=10, t=10, b=10)
        )

        fig.update_traces(
            hovertemplate='<b>Tanggal: %{x|%d %b %Y}</b><br>Total server: %{y}'
        )

        st.plotly_chart(fig, use_container_width=True)

        # Tambahkan analisis pertumbuhan
        growth_analysis = analyze_growth(server_growth)

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Analisis Pertumbuhan")
            st.markdown(f"""
            - **Periode Total**: {growth_analysis['total_period']} hari
            - **CAGR**: {growth_analysis['cagr']:.2f}% (Tingkat Pertumbuhan Tahunan Gabungan)
            - **Laju Rata-rata**: {growth_analysis['avg_growth_rate']:.2f} server per bulan
            """)

        with col2:
            st.subheader("Proyeksi")
            st.markdown(f"""
            - **Proyeksi 3 Bulan**: ~{growth_analysis['projection_3m']} server tambahan
            - **Proyeksi 6 Bulan**: ~{growth_analysis['projection_6m']} server tambahan
            - **Proyeksi 1 Tahun**: ~{growth_analysis['projection_1y']} server tambahan
            """)

    st.markdown('</div>', unsafe_allow_html=True)


def analyze_growth(server_growth):
    """Analisis statistik pertumbuhan server."""
    first_date = server_growth['OpenDateTime'].min()
    last_date = server_growth['OpenDateTime'].max()
    period_days = (last_date - first_date).days

    total_servers = len(server_growth)

    # Hitung CAGR (Compound Annual Growth Rate)
    years = period_days / 365.0
    if years > 0 and total_servers > 1:
        cagr = (total_servers ** (1 / years) - 1) * 100
    else:
        cagr = 0

    # Hitung laju pertumbuhan rata-rata
    if period_days > 30:
        avg_growth_rate = total_servers / (period_days / 30)  # server per bulan
    else:
        avg_growth_rate = total_servers

    # Proyeksikan pertumbuhan
    projection_3m = int(avg_growth_rate * 3)
    projection_6m = int(avg_growth_rate * 6)
    projection_1y = int(avg_growth_rate * 12)

    return {
        'total_period': period_days,
        'cagr': cagr,
        'avg_growth_rate': avg_growth_rate,
        'projection_3m': projection_3m,
        'projection_6m': projection_6m,
        'projection_1y': projection_1y
    }


def render_recent_servers_table(df):
    """Render tabel dengan server terbaru."""
    st.markdown('<div class="insight-card">', unsafe_allow_html=True)
    with st.expander("### Server Terbaru yang Dibuka", expanded=True):
        st.markdown("Berikut adalah 10 server terbaru yang dibuka:")

        # Persiapkan data untuk server terbaru
        recent_servers = df.sort_values(by='OpenDateTime', ascending=False).head(10)

        # Siapkan tampilan yang lebih ramah pengguna
        display_recent = recent_servers[['ServerId', 'OpenDateTime', 'MapType', 'DistrictId']].copy()
        display_recent.columns = ['ID Server', 'Tanggal Dibuka', 'Jenis Peta', 'ID District']

        # Format tanggal
        display_recent['Tanggal Dibuka'] = display_recent['Tanggal Dibuka'].dt.strftime('%d %b %Y %H:%M')

        st.dataframe(
            display_recent,
            use_container_width=True,
            height=400
        )
    st.markdown('</div>', unsafe_allow_html=True)


def render_map_distribution_chart(df, color_scheme):
    """Render distribusi jenis peta."""
    st.markdown('<div class="insight-card">', unsafe_allow_html=True)
    st.markdown("### Distribusi Server Berdasarkan Jenis Peta")
    st.markdown("Diagram berikut menunjukkan pembagian server berdasarkan jenis peta:")

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
    st.markdown('</div>', unsafe_allow_html=True)


def create_dashboard_widget(title, content, expanded=True):
    """Utility untuk membuat widget dashboard konsisten."""
    st.markdown('<div class="insight-card">', unsafe_allow_html=True)
    with st.expander(f"### {title}", expanded=expanded):
        content()
    st.markdown('</div>', unsafe_allow_html=True)