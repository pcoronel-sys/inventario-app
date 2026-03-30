import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Inventario por Lotes", page_icon="🏷️", layout="wide")

st.title("🏷️ Comparador de Inventario: Material + Lote")
st.markdown("""
Esta versión **concatena el Material con el Lote** para asegurar que la comparación sea exacta por cada partida.
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
        
        # 1. Normalizar nombres de columnas
        df1.columns = df1.columns.astype(str).str.strip().str.upper()
        df2.columns = df2.columns.astype(str).str.strip().str.upper()

        columnas_requeridas = ['MATERIAL', 'DESCRIPCION', 'LOTE', 'TOTAL']

        if all(col in df1.columns for col in columnas_requeridas) and \
           all(col in df2.columns for col in columnas_requeridas):
            
            # 2. Función para preparar los datos
            def preparar_df(df):
                # Asegurar que LOTE y MATERIAL sean strings para concatenar sin errores
                df['MATERIAL'] = df['MATERIAL'].astype(str).str.strip()
                df['LOTE'] = df['LOTE'].astype(str).str.strip()
                df['DESCRIPCION'] = df['DESCRIPCION'].astype(str).str.strip()
                
                # Agrupamos y sumamos por si hay filas repetidas del mismo Material+Lote
                return df.groupby(['MATERIAL', 'DESCRIPCION', 'LOTE'])['TOTAL'].sum().reset_index()

            df1_final = preparar_df(df1)
            df2_final = preparar_df(df2)

            # 3. COMPARACIÓN (Merge por la combinación de las 3 columnas)
            res = pd.merge(
                df1_final, 
                df2_final, 
                on=['MATERIAL', 'DESCRIPCION', 'LOTE'], 
                how='outer', 
                suffixes=('_ANT', '_NUEVO')
            ).fillna(0)
            
            # 4. Cálculo de Diferencia
            res['DIFERENCIA'] = res['TOTAL_NUEVO'] - res['TOTAL_ANT']

            # --- INTERFAZ DE RESULTADOS ---
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Combinaciones Únicas", len(res))
            col_b.metric("Entradas / Sobrantes", len(res[res['DIFERENCIA'] > 0]))
            col_c.metric("Salidas / Faltantes", len(res[res['DIFERENCIA'] < 0]))

            st.divider()

            # Buscador
            search = st.text_input("🔍 Buscar (Material, Lote o Descripción):")
            if search:
                mask = res.apply(lambda x: x.astype(str).str.contains(search, case=False).any(), axis=1)
                res_display = res[mask]
            else:
                res_display = res

            # Tabla con Estilo
            st.subheader("📋 Reporte de Inventario Concatenado")
            st.dataframe(
                res_display.style.highlight_between(left=-99999, right=-0.1, color='#ffcccc', subset=['DIFERENCIA'])
                                  .highlight_between(left=0.1, right=99999, color='#ccffcc', subset=['DIFERENCIA']),
                use_container_width=True
            )

            # Botón de descarga
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                res.to_excel(writer, index=False)
            st.download_button("📥 Descargar Reporte (Excel)", output.getvalue(), "comparativo_lotes.xlsx")

        else:
            st.error("⚠️ Verifica que ambos archivos tengan las columnas: MATERIAL, DESCRIPCION, LOTE y TOTAL")
            
    except Exception as e:
        st.error(f"Error al procesar los archivos: {e}")
