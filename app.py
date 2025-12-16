import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# --- 1. Konfigurasi Halaman & Fungsi Mode Gelap/Terang ---
st.set_page_config(
    page_title="Dashboard Analisis Biofarmaka Jawa Barat",
    layout="wide",
    initial_sidebar_state="expanded"
)

BACKGROUND_IMAGE_LIGHT = "https://i.ibb.co/L9hVf7b/soft-white-linen-texture.jpg" 
BACKGROUND_IMAGE_DARK = "https://i.ibb.co/h8W5b1Y/dark-subtle-plant-shadow.jpg" 

# Custom CSS untuk Tema HIJAU 
LIGHT_THEME_CSS = f"""
.stApp {{
    background-color: #D9F3D8;
    background-image: url({BACKGROUND_IMAGE_LIGHT});
    background-size: cover;
    background-attachment: fixed;
    background-position: center;
    color: #1D331D; 
}}

/* 2. Area Konten Utama */
[data-testid="stAppViewBlockContainer"] {{
    background-color: rgba(217, 243, 216, 0.98);
    padding: 2rem;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1); 
}}

/* Sidebar background */
[data-testid="stSidebar"] {{
    background-color: #C8E6C9; 
    color: #1D331D;
}}

.stSelectbox, .stMultiSelect, .stTextInput, .stNumberInput, .stTextarea {{
    color: #1D331D !important;
}}

/* Header/Title style */
h1 {{
    color: #2E7D32; 
    border-bottom: 2px solid #A5D6A7; 
    padding-bottom: 10px;
}}
h2, h3, h4 {{
    color: #388E3C; 
}}

/* Metric boxes */
[data-testid="stMetricValue"] {{
    color: #558B2F;
    font-weight: bold;
}}
[data-testid="stMetricLabel"] {{
    color: #1D331D; 
}}

.stButton>button {{
    background-color: #66BB6A; 
    color: white; 
    border: 1px solid #388E3C;
    border-radius: 8px;
}}
.stButton>button:hover {{
    background-color: #388E3C;
    color: white; 
}}

hr {{
    border-top: 1px solid #A5D6A7;
}}
"""

# Custom CSS untuk Tema HIJAU HUTAN 
DARK_THEME_CSS = f"""
.stApp {{
    background-color: #1E311D;
    background-image: url({BACKGROUND_IMAGE_DARK});
    background-size: cover;
    background-attachment: fixed;
    background-position: center;
    color: #EFEBE9;
}}

/* Area Konten Utama */
[data-testid="stAppViewBlockContainer"] {{
    background-color: rgba(30, 49, 29, 0.95);
    padding: 2rem;
    border-radius: 12px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.5);
}}

/* Sidebar background */
[data-testid="stSidebar"] {{
    background-color: #3C5139; 
    color: #EFEBE9;
}}

/* Header/Title style */
h1 {{
    color: #D5E1D4;
    border-bottom: 2px solid #5C7A59;
    padding-bottom: 10px;
}}
h2, h3, h4 {{
    color: #9EAF9D; 
}}

/* Metric boxes */
[data-testid="stMetricValue"] {{
    color: #9CCC65; 
    font-weight: bold;
}}
[data-testid="stMetricLabel"] {{
    color: #9EAF9D;
}}

/* Tombol (aksen hijau cerah) */
.stButton>button {{
    background-color: #558B2F; 
    color: #D5E1D4;
    border: 1px solid #9CCC65;
    border-radius: 8px;
}}
.stButton>button:hover {{
    background-color: #388E3C;
    color: white;
}}

/* Garis pemisah */
hr {{
    border-top: 1px solid #5C7A59;
}}
"""

