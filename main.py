import streamlit as st
import pandas as pd
import io

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Dashboard Inventario | Bagó", page_icon="🧪", layout="wide")

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
    .stDownloadButton button {{
        background: linear-gradient(90deg, {MAGENTA_BAGO} 0%, #A00055 100%) !important;
        color: white !important;
        border-radius: 10px !important;
        font-weight: bold !important;
        height: 3.8em !important;
        width: 100% !important;
        border: none !important;
        text-transform: uppercase !important;
    }}
    .stButton button {{
        background: #212529 !important;
        color: white !important;
        border-radius: 10px !important;
        font-weight: bold !important;
        height: 3.8em !important;
        width: 100% !important;
        border: none !important;
    }}
    h1, h2, h3 {{ color: {MAGENTA_BAGO} !important; font-weight: 800; }}
    </style>
    """, unsafe_allow_html=True)

def borrar_todo():
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()

# --- CABECERA ---
st.title("🧪 Conciliador de Inventarios Pro")
st.write("Soporte para Materiales con y sin Lote | Laboratorios Bagó")
st.divider()

# --- CARGA DE ARCHIVOS ---
c_file1, c_file2 = st.columns(2)
with c_file1:
    f1 = st.file_uploader("📂 Inventario BAGO", type=['xlsx'], key="file1")
with c_file2:
    f2 = st.file_uploader("📂 Inventario FP/QX", type=['xlsx'], key="file2")

if f1 and f2:
    try:
        df1 = pd.read_excel(f1)
        df2 = pd.read_excel(f2)
        
        df1.columns = df1.columns.astype(str).str.strip().str.upper()
        df2.columns = df2.columns.astype(str).str.strip().str.upper()

        # --- LÓGICA DE BLINDAJE PARA EL LOTE ---
        def normalizar_lotes(df):
            # Si no existe la columna LOTE, la creamos
            if 'LOTE' not in df.columns:
                df['LOTE'] = 'SIN LOTE'
            # Si existe, llenamos los vacíos (NaN) con "SIN LOTE"
            else:
                df['LOTE'] = df['LOTE'].fillna('SIN LOTE').astype(str).str.strip()
            return df

        df1 = normalizar_lotes(df1)
        df2 = normalizar_lotes(df2)

        columnas_req = ['MATERIAL', 'TOTAL'] # LOTE ya está garantizado arriba
        tiene_desc = 'DESCRIPCION' in df1.columns and 'DESCRIPCION' in df2.columns

        if all(col in df1.columns for col in columnas_req) and all(col in df2.columns for col in columnas_req):
            
            def procesar(df):
                df['MATERIAL'] = df['MATERIAL'].astype(str).str.strip()
                agg = {'TOTAL': 'sum'}
                if tiene_desc: 
                    df['DESCRIPCION'] = df['DESCRIPCION'].astype(str).str.strip()
                    agg['DESCRIPCION'] = 'first'
                # Agrupamos por MATERIAL y LOTE (aunque diga "SIN LOTE")
                return df.groupby(['MATERIAL', 'LOTE']).agg(agg).reset_index()

            d1 = procesar(df1)
            d2 = procesar(df2)

            res = pd.merge(d1, d2, on=['MATERIAL', 'LOTE'], how='outer', suffixes=('_BAGO', '_FPQX')).fillna(0)
            res['DIFERENCIA'] = res['TOTAL_BAGO'] - res['TOTAL_FPQX']

            # Métricas
            st.markdown("### 🔍 Resumen Ejecutivo")
            m1, m2, m3 = st.columns(3)
            m1.metric("Ítems Únicos", len(res))
            m2.metric("Sobrantes (+)", len(res[res['DIFERENCIA'] > 0]), delta="Ingresos")
            m3.metric("Faltantes (-)", len(res[res['DIFERENCIA'] < 0]), delta="Bajas", delta_color="inverse")

            st.divider()

            # Filtros
            f_col1, f_col2 = st.columns([2, 1])
            with f_col1:
                busqueda = st.text_input("🔎 Localizar Material o Lote:")
            with f_col2:
                opcion = st.selectbox("🎯 Filtrar por:", ["Todo", "Diferencias Detectadas", "Sobrantes", "Faltantes"])

            res_final = res.copy()
            if busqueda:
                res_final = res_final[res_final['MATERIAL'].str.contains(busqueda, case=False) | 
                                      res_final['LOTE'].str.contains(busqueda, case=False)]
            
            if opcion == "Diferencias Detectadas":
                res_final = res_final[res_final['DIFERENCIA'] != 0]
            elif opcion == "Sobrantes":
                res_final = res_final[res_final['DIFERENCIA'] > 0]
            elif opcion == "Faltantes":
                res_final = res_final[res_final['DIFERENCIA'] < 0]

            res_final = res_final.rename(columns={'TOTAL_BAGO': 'TOTAL BAGO', 'TOTAL_FPQX': 'TOTAL FP/QX'})
            
            # Tabla
            st.dataframe(
                res_final.style.highlight_between(left=-999999, right=-0.1, color='#ffdadb', subset=['DIFERENCIA'])
                               .highlight_between(left=0.1, right=999999, color='#d4edda', subset=['DIFERENCIA']),
                use_container_width=True
            )

            # --- BOTONES AL FINAL ---
            st.divider()
            col_descarga, col_reset = st.columns([0.7, 0.3])
            with col_descarga:
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    res_final.to_excel(writer, index=False)
                st.download_button(label="📥 DESCARGAR REPORTE EXCEL", data=output.getvalue(), file_name="Reporte_Conciliacion.xlsx")
            with col_reset:
                if st.button("🔄 REINICIAR TODO"): borrar_todo()
        else:
            st.error("⚠️ Verifica que los archivos tengan al menos las columnas: MATERIAL y TOTAL.")
    except Exception as e:
        st.error(f"Error: {e}")
else:
    if st.button("🔄 LIMPIAR PANTALLA"): borrar_todo()
    st.info("👋 Por favor, carga los archivos Excel para comenzar.")
