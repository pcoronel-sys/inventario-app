import streamlit as st
import pandas as pd
import io
import plotly.express as px

st.set_page_config(page_title="App Inventario Unificado", page_icon="📦", layout="wide")

st.title("📦 Comparador de Inventarios (Unificado por Lotes)")
st.markdown("""
Esta versión **suma automáticamente** las cantidades si un material se repite en varias filas. 
Busca las columnas: **MATERIAL**, **DESCRIPCION**, **LOTE** y **TOTAL**.
""")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("Configuración")
    f1 = st.file_uploader("Archivo ANTERIOR (Excel)", type=['xlsx'])
    f2 = st.file_uploader("Archivo NUEVO (Excel)", type=['xlsx'])

if f1 and f2:
    try:
        df1 = pd.read_excel(f1)
        df2 = pd.read_excel(f2)
        
        # 1. Limpieza de nombres de columnas
        df1.columns = df1.columns.astype(str).str.strip().str.upper()
        df2.columns = df2.columns.astype(str).str.strip().str.upper()

        columnas_clave = ['MATERIAL', 'DESCRIPCION', 'LOTE']
        col_valor = 'TOTAL'

        # Verificar columnas
        if all(col in df1.columns for col in columnas_clave + [col_valor]) and \
           all(col in df2.columns for col in columnas_clave + [col_valor]):
            
            # 2. UNIFICAR FILAS (La magia ocurre aquí)
            # Agrupamos por Material, Descripcion y Lote, y sumamos el TOTAL
            df1_agrupado = df1.groupby(columnas_clave)[col_valor].sum().reset_index()
            df2_agrupado = df2.groupby(columnas_clave)[col_valor].sum().reset_index()

            # 3. COMPARACIÓN (Merge)
            res = pd.merge(
                df1_agrupado, 
                df2_agrupado, 
                on=columnas_clave, 
                how='outer', 
                suffixes=('_ANT', '_NUEVO')
            ).fillna(0)
            
            res['DIFERENCIA'] = res['TOTAL_NUEVO'] - res['TOTAL_ANT']

            # --- VISUALIZACIÓN ---
            m1, m2, m3 = st.columns(3)
            m1.metric("Ítems Únicos", len(res))
            m2.metric("Sobrantes (Ingresos)", len(res[res['DIFERENCIA'] > 0]))
            m3.metric("Faltantes (Bajas)", len(res[res['DIFERENCIA'] < 0]))

            st.divider()

            # Buscador en tiempo real
            busqueda = st.text_input("🔍 Buscar por Material o Lote:")
            if busqueda:
                res = res[res['MATERIAL'].astype(str).str.contains(busqueda, case=False) | 
                          res['LOTE'].astype(str).str.contains(busqueda, case=False)]

            # Tabla con colores
            st.subheader("📋 Reporte Comparativo Unificado")
            st.dataframe(
                res.style.highlight_between(left=-99999, right=-0.1, color='#ffcccc', subset=['DIFERENCIA'])
                          .highlight_between(left=0.1, right=99999, color='#ccffcc', subset=['DIFERENCIA']),
                use_container_width=True
            )

            # Botón de descarga
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                res.to_excel(writer, index=False)
            st.download_button("📥 Descargar Reporte Consolidado", output.getvalue(), "inventario_unificado.xlsx")

        else:
            st.error("⚠️ Asegúrate de que AMBOS archivos tengan: MATERIAL, DESCRIPCION, LOTE y TOTAL")
            
    except Exception as e:
        st.error(f"Error técnico: {e}")