def mode_switcher():
    """Fungsi untuk mengubah mode tema melalui session state dan CSS injection."""
    if 'mode' not in st.session_state:
        st.session_state.mode = 'light'

    def toggle_mode():
        st.session_state.mode = 'dark' if st.session_state.mode == 'light' else 'light'

    # Injeksi CSS berdasarkan mode
    if st.session_state.mode == 'light':
        st.markdown(f"<style>{LIGHT_THEME_CSS}</style>", unsafe_allow_html=True)
    else:
        st.markdown(f"<style>{DARK_THEME_CSS}</style>", unsafe_allow_html=True)
        
    # Tampilkan tombol di sidebar
    st.sidebar.button(
        f"{'🌙 Beralih ke Dark Mode' if st.session_state.mode == 'light' else '☀️ Beralih ke Light Mode'}", 
        on_click=toggle_mode, 
        use_container_width=True
    )

# Panggil switcher mode sebelum konten utama
mode_switcher()

# --- Fungsi pembersihan dan pemuatan data ---
def clean_column_name(col_name):
    col_name = str(col_name).strip()
    col_name = col_name.replace(' ', '_').replace('/', '_').replace('(', '').replace(')', '')
    col_name = col_name.replace('_kilogram', '').replace('_Kg', '').replace('_meter_persegi', '').replace('_M2', '').replace('_pohon', '').replace('_Pohon', '').replace('__', '_')
    return col_name

@st.cache_data
def load_data():
    """Memuat semua data CSV dan menggabungkannya."""
    # Mapping file yang tersedia
    data_files = {
        'cluster_2022': 'cluster_2022.csv',
        'cluster_2023': 'cluster_2023.csv',
        'cluster_2024': 'cluster_2024.csv',
        'dataset_final': 'dataset_final.csv'
    }
    data = {}
    
    # Load dataset_final
    try:
        # Menggunakan file dataset_final.csv yang tersedia
        df_final = pd.read_csv(data_files['dataset_final'])
        df_final.columns = [clean_column_name(col) for col in df_final.columns]
        data['dataset_final'] = df_final
    except Exception:
        # Jika dataset_final gagal, aplikasi tidak bisa dilanjutkan
        return None
        
    # Load and combine cluster data
    cluster_dfs = []
    for year in ['2022', '2023', '2024']:
        file = data_files.get(f'cluster_{year}')
        if file:
            try:
                df_cluster_temp = pd.read_csv(file)
                df_cluster_temp.columns = [clean_column_name(col) for col in df_cluster_temp.columns]
                
                # Menemukan kolom klaster yang benar (Cluster_YYYY)
                cluster_col_name = [col for col in df_cluster_temp.columns if 'Cluster' in col and df_cluster_temp.columns.get_loc(col) == df_cluster_temp.shape[1]-1][0]
                df_cluster_temp = df_cluster_temp.rename(columns={cluster_col_name: 'Cluster'})
                
                for col in ['Produksi_Total', 'LuasPanen_Total', 'Cluster']:
                    if col in df_cluster_temp.columns:
                        df_cluster_temp[col] = pd.to_numeric(df_cluster_temp[col], errors='coerce').fillna(0).astype(int)
                        
                cluster_dfs.append(df_cluster_temp)
            except Exception:
                pass 

    if cluster_dfs:
        data['cluster_all'] = pd.concat(cluster_dfs, ignore_index=True)
    
    return data

