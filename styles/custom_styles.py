# styles/custom_styles.py
import streamlit as st


def apply_custom_styles():
    """
    Menerapkan gaya kustom untuk aplikasi Streamlit.
    Fungsi ini harus dipanggil di awal aplikasi.
    """
    # CSS untuk Mode Gelap yang lebih user-friendly dan terstruktur
    st.markdown("""
    <style>
        /* Menambahkan font Inter untuk tampilan yang lebih modern */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        /* Variabel CSS untuk konsistensi */
        :root {
            --bg-primary: #121212;
            --bg-secondary: #1E1E1E;
            --bg-tertiary: #2D2D2D;
            --color-primary: #BB86FC;
            --color-secondary: #03DAC6;
            --color-text-primary: #E0E0E0;
            --color-text-secondary: #BBBBBB;
            --spacing-xs: 4px;
            --spacing-sm: 8px;
            --spacing-md: 16px;
            --spacing-lg: 24px;
            --spacing-xl: 32px;
            --radius-sm: 4px;
            --radius-md: 8px;
            --radius-lg: 12px;
            --shadow-sm: 0 2px 4px rgba(0,0,0,0.2);
            --shadow-md: 0 4px 8px rgba(0,0,0,0.3);
            --shadow-lg: 0 8px 16px rgba(0,0,0,0.4);
            --border-width: 4px;
        }

        /* Gaya dasar untuk mode gelap */
        .main {
            background-color: var(--bg-primary);
            color: var(--color-text-primary);
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
        }

        /* Override untuk scrollbar utama */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }

        ::-webkit-scrollbar-track {
            background: var(--bg-secondary);
            border-radius: var(--radius-sm);
        }

        ::-webkit-scrollbar-thumb {
            background: var(--color-primary);
            border-radius: var(--radius-sm);
        }

        ::-webkit-scrollbar-thumb:hover {
            background: #9d70d1;
        }

        /* Header */
        .main-header {
            font-size: 2.5rem;
            color: var(--color-primary);
            text-align: center;
            padding: var(--spacing-md) 0;
            margin-bottom: var(--spacing-lg);
            font-weight: 600;
            letter-spacing: -0.5px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.5);
        }

        .sub-header {
            font-size: 1.5rem;
            color: var(--color-secondary);
            margin: var(--spacing-lg) 0 var(--spacing-md);
            font-weight: 500;
            letter-spacing: -0.25px;
            padding-bottom: var(--spacing-xs);
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }

        /* Info badge untuk memberikan penjelasan */
        .info-badge {
            background-color: var(--color-secondary);
            color: var(--bg-primary);
            padding: var(--spacing-xs) var(--spacing-sm);
            border-radius: var(--radius-sm);
            font-size: 0.8rem;
            margin-left: var(--spacing-sm);
            cursor: help;
            font-weight: 500;
            display: inline-block;
        }

        /* Grid system untuk layout yang lebih baik */
        .grid-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: var(--spacing-md);
            margin-bottom: var(--spacing-lg);
        }

        /* Kartu untuk metrik */
        .metric-card {
            background-color: var(--bg-secondary);
            border-radius: var(--radius-md);
            padding: var(--spacing-lg);
            box-shadow: var(--shadow-md);
            margin-bottom: var(--spacing-md);
            border-left: var(--border-width) solid var(--color-primary);
            transition: all 0.2s ease-in-out;
            position: relative;
            overflow: hidden;
        }

        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
            border-left-width: calc(var(--border-width) + 2px);
        }

        .metric-card::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 4px;
            background: linear-gradient(90deg, var(--color-primary), transparent);
            opacity: 0.5;
        }

        /* Penjelasan kartu */
        .card-explanation {
            font-size: 0.85rem;
            color: var(--color-text-secondary);
            margin-top: var(--spacing-sm);
            line-height: 1.4;
        }

        /* Bagian filter */
        .filter-section {
            background-color: var(--bg-secondary);
            border-radius: var(--radius-md);
            padding: var(--spacing-lg);
            margin-bottom: var(--spacing-lg);
            box-shadow: var(--shadow-sm);
            border-top: 1px solid rgba(255,255,255,0.05);
        }

        .filter-section h3 {
            margin-top: 0;
            margin-bottom: var(--spacing-md);
            color: var(--color-primary);
            font-size: 1.2rem;
            font-weight: 500;
        }

        /* Tampilan lebih baik untuk select box dan slider */
        .stSelectbox, .stSlider {
            padding: var(--spacing-xs) 0;
            margin-bottom: var(--spacing-sm);
        }

        /* Tab styling untuk navigasi yang lebih mudah */
        .stTabs [data-baseweb="tab-list"] {
            gap: var(--spacing-sm);
            padding: var(--spacing-xs) 0;
            background-color: rgba(0,0,0,0.2);
            border-radius: var(--radius-md);
            padding: var(--spacing-xs);
            margin-bottom: var(--spacing-md);
        }

        .stTabs [data-baseweb="tab"] {
            background-color: var(--bg-secondary);
            border-radius: var(--radius-sm);
            padding: var(--spacing-sm) var(--spacing-lg);
            color: var(--color-text-primary);
            font-weight: 500;
            transition: all 0.2s ease;
            border: 1px solid rgba(255,255,255,0.05);
        }

        .stTabs [aria-selected="true"] {
            background-color: var(--color-primary);
            color: #000;
            box-shadow: var(--shadow-sm);
            transform: translateY(-1px);
        }

        /* Bagian navigasi */
        .nav-section {
            display: flex;
            justify-content: space-between;
            margin-bottom: var(--spacing-lg);
            background-color: var(--bg-secondary);
            padding: var(--spacing-lg);
            border-radius: var(--radius-md);
            align-items: center;
            box-shadow: var(--shadow-md);
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }

        /* Tooltip styling */
        .tooltip {
            position: relative;
            display: inline-block;
        }

        .tooltip .tooltiptext {
            visibility: hidden;
            width: 200px;
            background-color: var(--bg-tertiary);
            color: var(--color-text-primary);
            text-align: center;
            border-radius: var(--radius-sm);
            padding: var(--spacing-sm) var(--spacing-md);
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            margin-left: -100px;
            opacity: 0;
            transition: opacity 0.3s;
            box-shadow: var(--shadow-md);
            font-size: 0.85rem;
            line-height: 1.4;
        }

        .tooltip:hover .tooltiptext {
            visibility: visible;
            opacity: 1;
        }

        /* Kartu insight untuk konten */
        .insight-card {
            background-color: var(--bg-secondary);
            border-radius: var(--radius-md);
            padding: var(--spacing-lg) var(--spacing-xl);
            margin-bottom: var(--spacing-lg);
            border-left: var(--border-width) solid var(--color-secondary);
            box-shadow: var(--shadow-md);
            position: relative;
        }

        .insight-card h3 {
            color: var(--color-secondary);
            margin-top: 0;
            margin-bottom: var(--spacing-md);
            font-size: 1.3rem;
            font-weight: 500;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            padding-bottom: var(--spacing-xs);
        }

        /* Membuat grafik lebih terlihat */
        .js-plotly-plot, .plotly, .plot-container {
            z-index: 10 !important;
        }

        div.stPlotlyChart {
            background-color: transparent !important;
            z-index: 10 !important;
            padding: 0 !important;
            margin-bottom: var(--spacing-md);
            border-radius: var(--radius-md);
            overflow: hidden;
        }

        /* Meningkatkan tampilan expander */
        .streamlit-expanderHeader {
            background-color: rgba(255,255,255,0.05) !important;
            border-radius: var(--radius-sm);
            padding: var(--spacing-sm) var(--spacing-md) !important;
            margin-bottom: var(--spacing-sm);
        }

        .streamlit-expanderContent {
            padding: var(--spacing-md) !important;
            border-radius: var(--radius-sm);
            background-color: rgba(0,0,0,0.1);
        }

        /* Override latar belakang container */
        div[data-testid="stVerticalBlock"] {
            background-color: transparent !important;
            padding: 0 var(--spacing-xs);
        }

        /* Dataframe styling */
        .dataframe {
            background-color: var(--bg-secondary);
            color: var(--color-text-primary);
            border-radius: var(--radius-sm);
            overflow: hidden;
        }

        .dataframe thead th {
            background-color: rgba(0,0,0,0.2);
            padding: var(--spacing-sm) var(--spacing-md) !important;
            border-bottom: 2px solid var(--color-primary);
        }

        .dataframe tbody tr:nth-child(even) {
            background-color: rgba(255,255,255,0.05);
        }

        .dataframe tbody td {
            padding: var(--spacing-sm) var(--spacing-md) !important;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }

        /* Stlying untuk tombol */
        .stButton > button {
            background-color: var(--color-primary);
            color: #000;
            border: none;
            padding: var(--spacing-sm) var(--spacing-lg);
            border-radius: var(--radius-sm);
            font-weight: 500;
            transition: all 0.2s ease;
            box-shadow: var(--shadow-sm);
        }

        .stButton > button:hover {
            background-color: #9d70d1;
            box-shadow: var(--shadow-md);
            transform: translateY(-1px);
        }

        /* Footer */
        .footer {
            text-align: center;
            padding: var(--spacing-xl) var(--spacing-md);
            font-size: 0.8rem;
            color: var(--color-text-secondary);
            margin-top: var(--spacing-xl);
            border-top: 1px solid rgba(255,255,255,0.05);
            background-color: var(--bg-secondary);
            border-radius: var(--radius-md);
        }

        /* Tombol bantuan di pojok kanan atas */
        .help-button {
            position: fixed;
            top: var(--spacing-md);
            right: var(--spacing-md);
            background-color: var(--color-primary);
            color: #000;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            display: flex;
            justify-content: center;
            align-items: center;
            font-weight: bold;
            cursor: pointer;
            z-index: 1000;
            box-shadow: var(--shadow-md);
            transition: all 0.2s ease;
        }

        .help-button:hover {
            transform: scale(1.1);
            box-shadow: var(--shadow-lg);
        }

        /* Panel bantuan */
        .help-panel {
            position: fixed;
            top: 60px;
            right: var(--spacing-md);
            background-color: var(--bg-secondary);
            border-radius: var(--radius-md);
            padding: var(--spacing-lg);
            max-width: 300px;
            box-shadow: var(--shadow-lg);
            z-index: 1000;
            border-left: var(--border-width) solid var(--color-primary);
        }

        .help-panel h3 {
            margin-top: 0;
            color: var(--color-primary);
            margin-bottom: var(--spacing-md);
            font-size: 1.2rem;
            font-weight: 500;
        }

        .help-panel ul {
            padding-left: var(--spacing-lg);
            margin-bottom: var(--spacing-md);
        }

        .help-panel li {
            margin-bottom: var(--spacing-xs);
        }

        /* Loading indicator yang lebih menarik */
        .stSpinner > div > div {
            border-color: var(--color-primary) !important;
        }

        /* Meningkatkan tampilan metrik */
        div[data-testid="metric-container"] {
            background-color: rgba(0,0,0,0.1);
            border-radius: var(--radius-sm);
            padding: var(--spacing-sm);
            box-shadow: inset 0 1px 2px rgba(0,0,0,0.1);
        }

        div[data-testid="metric-container"] label {
            color: var(--color-secondary);
            font-size: 1rem;
            font-weight: 500;
        }

        div[data-testid="metric-container"] div {
            margin-top: var(--spacing-xs);
        }

        div[data-testid="metric-container"] p {
            font-size: 1.5rem;
            font-weight: 600;
        }
    </style>
    """, unsafe_allow_html=True)

    # Tombol bantuan di pojok kanan atas dengan animasi
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


