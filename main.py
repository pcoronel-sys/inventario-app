import streamlit as st
import pandas as pd
import io

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Inventario Bagó | Filtros Pro", page_icon="🧪", layout="wide")

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
    /* Estilo de los Selectores y Buscadores */
    .stSelectbox, .stTextInput {{
        color: {MAGENTA_BAGO};
    }}
    /* Botón de Descarga */
    .stDownloadButton button {{
        background: linear-gradient(90deg, {MAGENTA_BAGO} 0%, #A00055 100%) !important;
        color: white !important;
        border-radius: 10px !important;
        height: 3.5em !important;
        width: 100% !important;
        border: none !important;
        font-weight: bold !important;
    }}
    /* Botón Reiniciar */
    .stButton button {{
        background: #212529 !important;
        color: white !important;
        border-radius: 10px !important;
        height: 3.5em !important;
        width: 100% !important;
    }}
    h1, h2, h3 {{ color: {MAGENTA_BAGO} !important; text-align: center; font-weight: 800; }}
    </style>
    """, unsafe_allow_html=True)

# --- NAVEGACIÓN ---
if 'modo' not in st.session_state:
    st.session_state.modo = None

def seleccionar_modo(modo):
    st.session_state.modo = modo

def borrar_todo():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# --- MENÚ PRINCIPAL ---
if st.session_state.modo is None:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.title("🧪 Sistema de Conciliación Bagó")
    st.markdown("### Seleccione el método de cruce:")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📦 CRUCE POR MATERIAL + LOTE"):
            seleccionar_modo("con_lote")
            st.rerun()
    with col2:
        if st.button("🔢 CRUCE SOLO POR MATERIAL"):
            seleccionar_modo("sin_lote")
            st.rerun()

# --- APLICACIÓN PRINCIPAL ---
else:
    modo_txt = "CON LOTE" if st.session_state.modo == "con_lote" else "SIN LOTE"
    st.title(f"🧪 Reporte Unificado {modo_txt}")
    
    if st.button("⬅️ Cambiar Método / Volver"):
        borrar_todo()

    st.divider()

    # Carga de archivos
    c1, c2 = st.columns(2)
    with c1:
        f1 = st.file_uploader("📂 Archivo BASE (Bagó - Manda cantidad de filas)", type=['xlsx'], key="f1")
    with c2:
        f2 = st.file_uploader("📂 Archivo COMPARATIVO (FP/QX)", type=['xlsx'], key="f2")

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

            # --- LEFT JOIN (Para mantener exactamente las filas de Bagó) ---
            keys = ['MATERIAL', 'LOTE'] if st.session_state.modo == "con_lote" else ['MATERIAL']
            res = pd.merge(d1, d2, on=keys, how='left', suffixes=('_BAGO', '_FPQX')).fillna(0)
            res['DIFERENCIA'] = res['TOTAL_BAGO'] - res['TOTAL_FPQX']

            # Métricas rápidas
            st.markdown("### 📊 Resumen Ejecutivo")
            m1, m2, m3 = st.columns(3)
            m1.metric("Registros Base", len(res))
            m2.metric("Con Diferencia", len(res[res['DIFERENCIA'] != 0]))
            m3.metric("Sin Diferencia", len(res[res['DIFERENCIA'] == 0]))

            st.divider()

            # --- SECCIÓN DE FILTROS DESPLEGABLES ---
            st.markdown("#### 🛠️ Filtros de Análisis")
            col_f1, col_f2 = st.columns([2, 1])
            
            with col_f1:
                busqueda = st.text_input("🔍 Buscar por Código o Descripción:", placeholder="Ej: 100234...")
            
            with col_f2:
                filtro_estado = st.selectbox(
                    "🎯 Filtrar por Estado:",
                    ["Mostrar Todo", "Solo con Diferencias", "Sin Diferencias (OK)"]
                )

            # --- LÓGICA DE FILTRADO ---
            res_final = res.copy()
            
            # 1. Filtro por Estado
            if filtro_estado == "Solo con Diferencias":
                res_final = res_final[res_final['DIFERENCIA'] != 0]
            elif filtro_estado == "Sin Diferencias (OK)":
                res_final = res_final[res_final['DIFERENCIA'] == 0]
            
            # 2. Filtro por Texto
            if busqueda:
                # Busca en todas las columnas de texto
                res_final = res_final[res_final.apply(lambda row: row.astype(str).str.contains(busqueda, case=False).any(), axis=1)]

            # Limpiar nombres de columnas para la vista
            if 'DESCRIPCION_BAGO' in res_final.columns:
                res_final = res_final.rename(columns={'DESCRIPCION_BAGO': 'DESCRIPCION'})
            
            cols_vista = ['MATERIAL']
            if 'LOTE' in res_final.columns: cols_vista.append('LOTE')
            if 'DESCRIPCION' in res_final.columns: cols_vista.append('DESCRIPCION')
            cols_vista += ['TOTAL_BAGO', 'TOTAL_FPQX', 'DIFERENCIA']
            
            res_final = res_final[cols_vista]

            # --- TABLA DE RESULTADOS ---
            st.dataframe(
                res_final.style.highlight_between(left=-999999, right=-0.1, color='#ffdadb', subset=['DIFERENCIA'])
                               .highlight_between(left=0.1, right=999999, color='#d4edda', subset=['DIFERENCIA']),
                use_container_width=True
            )

            # --- ACCIONES FINALES ---
            st.divider()
            c_d, c_r = st.columns([0.7, 0.3])
            with c_d:
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    res_final.to_excel(writer, index=False)
                st.download_button("📥 DESCARGAR REPORTE FILTRADO", data=output.getvalue(), file_name=f"Reporte_Bago.xlsx")
            with c_r:
                if st.button("🔄 REINICIAR"):
                    borrar_todo()

        except Exception as e:
            st.error(f"Error procesando archivos: {e}")
    else:
        st.info(f"Suba los archivos para iniciar la conciliación {modo_txt}")
