import streamlit as st
import pandas as pd
import io

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Bagó | Intel-Stock Pro", page_icon="🧪", layout="wide")

# --- DISEÑO EQUILIBRADO ---
MAGENTA_BAGO = "#C7006A" 
MAGENTA_OSCURO = "#8A004A"

st.markdown(f"""
    <style>
    /* Reset de espacios para evitar el scroll */
    .block-container {{ padding-top: 2rem !important; padding-bottom: 0rem !important; }}
    .main {{ background: white; }}
    
    /* Título Elegante */
    .hero-title {{
        color: {MAGENTA_BAGO};
        font-size: 3.5rem !important;
        font-weight: 900 !important;
        text-align: center;
        margin-bottom: 5px;
        letter-spacing: -2px;
    }}

    /* BOTONES GLASSMorphism (Tamaño Justo) */
    div.stButton > button {{
        background: rgba(248, 249, 252, 0.8) !important;
        border: 1px solid #eee !important;
        border-radius: 30px !important;
        height: 220px !important;
        box-shadow: 0 15px 35px rgba(0,0,0,0.05) !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        font-size: 1.2rem !important;
        font-weight: 800 !important;
    }}

    div.stButton > button:hover {{
        background: linear-gradient(145deg, {MAGENTA_BAGO}, {MAGENTA_OSCURO}) !important;
        color: white !important;
        transform: translateY(-10px) !important;
        box-shadow: 0 20px 40px rgba(199, 0, 106, 0.2) !important;
    }}

    /* MÉTRICAS FLOTANTES */
    div[data-testid="stMetric"] {{
        background: #f8f9fc !important;
        border-radius: 20px !important;
        padding: 15px !important;
        border-left: 5px solid {MAGENTA_BAGO} !important;
    }}

    /* Footer sutil */
    .footer-text {{
        text-align: center;
        color: #bbb;
        font-size: 0.8rem;
        margin-top: 20px;
    }}
    </style>
    """, unsafe_allow_html=True)

if 'modo' not in st.session_state:
    st.session_state.modo = None

def reset():
    for k in list(st.session_state.keys()): del st.session_state[k]
    st.rerun()

# --- PANTALLA 1: INICIO ESTÉTICO ---
if st.session_state.modo is None:
    st.markdown('<p class="hero-title">Laboratorios Bagó</p>', unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#888; font-size:1.2rem; margin-bottom:40px;'>Seleccione el centro de costos para iniciar la auditoría</p>", unsafe_allow_html=True)
    
    # Grid central
    _, col1, col2, _ = st.columns([2, 3, 3, 2])
    
    with col1:
        if st.button("📦\n\nALMACÉN 1010\n\nMaterial de Empaque"):
            st.session_state.modo = "con_lote"
            st.rerun()
            
    with col2:
        if st.button("🔢\n\nALMACÉN 1070\n\nMaterial Promocional"):
            st.session_state.modo = "sin_lote"
            st.rerun()

    st.markdown('<p class="footer-text">Intel-Stock System v3.0 | Propiedad de Laboratorios Bagó</p>', unsafe_allow_html=True)

# --- PANTALLA 2: DASHBOARD PROFESIONAL ---
else:
    with st.sidebar:
        st.markdown(f"<h1 style='color:{MAGENTA_BAGO};'>⚙️ Filtros</h1>", unsafe_allow_html=True)
        st.info(f"📍 {'Empaque (Lote)' if st.session_state.modo == 'con_lote' else 'Promocional'}")
        busq = st.text_input("🔍 Buscar ítem...")
        vista = st.selectbox("Vista:", ["Diferencias", "Todo", "No en Base"])
        st.divider()
        if st.button("🏠 Inicio"): reset()

    # Layout de reporte compacto pero aireado
    row1_1, row1_2 = st.columns([2, 4])
    with row1_1: st.markdown(f"<h2 style='color:{MAGENTA_BAGO}; margin:0;'>📊 Dashboard</h2>", unsafe_allow_html=True)
    with row1_2:
        c1, c2 = st.columns(2)
        f1 = c1.file_uploader("Base Bagó", type=['xlsx'], key="f1", label_visibility="collapsed")
        f2 = c2.file_uploader("FP/QX", type=['xlsx'], key="f2", label_visibility="collapsed")

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

            m1.metric("SKUs", len(base_bago))
            m2.metric("Diff", len(diff), delta="-Err" if len(diff)>0 else None)
            m3.metric("Nuevos", len(desc))
            m4.metric("Precisión", f"{round((1 - (len(diff)/len(base_bago)))*100,1)}%" if len(base_bago)>0 else "100%")

            # Tabla
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
                    use_container_width=True, height=400
                )
                with st.sidebar:
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer: final.to_excel(writer, index=False)
                    st.download_button("📥 DESCARGAR EXCEL", data=output.getvalue(), file_name="Reporte.xlsx")
        except Exception as e:
            st.error(f"Error: {e}")