def apply_light_mode_styles():
    """
    Menerapkan gaya mode terang untuk aplikasi Streamlit.
    Mode ini lebih cocok untuk presentasi atau lingkungan dengan pencahayaan yang baik.
    """
    # CSS untuk Mode Terang
    st.markdown("""
    <style>
        /* Variabel CSS untuk mode terang */
        :root {
            --bg-primary: #FFFFFF;
            --bg-secondary: #F6F6F6;
            --bg-tertiary: #EEEEEE;
            --color-primary: #6200EE;
            --color-secondary: #03DAC5;
            --color-text-primary: #333333;
            --color-text-secondary: #666666;
            /* Variabel lainnya sama dengan mode gelap */
        }

        /* Gaya dasar untuk mode terang */
        .main {
            background-color: var(--bg-primary);
            color: var(--color-text-primary);
        }

        /* Overrides khusus mode terang */
        .insight-card {
            border-left: var(--border-width) solid var(--color-primary);
        }

        .metric-card {
            background-color: var(--bg-secondary);
            border-left: var(--border-width) solid var(--color-primary);
        }

        /* ... dan seterusnya dengan overrides khusus mode terang */
    </style>
    """, unsafe_allow_html=True)


def apply_print_friendly_styles():
    """
    Menerapkan gaya yang ramah cetak untuk aplikasi Streamlit.
    Mode ini lebih cocok untuk ekspor ke PDF atau pencetakan fisik.
    """
    # CSS untuk Mode Ramah Cetak
    st.markdown("""
    <style>
        /* Variabel CSS untuk mode ramah cetak */
        @media print {
            :root {
                --bg-primary: #FFFFFF;
                --bg-secondary: #FAFAFA;
                --bg-tertiary: #F6F6F6;
                --color-primary: #000000;
                --color-secondary: #444444;
                --color-text-primary: #000000;
                --color-text-secondary: #444444;
            }

            /* Hapus elemen yang tidak perlu dicetak */
            .stSidebar, .help-button, .help-panel {
                display: none !important;
            }

            /* Maksimalkan area cetak */
            .main {
                width: 100% !important;
                padding: 0 !important;
            }

            /* Hindari pemisahan elemen */
            .insight-card, .metric-card {
                page-break-inside: avoid;
            }

            /* ... dan seterusnya dengan overrides khusus pencetakan */
        }
    </style>
    """, unsafe_allow_html=True)