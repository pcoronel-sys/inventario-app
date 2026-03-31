import streamlit as st
import pandas as pd
import io
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Bagó | Intel-Stock Pro", page_icon="🧪", layout="wide")

# --- DISEÑO ESTÉTICO UI/UX PRO (EFECTO GLASS Y ANIMACIONES) ---
MAGENTA_BAGO = "#C7006A" 
MAGENTA_OSCURO = "#8A004A"

st.markdown(f"""
    <style>
    /* Fondo con gradiente dinámico */
    .main {{ 
        background: radial-gradient(circle at top right, #ffffff, #f0f2f6); 
    }}
    
    /* Saludo Dinámico */
    .welcome-text {{
        text-align: center;
        color: #888;
        font-size: 1.2rem;
        font-weight: 300;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: -10px;
    }}

    /* Título Impactante */
    .main-title {{
        color: {MAGENTA_BAGO};
        font-size: 5rem !important;
        font-weight: 900 !important;
        text-align: center;
        margin-top: 0px;
        letter-spacing: -4px;
        filter: drop-shadow(0px 10px 15px rgba(199, 0, 106, 0.2));
        line-height: 1;
    }}

    /* BOTONES TIPO TARJETA PREMIUM */
    div.stButton > button {{
        background: rgba(255, 255, 255, 0.7) !important;
        backdrop-filter: blur(15px) !important;
        color: #333 !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 35px !important;
        height: 250px !important;
        width: 100% !important;
        box-shadow: 0 20px 40px rgba(0,0,0,0.05) !important;
        transition: all 0.6s cubic-bezier(0.165, 0.84, 0.44, 1.0) !important;
        font-size: 1.4rem !important;
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
    .almacen-tag {{
        text-align: center;
        color: {MAGENTA_BAGO};
        font-weight: 800;
        font-size: 1rem;
        margin-bottom: 10px;
        letter-spacing: 1px;
    }}

    /* Footer Informativo con Estilo de Tarjeta */
    .footer-card {{
        background: white;
        border-radius: 25px;
        padding: 30px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
        border-bottom: 5px solid {MAGENTA_BAGO};
        transition: 0.3s;
    }}
    .footer-card:hover {{
        transform: translateY(-5px);
    }}

    /* Sidebar y Métricas */
    [data-testid="stSidebar"] {{
        background-color: white !important;
        border-right: 1px solid #eee;
    }}
    div[data-testid="stMetric"] {{
        background: white !important;
        border-radius: 20px !important;
        padding: 20px !important;
        border-left: 8px solid {MAGENTA_BAGO} !important;
        box-shadow: 0 10px 20px rgba(0,0,0,0.04) !important;
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
saludo_txt = "Buenos días" if hora < 12 else "Buenas tardes" if hora < 19 else "Buenas noches"

# --- PANTALLA 1: INICIO "CHEVERE" ---
if st.session_state.modo is None:
    st.markdown(f'<p class="welcome-text">{saludo_txt}, Equipo Bagó</p>', unsafe_allow_html=True)
    st.markdown('<p class="main-title">Laboratorios Bagó</p>', unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center; color:#555; font-weight:300; margin-bottom:60px;'>Intel-Stock Management</h3>", unsafe_allow_html=True)
    
    _, col_l, col_r, _ = st.columns([6.5, 1.8, 1.8, 6.5])
    
    with col_l:
        st.markdown(f'<p class="almacen-tag">ALMACÉN 1010</p>', unsafe_allow_html=True)
        if st.button("📦\n\nEMPAQUE\n\n(Gestión por Lote)"):
            st.session_state.modo = "con_lote"
            st.rerun()
            
    with col_r:
        st.markdown(f'<p class="almacen-tag">ALMACÉN 1070</p>', unsafe_allow_html=True)
        if st.button("🔢\n\nPROMOCIONAL\n\n(Gestión Global)"):
            st.session_state.modo = "sin_lote"
            st.rerun()

    st.markdown("<br><br><br>", unsafe_allow_html=True)
    f1, f2, f3 = st.columns(3)
    with f1: st.markdown("<div class='footer-card'><h3>📂 1. Conexión</h3>Subida de maestros de inventario</div>", unsafe_allow_html=True)
    with f2: st.markdown("<div class='footer-card'><h3>⚡ 2. Proceso</h3>Cruce inteligente de datos en tiempo real</div>", unsafe_allow_html=True)
    with f3: st.markdown("<div class='footer-card'><h3>📊 3. Auditoría</h3>Descarga inmediata del reporte final</div>", unsafe_allow_html=True)

# --- PANTALLA 2: REPORTE ---
else:
    with st.sidebar:
        st.markdown(f"<h2 style='color:{MAGENTA_BAGO};'>⚙️ Controles</h2>", unsafe_allow_html=True)
        st.info(f"📍 Bodega: {'1010' if st.session_state.modo == 'con_lote' else '1070'}")
        busq = st.text_input("🔍 Buscar Código...")
        # ACTUALIZADO: Filtros en sidebar para las nuevas métricas
        vista = st.selectbox("🎯 Vista:", ["Base Bagó", "Diferencias", "No en Bagó", "No en FP/QX", "Total Diferencias"])
        st.divider()
        if st.button("🏠 Volver al Inicio"): borrar_todo()

    st.markdown(f"<h2 style='color:{MAGENTA_BAGO};'>📊 Dashboard de Inventario</h2>", unsafe_allow_html=True)
    c_f1, c_f2 = st.columns(2)
    with c_f1: f1 = st.file_uploader("Subir Base Bagó", type=['xlsx'], key="f1")
    with c_f2: f2 = st.file_uploader("Subir Base QX/FP", type=['xlsx'], key="f2")

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

            # --- NUEVA LÓGICA DE MÉTRICAS (5 COLUMNAS) ---
            m1, m2, m3, m4, m5 = st.columns(5)
            
            base_bago = res_maestro[res_maestro['TOTAL_BAGO'] > 0]
            # No en Bagó: Existe en FP/QX pero su cantidad en Bagó es 0
            no_en_bago = res_maestro[(res_maestro['TOTAL_BAGO'] == 0) & (res_maestro['TOTAL_FPQX'] > 0)]
            # No en FP/QX: Existe en Bagó pero su cantidad en FP/QX es 0
            no_en_qx = res_maestro[(res_maestro['TOTAL_BAGO'] > 0) & (res_maestro['TOTAL_FPQX'] == 0)]
            # Diferencias: Existe en ambos pero las cantidades no coinciden
            diff_stock = res_maestro[(res_maestro['TOTAL_BAGO'] > 0) & (res_maestro['TOTAL_FPQX'] > 0) & (res_maestro['DIFERENCIA'] != 0)]

            m1.metric("SKUs Bagó", len(base_bago))
            m2.metric("Diferencias", len(diff_stock), delta="-Error" if len(diff_stock)>0 else None, delta_color="normal")
            m3.metric("No en Bagó", len(no_en_bago), delta="Sobrante QX", delta_color="inverse")
            m4.metric("No en FP/QX", len(no_en_qx), delta="Faltante QX")
            m5.metric("Precisión", f"{round((1 - (len(diff_stock)+len(no_en_qx))/len(base_bago))*100,1)}%" if len(base_bago)>0 else "100%")

            st.divider()
            
            # --- FILTRADO POR VISTA ---
            if vista == "Base Bagó": res_final = base_bago.copy()
            elif vista == "Diferencias": res_final = diff_stock.copy()
            elif vista == "No en Bagó": res_final = no_en_bago.copy()
            elif vista == "No en FP/QX": res_final = no_en_qx.copy()
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
