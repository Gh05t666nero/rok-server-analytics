# components/map_analysis.py
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np


def render_map_analysis_tab(filtered_df, color_scheme):
    """
    Render tab analisis tipe peta dengan visualisasi terkait peta server.

    Parameters:
        filtered_df (pandas.DataFrame): DataFrame yang sudah difilter
        color_scheme (list): Skema warna untuk visualisasi
    """
    st.markdown('<p class="sub-header">Analisis Tipe Peta</p>', unsafe_allow_html=True)

    # Distribusi jenis peta sepanjang waktu
    st.markdown('<div class="insight-card">', unsafe_allow_html=True)
    with st.expander("### Distribusi Tipe Peta Sepanjang Waktu", expanded=True):
        render_map_distribution_over_time(filtered_df, color_scheme)
    st.markdown('</div>', unsafe_allow_html=True)

    # Tata letak dua kolom untuk organisasi yang lebih baik
    col1, col2 = st.columns([1, 1])

    with col1:
        # Grafik area persentase tumpukan
        st.markdown('<div class="insight-card">', unsafe_allow_html=True)
        with st.expander("### Distribusi Relatif Tipe Peta", expanded=True):
            render_map_relative_distribution(filtered_df, color_scheme)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        # Analisis district
        st.markdown('<div class="insight-card">', unsafe_allow_html=True)
        with st.expander("### Analisis District", expanded=True):
            render_district_analysis(filtered_df, color_scheme)
        st.markdown('</div>', unsafe_allow_html=True)

    # Karakteristik jenis peta
    st.markdown('<div class="insight-card">', unsafe_allow_html=True)
    with st.expander("### Karakteristik Tipe Peta", expanded=True):
        render_map_characteristics(filtered_df)
    st.markdown('</div>', unsafe_allow_html=True)

    # Analisis pola rotasi tipe peta
    st.markdown('<div class="insight-card">', unsafe_allow_html=True)
    with st.expander("### Pola Rotasi Tipe Peta", expanded=True):
        render_map_rotation_pattern(filtered_df, color_scheme)
    st.markdown('</div>', unsafe_allow_html=True)


def render_map_distribution_over_time(df, color_scheme):
    """Render distribusi tipe peta sepanjang waktu."""
    st.markdown("""
    Grafik ini menunjukkan perubahan penggunaan jenis peta selama bertahun-tahun.
    Anda dapat melihat kapan jenis peta tertentu mulai digunakan atau semakin populer.
    """)

    # Kelompokkan berdasarkan tahun dan jenis peta
    yearly_map_type = df.groupby(['Year', 'MapType']).size().reset_index(name='Count')

    # Pilihan tampilan grafik
    chart_type = st.radio(
        "Pilih Jenis Grafik",
        ["Bar Chart", "Line Chart", "Area Chart"],
        horizontal=True
    )

    if chart_type == "Bar Chart":
        fig = px.bar(
            yearly_map_type,
            x='Year',
            y='Count',
            color='MapType',
            title='Tipe Peta Server Sepanjang Tahun',
            barmode='group',
            color_discrete_sequence=color_scheme
        )
    elif chart_type == "Line Chart":
        fig = px.line(
            yearly_map_type,
            x='Year',
            y='Count',
            color='MapType',
            title='Tipe Peta Server Sepanjang Tahun',
            markers=True,
            color_discrete_sequence=color_scheme
        )
    else:  # Area Chart
        fig = px.area(
            yearly_map_type,
            x='Year',
            y='Count',
            color='MapType',
            title='Tipe Peta Server Sepanjang Tahun',
            color_discrete_sequence=color_scheme
        )

    fig.update_layout(
        template="plotly_dark",
        height=400,
        xaxis_title='Tahun',
        yaxis_title='Jumlah Server',
        xaxis=dict(type='category')
    )

    fig.update_traces(
        hovertemplate='<b>Tahun: %{x}</b><br>Jenis peta: %{data.name}<br>Jumlah server: %{y}'
    )

    st.plotly_chart(fig, use_container_width=True)

    # Tambahkan insight tentang evolusi tipe peta
    st.subheader("Insight Evolusi Tipe Peta")

    # Temukan tanggal pertama setiap tipe peta
    first_appearance = df.groupby('MapType')['OpenDateTime'].min().reset_index()
    first_appearance.columns = ['MapType', 'FirstAppearance']
    first_appearance = first_appearance.sort_values('FirstAppearance')

    st.markdown("### Kronologi Pengenalan Tipe Peta")
    for _, row in first_appearance.iterrows():
        st.markdown(
            f"- **{row['MapType']}**: Pertama kali digunakan pada {row['FirstAppearance'].strftime('%d %B %Y')}")

    # Analisis tren popularitas
    st.markdown("### Tren Popularitas Tipe Peta")

    # Hitung tipe peta terpopuler per tahun
    popular_per_year = yearly_map_type.loc[yearly_map_type.groupby('Year')['Count'].idxmax()]
    st.markdown("Tipe peta paling populer per tahun:")

    for _, row in popular_per_year.iterrows():
        st.markdown(f"- **{row['Year']}**: {row['MapType']} ({row['Count']} server)")


