import streamlit as st
import pandas as pd
import io
import plotly.express as px

st.set_page_config(page_title="App Inventario Pro", page_icon="🚀", layout="wide")

st.title("🚀 Panel de Control de Inventarios")
st.write("Sube tus archivos Excel para comparar MATERIAL, DESCRIPCION y TOTAL.")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("Configuración")
    f1 = st.file_uploader("Archivo ANTERIOR", type=['xlsx'])
    f2 = st.file_uploader("Archivo NUEVO", type=['xlsx'])

if f1 and f2:
    try:
        df1 = pd.read_excel(f1)
        df2 = pd.read_excel(f2)
        
        # Limpiar nombres de columnas: Quitar espacios y pasar a MAYÚSCULAS
        df1.columns = df1.columns.astype(str).str.strip().str.upper()
        df2.columns = df2.columns.astype(str).str.strip().str.upper()

        # Columnas que vamos a usar
        columnas_base = ['MATERIAL', 'DESCRIPCION', 'TOTAL']
        
        # Verificar que existan las columnas necesarias
        if all(col in df1.columns for col in columnas_base) and all(col in df2.columns for col in columnas_base):
            
            # Unión de datos usando MATERIAL y DESCRIPCION como claves
            # Así, si la descripción cambia o se mantiene, aparecerá correctamente
            res = pd.merge(
                df1[columnas_base], 
                df2[columnas_base], 
                on=['MATERIAL', 'DESCRIPCION'], 
                how='outer', 
                suffixes=('_ANT', '_NUEVO')
            ).fillna(0)
            
            res['DIFERENCIA'] = res['TOTAL_NUEVO'] - res['TOTAL_ANT']

            # --- MÉTRICAS Y GRÁFICOS ---
            col_m1, col_m2 = st.columns([1, 2])
            
            with col_m1:
                st.metric("Total de Ítems", len(res))
                # Crear gráfico circular de cambios
                res['ESTADO_GRAFICO'] = res['DIFERENCIA'].apply(lambda x: "Sin Cambios" if x == 0 else ("Aumento" if x > 0 else "Disminución"))
                fig = px.pie(res, names='ESTADO_GRAFICO', title="Estado del Inventario", hole=0.4,
                             color='ESTADO_GRAFICO', color_discrete_map={'Sin Cambios':'grey', 'Aumento':'green', 'Disminución':'red'})
                st.plotly_chart(fig, use_container_width=True)

            with col_m2:
                st.subheader("🔍 Tabla Comparativa")
                filtro = st.selectbox("Filtrar por:", ["Todos", "Solo con Diferencias", "Nuevos Ingresos (Stock 0 antes)", "Agotados (Stock 0 ahora)"])
                
                df_mostrar = res.copy()
                if filtro == "Solo con Diferencias":
                    df_mostrar = res[res['DIFERENCIA'] != 0]
                elif filtro == "Nuevos Ingresos (Stock 0 antes)":
                    df_mostrar = res[res['TOTAL_ANT'] == 0]
                elif filtro == "Agotados (Stock 0 ahora)":
                    df_mostrar = res[res['TOTAL_NUEVO'] == 0]

                # Aplicar colores a la columna DIFERENCIA
                st.dataframe(
                    df_mostrar.style.highlight_between(left=-999999, right=-0.01, color='#ffcccc', subset=['DIFERENCIA'])
                                  .highlight_between(left=0.01, right=999999, color='#ccffcc', subset=['DIFERENCIA']),
                    use_container_width=True
                )

            # Botón de descarga en Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                res.drop(columns=['ESTADO_GRAFICO']).to_excel(writer, index=False)
            st.download_button("📥 Descargar Reporte Completo (Excel)", output.getvalue(), "reporte_inventario_descripcion.xlsx")
            
        else:
            columnas_faltantes1 = [c for c in columnas_base if c not in df1.columns]
            columnas_faltantes2 = [c for c in columnas_base if c not in df2.columns]
            if columnas_faltantes1: st.error(f"Faltan columnas en Archivo Anterior: {columnas_faltantes1}")
            if columnas_faltantes2: st.error(f"Faltan columnas en Archivo Nuevo: {columnas_faltantes2}")
            
    except Exception as e:
        st.error(f"Ocurrió un error inesperado: {e}")