def preprocess_biofarmaka_data(df_final):
    """Melakukan pivoting dan pembersihan untuk data komoditas, termasuk menghitung efisiensi."""
    prod_cols = [col for col in df_final.columns if 'Produksi_' in col]
    luas_cols = [col for col in df_final.columns if 'Luas_Panen_' in col]
    
    komoditas_prod_map = {col: col.replace('Produksi_', '') for col in prod_cols}
    komoditas_luas_map = {col: col.replace('Luas_Panen_', '') for col in luas_cols}
    
    common_komoditas = list(set(komoditas_prod_map.values()) & set(komoditas_luas_map.values()))
    
    final_prod_cols = [k for k, v in komoditas_prod_map.items() if v in common_komoditas]
    final_luas_cols = [k for k, v in komoditas_luas_map.items() if v in common_komoditas]
    
    df_prod = df_final[['Kabupaten_Kota', 'Tahun'] + final_prod_cols].copy()
    df_prod = df_prod.rename(columns={k: komoditas_prod_map[k] for k in final_prod_cols})
    df_prod_melt = df_prod.melt(id_vars=['Kabupaten_Kota', 'Tahun'], value_vars=common_komoditas, var_name='Komoditas', value_name='Produksi_Kg')

    df_luas = df_final[['Kabupaten_Kota', 'Tahun'] + final_luas_cols].copy()
    df_luas = df_luas.rename(columns={k: komoditas_luas_map[k] for k in final_luas_cols})
    df_luas_melt = df_luas.melt(id_vars=['Kabupaten_Kota', 'Tahun'], value_vars=common_komoditas, var_name='Komoditas', value_name='Luas_Panen')
    
    df_merged = pd.merge(df_prod_melt, df_luas_melt, on=['Kabupaten_Kota', 'Tahun', 'Komoditas'])
    
    df_merged['Produksi_Kg'] = pd.to_numeric(df_merged['Produksi_Kg'], errors='coerce').fillna(0)
    df_merged['Luas_Panen'] = pd.to_numeric(df_merged['Luas_Panen'], errors='coerce').fillna(0)
    
    # HITUNG METRIK BARU: Efisiensi Produksi (Kg/M2)
    df_merged['Efisiensi_Kg_per_M2'] = np.where(
        df_merged['Luas_Panen'] > 0,
        df_merged['Produksi_Kg'] / df_merged['Luas_Panen'],
        0 
    )
    
    return df_merged

# --- Muat Data ---
data_dict = load_data()

