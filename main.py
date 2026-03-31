import streamlit as st
import pandas as pd
import io
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Bagó | Intel-Stock Pro", page_icon="🧪", layout="wide")

# --- DISEÑO ESTÉTICO UI/UX PREMIUM ---
MAGENTA_BAGO = "#C7006A" 
MAGENTA_OSCURO = "#8A004A"

st.markdown(f"""
    <style>
    .main {{ background: linear-gradient(135deg, #f8f9fc 0%, #e2e7f0 100%); }}
    
    /* Saludo Dinámico */
    .welcome-text {{
        text-align: center;
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 20px;
        font-weight: 400;
    }}

    /* Título con Reflejo */
    .main-title {{
        color: {MAGENTA_BAGO};
        font-size: 3.8rem !important;
        font-weight: 800 !important;
        text-align: center;
        margin-top: 10px;
        margin-bottom: 0px;
        letter-spacing: -2px;
        filter: drop-shadow(0px 4px 4px rgba(0,0,0,0.1));
    }}

    /* Botones de Inicio con Estilo */
    div.stButton > button {{
        background: white !important;
        color: #333 !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 28px !important;
        height: 200px !important;
        width: 100% !important;
        box-shadow: 0 15px 35px rgba(0,0,0,0.05) !important;
        transition: all 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        font-weight: 700 !important;
    }}

    div.stButton > button:hover {{
        background: linear-gradient(145deg, {MAGENTA_BAGO}, {MAGENTA_OSCURO}) !important;
        color: white !important;
        transform: translateY(-10px) scale(1.02) !important;
        box-shadow: 0 20px 40px rgba(199, 0, 106, 0.25) !important;
    }}

    /* Tarjetas de Métricas (Manteniendo el Estilo de la Imagen) */
    div[data-testid="stMetric"] {{
        background: white !important;
        border-radius: 20px !important;
        padding: 20px !important;
        border-left: 6px solid {MAGENTA_BAGO} !important;
        box-shadow: 0 8px 25px rgba(0,0,0,0.04) !important;
    }}

    /* Footer Informativo */
    .footer-box {{
        background: rgba(255,255,255,0.5);
        border-radius: 20px;
        padding: 20px;
        margin-top: 50px;
        text-align: center;
        border: 1px dashed {MAGENTA_BAGO};
    }}

    [data-testid="stSidebar"] {{
        background-color: white !important;
        border-right: 2px solid {MAGENTA_BAGO}22;
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

# --- SALUDO DINÁMICO ---
hora = datetime.now().hour
if hora < 12: saludo = "☀️ Buenos días"
elif hora < 19: saludo = "🌤️ Buenas tardes"
else: saludo = "🌙 Buenas noches"

# --- PANTALLA 1: INICIO ---
if st.session_state.modo is None:
    st.markdown(f'<p class="welcome-text">{saludo}, Equipo Bagó</p>', unsafe_allow_html=True)
    st.markdown('<p class="main-title">Laboratorios Bagó</p>', unsafe_allow_html=True)
    st.markdown("<h4 style='text-align:center; color:#888; font-weight:300; margin-bottom:50px;'>Intelligence Stock Management System</h4>", unsafe_allow_html=True)
    
    _, col_l, col_r, _ = st.columns([7.5, 2.2, 2.2, 5.5])
    
    with col_l:
        st.markdown(f"<div style='text-align:center; color:{MAGENTA_BAGO}; font-weight:bold; margin-bottom:10px;'>BODEGA DE EMPAQUE</div>", unsafe_allow_html=True)
        if st.button("📦\n\nALMACÉN 1010\n\n"):
            st.session_state.modo = "con_lote"
            st.rerun()
            
    with col_r:
        st.markdown(f"<div style='text-align:center; color:{MAGENTA_BAGO}; font-weight:bold; margin-bottom:10px;'>BODEGA PROMOCIONAL</div>", unsafe_allow_html=True)
        if st.button("🔢\n\nALMACÉN 1070\n\n"):
            st.session_state.modo = "sin_lote"
            st.rerun()

    f1, f2, f3 = st.columns(3)
    with f1: st.markdown("<div class='footer-box'><b>1. Selecciona</b><br>El almacén a auditar.</div>", unsafe_allow_html=True)
    with f2: st.markdown("<div class='footer-box'><b>2. Carga</b><br>Sube tus archivos de Excel.</div>", unsafe_allow_html=True)
    with f3: st.markdown("<div class='footer-box'><b>3. Reporta</b><br>Descarga el cruce final.</div>", unsafe_allow_html=True)

# --- PANTALLA 2: REPORTE ---
else:
    with st.sidebar:
        st.markdown(f"<h2 style='color:{MAGENTA_BAGO};'>⚙️ Controles</h2>", unsafe_allow_html=True)
        st.info(f"📍 Bodega: {'1010' if st.session_state.modo == 'con_lote' else '1070'}")
        busq = st.text_input("🔍 Buscar Material...")
        vista = st.selectbox("🎯 Vista:", ["Base Bagó", "Diferencias", "No en Base", "Todo"])
        st.divider()
        if st.button("🏠 Volver al Inicio"): borrar_todo()

    st.markdown(f"<h2 style='color:{MAGENTA_BAGO};'>📊 Dashboard de Inventario</h2>", unsafe_allow_html=True)
    c_f1, c_f2 = st.columns(2)
    with c_f1: f1 = st.file_uploader("Subir Base Bagó", type=['xlsx'], key="f1")
    with c_f2: f2 = st.file_uploader("Subir Comparar", type=['xlsx'], key="f2")

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
                    df['LOTE'] = df['LOTE'].fillna('SN').astype(str).str.strip().str.upper() if 'LOTE' in df.columns else 'SN'
                    return df.groupby(['MATERIAL', 'LOTE']).agg(agg).reset_index()
                return df.groupby(['MATERIAL']).agg(agg).reset_index()

            d1, d2 = limpiar(df1), limpiar(df2)
            keys = ['MATERIAL', 'LOTE'] if st.session_state.modo == "con_lote" else ['MATERIAL']
            res_maestro = pd.merge(d1, d2, on=keys, how='outer', suffixes=('_BAGO', '_FPQX'))
            
            for col in ['DESCRIPCION', 'LOTE']:
                if col in res_maestro.columns:
                    res_maestro[col] = res_maestro[col].replace([0, '0', '0.0'], 'SN').fillna('SN').astype(str)

            res_maestro['TOTAL_BAGO'] = res_maestro['TOTAL_BAGO'].fillna(0)
            res_maestro['TOTAL_FPQX'] = res_maestro['TOTAL_FPQX'].fillna(0)
            res_maestro['DIFERENCIA'] = res_maestro['TOTAL_BAGO'] - res_maestro['TOTAL_FPQX']
            for col in ['TOTAL_BAGO', 'TOTAL_FPQX', 'DIFERENCIA']:
                res_maestro[col] = res_maestro[col].astype(int)

            # --- MÉTRICAS (IGUAL A LA IMAGEN) ---
            m1, m2, m3, m4 = st.columns(4)
            base_bago = res_maestro[res_maestro['TOTAL_BAGO'] > 0]
            desconocidos = res_maestro[(res_maestro['TOTAL_BAGO'] == 0) & (res_maestro['TOTAL_FPQX'] > 0)]
            diff_stock = base_bago[base_bago['DIFERENCIA'] != 0]

            m1.metric("SKUs Bagó", len(base_bago))
            m2.metric("Discrepancias", len(diff_stock), delta="-Error" if len(diff_stock)>0 else None, delta_color="normal")
            m3.metric("No en Base", len(desconocidos))
            m4.metric("Precisión", f"{round((1 - (len(diff_stock)/len(base_bago)))*100,1)}%" if len(base_bago)>0 else "100%")

            st.divider()
            
            if vista == "Base Bagó": res_final = base_bago.copy()
            elif vista == "Diferencias": res_final = diff_stock.copy()
            elif vista == "No en Base": res_final = desconocidos.copy()
            else: res_final = res_maestro[res_maestro['DIFERENCIA'] != 0].copy()

            if busq:
                res_final = res_final[res_final.apply(lambda r: r.astype(str).str.contains(busq, case=False).any(), axis=1)]

            if not res_final.empty:
                res_final = res_final.rename(columns={'TOTAL_BAGO': 'BAGÓ', 'TOTAL_FPQX': 'FP/QX', 'DIFERENCIA': 'DIF.'})
                st.dataframe(res_final.style.highlight_between(left=-999999, right=-1, color='#ffdadb', subset=['DIF.']), use_container_width=True)
                
                with st.sidebar:
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        res_final.to_excel(writer, index=False)
                    st.download_button("📥 DESCARGAR EXCEL", data=output.getvalue(), file_name="Auditoria.xlsx")
        except Exception as e:
            st.error(f"Error: {e}")