def render_map_relative_distribution(df, color_scheme):
    """Render distribusi relatif tipe peta."""
    st.markdown("""
    Grafik ini menunjukkan persentase setiap jenis peta per tahun.
    Ini membantu melihat tren relatif dalam penggunaan tipe peta.
    """)

    # Kelompokkan berdasarkan tahun dan jenis peta
    yearly_map_type = df.groupby(['Year', 'MapType']).size().reset_index(name='Count')

    # Hitung persentase berdasarkan tahun
    yearly_total = df.groupby('Year').size().reset_index(name='Total')
    yearly_map_type = pd.merge(yearly_map_type, yearly_total, on='Year')
    yearly_map_type['Percentage'] = yearly_map_type['Count'] / yearly_map_type['Total'] * 100

    fig = px.area(
        yearly_map_type,
        x='Year',
        y='Percentage',
        color='MapType',
        title='Distribusi Persentase Tipe Peta per Tahun',
        groupnorm='percent',
        color_discrete_sequence=color_scheme
    )

    fig.update_layout(
        template="plotly_dark",
        height=350,
        xaxis_title='Tahun',
        yaxis_title='Persentase (%)',
        xaxis=dict(type='category')
    )

    fig.update_traces(
        hovertemplate='<b>Tahun: %{x}</b><br>Jenis peta: %{data.name}<br>Persentase: %{y:.1f}%'
    )

    st.plotly_chart(fig, use_container_width=True)

    # Tambahkan insight
    st.markdown("""
    ### Interpretasi Distribusi Relatif

    Grafik di atas menunjukkan bagaimana komposisi tipe peta berubah dari waktu ke waktu. 
    Perhatikan bagaimana beberapa tipe peta mungkin menjadi lebih dominan atau berkurang penggunaannya relatif terhadap tipe lainnya.

    Area yang lebih luas menunjukkan tipe peta yang lebih dominan pada tahun tersebut.
    """)


def render_district_analysis(df, color_scheme):
    """Render analisis district."""
    st.markdown("""
    Grafik ini menunjukkan distribusi server berdasarkan ID District.
    District adalah pengelompokan server dalam game.
    """)

    # Distribusi district
    district_count = df['DistrictId'].value_counts().reset_index()
    district_count.columns = ['DistrictId', 'Count']
    district_count = district_count.sort_values('DistrictId')

    # Jika terlalu banyak district, tampilkan 20 teratas
    if len(district_count) > 20:
        show_top = st.checkbox("Tampilkan hanya 20 district teratas", value=True)
        if show_top:
            district_count = district_count.sort_values('Count', ascending=False).head(20)
            st.info("Menampilkan 20 District dengan server terbanyak")

    fig = px.bar(
        district_count,
        x='DistrictId',
        y='Count',
        title='Distribusi Server per District',
        color='Count',
        color_continuous_scale=color_scheme
    )

    fig.update_layout(
        template="plotly_dark",
        height=350,
        xaxis_title='ID District',
        yaxis_title='Jumlah Server',
        coloraxis_showscale=False
    )

    fig.update_traces(
        hovertemplate='<b>District ID: %{x}</b><br>Jumlah server: %{y}'
    )

    st.plotly_chart(fig, use_container_width=True)

    # Analisis hubungan antara District dan MapType
    st.subheader("Hubungan antara District dan Tipe Peta")

    # Tampilkan crosstab District vs MapType
    district_map_cross = pd.crosstab(
        df['DistrictId'],
        df['MapType'],
        margins=True,
        margins_name='Total'
    )

    # Terlalu banyak district akan membuat tabel sulit dibaca, batasi jika perlu
    if len(district_map_cross) > 20:
        # Ambil 20 district dengan total tertinggi
        top_districts = district_map_cross.sort_values('Total', ascending=False).head(20).index[:-1]  # exclude 'Total'
        district_map_cross = district_map_cross.loc[list(top_districts) + ['Total']]

    st.dataframe(district_map_cross, use_container_width=True)


