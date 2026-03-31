import streamlit as st
import pandas as pd
import io

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Sistema Inventario - Bagó", page_icon="🧪", layout="wide")

# --- DEFINICIÓN DEL COLOR MAGENTA DE BAGÓ ---
# Un tono magenta profesional alineado con la identidad de laboratorios.
MAGENTA_BAGO = "#C7006A" 

# --- APLICACIÓN DE ESTILO CSS PERSONALIZADO ---
# Cambiamos los colores de la interfaz para usar el magenta Bagó
st.markdown(f"""
    <style>
    /* Fondo de la aplicación */
    .main {{
        background-color: #f8f9fa;
    }}
    
    /* Cambiar el color de los títulos principales H1 */
    h1 {{
        color: {MAGENTA_BAGO} !important;
        font-weight: 700 !important;
    }}
    
    /* Cambiar el color de los subtítulos H3 */
    h3 {{
        color: #333333;
        font-weight: 600 !important;
    }}

    /* Estilo de las tarjetas de Métricas (KPIs) */
    [data-testid="stMetricValue"] {{
        color: {MAGENTA_BAGO};
        font-weight: 700;
    }}
    
    .stMetric {{
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-left: 5px solid {MAGENTA_BAGO};
    }}

    /* Estilo del Botón de Descarga Principal */
    div.stButton > button:first-child {{
        background-color: {MAGENTA_BAGO};
        color: white;
        border-radius: 8px;
        height: 3.5em;
        width: 100%;
        font-weight: 700;
        font-size: 1.1em;
        border: none;
        box-shadow: 0 4px 6px rgba(199, 0, 106, 0.2);
        transition: all 0.3s ease;
    }}
    
    div.stButton > button:first-child:hover {{
        background-color: #A00055; /* Un tono más oscuro para el hover */
        box-shadow: 0 6px 8px rgba(199, 0, 106, 0.3);
    }}

    /* Cambiar el color de los mensajes de información (Banners) */
    .stAlert {{
        background-color: #fdf2f8;
        color: {MAGENTA_BAGO};
        border-color: {MAGENTA_BAGO};
        border-radius: 8px;
    }}
    
    .stAlert svg {{
        fill: {MAGENTA_BAGO};
    }}
    </style>
    """, unsafe_allow_html=True)

# --- ENCABEZADO PRINCIPAL (Con Logo o Nombre) ---
st.markdown("# 🧪 Laboratorios Bagó")
st.subheader("Sistema Centralizado de Conciliación de Inventarios")
st.divider()

# --- SECCIÓN DE CARGA DE ARCHIVOS ---
with st.container():
    st.markdown("### 1. Carga de Datos")
    col_file1, col_file2 = st.columns(2)
    with col_file1:
        st.info("**PASO A:** Sube el Inventario Base (Excel Anterior)")
        f1 = st.file_uploader("Someter Archivo Base", type=['xlsx'], key="file1")
    with col_file2:
        st.info("**PASO B:** Sube el Inventario Nuevo (Excel Actualizado)")
        f2 = st.file_uploader("Someter Archivo Actual", type=['xlsx'], key="file2")

