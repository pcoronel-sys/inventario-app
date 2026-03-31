import streamlit as st
import pandas as pd
import io

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Bagó | Intel-Stock", page_icon="🧪", layout="wide")

# --- IDENTIDAD VISUAL Y CSS DINÁMICO ---
MAGENTA_BAGO = "#C7006A" 
MAGENTA_OSCURO = "#8A004A"

st.markdown(f"""
    <style>
    /* Fondo General */
    .main {{ background: #f4f7f9; }}
    
    /* Diseño de las Tarjetas del Menú Principal */
    .menu-card {{
        background: white;
        padding: 40px;
        border-radius: 20px;
        border-bottom: 8px solid {MAGENTA_BAGO};
        text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
        cursor: pointer;
        margin-bottom: 20px;
    }}
    .menu-card:hover {{
        transform: translateY(-10px);
        box-shadow: 0 15px 35px rgba(199, 0, 106, 0.15);
        background: linear-gradient(180deg, #ffffff 0%, #fff0f6 100%);
    }}
    
    /* Estilo de los Botones de Selección */
    .stButton > button {{
        width: 100%;
        border-radius: 12px !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
    }}

    /* Botón de Selección del Menú (Especial) */
    .menu-btn > div > button {{
        height: 80px !important;
        background: white !important;
        color: {MAGENTA_BAGO} !important;
        border: 2px solid {MAGENTA_BAGO} !important;
    }}
    .menu-btn > div > button:hover {{
        background: {MAGENTA_BAGO} !important;
        color: white !important;
    }}

    /* Botón de Descarga Premium */
    .stDownloadButton button {{
        background: linear-gradient(90deg, {MAGENTA_BAGO} 0%, {MAGENTA_OSCURO} 100%) !important;
        color: white !important;
        border-radius: 12px !important;
        font-weight: bold !important;
        height: 3.8em !important;
        width: 100% !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(199, 0, 106, 0.3) !important;
        transition: transform 0.2s !important;
    }}
    .stDownloadButton button:hover {{
        transform: scale(1.02) !important;
    }}

    /* Métricas */
    [data-testid="stMetric"] {{
        background: white;
        border-radius: 15px;
        padding: 15px;
        border-left: 5px solid {MAGENTA_BAGO};
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }}
    
    h1 {{ color: {MAGENTA_BAGO} !important; font-weight: 800; text-align: center; letter-spacing: -1px; }}
    h3 {{ color: #444 !important; text-align: center; font-weight: 400; }}
    </style>
    """, unsafe_allow_html=True)

# --- NAVEGACIÓN ---
if 'modo' not in st.session_state:
    st.session_state.modo = None

def seleccionar_modo(modo):
    st.session_state.modo = modo

