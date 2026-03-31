import streamlit as st
import pandas as pd
import io

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Dashboard Inventario | Bagó", page_icon="🧪", layout="wide")

# --- IDENTIDAD VISUAL Y CSS PREMIUM ---
MAGENTA_BAGO = "#C7006A" 

st.markdown(f"""
    <style>
    .main {{ background: #f8f9fa; }}
    
    /* Tarjetas de métricas con efecto de elevación */
    [data-testid="stMetric"] {{
        background-color: white;
        border-radius: 15px;
        padding: 20px;
        border-left: 6px solid {MAGENTA_BAGO};
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }}

    /* Botón de Descarga con degradado Bagó */
    div.stButton > button:first-child {{
        background: linear-gradient(90deg, {MAGENTA_BAGO} 0%, #A00055 100%) !important;
        color: white !important;
        border-radius: 10px;
        font-weight: bold;
        height: 3.8em;
        width: 100%;
        border: none;
        text-transform: uppercase;
        box-shadow: 0 4px 15px rgba(199, 0, 106, 0.3);
        transition: transform 0.2s;
    }}
    
    div.stButton > button:first-child:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(199, 0, 106, 0.4);
    }}

    h1, h2, h3 {{ color: {MAGENTA_BAGO} !important; font-weight: 800; }}
    </style>
    """, unsafe_allow_html=True)

# --- CABECERA ---
st.title("🧪 Conciliador de Inventarios Pro")
st.write("Panel de Control Unificado | Laboratorios Bagó")
st.divider()

# --- CARGA DE ARCHIVOS ---
c1, c2 = st.columns(2)
with c1:
    f1 = st.file_uploader("📂 Inventario BAGO (Anterior)", type=['xlsx'])
with c2:
    f2 = st.file_uploader("📂 Inventario FP/QX (Nuevo)", type=['xlsx'])

if f1 and f2:
    try:
        # Procesamiento directo sin botones de despliegue
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

            res = pd.merge(d1, d2, on=['MATERIAL', 'LOTE'], how='outer', suffixes=('_BAGO', '_FPQX')).fillna(0)
            res['DIFERENCIA'] = res['TOTAL_BAGO'] - res['TOTAL_FPQX']

            if tiene_desc:
                res['DESCRIPCION'] = res['DESCRIPCION_FPQX'].replace(0, '')
                res.loc[res['DESCRIPCION'] == '', 'DESCRIPCION'] = res['DESCRIPCION_ANT'] if 'DESCRIPCION_ANT' in res else res['DESCRIPCION_BAGO']
                # Limpiar columnas sobrantes
                for col in ['DESCRIPCION_BAGO', 'DESCRIPCION_FPQX']:
                    if col in res: res = res.drop(columns=[col])

            # --- 📊 MÉTRICAS EJECUTIVAS ---
            st.markdown("### 🔍 Resumen Ejecutivo")
            m1, m2, m3 = st.columns(3)
            
            m1.metric("Ítems Únicos", len(res))
            m2.metric("Sobrantes (+)", len(res[res['DIFERENCIA'] > 0]), delta="Ingresos")
            m3.metric("Faltantes (-)", len(res[res['DIFERENCIA'] < 0]), delta="Bajas", delta_color="inverse")

            st.divider()

            # --- 🔍 FILTROS ---
            f_col1, f_col2 = st.columns([2, 1])
            with f_col1:
                busqueda = st.text_input("🔎 Localizar Material o Lote:")
            with f_col2:
                opcion = st.selectbox("🎯 Filtrar por categoría:", ["Ver Todo", "Diferencias Detectadas", "Sobrantes", "Faltantes"])

            # Lógica de Filtros
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

            # Nombres finales de columnas
            res_final = res_final.rename(columns={'TOTAL_BAGO': 'TOTAL BAGO', 'TOTAL_FPQX': 'TOTAL FP/QX'})
            cols = ['MATERIAL', 'LOTE']
            if tiene_desc: cols.append('DESCRIPCION')
            cols += ['TOTAL BAGO', 'TOTAL FP/QX', 'DIFERENCIA']
            res_final = res_final[cols]

            # --- TABLA DE DATOS ---
            st.dataframe(
                res_final.style.highlight_between(left=-999999, right=-0.1, color='#ffdadb', subset=['DIFERENCIA'])
                               .highlight_between(left=0.1, right=999999, color='#d4edda', subset=['DIFERENCIA']),
                use_container_width=True
            )

            # --- EXPORTACIÓN ---
            st.divider()
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                res_final.to_excel(writer, index=False)
            
            st.download_button(
                label="📥 DESCARGAR REPORTE OFICIAL EN EXCEL",
                data=output.getvalue(),
                file_name="Reporte_Bago_Conciliacion.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.error("⚠️ Estructura incorrecta. Asegúrate de incluir: MATERIAL, LOTE y TOTAL.")
    except Exception as e:
        st.error(f"Falla crítica en el proceso: {e}")
else:
    st.info("👋 Listo para procesar. Por favor sube los archivos de inventario.")
