import streamlit as st
import pandas as pd
import io
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA (Layout Wide es Clave) ---
st.set_page_config(page_title="Bagó | Intel-Stock Pro", page_icon="🧪", layout="wide")

# --- DISEÑO ULTRA-COMPACTO ---
MAGENTA_BAGO = "#C7006A" 
MAGENTA_OSCURO = "#8A004A"

st.markdown(f"""
    <style>
    /* 1. Eliminar el espacio superior por defecto de Streamlit */
    .block-container {{ padding-top: 1rem !important; padding-bottom: 0rem !important; }}
    
    .main {{ background: radial-gradient(circle at center, #ffffff 0%, #f0f2f6 100%); }}
    
    /* Título Compacto */
    .hero-title {{
        color: {MAGENTA_BAGO};
        font-size: 3rem !important;
        font-weight: 900 !important;
        text-align: center;
        margin-top: 0px;
        margin-bottom: 10px;
        letter-spacing: -2px;
    }}

    /* BOTONES DE INICIO COMPACTOS */
    div.stButton > button {{
        background: rgba(255, 255, 255, 0.7) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 25px !important;
        height: 140px !important; /* Altura reducida a la mitad */
        box-shadow: 0 10px 20px rgba(0,0,0,0.05) !important;
        transition: all 0.4s ease !important;
        font-weight: 700 !important;
    }}

    div.stButton > button:hover {{
        background: linear-gradient(135deg, {MAGENTA_BAGO} 0%, {MAGENTA_OSCURO} 100%) !important;
        color: white !important;
        transform: translateY(-5px) !important;
    }}

    /* MÉTRICAS COMPACTAS */
    div[data-testid="stMetric"] {{
        background: white !important;
        border-radius: 15px !important;
        padding: 10px 15px !important; /* Menos relleno */
        border-bottom: 4px solid {MAGENTA_BAGO} !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03) !important;
    }}

    /* TABLA AJUSTADA AL ALTO DE PANTALLA */
    .stDataFrame {{
        max-height: 400px !important; /* Evita que la tabla empuje todo hacia abajo */
    }}

    /* Texto de pasos pequeño */
    .step-card {{
        background: white;
        border-radius: 15px;
        padding: 10px;
        font-size: 0.85rem;
        text-align: center;
        border-bottom: 2px solid {MAGENTA_BAGO};
    }}
    </style>
    """, unsafe_allow_html=True)

if 'modo' not in st.session_state:
    st.session_state.modo = None

def reset():
    for k in list(st.session_state.keys()): del st.session_state[k]
    st.rerun()

# --- PANTALLA 1: INICIO COMPACTO ---
if st.session_state.modo is None:
    st.markdown('<p style="text-align:center; color:#888; font-size:0.9rem; margin-bottom:0;">Intelligence System</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-title">Laboratorios Bagó</p>', unsafe_allow_html=True)
    
    _, col1, col2, _ = st.columns([3, 2, 2, 3])
    
    with col1:
        st.markdown(f"<p style='text-align:center; color:{MAGENTA_BAGO}; font-weight:bold; font-size:0.8rem; margin-bottom:5px;'>BODEGA 1010</p>", unsafe_allow_html=True)
        if st.button("📦 EMPAQUE\n(LOTE)"):
            st.session_state.modo = "con_lote"
            st.rerun()
            
    with col2:
        st.markdown(f"<p style='text-align:center; color:{MAGENTA_BAGO}; font-weight:bold; font-size:0.8rem; margin-bottom:5px;'>BODEGA 1070</p>", unsafe_allow_html=True)
        if st.button("🔢 PROMOCIONAL\n(MATERIAL)"):
            st.session_state.modo = "sin_lote"
            st.rerun()

    # Pasos en una sola línea compacta
    st.markdown("<br>", unsafe_allow_html=True)
    f1, f2, f3 = st.columns(3)
    with f1: st.markdown("<div class='step-card'><b>1. CONEXIÓN:</b> Sube archivos</div>", unsafe_allow_html=True)
    with f2: st.markdown("<div class='step-card'><b>2. PROCESO:</b> Cruce automático</div>", unsafe_allow_html=True)
    with f3: st.markdown("<div class='step-card'><b>3. AUDIT:</b> Baja el reporte</div>", unsafe_allow_html=True)

# --- PANTALLA 2: DASHBOARD TODO EN UNO ---
else:
    with st.sidebar:
        st.markdown(f"<h2 style='color:{MAGENTA_BAGO}; font-size:1.2rem; margin:0;'>⚙️ Controles</h2>", unsafe_allow_html=True)
        st.caption(f"Modo: {'Lote' if st.session_state.modo == 'con_lote' else 'Material'}")
        st.divider()
        busq = st.text_input("🔍 Buscar...", placeholder="Escribe...")
        vista = st.selectbox("🎯 Vista:", ["Diferencias", "Todo", "No en Base"])
        if st.button("🏠 Inicio"): reset()
        st.divider()
        # Botón de descarga aquí para ahorrar espacio central
        st.write("---")

    # Header y Carga en una sola línea para ahorrar espacio
    head1, head2, head3 = st.columns([2, 2, 2])
    with head1: st.markdown(f"<h3 style='color:{MAGENTA_BAGO}; margin:0;'>📊 Panel</h3>", unsafe_allow_html=True)
    with head2: f1 = st.file_uploader("Base Bagó", type=['xlsx'], key="f1", label_visibility="collapsed")
    with head3: f2 = st.file_uploader("FP/QX", type=['xlsx'], key="f2", label_visibility="collapsed")

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

            # Métricas compactas
            m1, m2, m3, m4 = st.columns(4)
            base_bago = res[res['TOTAL_BAGO'] > 0]
            desc = res[(res['TOTAL_BAGO'] == 0) & (res['TOTAL_FPQX'] > 0)]
            diff = base_bago[base_bago['DIFERENCIA'] != 0]

            m1.metric("Items", len(base_bago))
            m2.metric("Diff", len(diff), delta="-Err" if len(diff)>0 else "OK")
            m3.metric("Nuevos", len(desc))
            m4.metric("Exacto", f"{round((1 - (len(diff)/len(base_bago)))*100,1)}%" if len(base_bago)>0 else "100%")

            # Filtrado y Tabla
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
                    use_container_width=True, height=350 # Altura fija para no desplazar la pantalla
                )
                with st.sidebar:
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer: final.to_excel(writer, index=False)
                    st.download_button("📥 EXCEL", data=output.getvalue(), file_name="Reporte.xlsx")
        except Exception as e:
            st.error(f"Error: {e}")
