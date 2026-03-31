import streamlit as st
import pandas as pd
import io

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Bagó | Sistema Unificado", page_icon="🧪", layout="wide")

# --- IDENTIDAD VISUAL Y CSS (BOTONES MÁS COMPACTOS) ---
MAGENTA_BAGO = "#C7006A" 
MAGENTA_OSCURO = "#8A004A"

st.markdown(f"""
    <style>
    .main {{ background: #f4f7f9; }}
    
    /* TARJETAS PRINCIPALES MÁS COMPACTAS (180px) */
    div.stButton > button {{
        background-color: white !important;
        color: #444 !important;
        border: 2px solid #eee !important;
        border-radius: 20px !important;
        height: 180px !important; /* Tamaño reducido de 300 a 180 */
        width: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05) !important;
        transition: all 0.3s ease-in-out !important;
        white-space: normal !important;
        padding: 15px !important;
    }}

    /* EFECTO HOVER */
    div.stButton > button:hover {{
        background: linear-gradient(135deg, {MAGENTA_BAGO} 0%, {MAGENTA_OSCURO} 100%) !important;
        color: white !important;
        transform: translateY(-5px) !important;
        border-color: {MAGENTA_BAGO} !important;
        box-shadow: 0 12px 25px rgba(199, 0, 106, 0.25) !important;
    }}

    /* Estilo de las Métricas del Reporte */
    [data-testid="stMetric"] {{
        background: white;
        border-radius: 15px;
        padding: 20px;
        border-left: 6px solid {MAGENTA_BAGO};
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }}

    /* Botón de Descarga */
    .stDownloadButton button {{
        background: linear-gradient(90deg, {MAGENTA_BAGO} 0%, {MAGENTA_OSCURO} 100%) !important;
        color: white !important;
        height: 3.5em !important;
        border-radius: 12px !important;
        font-weight: bold !important;
    }}

    h1 {{ color: {MAGENTA_BAGO} !important; font-weight: 800; text-align: center; }}
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE SESIÓN ---
if 'modo' not in st.session_state:
    st.session_state.modo = None

def seleccionar_modo(modo):
    st.session_state.modo = modo

def borrar_todo():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# --- PANTALLA 1: MENÚ PRINCIPAL COMPACTO ---
if st.session_state.modo is None:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h1>🧪 Laboratorios Bagó</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center; color:#666;'>Seleccione el método de trabajo</h3>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📦 MODO LOTE\n\nCruce por código y lote. Máxima precisión farmacéutica.", key="btn_lote"):
            seleccionar_modo("con_lote")
            st.rerun()
    with col2:
        if st.button("🔢 MODO MATERIAL\n\nCruce global por código. Suma total de existencias.", key="btn_sin_lote"):
            seleccionar_modo("sin_lote")
            st.rerun()

# --- PANTALLA 2: REPORTE DINÁMICO (MANTENIENDO COLORES Y CUADROS) ---
else:
    c_head1, c_head2 = st.columns([4, 1])
    with c_head1:
        modo_txt = "CON LOTE" if st.session_state.modo == "con_lote" else "SIN LOTE"
        st.markdown(f"<h2 style='text-align: left; color:{MAGENTA_BAGO}; margin:0;'>🧪 Conciliación: {modo_txt}</h2>", unsafe_allow_html=True)
    with c_head2:
        if st.button("🔄 Volver al Menú"):
            borrar_todo()

    st.divider()

    # Carga de archivos
    c_f1, c_f2 = st.columns(2)
    with c_f1:
        st.info("📂 Archivo BASE (Bagó)")
        f1 = st.file_uploader("Subir", type=['xlsx'], key="f1", label_visibility="collapsed")
    with c_f2:
        st.info("📂 Archivo COMPARAR (FP/QX)")
        f2 = st.file_uploader("Subir", type=['xlsx'], key="f2", label_visibility="collapsed")

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

            # --- CRUCE (LEFT JOIN PARA MANTENER REGISTROS BASE) ---
            keys = ['MATERIAL', 'LOTE'] if st.session_state.modo == "con_lote" else ['MATERIAL']
            res_base = pd.merge(d1, d2, on=keys, how='left', suffixes=('_BAGO', '_FPQX')).fillna(0)
            
            # Detectar Desconocidos (Dashboard Alerta)
            extra_df = pd.merge(d2, d1, on=keys, how='left', indicator=True)
            solo_en_fpqx = extra_df[extra_df['_merge'] == 'left_only'].drop(columns=['_merge'])

            # --- 📊 DASHBOARD (CUADROS MAGENTA) ---
            m1, m2, m3, m4 = st.columns(4)
            diferencias = len(res_base[res_base['TOTAL_BAGO'] != res_base['TOTAL_FPQX']])
            codigos_extra = len(solo_en_fpqx)

            m1.metric("Items Bagó", len(d1))
            m2.metric("Discrepancias", diferencias, delta_color="inverse")
            m3.metric("Faltantes en Bagó", codigos_extra, delta="⚠️ EXTRA", delta_color="inverse" if codigos_extra > 0 else "normal")
            m4.metric("Precisión", f"{round((1 - (codigos_extra/len(d1)))*100,1)}%" if len(d1)>0 else "0%")

            st.divider()

            # --- FILTROS ---
            col_busq, col_ver = st.columns([2, 1])
            with col_busq:
                busqueda = st.text_input("🔍 Buscar Material o Descripción...")
            with col_ver:
                opcion_vista = st.selectbox("🎯 Vista:", ["Reporte Base (Bagó)", "Solo Diferencias", "Ver Desconocidos (Solo FP/QX)"])

            if opcion_vista == "Reporte Base (Bagó)":
                res_final = res_base.copy()
            elif opcion_vista == "Solo Diferencias":
                res_final = res_base[res_base['TOTAL_BAGO'] != res_base['TOTAL_FPQX']]
            else:
                res_final = solo_en_fpqx.copy()

            if busqueda:
                res_final = res_final[res_final.apply(lambda row: row.astype(str).str.contains(busqueda, case=False).any(), axis=1)]

            if not res_final.empty:
                # Normalizar columnas para cálculo de diferencia
                if 'TOTAL_BAGO' not in res_final.columns: res_final['TOTAL_BAGO'] = 0
                if 'TOTAL_FPQX' not in res_final.columns: res_final['TOTAL_FPQX'] = 0
                res_final['DIFERENCIA'] = res_final['TOTAL_BAGO'] - res_final['TOTAL_FPQX']
                
                # Renombrar para vista de usuario
                res_final = res_final.rename(columns={'TOTAL_BAGO': 'TOTAL BAGO', 'TOTAL_FPQX': 'TOTAL FP/QX'})
                
                # --- TABLA CON COLORES DE REPORTE (ROJO/VERDE) ---
                st.dataframe(
                    res_final.style.highlight_between(left=-999999, right=-0.1, color='#ffdadb', subset=['DIFERENCIA'] if 'DIFERENCIA' in res_final.columns else [])
                                   .highlight_between(left=0.1, right=999999, color='#d4edda', subset=['DIFERENCIA'] if 'DIFERENCIA' in res_final.columns else []),
                    use_container_width=True
                )

                # Exportar
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    res_final.to_excel(writer, index=False)
                st.download_button("📥 DESCARGAR REPORTE EXCEL", data=output.getvalue(), file_name=f"Bago_Reporte.xlsx")
            else:
                st.info("No hay datos para esta selección.")

        except Exception as e:
            st.error(f"Falla técnica: {e}")