def render_map_characteristics(df):
    """Render karakteristik tipe peta."""
    st.markdown("""
    Tabel berikut menampilkan ringkasan karakteristik setiap jenis peta,
    termasuk jumlah server, tanggal server pertama dan terakhir, serta rata-rata ID District.
    """)

    # Tabel yang menunjukkan karakteristik setiap jenis peta
    map_type_stats = df.groupby('MapType').agg(
        Jumlah=('ServerId', 'count'),
        ServerPertama=('OpenDateTime', 'min'),
        ServerTerakhir=('OpenDateTime', 'max'),
        RataRataDistrictId=('DistrictId', 'mean'),
        MedianDistrictId=('DistrictId', 'median'),
        MinDistrictId=('DistrictId', 'min'),
        MaxDistrictId=('DistrictId', 'max')
    ).reset_index()

    map_type_stats['ServerPertama'] = map_type_stats['ServerPertama'].dt.strftime('%Y-%m-%d')
    map_type_stats['ServerTerakhir'] = map_type_stats['ServerTerakhir'].dt.strftime('%Y-%m-%d')
    map_type_stats['RataRataDistrictId'] = map_type_stats['RataRataDistrictId'].round(1)
    map_type_stats['MedianDistrictId'] = map_type_stats['MedianDistrictId'].round(1)

    # Ganti nama kolom untuk tampilan
    map_type_stats.columns = ['Jenis Peta', 'Jumlah Server', 'Server Pertama', 'Server Terakhir',
                              'Rata-rata ID District', 'Median ID District', 'Min ID District', 'Max ID District']

    st.dataframe(map_type_stats, use_container_width=True)

    st.markdown("### Hubungan antara ID District dan Jenis Peta")
    st.markdown("""
    Scatter plot ini menunjukkan hubungan antara ID District dan jenis peta.
    District tertentu mungkin lebih sering menggunakan jenis peta tertentu.
    """)

    # Hubungan antara ID District dan MapType - visualisasi yang lebih baik
    district_map_type = df.groupby(['DistrictId', 'MapType']).size().reset_index(name='Count')

    fig = px.scatter(
        district_map_type,
        x='DistrictId',
        y='Count',
        color='MapType',
        size='Count',
        title='Hubungan antara ID District dan Jenis Peta',
        hover_data=['DistrictId', 'MapType', 'Count']
    )

    fig.update_layout(
        template="plotly_dark",
        height=400,
        xaxis_title='ID District',
        yaxis_title='Jumlah Server',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    fig.update_traces(
        hovertemplate='<b>District ID: %{x}</b><br>Jenis peta: %{data.name}<br>Jumlah server: %{marker.size}'
    )

    st.plotly_chart(fig, use_container_width=True)


def render_map_rotation_pattern(df, color_scheme):
    """Render analisis pola rotasi tipe peta."""
    st.markdown("""
    Analisis ini melihat apakah ada pola berulang dalam penggunaan tipe peta.
    Misalnya, apakah tipe peta dirotasi secara berurutan dalam urutan tertentu.
    """)

    # Urutkan data berdasarkan waktu
    df_sorted = df.sort_values('OpenDateTime').reset_index(drop=True)

    # Lihat urutan tipe peta
    map_sequence = df_sorted['MapType'].tolist()

    # Deteksi pola rotasi
    pattern_length = detect_pattern_length(map_sequence)

    if pattern_length > 0:
        # Temukan pola yang terdeteksi
        detected_pattern = map_sequence[:pattern_length]

        st.success(f"Terdeteksi pola rotasi tipe peta dengan panjang {pattern_length}!")

        st.markdown("### Pola Rotasi yang Terdeteksi")
        for i, map_type in enumerate(detected_pattern, 1):
            st.markdown(f"{i}. **{map_type}**")

        # Visualisasikan pola rotasi
        visualize_map_rotation(df_sorted, pattern_length, color_scheme)

        # Analisis kepatuhan pada pola
        analyze_pattern_compliance(df_sorted, pattern_length)
    else:
        st.warning("Tidak terdeteksi pola rotasi yang jelas dalam penggunaan tipe peta.")

        # Tampilkan distribusi penggunaan berikutnya
        st.markdown("### Analisis Tipe Peta Berikutnya")
        st.markdown("""
        Meskipun tidak ada pola rotasi yang jelas, kita dapat melihat tipe peta apa 
        yang cenderung mengikuti tipe peta tertentu.
        """)

        analyze_next_map_distribution(df_sorted, color_scheme)


def detect_pattern_length(sequence, max_length=8):
    """
    Mencoba mendeteksi panjang pola dalam urutan tipe peta.

    Parameters:
        sequence (list): Urutan tipe peta
        max_length (int): Panjang pola maksimum yang akan dicari

    Returns:
        int: Panjang pola yang terdeteksi, atau 0 jika tidak ada pola
    """
    if len(sequence) < 4:
        return 0

    # Coba berbagai panjang pola
    for length in range(1, min(max_length, len(sequence) // 2) + 1):
        # Ambil pola potensial
        pattern = sequence[:length]

        # Periksa apakah pola berulang
        matches = 0
        expected_matches = (len(sequence) - length) // length

        for i in range(length, len(sequence) - length + 1, length):
            if sequence[i:i + length] == pattern:
                matches += 1

        # Jika 70% atau lebih dari yang diharapkan cocok dengan pola
        if matches >= 0.7 * expected_matches and matches > 1:
            return length

    return 0


def visualize_map_rotation(df, pattern_length, color_scheme):
    """
    Visualisasikan pola rotasi tipe peta.

    Parameters:
        df (pandas.DataFrame): DataFrame terurut berdasarkan waktu
        pattern_length (int): Panjang pola yang terdeteksi
        color_scheme (list): Skema warna untuk visualisasi
    """
    # Tambahkan kolom posisi dalam pola
    df = df.copy()
    df['PatternPosition'] = (df.index % pattern_length) + 1

    # Analisis distribusi tipe peta di setiap posisi pola
    pattern_distribution = pd.crosstab(
        df['PatternPosition'],
        df['MapType'],
        normalize='index'
    ) * 100

    # Plot distribusi tipe peta berdasarkan posisi dalam pola
    fig = px.imshow(
        pattern_distribution,
        labels=dict(x="Tipe Peta", y="Posisi dalam Pola", color="Persentase (%)"),
        x=pattern_distribution.columns,
        y=pattern_distribution.index,
        color_continuous_scale=color_scheme,
        aspect="auto",
        title="Distribusi Tipe Peta Berdasarkan Posisi dalam Pola Rotasi"
    )

    fig.update_layout(
        template="plotly_dark",
        height=400
    )

    fig.update_traces(
        hovertemplate='Posisi: %{y}<br>Tipe Peta: %{x}<br>Persentase: %{z:.1f}%'
    )

    st.plotly_chart(fig, use_container_width=True)


def analyze_pattern_compliance(df, pattern_length):
    """
    Analisis kepatuhan pada pola rotasi.

    Parameters:
        df (pandas.DataFrame): DataFrame terurut berdasarkan waktu
        pattern_length (int): Panjang pola yang terdeteksi
    """
    # Deteksi pola dasar dari data awal
    base_pattern = []
    for i in range(pattern_length):
        # Ambil tipe peta yang paling umum pada posisi ini
        most_common = df[df.index % pattern_length == i]['MapType'].value_counts().idxmax()
        base_pattern.append(most_common)

    # Periksa setiap server apakah mengikuti pola
    df = df.copy()
    df['ExpectedMapType'] = [base_pattern[i % pattern_length] for i in df.index]
    df['FollowsPattern'] = df['MapType'] == df['ExpectedMapType']

    # Hitung persentase kepatuhan
    compliance_rate = df['FollowsPattern'].mean() * 100

    st.markdown(f"### Tingkat Kepatuhan pada Pola: {compliance_rate:.1f}%")

    if compliance_rate > 90:
        st.success("Pola rotasi sangat konsisten!")
    elif compliance_rate > 70:
        st.info("Pola rotasi cukup konsisten dengan beberapa penyimpangan.")
    else:
        st.warning("Pola rotasi kurang konsisten, banyak penyimpangan.")

    # Visualisasikan ketidakpatuhan seiring waktu
    st.subheader("Ketidakpatuhan pada Pola Seiring Waktu")

    # Kelompokkan berdasarkan bulan-tahun untuk melihat tren
    df['YearMonth'] = df['OpenDateTime'].dt.strftime('%Y-%m')
    monthly_compliance = df.groupby('YearMonth')['FollowsPattern'].mean() * 100
    monthly_compliance = monthly_compliance.reset_index()

    fig = px.line(
        monthly_compliance,
        x='YearMonth',
        y='FollowsPattern',
        title='Tingkat Kepatuhan pada Pola per Bulan',
        labels={'YearMonth': 'Bulan-Tahun', 'FollowsPattern': 'Kepatuhan (%)'}
    )

    fig.update_layout(
        template="plotly_dark",
        height=350,
        xaxis=dict(tickangle=45)
    )

    fig.update_traces(
        hovertemplate='<b>%{x}</b><br>Kepatuhan: %{y:.1f}%'
    )

    st.plotly_chart(fig, use_container_width=True)


def analyze_next_map_distribution(df, color_scheme):
    """
    Analisis distribusi tipe peta berikutnya setelah tipe peta tertentu.

    Parameters:
        df (pandas.DataFrame): DataFrame terurut berdasarkan waktu
        color_scheme (list): Skema warna untuk visualisasi
    """
    # Tambahkan kolom untuk tipe peta berikutnya
    df = df.copy()
    df['NextMapType'] = df['MapType'].shift(-1)

    # Hilangkan baris terakhir yang tidak memiliki "berikutnya"
    df = df.dropna(subset=['NextMapType'])

    # Buat heatmap transisi
    transition_matrix = pd.crosstab(
        df['MapType'],
        df['NextMapType'],
        normalize='index'
    ) * 100

    fig = px.imshow(
        transition_matrix,
        labels=dict(x="Tipe Peta Berikutnya", y="Tipe Peta Saat Ini", color="Probabilitas (%)"),
        x=transition_matrix.columns,
        y=transition_matrix.index,
        color_continuous_scale=color_scheme,
        aspect="auto",
        title="Probabilitas Tipe Peta Berikutnya"
    )

    fig.update_layout(
        template="plotly_dark",
        height=400
    )

    fig.update_traces(
        hovertemplate='Dari: %{y}<br>Ke: %{x}<br>Probabilitas: %{z:.1f}%'
    )

    st.plotly_chart(fig, use_container_width=True)

    # Tambahkan insight tentang transisi yang paling umum
    st.subheader("Transisi Paling Umum")

    for map_type in transition_matrix.index:
        next_most_likely = transition_matrix.loc[map_type].idxmax()
        probability = transition_matrix.loc[map_type, next_most_likely]
        st.markdown(
            f"- Setelah **{map_type}**, tipe peta berikutnya paling mungkin adalah **{next_most_likely}** ({probability:.1f}%)")