import streamlit as st
import pandas as pd
import io
from datetime import datetime, timedelta

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Bagó | Intel-Stock Pro", page_icon="🧪", layout="wide")

# --- DISEÑO ESTÉTICO UI/UX PRO + SEMÁFORO + LOGO ---
MAGENTA_BAGO = "#C7006A" 
MAGENTA_OSCURO = "#8A004A"

st.markdown(f"""
    <style>
    .main {{ background: radial-gradient(circle at top right, #ffffff, #f0f2f6); }}
    
    /* Estilo del Logo en Sidebar */
    .sidebar-logo {{
        display: block;
        margin-left: auto;
        margin-right: auto;
        width: 80%;
        margin-bottom: 20px;
        filter: drop-shadow(0px 4px 4px rgba(0,0,0,0.1));
    }}

    .welcome-text {{ text-align: center; color: #888; font-size: 1.2rem; font-weight: 300; letter-spacing: 2px; text-transform: uppercase; margin-bottom: -10px; }}
    .main-title {{ color: {MAGENTA_BAGO}; font-size: 5rem !important; font-weight: 900 !important; text-align: center; margin-top: 0px; letter-spacing: -4px; filter: drop-shadow(0px 10px 15px rgba(199, 0, 106, 0.2)); line-height: 1; }}
    
    div.stButton > button {{ background: rgba(255, 255, 255, 0.7) !important; backdrop-filter: blur(15px) !important; color: #333 !important; border: 1px solid rgba(255, 255, 255, 0.3) !important; border-radius: 35px !important; height: 250px !important; width: 100% !important; box-shadow: 0 20px 40px rgba(0,0,0,0.05) !important; transition: all 0.6s cubic-bezier(0.165, 0.84, 0.44, 1.0) !important; font-size: 1.4rem !important; font-weight: 800 !important; display: flex; flex-direction: column; justify-content: center; }}
    div.stButton > button:hover {{ background: linear-gradient(135deg, {MAGENTA_BAGO} 0%, {MAGENTA_OSCURO} 100%) !important; color: white !important; transform: translateY(-15px) scale(1.03) !important; box-shadow: 0 30px 60px rgba(199, 0, 106, 0.3) !important; border: 1px solid {MAGENTA_BAGO} !important; }}
    
    .footer-card {{ background: white; border-radius: 25px; padding: 30px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.03); border-bottom: 5px solid {MAGENTA_BAGO}; transition: 0.3s; }}
    
    /* Métricas Base */
    div[data-testid="stMetric"] {{ background: white !important; border-radius: 20px !important; padding: 20px !important; border-left: 8px solid {MAGENTA_BAGO} !important; box-shadow: 0 10px 20px rgba(0,0,0,0.04) !important; }}
    
    /* Colores del Semáforo para Precisión (Clases dinámicas) */
    .metric-excelente {{ border-left: 8px solid #28a745 !important; }}
    .metric-alerta {{ border-left: 8px solid #ffc107 !important; }}
    .metric-critico {{ border-left: 8px solid #dc3545 !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE NAVEGACIÓN ---
if 'modo' not in st.session_state:
    st.session_state.modo = None

def borrar_todo():
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()

# --- SALUDO GMT-5 ---
hora_ajustada = (datetime.now() - timedelta(hours=5)).hour
if 5 <= hora_ajustada < 12: saludo_txt = "☀️ Buenos días"
elif 12 <= hora_ajustada < 19: saludo_txt = "🌤️ Buenas tardes"
else: saludo_txt = "🌙 Buenas noches"

# --- PANTALLA 1: INICIO ---
if st.session_state.modo is None:
    st.markdown(f'<p class="welcome-text">{saludo_txt}, Equipo Bagó</p>', unsafe_allow_html=True)
    st.markdown('<p class="main-title">Laboratorios Bagó</p>', unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center; color:#555; font-weight:300; margin-bottom:60px;'>Intel-Stock Management</h3>", unsafe_allow_html=True)
    
    _, col_l, col_r, _ = st.columns([6.5, 1.8, 1.8, 6.5])
    with col_l:
        st.markdown(f'<p style="text-align:center; color:{MAGENTA_BAGO}; font-weight:800;">ALMACÉN 1010</p>', unsafe_allow_html=True)
        if st.button("📦\n\n MATERIAL DE EMPAQUE\n\n"):
            st.session_state.modo = "con_lote"; st.rerun()
    with col_r:
        st.markdown(f'<p style="text-align:center; color:{MAGENTA_BAGO}; font-weight:800;">ALMACÉN 1070</p>', unsafe_allow_html=True)
        if st.button("🔢\n\nMATERIAL PROMOCIONAL\n\n"):
            st.session_state.modo = "sin_lote"; st.rerun()

    st.markdown("<br><br><br>", unsafe_allow_html=True)
    f1, f2, f3 = st.columns(3)
    with f1: st.markdown("<div class='footer-card'><h3>📂 1. Conexión</h3>Maestros de inventario</div>", unsafe_allow_html=True)
    with f2: st.markdown("<div class='footer-card'><h3>⚡ 2. Proceso</h3>Cruce inteligente</div>", unsafe_allow_html=True)
    with f3: st.markdown("<div class='footer-card'><h3>📊 3. Auditoría</h3>Reporte final</div>", unsafe_allow_html=True)

# --- PANTALLA 2: REPORTE ---
else:
    with st.sidebar:
        # LOGO BAGÓ (Imagen Placeholder o URL oficial)
        st.markdown(f'<h1 style="color:{MAGENTA_BAGO}; text-align:center; margin-bottom:0;">BAGÓ</h1>', unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center; color:#888; font-size:0.8rem; margin-top:0;'>AUDITORÍA INTELIGENTE</p>", unsafe_allow_html=True)
        st.divider()
        st.info(f"📍 Bodega: {'1010' if st.session_state.modo == 'con_lote' else '1070'}")
        busq = st.text_input("🔍 Buscar Código...", help="Puedes buscar por código de material o descripción.")
        vista = st.selectbox("🎯 Vista:", ["Base Bagó", "Diferencias", "No en Bagó", "No en FP/QX", "Total Diferencias"])
        st.divider()
        if st.button("🏠 Volver al Inicio"): borrar_todo()

    st.markdown(f"<h2 style='color:{MAGENTA_BAGO};'>📊 Dashboard de Inventario</h2>", unsafe_allow_html=True)
    c_f1, c_f2 = st.columns(2)
    with c_f1: f1 = st.file_uploader("Subir Base Bagó", type=['xlsx'], key="f1")
    with c_f2: f2 = st.file_uploader("Subir Base QX/FP", type=['xlsx'], key="f2")

    if f1 and f2:
        try:
            with st.spinner('🧪 Procesando inteligencia de stock...'):
                df1, df2 = pd.read_excel(f1), pd.read_excel(f2)
                def limpiar(df):
                    df.columns = df.columns.astype(str).str.strip().str.upper()
                    df['MATERIAL'] = df['MATERIAL'].astype(str).str.strip().str.upper()
                    agg = {'TOTAL': 'sum'}
                    if 'DESCRIPCION' in df.columns:
                        df['DESCRIPCION'] = df['DESCRIPCION'].astype(str).str.strip().str.upper(); agg['DESCRIPCION'] = 'first'
                    if st.session_state.modo == "con_lote":
                        df['LOTE'] = df['LOTE'].fillna('SN').astype(str).str.strip().str.upper() if 'LOTE' in df.columns else 'SN'
                        return df.groupby(['MATERIAL', 'LOTE']).agg(agg).reset_index()
                    return df.groupby(['MATERIAL']).agg(agg).reset_index()

                d1, d2 = limpiar(df1), limpiar(df2)
                keys = ['MATERIAL', 'LOTE'] if st.session_state.modo == "con_lote" else ['MATERIAL']
                res = pd.merge(d1, d2, on=keys, how='outer', suffixes=('_BAGO', '_FPQX'))
                
                for col in ['DESCRIPCION', 'LOTE']:
                    if col in res.columns: res[col] = res[col].replace([0, '0', '0.0'], 'SN').fillna('SN').astype(str)

                res['TOTAL_BAGO'] = res['TOTAL_BAGO'].fillna(0); res['TOTAL_FPQX'] = res['TOTAL_FPQX'].fillna(0)
                res['DIFERENCIA'] = res['TOTAL_BAGO'] - res['TOTAL_FPQX']
                for col in ['TOTAL_BAGO', 'TOTAL_FPQX', 'DIFERENCIA']: res[col] = res[col].astype(int)

                # --- MÉTRICAS ---
                m1, m2, m3, m4, m5 = st.columns(5)
                base_bago = res[res['TOTAL_BAGO'] > 0]
                no_en_bago = res[(res['TOTAL_BAGO'] == 0) & (res['TOTAL_FPQX'] > 0)]
                no_en_qx = res[(res['TOTAL_BAGO'] > 0) & (res['TOTAL_FPQX'] == 0)]
                diff_stock = res[(res['TOTAL_BAGO'] > 0) & (res['TOTAL_FPQX'] > 0) & (res['DIFERENCIA'] != 0)]
                
                precision_val = round((1 - (len(diff_stock)+len(no_en_qx))/len(base_bago))*100,1) if len(base_bago)>0 else 100.0

                m1.metric("SKUs Bagó", len(base_bago), help="Cantidad de materiales únicos en el maestro de Bagó.")
                m2.metric("Diferencias", len(diff_stock), delta="-Error" if len(diff_stock)>0 else None, help="Ítems que están en ambos sistemas pero con cantidades distintas.")
                m3.metric("No en Bagó", len(no_en_bago), delta="Sobrante QX", delta_color="inverse", help="Artículos contados en QX que no existen en el sistema Bagó.")
                m4.metric("No en FP/QX", len(no_en_qx), delta="Faltante QX", help="Artículos en sistema Bagó que no fueron encontrados físicamente.")
                
                # Semáforo de Precisión
                p_label = "Excelente" if precision_val >= 95 else "Atención" if precision_val >= 80 else "Crítico"
                m5.metric("Precisión", f"{precision_val}%", delta=p_label, help="Porcentaje de exactitud del inventario real contra el sistema.")

                st.divider()
                
                if vista == "Base Bagó": res_final = base_bago.copy()
                elif vista == "Diferencias": res_final = diff_stock.copy()
                elif vista == "No en Bagó": res_final = no_en_bago.copy()
                elif vista == "No en FP/QX": res_final = no_en_qx.copy()
                else: res_final = res[res['DIFERENCIA'] != 0].copy()

                if busq: res_final = res_final[res_final.apply(lambda r: r.astype(str).str.contains(busq, case=False).any(), axis=1)]

                if not res_final.empty:
                    res_final = res_final.rename(columns={'TOTAL_BAGO': 'BAGÓ', 'TOTAL_FPQX': 'FP/QX', 'DIFERENCIA': 'DIF.'})
                    st.dataframe(res_final.style.highlight_between(left=-999999, right=-1, color='#ffdadb', subset=['DIF.']), use_container_width=True)
                    with st.sidebar:
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer: res_final.to_excel(writer, index=False)
                        st.download_button("📥 DESCARGAR REPORTE", data=output.getvalue(), file_name="Auditoria_Final.xlsx")
                        st.success("✅ Datos procesados")
        except Exception as e: st.error(f"Error: {e}")
