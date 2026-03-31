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

    /* Botones con Etiquetas (Badges) */
    div.stButton > button {{
        background: white !important;
        color: #333 !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 28px !important;
        height: 200px !important;
        width: 100% !important;
        box-shadow: 0 15px 35px rgba(0,0,0,0.05) !important;
        transition: all 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }}

    div.stButton > button:hover {{
        background: linear-gradient(145deg, {MAGENTA_BAGO}, {MAGENTA_OSCURO}) !important;
        color: white !important;
        transform: translateY(-10px) scale(1.02) !important;
        box-shadow: 0 20px 40px rgba(199, 0, 106, 0.25) !important;
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

    /* Sidebar Estilizada */
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

# --- DETERMINAR SALUDO ---
hora = datetime.now().hour
if hora < 12: saludo = "☀️ Buenos días"
elif hora < 19: saludo = "🌤️ Buenas tardes"
else: saludo = "🌙 Buenas noches"

# --- PANTALLA 1: INICIO RENOVADO ---
if st.session_state.modo is None:
    st.markdown(f'<p class="welcome-text">{saludo}, Equipo Bagó</p>', unsafe_allow_html=True)
    st.markdown('<p class="main-title">Laboratorios Bagó</p>', unsafe_allow_html=True)
    st.markdown("<h4 style='text-align:center; color:#888; font-weight:300; margin-bottom:50px;'>Intelligence Stock Management System</h4>", unsafe_allow_html=True)
    
    # Botones principales
    _, col_l, col_r, _ = st.columns([3, 2.2, 2.2, 3])
    
    with col_l:
        st.markdown("<div style='text-align:center; color:#C7006A; font-weight:bold; margin-bottom:10px;'>BODEGA DE EMPAQUE</div>", unsafe_allow_html=True)
        if st.button("📦\n\nALMACÉN 1010\n\n(Cruce por Lote)"):
            st.session_state.modo = "con_lote"
            st.rerun()
            
    with col_r:
        st.markdown("<div style='text-align:center; color:#C7006A; font-weight:bold; margin-bottom:10px;'>BODEGA PROMOCIONAL</div>", unsafe_allow_html=True)
        if st.button("🔢\n\nALMACÉN 1070\n\n(Cruce por Material)"):
            st.session_state.modo = "sin_lote"
            st.rerun()

    # Guía de pasos inferior
    st.markdown("<br><br>", unsafe_allow_html=True)
    f1, f2, f3 = st.columns(3)
    with f1:
        st.markdown("<div class='footer-box'><b>1. Selecciona</b><br>El almacén correspondiente a tu inventario.</div>", unsafe_allow_html=True)
    with f2:
        st.markdown("<div class='footer-box'><b>2. Carga</b><br>Sube los archivos .xlsx de Bagó y FP/QX.</div>", unsafe_allow_html=True)
    with f3:
        st.markdown("<div class='footer-box'><b>3. Audita</b><br>Descarga el reporte con diferencias detectadas.</div>", unsafe_allow_html=True)

# --- PANTALLA 2: REPORTE (CON FILTROS EN SIDEBAR) ---
else:
    with st.sidebar:
        st.markdown(f"<h2 style='color:{MAGENTA_BAGO};'>⚙️ Controles</h2>", unsafe_allow_html=True)
        st.info(f"📍 Bodega: {'1010 - Empaque' if st.session_state.modo == 'con_lote' else '1070 - Promocional'}")
        
        st.divider()
        st.markdown("### 🔍 Herramientas")
        busq = st.text_input("Buscar por Código o Nombre...", placeholder="Escribe aquí...")
        vista = st.selectbox("Filtrar Tabla por:", 
                            ["Reporte Base (Bagó)", "Diferencias de Stock", "Ítems Desconocidos", "Auditoría Total"])
        
        st.divider()
        if st.button("🏠 Volver al Inicio"): borrar_todo()

    # Cuerpo del Dashboard
    st.markdown(f"<h2 style='color:{MAGENTA_BAGO};'>📊 Panel de Análisis de Inventario</h2>", unsafe_allow_html=True)
    
    c_f1, c_f2 = st.columns(2)
    with c_f1:
        f1 = st.file_uploader("📂 Subir Base Bagó", type=['xlsx'], key="f1")
    with c_f2:
        f2 = st.file_uploader("📂 Subir Comparativo FP/QX", type=['xlsx'], key="f2")

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
            
            # PROCESO CRUCE
            res_maestro = pd.merge(d1, d2, on=keys, how='outer', suffixes=('_BAGO', '_FPQX'))
            
            # Limpieza SN forzada
            for col in ['DESCRIPCION', 'LOTE']:
                if col in res_maestro.columns:
                    res_maestro[col] = res_maestro[col].replace([0, '0', '0.0'], 'SN').fillna('SN').astype(str)

            res_maestro['TOTAL_BAGO'] = res_maestro['TOTAL_BAGO'].fillna(0)
            res_maestro['TOTAL_FPQX'] = res_maestro['TOTAL_FPQX'].fillna(0)
            res_maestro['DIFERENCIA'] = res_maestro['TOTAL_BAGO'] - res_maestro['TOTAL_FPQX']

            # Formato Entero
            for col in ['TOTAL_BAGO', 'TOTAL_FPQX', 'DIFERENCIA']:
                res_maestro[col] = res_maestro[col].astype(int)

            # MÉTRICAS DASHBOARD
            m1, m2, m3, m4 = st.columns(4)
            base_bago = res_maestro[res_maestro['TOTAL_BAGO'] > 0]
            desconocidos = res_maestro[(res_maestro['TOTAL_BAGO'] == 0) & (res_maestro['TOTAL_FPQX'] > 0)]
            diff_stock = base_bago[base_bago['DIFERENCIA'] != 0]

            m1.metric("SKUs Bagó", len(base_bago))
            m2.metric("Discrepancias", len(diff_stock), delta="-Error" if len(diff_stock)>0 else "OK")
            m3.metric("No en Base", len(desconocidos))
            m4.metric("Precisión", f"{round((1 - (len(diff_stock)/len(base_bago)))*100,1)}%" if len(base_bago)>0 else "100%")

            st.divider()

            # FILTRADO DE VISTA
            if vista == "Reporte Base (Bagó)": res_final = base_bago.copy()
            elif vista == "Diferencias de Stock": res_final = diff_stock.copy()
            elif vista == "Ítems Desconocidos": res_final = desconocidos.copy()
            else: res_final = res_maestro[res_maestro['DIFERENCIA'] != 0].copy()

            if busq:
                res_final = res_final[res_final.apply(lambda r: r.astype(str).str.contains(busq, case=False).any(), axis=1)]

            if not res_final.empty:
                # REFUERZO SN FINAL
                if 'DESCRIPCION' in res_final.columns:
                    res_final['DESCRIPCION'] = res_final['DESCRIPCION'].replace(['0', 0, '0.0'], 'SN')

                res_final = res_final.rename(columns={'TOTAL_BAGO': 'BAGÓ', 'TOTAL_FPQX': 'FP/QX', 'DIFERENCIA': 'DIF.'})
                
                # MOSTRAR TABLA
                st.dataframe(
                    res_final.style.highlight_between(left=-999999, right=-1, color='#ffdadb', subset=['DIF.'])
                                   .highlight_between(left=1, right=999999, color='#d4edda', subset=['DIF.']),
                    use_container_width=True
                )
                
                # Descarga en Sidebar
                with st.sidebar:
                    st.divider()
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        res_final.to_excel(writer, index=False)
                    st.download_button("📥 DESCARGAR REPORTE EXCEL", data=output.getvalue(), file_name=f"Auditoria_{st.session_state.modo}.xlsx")
            else:
                st.warning("No hay datos para mostrar con los filtros actuales.")
        except Exception as e:
            st.error(f"Error crítico: {e}")