if data_dict is not None and 'dataset_final' in data_dict:
    df_final = data_dict['dataset_final']
    df_cluster = data_dict.get('cluster_all')
    
    # ==========================================================
    # BAGIAN BARU: Filter Data "Sampah" (Angka sementara, dll)
    # ==========================================================
    junk_values = ['0', 'Angka sementara', 'Angka tetap', 'Catatan']
    df_final = df_final[~df_final['Kabupaten_Kota'].isin(junk_values)]
    # ==========================================================

    try:
        df_biofarmaka = preprocess_biofarmaka_data(df_final)
    except Exception as e:
        st.error(f"Error saat pra-pemrosesan data: {e}")
        st.stop()
        
    # --- Judul Aplikasi ---
    st.title("🌿 Dashboard Analisis Biofarmaka Jawa Barat 🌾")
    st.caption("Analisis Komprehensif Produksi, Luas Panen, Efisiensi, dan Klastering Wilayah (2022-2024)")

    # --- Sidebar untuk Filter Global ---
    with st.sidebar:
        st.header("⚙️ Pengaturan Data")
        
        available_years = sorted(df_final['Tahun'].unique())
        selected_year = st.selectbox("Pilih Tahun Analisis:", available_years)

        available_kabkota = sorted(df_final['Kabupaten_Kota'].unique())
        
        # Logika agar tidak error jika data kosong setelah difilter
        if available_kabkota:
            default_kabkota_trend = available_kabkota[:2] if len(available_kabkota) >= 2 else available_kabkota
        else:
            default_kabkota_trend = []
            
        selected_kabkota_trend = st.multiselect("Pilih Kab/Kota untuk Tren Komoditas:", available_kabkota, default=default_kabkota_trend)
        
        available_komoditas = sorted(df_biofarmaka['Komoditas'].unique())
        selected_komoditas = st.selectbox("Pilih Komoditas untuk Tren:", available_komoditas)
        
        st.divider()
        st.subheader("Filter Riwayat Klaster")
        
        # Logika agar tidak error jika data kosong
        if available_kabkota:
            selected_kabkota_cluster = st.selectbox(
                "Pilih Kabupaten/Kota untuk Riwayat Klaster:", 
                available_kabkota,
                index=0
            )
        else:
            st.warning("Data Kabupaten/Kota kosong.")
            selected_kabkota_cluster = None

    # --- Tab Aplikasi ---
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Ringkasan & Tren Waktu", 
        "🗺️ Klastering & Peringkat Wilayah", 
        "📈 Perbandingan & Efisiensi Komoditas", 
        "Raw Data"])

    # Tentukan template Plotly berdasarkan mode tema
    plotly_template = "plotly_white" if st.session_state.mode == 'light' else "plotly_dark"

    # --- Tab 1: Ringkasan & Tren Waktu ---
    with tab1:
        st.header(f"Total Agregat Produksi Tahun {selected_year}")
        
        df_bio_year = df_biofarmaka[df_biofarmaka['Tahun'] == selected_year]
        
        total_produksi = df_bio_year['Produksi_Kg'].sum()
        total_luas_panen = df_bio_year['Luas_Panen'].sum()
        avg_efficiency = df_bio_year['Efisiensi_Kg_per_M2'].mean()
        
        # Perhitungan YoY untuk Produksi
        prod_yoy = None
        try:
            df_prev_year = df_biofarmaka[df_biofarmaka['Tahun'] == (selected_year - 1)]
            prev_production = df_prev_year['Produksi_Kg'].sum()
            prod_yoy = ((total_produksi - prev_production) / prev_production) * 100 if prev_production else 0
        except:
            pass

        col_metric_1, col_metric_2, col_metric_3, col_metric_4 = st.columns(4)
        
        with col_metric_1:
            st.info(f"Tahun Analisis: **{selected_year}**", icon="📅")
        
        with col_metric_2:
            st.metric(
                "Total Produksi", 
                f"{total_produksi:,.0f} Kg",
                delta=f"{prod_yoy:.1f} % YoY" if prod_yoy is not None else None,
                delta_color="normal"
            )
        with col_metric_3:
            st.metric("Total Luas Panen", f"{total_luas_panen:,.0f} M2/Pohon")

        with col_metric_4:
            st.metric("Rata-rata Efisiensi", f"{avg_efficiency:.3f} Kg/M2")

        st.divider()

        st.subheader(f"📈 Tren Produksi {selected_komoditas} Antar Wilayah")
        
        df_trend = df_biofarmaka[
            (df_biofarmaka['Kabupaten_Kota'].isin(selected_kabkota_trend)) & 
            (df_biofarmaka['Komoditas'] == selected_komoditas)
        ]

        if not df_trend.empty:
            df_trend_agg = df_trend.groupby(['Tahun', 'Kabupaten_Kota'])['Produksi_Kg'].sum().reset_index()
            fig_trend = px.line(
                df_trend_agg, x='Tahun', y='Produksi_Kg', color='Kabupaten_Kota',
                title=f'Perkembangan Produksi {selected_komoditas} ({available_years[0]}-{available_years[-1]})',
                labels={'Produksi_Kg': 'Produksi (Kg)', 'Tahun': 'Tahun'}, 
                markers=True, template=plotly_template
            )
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("Pilih Kabupaten/Kota dan Komoditas di sidebar untuk melihat tren waktu.")


    # --- Tab 2: Klastering & Peringkat Wilayah ---
    with tab2:
        st.header("🗺️ Analisis Klastering Wilayah (K-Means)")
        
        col_scatter, col_box = st.columns(2)

        if df_cluster is not None and not df_cluster.empty:
            df_cluster_year = df_cluster[df_cluster['Tahun'] == selected_year]
            
            if 'Produksi_Total' in df_cluster_year.columns and 'LuasPanen_Total' in df_cluster_year.columns:
                
                with col_scatter:
                    st.subheader(f"Sebaran Klaster Produksi vs Luas Panen Tahun {selected_year}")
                    fig_cluster = px.scatter(
                        df_cluster_year, x='LuasPanen_Total', y='Produksi_Total',
                        color='Cluster', 
                        hover_data=['Kabupaten_Kota', 'Produksi_Total', 'LuasPanen_Total'],
                        title='Klastering Wilayah Biofarmaka',
                        labels={'LuasPanen_Total': 'Luas Panen Total (M2/Pohon)', 'Produksi_Total': 'Produksi Total (Kg)'},
                        color_continuous_scale=px.colors.qualitative.Antique, 
                        template=plotly_template
                    )
                    st.plotly_chart(fig_cluster, use_container_width=True)
                    

                with col_box:
                    st.subheader(f"Distribusi Produksi per Klaster Tahun {selected_year} (Box Plot)")
                    fig_box_cluster = px.box(
                        df_cluster_year, 
                        x='Cluster', 
                        y='Produksi_Total',
                        color='Cluster',
                        title='Distribusi Produksi Total Berdasarkan Klaster',
                        labels={'Produksi_Total': 'Produksi Total (Kg)', 'Cluster': 'Kategori Klaster'},
                        template=plotly_template
                    )
                    st.plotly_chart(fig_box_cluster, use_container_width=True)
            else:
                st.warning("Kolom Klastering tidak ditemukan di file Klaster.")
        else:
            st.info("File klastering tidak tersedia atau gagal dimuat.")
            
        st.divider()
        
        # Riwayat Klaster Tahunan
        st.subheader(f"🔍 Riwayat Klaster Tahunan untuk Kabupaten/Kota: **{selected_kabkota_cluster}**")
        
        if df_cluster is not None and not df_cluster.empty:
            df_history = df_cluster[df_cluster['Kabupaten_Kota'] == selected_kabkota_cluster].sort_values(by='Tahun')
            
            if not df_history.empty:
                fig_history = px.line(
                    df_history, x='Tahun', y='Cluster', 
                    title=f'Perubahan Kategori Klaster {selected_kabkota_cluster} (2022-2024)',
                    labels={'Cluster': 'Kategori Klaster (0=Rendah, 2=Tinggi)'},
                    markers=True, template=plotly_template
                )
                fig_history.update_yaxes(tick0=0, dtick=1, range=[-0.5, 2.5]) 
                st.plotly_chart(fig_history, use_container_width=True)
                
                st.markdown("### Tabel Detail Klaster Tahunan")
                st.dataframe(
                    df_history[['Tahun', 'Produksi_Total', 'LuasPanen_Total', 'Cluster']].sort_values(by='Tahun', ascending=False),
                    column_config={
                        "Produksi_Total": st.column_config.NumberColumn("Produksi Total (Kg)", format="%.0f"),
                        "LuasPanen_Total": st.column_config.NumberColumn("Luas Panen Total", format="%.0f"),
                        "Cluster": st.column_config.TextColumn("Kategori Klaster (0/1/2)")
                    },
                    use_container_width=True, hide_index=True
                )
                st.caption("Interpretasi Klaster: 0=Rendah/Kurang Potensi, 1=Sedang, 2=Tinggi/Potensi Utama.")
            else:
                st.info(f"Data klastering tidak ditemukan untuk {selected_kabkota_cluster}.")
        


    # --- Tab 3: Perbandingan & Efisiensi Komoditas ---
    with tab3:
        st.header(f"Analisis Efisiensi dan Kontribusi Komoditas Tahun {selected_year}")
        
        df_compare = df_bio_year.groupby('Komoditas').agg(
            Total_Produksi_Kg=('Produksi_Kg', 'sum'),
            Total_Luas_Panen=('Luas_Panen', 'sum'),
            Rata_rata_Efisiensi=('Efisiensi_Kg_per_M2', 'mean')
        ).reset_index()
        
        # --- Analisis Efisiensi Produksi (Scatter Plot) ---
        st.subheader("⚖️ Analisis Efisiensi Produksi (Kg/M2) Komoditas")
        st.caption("Visualisasi ini membandingkan total produksi (ukuran gelembung) dengan rata-rata efisiensi (sumbu Y). Komoditas yang berada di atas adalah yang paling efisien dalam menggunakan lahan.")
        
        fig_eff = px.scatter(
            df_compare, 
            x='Total_Luas_Panen', 
            y='Rata_rata_Efisiensi', 
            color='Komoditas', 
            size='Total_Produksi_Kg', 
            hover_data=['Total_Produksi_Kg', 'Total_Luas_Panen'],
            title=f'Perbandingan Efisiensi Produksi Komoditas ({selected_year})',
            labels={'Total_Luas_Panen': 'Total Luas Panen (Log Scale)', 'Rata_rata_Efisiensi': 'Rata-rata Efisiensi (Kg/M2)'},
            log_x=True, 
            template=plotly_template
        )
        st.plotly_chart(fig_eff, use_container_width=True)
        
        
        st.divider()

        # --- Peringkat Komoditas per Wilayah (Tabel) ---
        st.subheader("🥇 Peringkat Komoditas Unggulan berdasarkan Produksi")
        
        selected_city_for_ranking = st.selectbox(
            "Pilih Kabupaten/Kota untuk Melihat Peringkat Komoditas Unggulan:", 
            ['Semua Wilayah'] + available_kabkota,
            index=0
        )
        
        if selected_city_for_ranking == 'Semua Wilayah':
            df_rank_data = df_compare[['Komoditas', 'Total_Produksi_Kg', 'Total_Luas_Panen', 'Rata_rata_Efisiensi']].copy()
            title_suffix = "Semua Wilayah"
        else:
            df_rank_data = df_bio_year[df_bio_year['Kabupaten_Kota'] == selected_city_for_ranking]
            df_rank_data = df_rank_data.groupby('Komoditas').agg(
                Total_Produksi_Kg=('Produksi_Kg', 'sum'),
                Total_Luas_Panen=('Luas_Panen', 'sum'),
                Rata_rata_Efisiensi=('Efisiensi_Kg_per_M2', 'mean')
            ).reset_index()
            title_suffix = selected_city_for_ranking
            
        df_rank_data = df_rank_data[df_rank_data['Total_Produksi_Kg'] > 0]
        df_rank_data['Peringkat_Prod'] = df_rank_data['Total_Produksi_Kg'].rank(method='min', ascending=False).astype(int)
        df_rank_data = df_rank_data.sort_values(by='Peringkat_Prod').head(10)
        
        st.markdown(f"**Top 10 Komoditas di {title_suffix} Tahun {selected_year}**")
        st.dataframe(
            df_rank_data, 
            column_order=['Peringkat_Prod', 'Komoditas', 'Total_Produksi_Kg', 'Rata_rata_Efisiensi'],
            column_config={
                "Peringkat_Prod": st.column_config.NumberColumn("Peringkat", format="%d"),
                "Komoditas": "Komoditas",
                "Total_Produksi_Kg": st.column_config.NumberColumn("Produksi (Kg)", format="%.0f"),
                "Rata_rata_Efisiensi": st.column_config.NumberColumn("Efisiensi (Kg/M2)", format="%.3f")
            },
            hide_index=True, 
            use_container_width=True
        )


    # --- Tab 4: Raw Data ---
    with tab4:
        st.header("Data Mentah dan Hasil Penggabungan")
        
        with st.expander("Data Final Produksi dan Luas Panen"):
            st.dataframe(df_final.head(), use_container_width=True)
        
        with st.expander("Data Klastering Gabungan (2022-2024)"):
            if df_cluster is not None:
                 st.dataframe(df_cluster, use_container_width=True)
            else:
                 st.info("Data klastering gabungan tidak tersedia.")

        with st.expander("Data Biofarmaka (Format Long, termasuk Efisiensi)"):
            st.dataframe(df_biofarmaka.head(), use_container_width=True)

else:
    st.error("Aplikasi gagal berjalan. Pastikan file `dataset_final.csv` dan file klaster ada dan terbaca dengan benar.")