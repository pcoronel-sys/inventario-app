import streamlit as st
import pandas as pd
import io

# Configuración de página con Modo Ancho
st.set_page_config(page_title="Sistema de Control de Inventarios", page_icon="🏢", layout="wide")

# Estilo CSS personalizado para mejorar la apariencia de las métricas y botones
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    div.stButton > button:first-child {
        background-color: #007bff;
        color: white;
        border-radius: 5px;
        height: 3em;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# Encabezado Principal con Icono
st.title("🏢 Sistema de Conciliación de Inventarios")
st.subheader("Comparación Inteligente por Material + Lote")
st.divider()

# --- SECCIÓN DE CARGA DE ARCHIVOS ---
with st.container():
    col_file1, col_file2 = st.columns(2)
    with col_file1:
        st.info("📂 **PASO 1:** Sube el Inventario Anterior")
        f1 = st.file_uploader("Cargar Excel Base", type=['xlsx'], key="file1")
    with col_file2:
        st.success("📂 **PASO 2:** Sube el Inventario Nuevo")
        f2 = st.file_uploader("Cargar Excel Actualizado", type=['xlsx'], key="file2")

if f1 and f2:
    try:
        with st.spinner('🚀 Procesando y unificando lotes...'):
            df1 = pd.read_excel(f1)
            df2 = pd.read_excel(f2)
            
            # Normalizar nombres de columnas
            df1.columns = df1.columns.astype(str).str.strip().str.upper()
            df2.columns = df2.columns.astype(str).str.strip().str.upper()

            columnas_necesarias = ['MATERIAL', 'LOTE', 'TOTAL']
            tiene_desc = 'DESCRIPCION' in df1.columns and 'DESCRIPCION' in df2.columns

            if all(col in df1.columns for col in columnas_necesarias) and \
               all(col in df2.columns for col in columnas_necesarias):
                
                # Función para procesar datos ignorando descripción en el cálculo
                def preparar_datos(df):
                    df['MATERIAL'] = df['MATERIAL'].astype(str).str.strip()
                    df['LOTE'] = df['LOTE'].astype(str).str.strip()
                    agg_dict = {'TOTAL': 'sum'}
                    if tiene_desc:
                        df['DESCRIPCION'] = df['DESCRIPCION'].astype(str).str.strip()
                        agg_dict['DESCRIPCION'] = 'first'
                    return df.groupby(['MATERIAL', 'LOTE']).agg(agg_dict).reset_index()

                df1_final = preparar_datos(df1)
                df2_final = preparar_datos(df2)

                # Comparación
                res = pd.merge(df1_final, df2_final, on=['MATERIAL', 'LOTE'], how='outer', suffixes=('_ANT', '_NUEVO')).fillna(0)
                res['DIFERENCIA'] = res['TOTAL_NUEVO'] - res['TOTAL_ANT']

                if tiene_desc:
                    res['DESCRIPCION'] = res['DESCRIPCION_NUEVO'].replace(0, '')
                    res.loc[res['DESCRIPCION'] == '', 'DESCRIPCION'] = res['DESCRIPCION_ANT']
                    res = res.drop(columns=['DESCRIPCION_ANT', 'DESCRIPCION_NUEVO'])

                # --- DASHBOARD DE MÉTRICAS ---
                st.markdown("### 📈 Resumen de Movimientos")
                m1, m2, m3, m4 = st.columns(4)
                
                total_items = len(res)
                sobrantes = len(res[res['DIFERENCIA'] > 0])
                faltantes = len(res[res['DIFERENCIA'] < 0])
                sin_cambio = len(res[res['DIFERENCIA'] == 0])

                m1.metric("Ítems Totales", total_items)
                m2.metric("Sobrantes (Ingresos)", sobrantes, f"{sobrantes}", delta_color="normal")
                m3.metric("Faltantes (Salidas)", faltantes, f"-{faltantes}", delta_color="inverse")
                m4.metric("Sin Cambios", sin_cambio)

                # --- FILTROS Y TABLA ---
                st.divider()
                col_search, col_filter = st.columns([2, 1])
                
                with col_search:
                    search = st.text_input("🔍 Buscador rápido (Material o Lote):")
                with col_filter:
                    filtro_estado = st.selectbox("🎯 Filtrar por estado:", ["Todos", "Diferencias", "Solo Sobrantes", "Solo Faltantes"])

                # Aplicar filtros
                if search:
                    res = res[res['MATERIAL'].str.contains(search, case=False) | res['LOTE'].str.contains(search, case=False)]
                
                if filtro_estado == "Diferencias":
                    res = res[res['DIFERENCIA'] != 0]
                elif filtro_estado == "Solo Sobrantes":
                    res = res[res['DIFERENCIA'] > 0]
                elif filtro_estado == "Solo Faltantes":
                    res = res[res['DIFERENCIA'] < 0]

                # Reordenar columnas para visualización
                cols = ['MATERIAL', 'LOTE']
                if tiene_desc: cols.append('DESCRIPCION')
                cols += ['TOTAL_ANT', 'TOTAL_NUEVO', 'DIFERENCIA']
                res = res[cols]

                st.dataframe(
                    res.style.highlight_between(left=-99999, right=-0.1, color='#ffdadb', subset=['DIFERENCIA'])
                              .highlight_between(left=0.1, right=99999, color='#d4edda', subset=['DIFERENCIA']),
                    use_container_width=True
                )

                # --- BOTÓN DE DESCARGA PREMIUM ---
                st.divider()
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    res.to_excel(writer, index=False)
                
                st.download_button(
                    label="📥 DESCARGAR REPORTE FINAL EN EXCEL",
                    data=output.getvalue(),
                    file_name="Reporte_Inventario_Pro.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

            else:
                st.error("❌ ERROR: No se encontraron las columnas necesarias (MATERIAL, LOTE, TOTAL).")

    except Exception as e:
        st.error(f"🤯 Algo salió mal: {e}")

else:
    st.warning("👋 ¡Bienvenido! Por favor, sube los archivos en la parte superior para comenzar.")
