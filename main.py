import streamlit as st
import pandas as pd
import io
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Bagó | Intel-Stock Pro", page_icon="🧪", layout="wide")

# --- DISEÑO ESTÉTICO UI/UX "ULTRA-PREMIUM" ---
MAGENTA_BAGO = "#C7006A" 
MAGENTA_OSCURO = "#8A004A"

st.markdown(f"""
    <style>
    /* Fondo con degradado profesional */
    .main {{ background: radial-gradient(circle at center, #ffffff 0%, #f0f2f6 100%); }}
    
    /* Saludo Dinámico Estilizado */
    .welcome-banner {{
        text-align: center;
        color: #888;
        font-size: 1.2rem;
        font-weight: 300;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: -10px;
    }}

    /* Título Impactante */
    .hero-title {{
        color: {MAGENTA_BAGO};
        font-size: 4.5rem !important;
        font-weight: 900 !important;
        text-align: center;
        margin-top: 0px;
        letter-spacing: -3px;
        line-height: 1;
        filter: drop-shadow(0px 10px 15px rgba(199, 0, 106, 0.15));
    }}

    /* TARJETAS DE SELECCIÓN "GLASS" */
    div.stButton > button {{
        background: rgba(255, 255, 255, 0.7) !important;
        backdrop-filter: blur(15px) !important;
        color: #333 !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 35px !important;
        height: 280px !important;
        width: 100% !important;
        box-shadow: 0 20px 40px rgba(0,0,0,0.05) !important;
        transition: all 0.6s cubic-bezier(0.23, 1, 0.32, 1) !important;
        font-size: 1.3rem !important;
        font-weight: 800 !important;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }}

    div.stButton > button:hover {{
        background: linear-gradient(135deg, {MAGENTA_BAGO} 0%, {MAGENTA_OSCURO} 100%) !important;
        color: white !important;
        transform: translateY(-15px) scale(1.03) !important;
        box-shadow: 0 30px 60px rgba(199, 0, 106, 0.3) !important;
        border: 1px solid {MAGENTA_BAGO} !important;
    }}

    /* Etiquetas de Almacén */
    .almacen-label {{
        text-align: center;
        color: {MAGENTA_BAGO};
        font-weight: 800;
        font-size: 0.9rem;
        letter-spacing: 1px;
        margin-bottom: 15px;
    }}

    /* Footer de Pasos */
    .step-card {{
        background: white;
        border-radius: 20px;
        padding: 25px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
        border-bottom: 4px solid {MAGENTA_BAGO};
        transition: 0.3s;
    }}
    .step-card:hover {{ transform: translateY(-5px); }}

    /* Sidebar y Métricas */
    [data-testid="stSidebar"] {{ background-color: white !important; border-right: 1px solid #eee; }}
    div[data-testid="stMetric"] {{
        background: white !important;
        border-radius: 20px !important;
        padding: 20px !important;
        border-bottom: 5px solid {MAGENTA_BAGO} !important;
        box-shadow: 0 10px 20px rgba(0,0,0,0.04) !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE NAVEGACIÓN ---
if 'modo' not in st.session_state:
    st.session_state.modo = None

def reset():
    for k in list(st.session_state.keys()): del st.session_state[k]
    st.rerun()

# --- PANTALLA 1: EL NUEVO "HERO START" ---
if st.session_state.modo is None:
    # Saludo según hora
    h = datetime.now().hour
    msg = "Buenos días" if h < 12 else "Buenas tardes" if h < 19 else "Buenas noches"
    
    st.markdown(f'<p class="welcome-banner">{msg}, Equipo de Auditoría</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-title">Laboratorios Bagó</p>', unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center; color:#555; font-weight:300; margin-bottom:60px;'>Intel-Stock Management Ecosystem</h3>", unsafe_allow_html=True)
    
    # Grid de selección central
    _, col1, col2, _ = st.columns([2.5, 2.5, 2.5, 2.5])
    
    with col1:
        st.markdown('<p class="almacen-label">ALMACÉN 1010</p>', unsafe_allow_html=True)
        if st.button("📦\n\nEMPAQUE\n\n(Análisis por Lote)"):
            st.session_state.modo = "con_lote"
            st.rerun()
            
    with col2:
        st.markdown('<p class="almacen-label">ALMACÉN 1070</p>', unsafe_allow_html=True)
        if st.button("🔢\n\nPROMOCIONAL\n\n(Análisis Global)"):
            st.session_state.modo = "sin_lote"
            st.rerun()

    # Guía visual al pie
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    f1, f2, f3 = st.columns(3)
    with f1: st.markdown("<div class='step-card'><h3>📂</h3><b>CONEXIÓN</b><br>Sube tus maestros de inventario</div>", unsafe_allow_html=True)
    with f2: st.markdown("<div class='step-card'><h3>⚡</h3><b>PROCESAMIENTO</b><br>Cruce inteligente en tiempo real</div>", unsafe_allow_html=True)
    with f3: st.markdown("<div class='step-card'><h3>📊</h3><b>AUDITORÍA</b><br>Descarga el informe de discrepancias</div>", unsafe_allow_html=True)

# --- PANTALLA 2: DASHBOARD ---
else:
    with st.sidebar:
        st.markdown(f"<h1 style='color:{MAGENTA_BAGO};'>⚙️ Controles</h1>", unsafe_allow_html=True)
        st.info(f"📍 Modo: {'Empaque (Lote)' if st.session_state.modo == 'con_lote' else 'Promocional'}")
        busq = st.text_input("🔍 Buscar ítem...", placeholder="Escribe aquí...")
        vista = st.selectbox("🎯 Filtro de Vista:", ["Todo", "Diferencias", "No en Base"])
        st.divider()
        if st.button("🏠 Volver al Inicio"): reset()

    st.markdown(f"<h2 style='color:{MAGENTA_BAGO};'>📊 Panel de Análisis</h2>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1: f1 = st.file_uploader("📂 Base Bagó", type=['xlsx'], key="f1")
    with c2: f2 = st.file_uploader("📂 Comparativo FP/QX", type=['xlsx'], key="f2")

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
            res = pd.merge(d1, d2, on=keys, how='outer', suffixes=('_BAGO', '_FPQX'))
            
            for col in ['DESCRIPCION', 'LOTE']:
                if col in res.columns:
                    res[col] = res[col].replace([0, '0', '0.0'], 'SN').fillna('SN').astype(str)

            res['TOTAL_BAGO'] = res['TOTAL_BAGO'].fillna(0)
            res['TOTAL_FPQX'] = res['TOTAL_FPQX'].fillna(0)
            res['DIFERENCIA'] = res['TOTAL_BAGO'] - res['TOTAL_FPQX']
            for col in ['TOTAL_BAGO', 'TOTAL_FPQX', 'DIFERENCIA']: res[col] = res[col].astype(int)

            # Métricas
            m1, m2, m3, m4 = st.columns(4)
            base_bago = res[res['TOTAL_BAGO'] > 0]
            desc = res[(res['TOTAL_BAGO'] == 0) & (res['TOTAL_FPQX'] > 0)]
            diff = base_bago[base_bago['DIFERENCIA'] != 0]

            m1.metric("SKUs Bagó", len(base_bago))
            m2.metric("Discrepancias", len(diff), delta="-Error" if len(diff)>0 else "OK")
            m3.metric("No en Base", len(desc))
            m4.metric("Precisión", f"{round((1 - (len(diff)/len(base_bago)))*100,1)}%" if len(base_bago)>0 else "100%")

            st.divider()

            if vista == "Diferencias": final = diff.copy()
            elif vista == "No en Base": final = desc.copy()
            else: final = res.copy()

            if busq:
                final = final[final.apply(lambda r: r.astype(str).str.contains(busq, case=False).any(), axis=1)]

            if not final.empty:
                final = final.rename(columns={'TOTAL_BAGO': 'BAGÓ', 'TOTAL_FPQX': 'FP/QX', 'DIFERENCIA': 'DIF.'})
                st.dataframe(
                    final.style.highlight_between(left=-999999, right=-1, color='#ffdadb', subset=['DIF.'])
                               .applymap(lambda x: 'color: #D3D3D3;' if x == 'SN' else '', subset=['DESCRIPCION', 'LOTE'] if 'LOTE' in final.columns else ['DESCRIPCION']),
                    use_container_width=True
                )
                with st.sidebar:
                    st.divider()
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer: final.to_excel(writer, index=False)
                    st.download_button("📥 DESCARGAR EXCEL", data=output.getvalue(), file_name="Reporte.xlsx")
        except Exception as e:
            st.error(f"Error: {e}")
