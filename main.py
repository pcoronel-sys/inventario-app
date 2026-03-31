import streamlit as st
import pandas as pd
import io

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Bagó | Intel-Stock Pro", page_icon="🧪", layout="wide")

# --- DISEÑO ESTÉTICO DE ALTO NIVEL (UI/UX) ---
MAGENTA_BAGO = "#C7006A" 
MAGENTA_OSCURO = "#8A004A"

st.markdown(f"""
    <style>
    /* Fondo con degradado sutil */
    .main {{ background: linear-gradient(135deg, #f8f9fc 0%, #e2e7f0 100%); }}
    
    /* Barra Lateral Estilizada */
    [data-testid="stSidebar"] {{
        background-color: white !important;
        border-right: 1px solid #e0e0e0;
        box-shadow: 4px 0px 15px rgba(0,0,0,0.05);
    }}

    /* Título Principal */
    .main-title {{
        color: {MAGENTA_BAGO};
        font-size: 3.2rem !important;
        font-weight: 800 !important;
        text-align: center;
        margin-top: 20px;
        letter-spacing: -1.5px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.05);
    }}

    /* Tarjetas de Métricas Pro */
    div[data-testid="stMetric"] {{
        background: rgba(255, 255, 255, 0.8) !important;
        backdrop-filter: blur(10px);
        border-radius: 20px !important;
        padding: 25px !important;
        border: 1px solid rgba(199, 0, 106, 0.1) !important;
        border-left: 8px solid {MAGENTA_BAGO} !important;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.07) !important;
        transition: transform 0.3s ease;
    }}
    div[data-testid="stMetric"]:hover {{ transform: scale(1.02); }}

    /* Botones de Inicio (Tarjetas Compactas) */
    div.stButton > button {{
        background: white !important;
        color: #333 !important;
        border: 1px solid #eee !important;
        border-radius: 22px !important;
        height: 160px !important;
        box-shadow: 0 10px 20px rgba(0,0,0,0.04) !important;
        transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1) !important;
        font-weight: 700 !important;
    }}
    div.stButton > button:hover {{
        background: linear-gradient(145deg, {MAGENTA_BAGO}, {MAGENTA_OSCURO}) !important;
        color: white !important;
        box-shadow: 0 15px 30px rgba(199, 0, 106, 0.2) !important;
    }}

    /* Estilo de la Tabla */
    .stDataFrame {{
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
    }}

    /* Botón de Descarga Lateral */
    .stDownloadButton button {{
        width: 100% !important;
        background: {MAGENTA_BAGO} !important;
        color: white !important;
        border-radius: 10px !important;
        border: none !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- NAVEGACIÓN ---
if 'modo' not in st.session_state:
    st.session_state.modo = None

def borrar_todo():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# --- PANTALLA 1: INICIO ---
if st.session_state.modo is None:
    st.markdown('<p class="main-title">Laboratorios Bagó</p>', unsafe_allow_html=True)
    st.markdown("<h4 style='text-align:center; color:#888; font-weight:400;'>Inventory Intelligence System</h4><br>", unsafe_allow_html=True)
    
    _, col_l, col_r, _ = st.columns([5.5, 2, 2, 5.5])
    with col_l:
        if st.button("📦\n\nALMACÉN 1010\n\nEmpaque"):
            st.session_state.modo = "con_lote"
            st.rerun()
    with col_r:
        if st.button("🔢\n\nALMACÉN 1070\n\nPromocional"):
            st.session_state.modo = "sin_lote"
            st.rerun()

# --- PANTALLA 2: DASHBOARD PRO ---
else:
    # --- BARRA LATERAL (FILTROS Y CONTROL) ---
    with st.sidebar:
        st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRz9GvY-N3M8I6n6u9S7gY8n9g8n9g8n9g", width=100) # Placeholder logo
        st.markdown(f"### ⚙️ Configuración")
        st.info(f"Modo: {'Empaque' if st.session_state.modo == 'con_lote' else 'Promocional'}")
        
        st.divider()
        st.markdown("### 🔍 Filtrado Real")
        busq = st.text_input("Buscar Material...", placeholder="Ej: Blister 10mg")
        vista = st.selectbox("Vista de Datos", ["Reporte Completo", "Solo Diferencias", "Solo Desconocidos", "Auditoría Total"])
        
        st.divider()
        if st.button("🏠 Regresar al Inicio"): borrar_todo()

    # --- CUERPO PRINCIPAL ---
    st.markdown(f"<h2 style='color:{MAGENTA_BAGO};'>📊 Dashboard de Inventario</h2>", unsafe_allow_html=True)
    
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        f1 = st.file_uploader("📥 Cargar Base Bagó (Excel)", type=['xlsx'], key="f1")
    with f_col2:
        f2 = st.file_uploader("📥 Cargar Comparativo FP/QX", type=['xlsx'], key="f2")

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
            
            # PROCESO DE CRUCE
            res_maestro = pd.merge(d1, d2, on=keys, how='outer', suffixes=('_BAGO', '_FPQX'))
            
            # Limpieza forzada de SN y 0
            for col in ['DESCRIPCION', 'LOTE']:
                if col in res_maestro.columns:
                    res_maestro[col] = res_maestro[col].replace([0, '0', '0.0'], 'SN').fillna('SN').astype(str)

            res_maestro['TOTAL_BAGO'] = res_maestro['TOTAL_BAGO'].fillna(0)
            res_maestro['TOTAL_FPQX'] = res_maestro['TOTAL_FPQX'].fillna(0)
            res_maestro['DIFERENCIA'] = res_maestro['TOTAL_BAGO'] - res_maestro['TOTAL_FPQX']

            # Formato Entero
            for col in ['TOTAL_BAGO', 'TOTAL_FPQX', 'DIFERENCIA']:
                res_maestro[col] = res_maestro[col].astype(int)

            # MÉTRICAS EN TARJETAS DE CRISTAL
            m1, m2, m3, m4 = st.columns(4)
            base_bago = res_maestro[res_maestro['TOTAL_BAGO'] > 0]
            desconocidos = res_maestro[(res_maestro['TOTAL_BAGO'] == 0) & (res_maestro['TOTAL_FPQX'] > 0)]
            diff_stock = base_bago[base_bago['DIFERENCIA'] != 0]

            m1.metric("Items Maestro", len(base_bago))
            m2.metric("Discrepancias", len(diff_stock))
            m3.metric("Nuevos (FP/QX)", len(desconocidos))
            m4.metric("Consistencia", f"{round((1 - (len(desconocidos)/len(base_bago)))*100,1)}%" if len(base_bago)>0 else "100%")

            st.divider()

            # LÓGICA DE FILTRADO PARA TABLA
            if vista == "Reporte Completo": res_final = base_bago.copy()
            elif vista == "Solo Diferencias": res_final = diff_stock.copy()
            elif vista == "Solo Desconocidos": res_final = desconocidos.copy()
            else: res_final = res_maestro[res_maestro['DIFERENCIA'] != 0].copy()

            if busq:
                res_final = res_final[res_final.apply(lambda r: r.astype(str).str.contains(busq, case=False).any(), axis=1)]

            if not res_final.empty:
                # REFUERZO DE SN
                if 'DESCRIPCION' in res_final.columns:
                    res_final['DESCRIPCION'] = res_final['DESCRIPCION'].replace(['0', 0, '0.0'], 'SN')

                res_final = res_final.rename(columns={'TOTAL_BAGO': 'BAGÓ', 'TOTAL_FPQX': 'FP/QX', 'DIFERENCIA': 'DIF.'})
                
                # TABLA ESTILIZADA
                st.dataframe(
                    res_final.style.highlight_between(left=-999999, right=-1, color='#ffdadb', subset=['DIF.'])
                                   .highlight_between(left=1, right=999999, color='#d4edda', subset=['DIF.']),
                    use_container_width=True
                )
                
                # Descarga en el Sidebar para no estorbar
                with st.sidebar:
                    st.divider()
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        res_final.to_excel(writer, index=False)
                    st.download_button("📥 DESCARGAR EXCEL", data=output.getvalue(), file_name="Auditoria_Bago.xlsx")
            else:
                st.warning("No se encontraron registros bajo este filtro.")
        except Exception as e:
            st.error(f"Error: {e}")
