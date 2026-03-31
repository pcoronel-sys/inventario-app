import streamlit as st
import pandas as pd
import io

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Inventario Bagó | Selección", page_icon="🧪", layout="wide")

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
        height: 5em !important;
        font-size: 1.2em !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
    }}
    .stButton > button:hover {{
        background: {MAGENTA_BAGO} !important;
        color: white !important;
        transform: scale(1.02);
    }}
    /* Botones de acción (Descarga/Reiniciar) */
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

# --- LÓGICA DE NAVEGACIÓN ---
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
    st.markdown("### Seleccione el método de cruce para comenzar:")
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_izq, col_der = st.columns(2)
    
    with col_izq:
        if st.button("📦 CRUCE CON LOTE\n(Máxima Precisión)"):
            seleccionar_modo("con_lote")
            st.rerun()
            
    with col_der:
        if st.button("🔢 CRUCE SIN LOTE\n(Solo Códigos de Material)"):
            seleccionar_modo("sin_lote")
            st.rerun()

# --- PANTALLA 2: APLICACIÓN (CUANDO YA SE ELIGIÓ UN MODO) ---
else:
    modo_texto = "CON LOTE" if st.session_state.modo == "con_lote" else "SIN LOTE"
    st.title(f"🧪 Conciliación {modo_texto}")
    
    # Botón pequeño para volver al menú
    if st.button("⬅️ Volver al Menú"):
        borrar_todo()

    st.divider()

    # --- CARGA DE ARCHIVOS ---
    c_f1, c_f2 = st.columns(2)
    with c_f1:
        f1 = st.file_uploader("📂 Inventario BAGO", type=['xlsx'], key="f1")
    with c_f2:
        f2 = st.file_uploader("📂 Inventario FP/QX", type=['xlsx'], key="f2")

    if f1 and f2:
        try:
            df1 = pd.read_excel(f1)
            df2 = pd.read_excel(f2)
            
            df1.columns = df1.columns.astype(str).str.strip().str.upper()
            df2.columns = df2.columns.astype(str).str.strip().str.upper()

            # Normalización según el modo elegido
            def preparar(df):
                df['MATERIAL'] = df['MATERIAL'].astype(str).str.strip()
                agg = {'TOTAL': 'sum'}
                
                # Si hay descripción, la guardamos
                tiene_desc = 'DESCRIPCION' in df.columns
                if tiene_desc:
                    df['DESCRIPCION'] = df['DESCRIPCION'].astype(str).str.strip()
                    agg['DESCRIPCION'] = 'first'
                
                # Agrupación según el modo
                if st.session_state.modo == "con_lote":
                    if 'LOTE' not in df.columns: df['LOTE'] = 'SIN LOTE'
                    df['LOTE'] = df['LOTE'].fillna('SIN LOTE').astype(str).str.strip()
                    return df.groupby(['MATERIAL', 'LOTE']).agg(agg).reset_index()
                else:
                    return df.groupby(['MATERIAL']).agg(agg).reset_index()

            d1 = preparar(df1)
            d2 = preparar(df2)

            # Cruce de datos
            llaves = ['MATERIAL', 'LOTE'] if st.session_state.modo == "con_lote" else ['MATERIAL']
            res = pd.merge(d1, d2, on=llaves, how='outer', suffixes=('_BAGO', '_FPQX')).fillna(0)
            res['DIFERENCIA'] = res['TOTAL_BAGO'] - res['TOTAL_FPQX']

            # Métricas
            st.markdown("### 🔍 Resumen Ejecutivo")
            m1, m2, m3 = st.columns(3)
            m1.metric("Ítems Únicos", len(res))
            m2.metric("Sobrantes (+)", len(res[res['DIFERENCIA'] > 0]), delta="Ingresos")
            m3.metric("Faltantes (-)", len(res[res['DIFERENCIA'] < 0]), delta="Bajas", delta_color="inverse")

            # Filtros
            st.divider()
            f_col1, f_col2 = st.columns([2, 1])
            with f_col1:
                busqueda = st.text_input("🔎 Localizar Material o Lote:")
            with f_col2:
                opcion = st.selectbox("🎯 Filtrar por:", ["Todo", "Diferencias Detectadas", "Sobrantes", "Faltantes"])

            res_final = res.copy()
            if busqueda:
                res_final = res_final[res_final.apply(lambda row: row.astype(str).str.contains(busqueda, case=False).any(), axis=1)]
            
            if opcion == "Diferencias Detectadas":
                res_final = res_final[res_final['DIFERENCIA'] != 0]
            elif opcion == "Sobrantes":
                res_final = res_final[res_final['DIFERENCIA'] > 0]
            elif opcion == "Faltantes":
                res_final = res_final[res_final['DIFERENCIA'] < 0]

            # Tabla
            st.dataframe(
                res_final.style.highlight_between(left=-999999, right=-0.1, color='#ffdadb', subset=['DIFERENCIA'])
                               .highlight_between(left=0.1, right=999999, color='#d4edda', subset=['DIFERENCIA']),
                use_container_width=True
            )

            # Botones de Acción
            st.divider()
            c_down, c_res = st.columns([0.7, 0.3])
            with c_down:
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    res_final.to_excel(writer, index=False)
                st.download_button("📥 DESCARGAR REPORTE EXCEL", data=output.getvalue(), file_name=f"Conciliacion_{st.session_state.modo}.xlsx")
            with c_res:
                if st.button("🔄 REINICIAR TODO"): borrar_todo()

        except Exception as e:
            st.error(f"Error al procesar: {e}")
    else:
        st.info(f"Esperando archivos para conciliación {modo_texto}...")