if f1 and f2:
    try:
        with st.spinner('🚀 Procesando conciliación por Material y Lote...'):
            df1 = pd.read_excel(f1)
            df2 = pd.read_excel(f2)
            
            # Normalizar nombres de columnas
            df1.columns = df1.columns.astype(str).str.strip().str.upper()
            df2.columns = df2.columns.astype(str).str.strip().str.upper()

            columnas_necesarias = ['MATERIAL', 'LOTE', 'TOTAL']
            # La descripción es opcional para el cálculo, pero la mostramos si existe
            tiene_desc = 'DESCRIPCION' in df1.columns and 'DESCRIPCION' in df2.columns

            if all(col in df1.columns for col in columnas_necesarias) and \
               all(col in df2.columns for col in columnas_necesarias):
                
                # Función para procesar datos (unificar lotes repetidos)
                def preparar_datos(df):
                    df['MATERIAL'] = df['MATERIAL'].astype(str).str.strip()
                    df['LOTE'] = df['LOTE'].astype(str).str.strip()
                    
                    # Agregación: Sumamos el TOTAL por Material y Lote
                    agg_dict = {'TOTAL': 'sum'}
                    if tiene_desc:
                        df['DESCRIPCION'] = df['DESCRIPCION'].astype(str).str.strip()
                        agg_dict['DESCRIPCION'] = 'first' # Tomamos la primera descripción
                    
                    return df.groupby(['MATERIAL', 'LOTE']).agg(agg_dict).reset_index()

                df1_final = preparar_datos(df1)
                df2_final = preparar_datos(df2)

                # Comparación de Inventarios (Merge)
                res = pd.merge(
                    df1_final, 
                    df2_final, 
                    on=['MATERIAL', 'LOTE'], 
                    how='outer', 
                    suffixes=('_ANT', '_NUEVO')
                ).fillna(0)
                
                res['DIFERENCIA'] = res['TOTAL_NUEVO'] - res['TOTAL_ANT']

                # Manejo de Descripciones Duplicadas
                if tiene_desc:
                    res['DESCRIPCION'] = res['DESCRIPCION_NUEVO'].replace(0, '')
                    res.loc[res['DESCRIPCION'] == '', 'DESCRIPCION'] = res['DESCRIPCION_ANT']
                    res = res.drop(columns=['DESCRIPCION_ANT', 'DESCRIPCION_NUEVO'])

                # --- DASHBOARD DE MÉTRICAS (KPIs) ---
                st.markdown("### 📈 Resumen General de Conciliación")
                m1, m2, m3 = st.columns(3)
                
                sobrantes = len(res[res['DIFERENCIA'] > 0])
                faltantes = len(res[res['DIFERENCIA'] < 0])

                m1.metric("Ítems Únicos", len(res))
                m2.metric("Sobrantes (+)", sobrantes, f"{sobrantes}", delta_color="normal")
                m3.metric("Faltantes (-)", faltantes, f"-{faltantes}", delta_color="inverse")

                # --- FILTROS Y TABLA DE RESULTADOS ---
                st.divider()
                st.markdown("### 🔍 Detalle por Ítem y Lote")
                col_search, col_filter = st.columns([2, 1])
                
                with col_search:
                    search = st.text_input("Buscar por Código de Material o Lote:")
                with col_filter:
                    filtro_estado = st.selectbox("Estado:", ["Mostrar Todo", "Solo Diferencias", "Nuevos Ingresos", "Faltantes"])

                # Aplicar Filtros
                if search:
                    res = res[res['MATERIAL'].str.contains(search, case=False) | res['LOTE'].str.contains(search, case=False)]
                
                if filtro_estado == "Solo Diferencias":
                    res = res[res['DIFERENCIA'] != 0]
                elif filtro_estado == "Nuevos Ingresos":
                    res = res[res['DIFERENCIA'] > 0]
                elif filtro_estado == "Faltantes":
                    res = res[res['DIFERENCIA'] < 0]

                # Ordenar columnas
                cols = ['MATERIAL', 'LOTE']
                if tiene_desc: cols.append('DESCRIPCION')
                cols += ['TOTAL_ANT', 'TOTAL_NUEVO', 'DIFERENCIA']
                res = res[cols]

                # Visualización de la Tabla
                st.dataframe(
                    res.style.highlight_between(left=-999999, right=-0.1, color='#ffdadb', subset=['DIFERENCIA'])
                              .highlight_between(left=0.1, right=999999, color='#d4edda', subset=['DIFERENCIA']),
                    use_container_width=True
                )

                # --- BOTÓN DE DESCARGA MAGENTA ---
                st.divider()
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    res.to_excel(writer, index=False)
                
                st.download_button(
                    label="📥 DESCARGAR REPORTE CONCILIADO (EXCEL)",
                    data=output.getvalue(),
                    file_name="Reporte_Conciliacion_Bago.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

            else:
                st.error("❌ ERROR FALTAL: No se encontraron las columnas requeridas (MATERIAL, LOTE, TOTAL) en los archivos.")

    except Exception as e:
        st.error(f"🤯 Ocurrió un error inesperado al procesar los archivos: {e}")

else:
    st.warning("⚠️ **ATENCIÓN:** Por favor, sube ambos archivos Excel para iniciar el proceso de conciliación.")
