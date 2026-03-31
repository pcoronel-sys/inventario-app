import streamlit as st
import pandas as pd
import io

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Inventario | Laboratorios Bagó", page_icon="🧪", layout="wide")

# --- IDENTIDAD VISUAL BAGÓ ---
MAGENTA_BAGO = "#C7006A" 

st.markdown(f"""
    <style>
    .main {{ background-color: #f8f9fa; }}
    /* Títulos y Subtítulos */
    h1, h2, h3 {{ color: {MAGENTA_BAGO} !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
    
    /* Tarjetas de Métricas (Botones de información) */
    [data-testid="stMetric"] {{
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        border-bottom: 5px solid {MAGENTA_BAGO};
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }}
    
    /* Botón de Descarga */
    div.stButton > button:first-child {{
        background-color: {MAGENTA_BAGO} !important;
        color: white !important;
        border-radius: 10px;
        font-weight: bold;
        height: 3.8em;
        width: 100%;
        border: none;
        font-size: 1.1em;
        box-shadow: 0 4px 15px rgba(199, 0, 106, 0.2);
    }}
    
    /* Estilo para el nombre Bagó */
    .bago-logo {{
        font-size: 48px;
        font-weight: 800;
        color: {MAGENTA_BAGO};
        letter-spacing: -2px;
        margin-bottom: 0;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- ENCABEZADO ---
col_l, col_t = st.columns([1, 3])
with col_l:
    st.markdown('<p class="bago-logo">Bagó</p>', unsafe_allow_html=True)
with col_t:
    st.title("Conciliador de Inventarios Inteligente")
    st.write("Unidad de Logística y Control de Stock")

st.divider()

# --- CARGA DE ARCHIVOS ---
with st.container():
    c1, c2 = st.columns(2)
    with c1:
        f1 = st.file_uploader("📂 Subir Inventario ANTERIOR (Base)", type=['xlsx'])
    with c2:
        f2 = st.file_uploader("📂 Subir Inventario NUEVO (Actual)", type=['xlsx'])

if f1 and f2:
    try:
        df1 = pd.read_excel(f1)
        df2 = pd.read_excel(f2)
        
        # Limpieza de columnas
        df1.columns = df1.columns.astype(str).str.strip().str.upper()
        df2.columns = df2.columns.astype(str).str.strip().str.upper()

        columnas_req = ['MATERIAL', 'LOTE', 'TOTAL']
        tiene_desc = 'DESCRIPCION' in df1.columns and 'DESCRIPCION' in df2.columns

        if all(col in df1.columns for col in columnas_req) and all(col in df2.columns for col in columnas_req):
            
            # Función para unificar lotes repetidos
            def procesar(df):
                df['MATERIAL'] = df['MATERIAL'].astype(str).str.strip()
                df['LOTE'] = df['LOTE'].astype(str).str.strip()
                agg = {'TOTAL': 'sum'}
                if tiene_desc: 
                    df['DESCRIPCION'] = df['DESCRIPCION'].astype(str).str.strip()
                    agg['DESCRIPCION'] = 'first'
                return df.groupby(['MATERIAL', 'LOTE']).agg(agg).reset_index()

            d1 = procesar(df1)
            d2 = procesar(df2)

            # Comparación Final
            res = pd.merge(d1, d2, on=['MATERIAL', 'LOTE'], how='outer', suffixes=('_ANT', '_NUEVO')).fillna(0)
            res['DIFERENCIA'] = res['TOTAL_NUEVO'] - res['TOTAL_ANT']

            if tiene_desc:
                res['DESCRIPCION'] = res['DESCRIPCION_NUEVO'].replace(0, '')
                res.loc[res['DESCRIPCION'] == '', 'DESCRIPCION'] = res['DESCRIPCION_ANT']
                res = res.drop(columns=['DESCRIPCION_ANT', 'DESCRIPCION_NUEVO'])

            # --- 📊 PANEL DE MÉTRICAS (LO QUE FALTABA) ---
            st.markdown("### 📊 Resumen de Diferencias")
            m1, m2, m3, m4 = st.columns(4)
            
            total_items = len(res)
            sobrantes = len(res[res['DIFERENCIA'] > 0])
            faltantes = len(res[res['DIFERENCIA'] < 0])
            sin_cambio = len(res[res['DIFERENCIA'] == 0])

            m1.metric("Ítems Totales", total_items)
            m2.metric("Sobrantes (+)", sobrantes, f"{sobrantes} Ingresos", delta_color="normal")
            m3.metric("Faltantes (-)", faltantes, f"-{faltantes} Bajas", delta_color="inverse")
            m4.metric("Sin Cambios", sin_cambio)

            st.divider()

            # --- 🛠️ HERRAMIENTAS DE FILTRO ---
            st.markdown("### 🔍 Herramientas de Análisis")
            f_col1, f_col2 = st.columns([2, 1])
            
            with f_col1:
                busqueda = st.text_input("Buscar Material o Lote específico:", placeholder="Escriba código o lote...")
            with f_col2:
                opcion = st.selectbox("Filtrar Tabla por Estado:", ["Ver Todo", "Solo con Diferencias", "Nuevos Ingresos", "Agotados/Faltantes"])

            # Aplicar Lógica de Filtros
            res_final = res.copy()
            if busqueda:
                res_final = res_final[res_final['MATERIAL'].str.contains(busqueda, case=False) | 
                                      res_final['LOTE'].str.contains(busqueda, case=False)]
            
            if opcion == "Solo con Diferencias":
                res_final = res_final[res_final['DIFERENCIA'] != 0]
            elif opcion == "Nuevos Ingresos":
                res_final = res_final[res_final['DIFERENCIA'] > 0]
            elif opcion == "Agotados/Faltantes":
                res_final = res_final[res_final['DIFERENCIA'] < 0]

            # Reordenar Columnas para el Excel y la vista
            cols = ['MATERIAL', 'LOTE']
            if tiene_desc: cols.append('DESCRIPCION')
            cols += ['TOTAL_ANT', 'TOTAL_NUEVO', 'DIFERENCIA']
            res_final = res_final[cols]

            # --- 📋 TABLA DE RESULTADOS ---
            st.dataframe(
                res_final.style.highlight_between(left=-999999, right=-0.1, color='#ffdadb', subset=['DIFERENCIA'])
                               .highlight_between(left=0.1, right=999999, color='#d4edda', subset=['DIFERENCIA']),
                use_container_width=True
            )

            # --- 📥 BOTÓN DE EXPORTACIÓN ---
            st.divider()
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                res_final.to_excel(writer, index=False)
            
            st.download_button(
                label="📥 EXPORTAR REPORTE OFICIAL BAGÓ A EXCEL",
                data=output.getvalue(),
                file_name="REPORTE_CONCILIACION_BAGO.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        else:
            st.error("⚠️ Error: Los archivos deben tener las columnas MATERIAL, LOTE y TOTAL.")
    except Exception as e:
        st.error(f"Falla técnica al procesar: {e}")
else:
    st.warning("👈 Por favor, cargue los archivos Excel arriba para generar el reporte de conciliación.")
