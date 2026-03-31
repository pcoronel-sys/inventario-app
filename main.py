import streamlit as st
import pandas as pd
import io

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Dashboard Inventario | Bagó", page_icon="🧪", layout="wide")

# --- IDENTIDAD VISUAL Y CSS AVANZADO ---
MAGENTA_BAGO = "#C7006A" 

st.markdown(f"""
    <style>
    /* Fondo degradado sutil */
    .main {{
        background: linear_gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    }}
    
    /* Efecto Glassmorphism en métricas */
    [data-testid="stMetric"] {{
        background-color: rgba(255, 255, 255, 0.9);
        border-radius: 20px;
        padding: 25px;
        border: 1px solid rgba(199, 0, 106, 0.1);
        box-shadow: 0 10px 20px rgba(0,0,0,0.05);
        transition: transform 0.3s ease;
    }}
    
    [data-testid="stMetric"]:hover {{
        transform: translateY(-5px);
        box-shadow: 0 15px 30px rgba(199, 0, 106, 0.1);
    }}

    /* Botón de Descarga con animación */
    div.stButton > button:first-child {{
        background: linear-gradient(90deg, {MAGENTA_BAGO} 0%, #A00055 100%) !important;
        color: white !important;
        border-radius: 12px;
        font-weight: bold;
        height: 4em;
        width: 100%;
        border: none;
        letter-spacing: 1px;
        text-transform: uppercase;
        transition: all 0.4s ease;
        box-shadow: 0 5px 15px rgba(199, 0, 106, 0.3);
    }}
    
    div.stButton > button:first-child:hover {{
        transform: scale(1.02);
        box-shadow: 0 8px 25px rgba(199, 0, 106, 0.5);
    }}

    /* Títulos con sombra de texto sutil */
    h1 {{
        color: {MAGENTA_BAGO} !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.05);
        font-weight: 800;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- CABECERA ---
st.title("🧪 Conciliador de Inventarios Pro")
st.markdown("##### Optimizado para **Laboratorios Bagó** | Logística Especializada")
st.divider()

# --- CARGA DE ARCHIVOS ---
with st.container():
    c1, c2 = st.columns(2)
    with c1:
        f1 = st.file_uploader("📂 Inventario BAGO (Anterior)", type=['xlsx'])
    with c2:
        f2 = st.file_uploader("📂 Inventario FP/QX (Nuevo)", type=['xlsx'])

if f1 and f2:
    try:
        # Barra de carga visual
        with st.status("🚀 Sincronizando bases de datos...", expanded=True) as status:
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
                    res.loc[res['DESCRIPCION'] == '', 'DESCRIPCION'] = res['DESCRIPCION_BAGO']
                    res = res.drop(columns=['DESCRIPCION_BAGO', 'DESCRIPCION_FPQX'])
                
                status.update(label="✅ Conciliación completada con éxito", state="complete", expanded=False)

                # --- 📊 MÉTRICAS VISUALES ---
                st.markdown("### 🔍 Resumen Ejecutivo")
                m1, m2, m3 = st.columns(3)
                
                m1.metric("Ítems Únicos", len(res), help="Suma de Material + Lote únicos")
                m2.metric("Sobrantes (+)", len(res[res['DIFERENCIA'] > 0]), delta="Ingresos")
                m3.metric("Faltantes (-)", len(res[res['DIFERENCIA'] < 0]), delta="Bajas", delta_color="inverse")

                st.divider()

                # --- 🔍 FILTROS INTELIGENTES ---
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

                res_final = res_final.rename(columns={'TOTAL_BAGO': 'TOTAL BAGO', 'TOTAL_FPQX': 'TOTAL FP/QX'})
                cols = ['MATERIAL', 'LOTE']
                if tiene_desc: cols.append('DESCRIPCION')
                cols += ['TOTAL BAGO', 'TOTAL FP/QX', 'DIFERENCIA']
                res_final = res_final[cols]

                # --- TABLA ESTILIZADA ---
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
                st.error("⚠️ Error en estructura: Faltan las columnas MATERIAL, LOTE o TOTAL.")
    except Exception as e:
        st.error(f"Falla crítica: {e}")
else:
    st.info("👋 Listo para procesar. Por favor sube los archivos de inventario.")
