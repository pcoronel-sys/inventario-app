import streamlit as st
import pandas as pd
import io

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Inventario Bagó | Unificado", page_icon="🧪", layout="wide")

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
    /* Botones del Menú y Filtros */
    .stButton > button {{
        background: white !important;
        color: {MAGENTA_BAGO} !important;
        border: 2px solid {MAGENTA_BAGO} !important;
        border-radius: 10px !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
        width: 100%;
    }}
    .stButton > button:hover {{
        background: {MAGENTA_BAGO} !important;
        color: white !important;
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
    h1, h2, h3 {{ color: {MAGENTA_BAGO} !important; text-align: center; font-weight: 800; }}
    </style>
    """, unsafe_allow_html=True)

# --- NAVEGACIÓN ---
if 'modo' not in st.session_state:
    st.session_state.modo = None
if 'filtro_boton' not in st.session_state:
    st.session_state.filtro_boton = "Todos"

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
    st.markdown("### Seleccione el método para unificar códigos:")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📦 UNIFICAR POR MATERIAL + LOTE"):
            seleccionar_modo("con_lote")
            st.rerun()
    with col2:
        if st.button("🔢 UNIFICAR SOLO POR MATERIAL"):
            seleccionar_modo("sin_lote")
            st.rerun()

# --- APLICACIÓN ---
else:
    modo_txt = "CON LOTE" if st.session_state.modo == "con_lote" else "SIN LOTE"
    st.title(f"🧪 Reporte Unificado {modo_txt}")
    
    if st.button("⬅️ Cambiar Método / Volver"):
        borrar_todo()

    st.divider()

    c1, c2 = st.columns(2)
    with c1:
        f1 = st.file_uploader("📂 Archivo PRINCIPAL (Base Bagó)", type=['xlsx'], key="f1")
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

            # --- LEFT JOIN (Mantiene los 188 registros de Bagó) ---
            keys = ['MATERIAL', 'LOTE'] if st.session_state.modo == "con_lote" else ['MATERIAL']
            res = pd.merge(d1, d2, on=keys, how='left', suffixes=('_BAGO', '_FPQX')).fillna(0)
            res['DIFERENCIA'] = res['TOTAL_BAGO'] - res['TOTAL_FPQX']

            # Métricas
            st.markdown("### 📊 Resumen Ejecutivo")
            m1, m2, m3 = st.columns(3)
            m1.metric("Registros Base", len(res))
            m2.metric("Con Diferencia", len(res[res['DIFERENCIA'] != 0]))
            m3.metric("Sin Diferencia", len(res[res['DIFERENCIA'] == 0]))

            st.divider()

            # --- BOTONES DE FILTRO RÁPIDO ---
            st.markdown("#### 🛠️ Filtros de Vista")
            f_col1, f_col2, f_col3 = st.columns(3)
            with f_col1:
                if st.button("📄 MOSTRAR TODO"): st.session_state.filtro_boton = "Todos"
            with f_col2:
                if st.button("⚠️ SOLO DIFERENCIAS"): st.session_state.filtro_boton = "Diferencias"
            with f_col3:
                if st.button("✅ SIN DIFERENCIAS"): st.session_state.filtro_boton = "Iguales"

            # Buscador de texto
            busq = st.text_input("🔍 O busca manualmente (Código o Descripción):")

            # Lógica de Filtrado Combinada
            res_final = res.copy()
            
            if st.session_state.filtro_boton == "Diferencias":
                res_final = res_final[res_final['DIFERENCIA'] != 0]
            elif st.session_state.filtro_boton == "Iguales":
                res_final = res_final[res_final['DIFERENCIA'] == 0]
            
            if busq:
                res_final = res_final[res_final.apply(lambda row: row.astype(str).str.contains(busq, case=False).any(), axis=1)]

            # Formatear columnas
            cols = ['MATERIAL']
            if 'LOTE' in res_final.columns: cols.append('LOTE')
            if 'DESCRIPCION_BAGO' in res_final.columns:
                res_final = res_final.rename(columns={'DESCRIPCION_BAGO': 'DESCRIPCION'})
                cols.append('DESCRIPCION')
            cols += ['TOTAL_BAGO', 'TOTAL_FPQX', 'DIFERENCIA']
            res_final = res_final[cols]

            # Tabla
            st.dataframe(
                res_final.style.highlight_between(left=-999999, right=-0.1, color='#ffdadb', subset=['DIFERENCIA'])
                               .highlight_between(left=0.1, right=999999, color='#d4edda', subset=['DIFERENCIA']),
                use_container_width=True
            )

            # Acciones finales
            st.divider()
            c_d, c_r = st.columns([0.7, 0.3])
            with c_d:
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    res_final.to_excel(writer, index=False)
                st.download_button("📥 DESCARGAR REPORTE", data=output.getvalue(), file_name=f"Reporte_Bago.xlsx")
            with c_r:
                if st.button("🔄 REINICIAR"): borrar_todo()

        except Exception as e:
            st.error(f"Error: {e}")
