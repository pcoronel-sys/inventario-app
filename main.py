import streamlit as st
import pandas as pd
import io

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Conciliador de Inventarios", page_icon="🧪", layout="wide")

# --- IDENTIDAD VISUAL ---
MAGENTA_BAGO = "#C7006A" 

st.markdown(f"""
    <style>
    .main {{ background-color: #f8f9fa; }}
    h1, h2, h3 {{ color: {MAGENTA_BAGO} !important; }}
    
    /* Tarjetas de Métricas */
    [data-testid="stMetric"] {{
        background-color: #ffffff;
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid {MAGENTA_BAGO};
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }}
    
    /* Botón de Descarga */
    div.stButton > button:first-child {{
        background-color: {MAGENTA_BAGO} !important;
        color: white !important;
        border-radius: 8px;
        font-weight: bold;
        height: 3.5em;
        width: 100%;
        border: none;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- ENCABEZADO LIMPIO ---
st.title("🧪 Conciliador de Inventarios")
st.write("Comparación de stock unificada por Material y Lote")
st.divider()

# --- CARGA DE ARCHIVOS ---
c1, c2 = st.columns(2)
with c1:
    f1 = st.file_uploader("📂 Inventario ANTERIOR", type=['xlsx'])
with c2:
    f2 = st.file_uploader("📂 Inventario NUEVO", type=['xlsx'])

if f1 and f2:
    try:
        df1 = pd.read_excel(f1)
        df2 = pd.read_excel(f2)
        
        df1.columns = df1.columns.astype(str).str.strip().str.upper()
        df2.columns = df2.columns.astype(str).str.strip().str.upper()

        columnas_req = ['MATERIAL', 'LOTE', 'TOTAL']
        tiene_desc = 'DESCRIPCION' in df1.columns and 'DESCRIPCION' in df2.columns

        if all(col in df1.columns for col in columnas_req) and all(col in df2.columns for col in columnas_req):
            
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

            res = pd.merge(d1, d2, on=['MATERIAL', 'LOTE'], how='outer', suffixes=('_ANT', '_NUEVO')).fillna(0)
            res['DIFERENCIA'] = res['TOTAL_NUEVO'] - res['TOTAL_ANT']

            if tiene_desc:
                res['DESCRIPCION'] = res['DESCRIPCION_NUEVO'].replace(0, '')
                res.loc[res['DESCRIPCION'] == '', 'DESCRIPCION'] = res['DESCRIPCION_ANT']
                res = res.drop(columns=['DESCRIPCION_ANT', 'DESCRIPCION_NUEVO'])

            # --- 📊 MÉTRICAS (SOLO LAS 3 QUE PEDISTE) ---
            st.markdown("### 📊 Resumen de Diferencias")
            m1, m2, m3 = st.columns(3)
            
            m1.metric("Ítems Totales", len(res))
            m2.metric("Sobrantes (+)", len(res[res['DIFERENCIA'] > 0]))
            m3.metric("Faltantes (-)", len(res[res['DIFERENCIA'] < 0]), delta_color="inverse")

            st.divider()

            # --- 🔍 FILTROS ---
            f_col1, f_col2 = st.columns([2, 1])
            with f_col1:
                busqueda = st.text_input("🔍 Buscar Material o Lote:")
            with f_col2:
                opcion = st.selectbox("🎯 Filtrar por:", ["Todo", "Diferencias", "Sobrantes", "Faltantes"])

            # Aplicar Filtros
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

            cols = ['MATERIAL', 'LOTE']
            if tiene_desc: cols.append('DESCRIPCION')
            cols += ['TOTAL_ANT', 'TOTAL_NUEVO', 'DIFERENCIA']
            res_final = res_final[cols]

            # --- TABLA ---
            st.dataframe(
                res_final.style.highlight_between(left=-999999, right=-0.1, color='#ffdadb', subset=['DIFERENCIA'])
                               .highlight_between(left=0.1, right=999999, color='#d4edda', subset=['DIFERENCIA']),
                use_container_width=True
            )

            # --- EXPORTAR ---
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                res_final.to_excel(writer, index=False)
            
            st.download_button(
                label="📥 EXPORTAR RESULTADOS A EXCEL",
                data=output.getvalue(),
                file_name="Reporte_Conciliacion.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.error("⚠️ Columnas no encontradas.")
    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("👋 Sube los archivos para comenzar.")
