import streamlit as st
import pandas as pd
import io

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Bagó | Gestion Stock", page_icon="🧪", layout="wide")

# --- DISEÑO ESTÉTICO CENTRADO Y COMPACTO ---
MAGENTA_BAGO = "#C7006A" 
MAGENTA_OSCURO = "#8A004A"

st.markdown(f"""
    <style>
    .main {{ 
        background: radial-gradient(circle at top right, #ffffff, #f0f2f6); 
    }}
    
    .main-title {{
        color: {MAGENTA_BAGO};
        font-size: 3.5rem !important;
        font-weight: 800 !important;
        text-align: center;
        margin-top: 50px;
        margin-bottom: 0px;
        letter-spacing: -2px;
    }}
    
    .sub-title {{
        color: #666;
        text-align: center;
        font-size: 1.2rem;
        margin-bottom: 40px;
    }}

    /* ESTILO DE LOS BOTONES TIPO TARJETA */
    div.stButton > button {{
        background: white !important;
        color: #333 !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 24px !important;
        height: 180px !important;
        width: 100% !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05) !important;
        transition: all 0.3s ease-in-out !important;
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        padding: 10px !important;
    }}

    div.stButton > button:hover {{
        background: linear-gradient(135deg, {MAGENTA_BAGO} 0%, {MAGENTA_OSCURO} 100%) !important;
        color: white !important;
        transform: translateY(-5px) !important;
        box-shadow: 0 12px 25px rgba(199, 0, 106, 0.25) !important;
    }}

    /* REPORTE METRICAS */
    [data-testid="stMetric"] {{
        background: white;
        border-radius: 20px;
        padding: 20px;
        border-left: 6px solid {MAGENTA_BAGO};
    }}

    .stDownloadButton button {{
        background: linear-gradient(90deg, {MAGENTA_BAGO}, {MAGENTA_OSCURO}) !important;
        color: white !important;
        border-radius: 14px !important;
        font-weight: bold !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE NAVEGACIÓN ---
if 'modo' not in st.session_state:
    st.session_state.modo = None

def borrar_todo():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# --- PANTALLA 1: MENÚ JUNTOS EN EL CENTRO ---
if st.session_state.modo is None:
    st.markdown('<p class="main-title">Laboratorios Bagó</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Sistema de cruce de inventarios</p>', unsafe_allow_html=True)
    
    # Ajuste de columnas para que los botones choquen en el medio
    _, col_l, col_r, _ = st.columns([5.5, 2, 2, 5.5])
    
    with col_l:
        if st.button("\n\nMATERIAL DE EMPAQUE\n\nALMACEN 1010", key="btn_lote"):
            st.session_state.modo = "con_lote"
            st.rerun()
    with col_r:
        if st.button("\n\nMATERIAL PROMOCIONAL\n\nALMACEN 1070", key="btn_sin_lote"):
            st.session_state.modo = "sin_lote"
            st.rerun()

# --- PANTALLA 2: REPORTE ---
else:
    c1, c2 = st.columns([4, 1])
    with c1:
        st.markdown(f"<h2 style='color:{MAGENTA_BAGO}; margin:0;'>📋 Panel: {'Lote' if st.session_state.modo == 'con_lote' else 'Material'}</h2>", unsafe_allow_html=True)
    with c2:
        if st.button("🔄 Salir"): borrar_todo()

    st.divider()

    f_col1, f_col2 = st.columns(2)
    with f_col1:
        st.info("📂 Inventario BASE (BAGÓ)")
        f1 = st.file_uploader("Subir", type=['xlsx'], key="f1", label_visibility="collapsed")
    with f_col2:
        st.info("📂 Inventario COMPARAR (FP/QX)")
        f2 = st.file_uploader("Subir", type=['xlsx'], key="f2", label_visibility="collapsed")

    if f1 and f2:
        try:
            df1, df2 = pd.read_excel(f1), pd.read_excel(f2)
            
            def limpiar(df):
                df.columns = df.columns.astype(str).str.strip().str.upper()
                df['MATERIAL'] = df['MATERIAL'].astype(str).str.strip().str.upper()
                agg = {'TOTAL': 'sum'}
                if 'DESCRIPCION' in df.columns:
                    df['DESCRIPCION'] = df['DESCRIPCION'].astype(str).str.strip().str.upper()
                    agg['DESCRIPCION'] = 'first'
                
                if st.session_state.modo == "con_lote":
                    # CORRECCIÓN AQUÍ: Agregamos .str para el upper()
                    if 'LOTE' in df.columns:
                        df['LOTE'] = df['LOTE'].fillna('SIN LOTE').astype(str).str.strip().str.upper()
                    else:
                        df['LOTE'] = 'SIN LOTE'
                    return df.groupby(['MATERIAL', 'LOTE']).agg(agg).reset_index()
                
                return df.groupby(['MATERIAL']).agg(agg).reset_index()

            d1, d2 = limpiar(df1), limpiar(df2)
            keys = ['MATERIAL', 'LOTE'] if st.session_state.modo == "con_lote" else ['MATERIAL']
            
            res_maestro = pd.merge(d1, d2, on=keys, how='outer', suffixes=('_BAGO', '_FPQX')).fillna(0)
            res_maestro['DIFERENCIA'] = res_maestro['TOTAL_BAGO'] - res_maestro['TOTAL_FPQX']

            # DASHBOARD
            m1, m2, m3, m4 = st.columns(4)
            base_bago = res_maestro[res_maestro['TOTAL_BAGO'] > 0]
            desconocidos = res_maestro[(res_maestro['TOTAL_BAGO'] == 0) & (res_maestro['TOTAL_FPQX'] > 0)]
            diff_stock = base_bago[base_bago['DIFERENCIA'] != 0]

            m1.metric("Items Bagó", len(base_bago))
            m2.metric("Discrepancias", len(diff_stock))
            m3.metric("Desconocidos", len(desconocidos), delta_color="inverse")
            m4.metric("TOTAL ERRORES", len(diff_stock) + len(desconocidos))

            st.divider()

            # FILTROS
            col_b, col_v = st.columns([2, 1])
            with col_b: busq = st.text_input("🔍 Búsqueda rápida...")
            with col_v: vista = st.selectbox("🎯 Filtro Auditoría:", 
                                ["Reporte Base", "Solo Diferencias", "Solo Desconocidos", "TOTAL DIFERENCIAS"])

            if vista == "Reporte Base": res_final = base_bago.copy()
            elif vista == "Solo Diferencias": res_final = diff_stock.copy()
            elif vista == "Solo Desconocidos": res_final = desconocidos.copy()
            else: res_final = res_maestro[res_maestro['DIFERENCIA'] != 0].copy()

            if busq:
                res_final = res_final[res_final.apply(lambda r: r.astype(str).str.contains(busq, case=False).any(), axis=1)]

            if not res_final.empty:
                res_final = res_final.rename(columns={'TOTAL_BAGO': 'TOTAL BAGO', 'TOTAL_FPQX': 'TOTAL FP/QX'})
                st.dataframe(res_final.style.highlight_between(left=-999999, right=-0.1, color='#ffdadb', subset=['DIFERENCIA']), use_container_width=True)
                
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    res_final.to_excel(writer, index=False)
                st.download_button("📥 DESCARGAR RESULTADOS", data=output.getvalue(), file_name="Bago_Reporte.xlsx")
        except Exception as e:
            st.error(f"Error detectado: {e}")
