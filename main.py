import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Inventario Material + Lote", page_icon="🎯", layout="wide")

st.title("🎯 Comparador Preciso: Material + Lote")
st.markdown("""
En esta versión, la **DESCRIPCIÓN** es solo informativa. La comparación real se hace **únicamente** cruzando el código de **MATERIAL** y el **LOTE**.
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

        columnas_necesarias = ['MATERIAL', 'LOTE', 'TOTAL']
        # La DESCRIPCION es opcional para el cálculo, pero la buscamos para mostrarla
        tiene_desc = 'DESCRIPCION' in df1.columns and 'DESCRIPCION' in df2.columns

        if all(col in df1.columns for col in columnas_necesarias) and \
           all(col in df2.columns for col in columnas_necesarias):
            
            # 2. Preparar los datos
            def preparar_datos(df):
                df['MATERIAL'] = df['MATERIAL'].astype(str).str.strip()
                df['LOTE'] = df['LOTE'].astype(str).str.strip()
                
                # Agrupamos solo por MATERIAL y LOTE para sumar el TOTAL
                # Usamos .agg para quedarnos con la primera DESCRIPCION que aparezca (si existe)
                agg_dict = {'TOTAL': 'sum'}
                if tiene_desc:
                    df['DESCRIPCION'] = df['DESCRIPCION'].astype(str).str.strip()
                    agg_dict['DESCRIPCION'] = 'first'
                
                return df.groupby(['MATERIAL', 'LOTE']).agg(agg_dict).reset_index()

            df1_final = preparar_datos(df1)
            df2_final = preparar_datos(df2)

            # 3. COMPARACIÓN (Merge solo por MATERIAL y LOTE)
            res = pd.merge(
                df1_final, 
                df2_final, 
                on=['MATERIAL', 'LOTE'], 
                how='outer', 
                suffixes=('_ANT', '_NUEVO')
            ).fillna(0)
            
            # 4. Cálculo de Diferencia
            res['DIFERENCIA'] = res['TOTAL_NUEVO'] - res['TOTAL_ANT']

            # Limpiar las descripciones duplicadas (unificar en una sola columna)
            if tiene_desc:
                res['DESCRIPCION'] = res['DESCRIPCION_NUEVO'].replace(0, '')
                res.loc[res['DESCRIPCION'] == '', 'DESCRIPCION'] = res['DESCRIPCION_ANT']
                # Quitamos las columnas temporales de descripción
                res = res.drop(columns=['DESCRIPCION_ANT', 'DESCRIPCION_NUEVO'])

            # --- INTERFAZ ---
            st.divider()
            c1, c2, c3 = st.columns(3)
            c1.metric("Items Totales", len(res))
            c2.metric("Sobrantes", len(res[res['DIFERENCIA'] > 0]))
            c3.metric("Faltantes", len(res[res['DIFERENCIA'] < 0]))

            # Ordenar columnas para que se vea bien
            cols_ordenadas = ['MATERIAL', 'LOTE']
            if tiene_desc: cols_ordenadas.append('DESCRIPCION')
            cols_ordenadas.extend(['TOTAL_ANT', 'TOTAL_NUEVO', 'DIFERENCIA'])
            
            res = res[cols_ordenadas]

            # Tabla
            st.subheader("📋 Reporte Final")
            st.dataframe(
                res.style.highlight_between(left=-99999, right=-0.1, color='#ffcccc', subset=['DIFERENCIA'])
                          .highlight_between(left=0.1, right=99999, color='#ccffcc', subset=['DIFERENCIA']),
                use_container_width=True
            )

            # Descarga
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                res.to_excel(writer, index=False)
            st.download_button("📥 Descargar Reporte Excel", output.getvalue(), "comparativo_material_lote.xlsx")

        else:
            st.error("⚠️ Error: Faltan las columnas MATERIAL, LOTE o TOTAL en tus archivos.")
            
    except Exception as e:
        st.error(f"Error técnico: {e}")
