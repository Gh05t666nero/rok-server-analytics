# 📊 Dasbor Analitik Server Rise of Kingdoms

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.31.0-FF4B4B.svg)](https://streamlit.io)
[![Pandas](https://img.shields.io/badge/Pandas-2.2.0-150458.svg)](https://pandas.pydata.org)
[![Plotly](https://img.shields.io/badge/Plotly-5.18.0-3F4F75.svg)](https://plotly.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

<p align="center">
  <img src="https://rok.lilith.com/assets/en/imgs/logo-new.png" alt="Dasbor Analitik Server Rise of Kingdoms" width="800"/>
</p>

> Analitik lanjutan dan pemodelan prediktif untuk server game Rise of Kingdoms, dengan peramalan deret waktu dan deteksi pola.

## 🌟 Gambaran Umum

Dasbor Analitik Server Rise of Kingdoms adalah alat komprehensif untuk menganalisis pola server, tren pertumbuhan, dan prediksi masa depan untuk game mobile populer Rise of Kingdoms. Proyek ini menampilkan teknik visualisasi data dan analisis deret waktu tingkat lanjut dalam dasbor yang interaktif dan elegan.

Dasbor ini mengumpulkan informasi server dari API game resmi dan mengubahnya menjadi wawasan yang dapat ditindaklanjuti, membantu pemain memahami pola pembukaan server, rotasi jenis peta, dan memprediksi rilis server di masa depan dengan tingkat akurasi yang tinggi.

### 🔗 Demo Langsung

Lihat demo langsung: [https://riseofkingdoms.streamlit.app/](https://riseofkingdoms.streamlit.app/)

## 🚀 Fitur Utama

### 📈 Analisis Data Server Komprehensif
- **Ikhtisar Server**: Ringkasan visual statistik server dan pola distribusi
- **Analisis Temporal**: Pola berbasis waktu dalam peluncuran server (harian, mingguan, bulanan)
- **Analisis Jenis Peta**: Distribusi dan evolusi jenis peta dari waktu ke waktu
- **Analisis Distrik**: Korelasi antara distrik server dan jenis peta

### 🔮 Analitik Prediktif
- **Peramalan Deret Waktu**: Model ARIMA dan SARIMA untuk memprediksi frekuensi pembukaan server
- **Deteksi Pola Rotasi Server**: Deteksi otomatis pola rotasi jenis peta
- **Prediksi Server Berikutnya**: Prediksi terperinci untuk server yang akan datang termasuk:
  - ID server yang diharapkan
  - Perkiraan tanggal dan waktu pembukaan
  - Prediksi jenis peta
  - Prediksi ID distrik
  - Hitungan mundur hingga peluncuran

### 🛠️ Dasbor Interaktif
- **Filter yang Dapat Disesuaikan**: Filter data berdasarkan jenis peta, tahun, rentang tanggal, dan lainnya
- **Beberapa Jenis Visualisasi**: Grafik garis, grafik batang, peta panas, diagram lingkaran, dan lainnya
- **Antarmuka Mode Gelap**: Desain mode gelap modern dan ramah mata
- **Opsi Ekspor Data**: Ekspor data dalam format CSV, Excel, atau JSON
- **Desain Responsif**: Beradaptasi dengan berbagai ukuran layar

## 🔧 Teknologi yang Digunakan

- **Frontend**: Streamlit (kerangka kerja dasbor interaktif)
- **Pemrosesan Data**: Pandas, NumPy
- **Visualisasi Data**: Plotly
- **Analisis Deret Waktu**: StatsModels (ARIMA, SARIMA)
- **Integrasi API**: Requests
- **Manajemen Lingkungan**: python-dotenv

## 📋 Persyaratan

- Python 3.9+
- Dependensi yang tercantum dalam `requirements.txt`
- Kredensial API untuk Rise of Kingdoms API (opsional - menggunakan data sampel sebagai fallback)

## 🔌 Instalasi

1. **Kloning repositori**
   ```bash
   git clone https://github.com/Gh05t666nero/rok-server-analytics.git
   cd rok-server-analytics
   ```

2. **Buat lingkungan virtual**
   ```bash
   python -m venv venv
   
   # Untuk Windows
   venv\Scripts\activate
   
   # Untuk macOS/Linux
   source venv/bin/activate
   ```

3. **Instal dependensi**
   ```bash
   pip install -r requirements.txt
   ```

4. **Siapkan variabel lingkungan**
   ```bash
   # Salin file contoh
   cp .env.example .env
   
   # Edit file .env dengan kredensial API Anda
   ```

5. **Jalankan aplikasi**
   ```bash
   streamlit run app.py
   ```

## 🔍 Cara Menggunakan

### Meluncurkan Dasbor
Setelah menjalankan aplikasi, dasbor akan terbuka di browser web default Anda di `http://localhost:8501`.

### Menggunakan Filter
1. Gunakan filter di sidebar untuk mempersempit data:
   - Pilih jenis peta yang diminati
   - Pilih tahun tertentu
   - Atur rentang tanggal kustom
   - Gunakan preset waktu cepat (30 hari, 90 hari, dll.)

### Menavigasi Tab
Dasbor ini diorganisir menjadi empat tab utama:

1. **📊 Ikhtisar**: Dapatkan ringkasan cepat tentang statistik dan distribusi server
2. **🕒 Analisis Waktu**: Jelajahi pola pembukaan server berdasarkan interval waktu yang berbeda
3. **🗺️ Analisis Peta**: Analisis distribusi dan pola jenis peta
4. **📈 Prediksi**: Lihat perkiraan untuk pembukaan server yang akan datang

### Menginterpretasi Prediksi
Tab prediksi menyediakan:
- Visualisasi data historis
- Dekomposisi deret waktu menjadi komponen tren, musiman, dan residual
- Model peramalan ARIMA/SARIMA
- Prediksi terperinci untuk server yang akan datang

### Mengekspor Data
1. Gunakan bagian "Ekspor Data" di sidebar
2. Pilih format yang Anda inginkan (CSV, Excel, JSON)
3. Klik "Ekspor Data" untuk mengunduh

## 🏗️ Struktur Proyek

```
rok_analysis/
├── app.py                 # File aplikasi utama
├── config.py              # Pengaturan konfigurasi
├── requirements.txt       # Dependensi proyek
├── utils/                 # Fungsi utilitas
│   ├── data_loader.py     # Fungsi pemuatan data API
│   ├── data_processor.py  # Fungsi pemrosesan data
│   └── time_series.py     # Analisis deret waktu dan peramalan
├── components/            # Komponen UI
│   ├── dashboard.py       # Elemen dasbor
│   ├── overview.py        # Tab ikhtisar
│   ├── time_analysis.py   # Tab analisis waktu
│   ├── map_analysis.py    # Tab analisis peta
│   └── predictions.py     # Tab prediksi
├── styles/                # Gaya UI
│   └── custom_styles.py   # Fungsi CSS dan gaya kustom
└── data/                  # Direktori data
    └── fallback_data.json # Data cadangan ketika API tidak tersedia
```

## 🔬 Detail Teknis

### Model Deret Waktu

Proyek ini menggunakan model ARIMA (AutoRegressive Integrated Moving Average) dan SARIMA (Seasonal ARIMA) untuk menangkap aspek berbeda dari pola pembukaan server:

- **ARIMA**: Menangkap tren umum dan pola autoregresif
- **SARIMA**: Menangkap pola musiman (misalnya, siklus bulanan, triwulanan, atau tahunan)

Model-model ini disetel secara otomatis menggunakan AIC (Akaike Information Criterion) untuk menemukan parameter optimal (p,d,q) yang menyeimbangkan kompleksitas dan kesesuaian model.

### Deteksi Pola

Aplikasi ini menggunakan algoritma khusus untuk mendeteksi pola berulang dalam rotasi jenis peta. Algoritma ini:
1. Menganalisis pembukaan server terbaru
2. Menguji berbagai panjang pola (2-5)
3. Memvalidasi pola terhadap data historis
4. Menghitung skor konsistensi

Ketika pola terdeteksi dengan konsistensi tinggi (>70%), pola tersebut digunakan untuk memprediksi jenis peta di masa depan.

### Prediksi ID Distrik

Prediksi ID distrik menggunakan kombinasi dari:
- Pola penugasan distrik historis
- Progresi ID server
- Korelasi jenis peta

Pendekatan multi-faktor ini memungkinkan prediksi penugasan distrik dengan keyakinan tinggi untuk server yang akan datang.

## 🚫 Keterbatasan

- Prediksi didasarkan pada pola historis dan mungkin tidak memperhitungkan pembaruan game atau acara yang tidak terduga
- Akses API memerlukan kredensial yang valid, meskipun aplikasi beralih ke data sampel jika tidak tersedia
- Peramalan deret waktu menjadi kurang andal untuk horizon prediksi yang lebih panjang (lebih dari 90 hari)

## 🤝 Kontribusi

Kontribusi sangat diterima! Jika Anda ingin meningkatkan proyek ini:

1. Fork repositori
2. Buat branch fitur Anda (`git checkout -b feature/fitur-luar-biasa`)
3. Commit perubahan Anda (`git commit -m 'Menambahkan fitur luar biasa'`)
4. Push ke branch (`git push origin feature/fitur-luar-biasa`)
5. Buka Pull Request

## 📃 Lisensi

Proyek ini dilisensikan di bawah Lisensi MIT - lihat file [LICENSE](LICENSE) untuk detailnya.

## 👏 Ucapan Terima Kasih

- Terima kasih kepada komunitas Rise of Kingdoms atas wawasan tentang pola server
- [Streamlit](https://streamlit.io/) untuk kerangka kerja dasbor mereka yang luar biasa
- [Plotly](https://plotly.com/) untuk visualisasi data interaktif
- [StatsModels](https://www.statsmodels.org/) untuk kemampuan peramalan deret waktu

## 📬 Kontak

[Muhammad Fauzan Wijaya] - [@fauzanwijaya](https://linkedin.com/in/fauzanwijaya)

Link Proyek: [https://github.com/Gh05t666nero/rok-server-analytics](https://github.com/Gh05t666nero/rok-server-analytics)
