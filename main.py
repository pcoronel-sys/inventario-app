import streamlit as st
import pandas as pd
import io
import plotly.express as px # Nueva librería para gráficos

st.set_page_config(page_title="App Inventario Pro", page_icon="🚀", layout="wide")

st.title("🚀 Panel de Control de Inventarios")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("Configuración")
    f1 = st.file_uploader("Archivo ANTERIOR", type=['xlsx'])
    f2 = st.file_uploader("Archivo NUEVO", type=['xlsx'])

if f1 and f2:
    df1 = pd.read_excel(f1)
    df2 = pd.read_excel(f2)
    
    df1.columns = df1.columns.astype(str).str.strip().str.upper()
    df2.columns = df2.columns.astype(str).str.strip().str.upper()

    if 'MATERIAL' in df1.columns and 'TOTAL' in df2.columns:
        res = pd.merge(df1[['MATERIAL', 'TOTAL']], df2[['MATERIAL', 'TOTAL']], 
                       on='MATERIAL', how='outer', suffixes=('_ANT', '_NUEVO')).fillna(0)
        res['DIFERENCIA'] = res['TOTAL_NUEVO'] - res['TOTAL_ANT']

        # --- MÉTRICAS Y GRÁFICOS ---
        col_m1, col_m2 = st.columns([1, 2])
        
        with col_m1:
            st.metric("Total Materiales", len(res))
            # Crear gráfico circular de cambios
            cambios = ["Sin Cambios" if d == 0 else "Con Diferencia" for d in res['DIFERENCIA']]
            fig = px.pie(names=cambios, title="Estado del Inventario", hole=0.4)
            st.plotly_chart(fig, use_container_width=True)

        with col_m2:
            st.subheader("🔍 Filtrar Resultados")
            filtro = st.selectbox("Ver:", ["Todos", "Solo con Diferencias", "Nuevos Ingresos", "Faltantes"])
            
            df_mostrar = res.copy()
            if filtro == "Solo con Diferencias":
                df_mostrar = res[res['DIFERENCIA'] != 0]
            elif filtro == "Nuevos Ingresos":
                df_mostrar = res[res['TOTAL_ANT'] == 0]
            elif filtro == "Faltantes":
                df_mostrar = res[res['TOTAL_NUEVO'] == 0]

            st.dataframe(df_mostrar.style.highlight_between(left=-9999, right=-0.01, color='#ffcccc')
                                  .highlight_between(left=0.01, right=9999, color='#ccffcc'), use_container_width=True)

        # Botón de descarga
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            res.to_excel(writer, index=False)
        st.download_button("📥 Descargar Reporte Completo", output.getvalue(), "inventario_pro.xlsx")
    else:
        st.error("Error: Revisa los nombres de las columnas.")
