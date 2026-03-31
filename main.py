import streamlit as st
import pandas as pd
import io

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Inventario | Laboratorios Bagó", page_icon="🧪", layout="wide")

# --- VARIABLES DE DISEÑO ---
MAGENTA_BAGO = "#C7006A" 

# --- ESTILO CSS (CORREGIDO Y MEJORADO) ---
st.markdown(f"""
    <style>
    .main {{ background-color: #f4f7f9; }}
    .stMetric {{
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid {MAGENTA_BAGO};
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }}
    /* Botón de descarga */
    div.stButton > button:first-child {{
        background-color: {MAGENTA_BAGO} !important;
        color: white !important;
        border-radius: 8px;
        font-weight: bold;
        height: 3.5em;
        width: 100%;
        border: none;
    }}
    h1, h2 {{ color: {MAGENTA_BAGO} !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- ENCABEZADO ---
col_logo, col_titulo = st.columns([1, 4])
with col_logo:
    # Título estilizado que reemplaza al logo si la imagen falla
    st.markdown(f"<h1 style='font-size: 50px; margin:0;'>Bagó</h1>", unsafe_allow_html=True)
with col_titulo:
    st.title("Conciliador de Inventarios Pro")
    st.write("Control de Calidad y Logística | Comparación Material + Lote")

st.divider()

# --- CARGA DE ARCHIVOS (CENTRAL) ---
with st.expander("📂 PANEL DE CARGA DE ARCHIVOS", expanded=True):
    c1, c2 = st.columns(2)
    with c1:
        f1 = st.file_uploader("Inventario ANTERIOR (Base)", type=['xlsx'])
    with c2:
        f2 = st.file_uploader("Inventario NUEVO (Actual)", type=['xlsx'])

if f1 and f2:
    try:
        df1 = pd.read_excel(f1)
        df2 = pd.read_excel(f2)
        
        # Limpieza de nombres de columnas
        df1.columns = df1.columns.astype(str).str.strip().str.upper()
        df2.columns = df2.columns.astype(str).str.strip().str.upper()

        columnas_req = ['MATERIAL', 'LOTE', 'TOTAL']
        tiene_desc = 'DESCRIPCION' in df1.columns and 'DESCRIPCION' in df2.columns

        if all(col in df1.columns for col in columnas_req) and all(col in df2.columns for col in columnas_req):
            
            # Procesamiento unificado
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

            # Comparación
            res = pd.merge(d1, d2, on=['MATERIAL', 'LOTE'], how='outer', suffixes=('_ANT', '_NUEVO')).fillna(0)
            res['DIFERENCIA'] = res['TOTAL_NUEVO'] - res['TOTAL_ANT']

            if tiene_desc:
                res['DESCRIPCION'] = res['DESCRIPCION_NUEVO'].replace(0, '')
                res.loc[res['DESCRIPCION'] == '', 'DESCRIPCION'] = res['DESCRIPCION_ANT']
                res = res.drop(columns=['DESCRIPCION_ANT', 'DESCRIPCION_NUEVO'])

            # --- PANEL DE FILTROS (LOS BOTONES QUE HACÍAN FALTA) ---
            st.markdown("### 🛠️ Herramientas de Análisis")
            f_col1, f_col2, f_col3 = st.columns([2, 1, 1])
            
            with f_col1:
                busqueda = st.text_input("🔍 Buscar Material o Lote:", placeholder="Escribe aquí...")
            with f_col2:
                # FILTRO DE ESTADO REINSTALADO
                opcion = st.selectbox("🎯 Ver solo:", ["Todo", "Diferencias", "Sobrantes", "Faltantes"])
            with f_col3:
                # MÉTRICA RÁPIDA
                st.metric("Total items", len(res))

            # Aplicar filtros al dataframe
            res_final = res.copy()
            if busqueda:
                res_final = res_final[res_final['MATERIAL'].str.contains(busqueda, case=False) | 
                                      res_final['LOTE'].str.contains(busqueda, case=False)]
            
            if opcion == "Diferencias":
                res_final = res_final[res_final['DIFERENCIA'] != 0]
            elif opcion == "Sobrantes":
                res_final = res_final[res_final['DIFERENCIA'] > 0]
            elif opcion == "Faltantes":
                res_final = res_final[res_final['DIFERENCIA'] < 0]

            # Reordenar columnas
            cols = ['MATERIAL', 'LOTE']
            if tiene_desc: cols.append('DESCRIPCION')
            cols += ['TOTAL_ANT', 'TOTAL_NUEVO', 'DIFERENCIA']
            res_final = res_final[cols]

            # --- TABLA DE RESULTADOS ---
            st.dataframe(
                res_final.style.highlight_between(left=-999999, right=-0.1, color='#ffdadb', subset=['DIFERENCIA'])
                               .highlight_between(left=0.1, right=999999, color='#d4edda', subset=['DIFERENCIA']),
                use_container_width=True
            )

            # --- BOTÓN DE EXPORTACIÓN ---
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                res_final.to_excel(writer, index=False)
            
            st.download_button(
                label="📥 EXPORTAR REPORTE OFICIAL A EXCEL",
                data=output.getvalue(),
                file_name="REPORTE_BAGO_INVENTARIO.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        else:
            st.error("⚠️ Columnas no encontradas. Verifica que tus Excel tengan: MATERIAL, LOTE, TOTAL.")
    except Exception as e:
        st.error(f"Error técnico: {e}")
else:
    st.info("👋 Bienvenido. Sube los dos archivos Excel arriba para comenzar la conciliación.")
