import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="App Inventario", page_icon="📦", layout="wide")

st.title("📦 Comparador de Inventarios")
st.write("Sube tus archivos Excel para comparar las columnas 'MATERIAL' y 'TOTAL'.")

col1, col2 = st.columns(2)
with col1:
    f1 = st.file_uploader("Archivo ANTERIOR", type=['xlsx'])
with col2:
    f2 = st.file_uploader("Archivo NUEVO", type=['xlsx'])

if f1 and f2:
    df1 = pd.read_excel(f1)
    df2 = pd.read_excel(f2)
    
    # Limpiar nombres de columnas a Mayúsculas
    df1.columns = df1.columns.astype(str).str.strip().str.upper()
    df2.columns = df2.columns.astype(str).str.strip().str.upper()

    if 'MATERIAL' in df1.columns and 'TOTAL' in df2.columns:
        res = pd.merge(df1[['MATERIAL', 'TOTAL']], df2[['MATERIAL', 'TOTAL']], 
                       on='MATERIAL', how='outer', suffixes=('_ANT', '_NUEVO')).fillna(0)
        res['DIFERENCIA'] = res['TOTAL_NUEVO'] - res['TOTAL_ANT']

        st.subheader("📊 Resultados")
        st.dataframe(res.style.highlight_between(left=-9999, right=-0.01, color='#ffcccc')
                              .highlight_between(left=0.01, right=9999, color='#ccffcc'))

        # Botón de descarga
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            res.to_excel(writer, index=False)
        st.download_button("📥 Descargar Excel Comparativo", output.getvalue(), "resultado.xlsx")
    else:
        st.error("Asegúrate de que ambos archivos tengan las columnas 'MATERIAL' y 'TOTAL'")