def borrar_todo():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# --- PANTALLA 1: MENÚ PRINCIPAL DINÁMICO ---
if st.session_state.modo is None:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h1>🧪 Laboratorios Bagó</h1>", unsafe_allow_html=True)
    st.markdown("<h3>Sistema Inteligente de Conciliación de Inventarios</h3>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col1, col_gap, col2 = st.columns([1, 0.1, 1])
    
    with col1:
        st.markdown('<div class="menu-card">', unsafe_allow_html=True)
        st.write("### 📦 Modo Lote")
        st.write("Cruce detallado por código de material y número de lote.")
        st.markdown('<div class="menu-btn">', unsafe_allow_html=True)
        if st.button("INICIAR CON LOTE", key="btn_lote"):
            seleccionar_modo("con_lote")
            st.rerun()
        st.markdown('</div></div>', unsafe_allow_html=True)
            
    with col2:
        st.markdown('<div class="menu-card">', unsafe_allow_html=True)
        st.write("### 🔢 Modo Material")
        st.write("Suma total por código de producto, ignorando lotes.")
        st.markdown('<div class="menu-btn">', unsafe_allow_html=True)
        if st.button("INICIAR SIN LOTE", key="btn_sin_lote"):
            seleccionar_modo("sin_lote")
            st.rerun()
        st.markdown('</div></div>', unsafe_allow_html=True)

# --- PANTALLA 2: APLICACIÓN DE CONCILIACIÓN ---
else:
    c_head1, c_head2 = st.columns([4, 1])
    with c_head1:
        modo_txt = "CON LOTE" if st.session_state.modo == "con_lote" else "SIN LOTE"
        st.markdown(f"<h2 style='text-align: left; color:{MAGENTA_BAGO}; margin:0;'>🧪 Reporte: {modo_txt}</h2>", unsafe_allow_html=True)
    with c_head2:
        if st.button("🔄 Volver al Menú"):
            borrar_todo()

    st.divider()

    # Carga de archivos en tarjetas limpias
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        st.info("**PASO 1:** Subir Inventario Base (Bagó)")
        f1 = st.file_uploader("Excel Principal", type=['xlsx'], key="f1", label_visibility="collapsed")
    with col_f2:
        st.info("**PASO 2:** Subir Inventario Comparativo (FP/QX)")
        f2 = st.file_uploader("Excel Comparar", type=['xlsx'], key="f2", label_visibility="collapsed")

    if f1 and f2:
        try:
            df1 = pd.read_excel(f1)
            df2 = pd.read_excel(f2)
            
            def limpiar_y_agrupar(df):
                df.columns = df.columns.astype(str).str.strip().str.upper()
                df['MATERIAL'] = df['MATERIAL'].astype(str).str.strip().str.upper()
                agg = {'TOTAL': 'sum'}
                if 'DESCRIPCION' in df.columns:
                    df['DESCRIPCION'] = df['DESCRIPCION'].astype(str).str.strip().str.upper()
                    agg['DESCRIPCION'] = 'first'
                
                if st.session_state.modo == "con_lote":
                    if 'LOTE' not in df.columns: df['LOTE'] = 'SIN LOTE'
                    df['LOTE'] = df['LOTE'].fillna('SIN LOTE').astype(str).str.strip().str.upper()
                    return df.groupby(['MATERIAL', 'LOTE']).agg(agg).reset_index()
                else:
                    return df.groupby(['MATERIAL']).agg(agg).reset_index()

            d1 = limpiar_y_agrupar(df1)
            d2 = limpiar_y_agrupar(df2)

            keys = ['MATERIAL', 'LOTE'] if st.session_state.modo == "con_lote" else ['MATERIAL']
            res_base = pd.merge(d1, d2, on=keys, how='left', suffixes=('_BAGO', '_FPQX')).fillna(0)
            
            extra_df = pd.merge(d2, d1, on=keys, how='left', indicator=True)
            solo_en_fpqx = extra_df[extra_df['_merge'] == 'left_only'].drop(columns=['_merge'])

            # --- DASHBOARD ---
            st.markdown("### 📊 Dashboard de Consistencia")
            m1, m2, m3, m4 = st.columns(4)
            diferencias = len(res_base[res_base['TOTAL_BAGO'] != res_base['TOTAL_FPQX']])
            codigos_faltantes = len(solo_en_fpqx)

            m1.metric("Items en Bagó", len(d1))
            m2.metric("Discrepancias", diferencias, delta_color="inverse")
            m3.metric("Faltantes en Bagó", codigos_faltantes, delta="⚠️ EXTRA", delta_color="inverse" if codigos_faltantes > 0 else "normal")
            m4.metric("Precisión", f"{round((1 - (codigos_faltantes/len(d1)))*100,1)}%" if len(d1)>0 else "0%")

            if codigos_faltantes > 0:
                st.warning(f"🚨 **ALERTA:** Se detectaron {codigos_faltantes} códigos en FP/QX que no existen en Bagó.")

            st.divider()

            # --- FILTROS ---
            col_busq, col_ver = st.columns([2, 1])
            with col_bus
