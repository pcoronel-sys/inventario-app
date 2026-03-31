import streamlit as st
import pandas as pd
import io

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Inventario Bagó | Sistema Pro", page_icon="🧪", layout="wide")

# --- IDENTIDAD VISUAL ---
MAGENTA_BAGO = "#C7006A" 

st.markdown(f"""
    <style>
    .main {{ background: #f8f9fa; }}
    [data-testid="stMetric"] {{
        background-color: white;
        border-radius: 15px;
        padding: 20px;
        border-left: 6px solid {MAGENTA_BAGO};
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }}
    /* Botones del Menú Principal */
    .stButton > button {{
        background: white !important;
        color: {MAGENTA_BAGO} !important;
        border: 2px solid {MAGENTA_BAGO} !important;
        border-radius: 15px !important;
        height: 6em !important;
        font-size: 1.1em !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
    }}
    .stButton > button:hover {{
        background: {MAGENTA_BAGO} !important;
        color: white !important;
    }}
    /* Botones de acción */
    .stDownloadButton button {{
        background: linear-gradient(90deg, {MAGENTA_BAGO} 0%, #A00055 100%) !important;
        color: white !important;
        border-radius: 10px !important;
        height: 3.5em !important;
        width: 100% !important;
        border: none !important;
    }}
    h1, h2, h3 {{ color: {MAGENTA_BAGO} !important; font-weight: 800; text-align: center; }}
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE NAVEGACIÓN Y LIMPIEZA ---
if 'modo' not in st.session_state:
    st.session_state.modo = None

def seleccionar_modo(modo):
    st.session_state.modo = modo

def borrar_todo():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# --- PANTALLA 1: MENÚ PRINCIPAL ---
if st.session_state.modo is None:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.title("🧪 Sistema de Conciliación Bagó")
    st.markdown("### Seleccione el método de cruce:")
    st.markdown("<br>", unsafe_allow_html=True)
    
    c_izq, c_der = st.columns(2)
    with c_izq:
        if st.button("📦 CRUCE CON LOTE\n(Diferencia por partida)"):
            seleccionar_modo("con_lote")
            st.rerun()
    with c_der:
        if st.button("🔢 CRUCE SIN LOTE\n(Total por Material)"):
            seleccionar_modo("sin_lote")
            st.rerun()

# --- PANTALLA 2: APLICACIÓN ---
else:
    modo_display = "CON LOTE" if st.session_state.modo == "con_lote" else "SIN LOTE"
    st.title(f"🧪 Conciliación {modo_display}")
    
    if st.button("⬅️ Volver al Menú Principal"):
        borrar_todo()

    st.divider()

    col_a, col_b = st.columns(2)
    with col_a:
        f1 = st.file_uploader("📂 Inventario BAGO", type=['xlsx'], key="f1")
    with col_b:
        f2 = st.file_uploader("📂 Inventario FP/QX", type=['xlsx'], key="f2")

    if f1 and f2:
        try:
            df1 = pd.read_excel(f1)
            df2 = pd.read_excel(f2)
            
            # --- FUNCIÓN DE LIMPIEZA Y AGRUPACIÓN ESTRICTA ---
            def preparar_dataframe(df):
                # Forzar mayúsculas y quitar espacios en blanco para evitar duplicados falsos
                df.columns = df.columns.astype(str).str.strip().str.upper()
                df['MATERIAL'] = df['MATERIAL'].astype(str).str.strip().str.upper()
                
                agg_logic = {'TOTAL': 'sum'}
                
                if 'DESCRIPCION' in df.columns:
                    df['DESCRIPCION'] = df['DESCRIPCION'].astype(str).str.strip().str.upper()
                    agg_logic['DESCRIPCION'] = 'first'
                
                if st.session_state.modo == "con_lote":
                    if 'LOTE' not in df.columns: df['LOTE'] = 'SIN LOTE'
                    df['LOTE'] = df['LOTE'].fillna('SIN LOTE').astype(str).str.strip().str.upper()
                    # Agrupa por ambos campos
                    return df.groupby(['MATERIAL', 'LOTE']).agg(agg_logic).reset_index()
                else:
                    # IGNORA EL LOTE: Suma todo lo que tenga el mismo código de material
                    return df.groupby(['MATERIAL']).agg(agg_logic).reset_index()

            d1 = preparar_dataframe(df1)
            d2 = preparar_dataframe(df2)

            # --- CRUCE (MERGE) ---
            keys = ['MATERIAL', 'LOTE'] if st.session_state.modo == "con_lote" else ['MATERIAL']
            
            # Realizamos un "Outer Merge" para no perder información de ninguno
            res = pd.merge(d1, d2, on=keys, how='outer', suffixes=('_BAGO', '_FPQX')).fillna(0)
            res['DIFERENCIA'] = res['TOTAL_BAGO'] - res['TOTAL_FPQX']

            # Limpieza de descripción post-merge
            if 'DESCRIPCION_BAGO' in res.columns:
                res['DESCRIPCION'] = res['DESCRIPCION_BAGO'].replace(0, '')
                res.loc[res['DESCRIPCION'] == '', 'DESCRIPCION'] = res['DESCRIPCION_FPQX']
                res = res.drop(columns=['DESCRIPCION_BAGO', 'DESCRIPCION_FPQX'])

            # --- MÉTRICAS ---
            st.markdown("### 📊 Resumen de Resultados")
            m1, m2, m3 = st.columns(3)
            m1.metric("Registros en Reporte", len(res), help="Suma de coincidencias + faltantes + sobrantes")
            m2.metric("Sobrantes (+)", len(res[res['DIFERENCIA'] > 0]))
            m3.metric("Faltantes (-)", len(res[res['DIFERENCIA'] < 0]), delta_color="inverse")

            st.divider()

            # --- FILTROS DE VISTA ---
            c_busq, c_filt = st.columns([2, 1])
            with c_busq:
                query = st.text_input("🔍 Buscar Material o Lote:")
            with c_filt:
                filter_opt = st.selectbox("🎯 Ver:", ["Todos", "Solo Diferencias", "Solo Coincidencias Exactas"])

            # Aplicar filtros
            res_final = res.copy()
            if query:
                res_final = res_final[res_final.apply(lambda row: row.astype(str).str.contains(query, case=False).any(), axis=1)]
            
            if filter_opt == "Solo Diferencias":
                res_final = res_final[res_final['DIFERENCIA'] != 0]
            elif filter_opt == "Solo Coincidencias Exactas":
                res_final = res_final[res_final['DIFERENCIA'] == 0]

            # Reordenar columnas para visualización
            final_cols = ['MATERIAL']
            if 'LOTE' in res_final.columns: final_cols.append('LOTE')
            if 'DESCRIPCION' in res_final.columns: final_cols.append('DESCRIPCION')
            final_cols += ['TOTAL_BAGO', 'TOTAL_FPQX', 'DIFERENCIA']
            res_final = res_final[final_cols]

            # --- TABLA ---
            st.dataframe(
                res_final.style.highlight_between(left=-999999, right=-0.1, color='#ffdadb', subset=['DIFERENCIA'])
                               .highlight_between(left=0.1, right=999999, color='#d4edda', subset=['DIFERENCIA']),
                use_container_width=True
            )

            # --- ACCIONES FINALES ---
            st.divider()
            c_desc, c_rein = st.columns([0.7, 0.3])
            with c_desc:
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    res_final.to_excel(writer, index=False)
                st.download_button("📥 DESCARGAR EXCEL", data=output.getvalue(), file_name=f"Reporte_{st.session_state.modo}.xlsx")
            with c_rein:
                if st.button("🔄 REINICIAR"): borrar_todo()

        except Exception as e:
            st.error(f"Error en el proceso: {e}")
    else:
        st.info(f"Suba los archivos para iniciar el cruce {modo_display}")
