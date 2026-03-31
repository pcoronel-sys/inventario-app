import streamlit as st
import pandas as pd
import io

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Inventario | Laboratorios Bagó", page_icon="🧪", layout="wide")

# --- VARIABLES DE MARCA ---
MAGENTA_BAGO = "#C7006A" 
LOGO_URL = "https://www.bago.com.ar/wp-content/themes/bago/img/logo-bago.png" # URL ejemplo del logo

# --- ESTILO CSS AVANZADO ---
st.markdown(f"""
    <style>
    .main {{
        background-color: #f0f2f6;
    }}
    .stMetric {{
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border-top: 4px solid {MAGENTA_BAGO};
    }}
    [data-testid="stSidebar"] {{
        background-color: #ffffff;
        border-right: 1px solid #e0e0e0;
    }}
    div.stButton > button:first-child {{
        background-color: {MAGENTA_BAGO};
        color: white;
        border-radius: 10px;
        height: 3.5em;
        font-weight: bold;
        border: none;
        box-shadow: 0 4px 15px rgba(199, 0, 106, 0.3);
    }}
    h1 {{
        color: {MAGENTA_BAGO};
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    # Intentamos cargar el logo, si falla ponemos el nombre en texto
    try:
        st.image(LOGO_URL, width=200)
    except:
        st.markdown(f"# **Bagó**")
    
    st.divider()
    st.markdown("### 📥 Carga de Archivos")
    f1 = st.file_uploader("Inventario ANTERIOR", type=['xlsx'])
    f2 = st.file_uploader("Inventario NUEVO", type=['xlsx'])
    st.divider()
    st.info("Desarrollado para Control de Calidad y Logística.")

# --- CUERPO PRINCIPAL ---
st.title("🧪 Conciliador de Inventarios")
st.markdown("### Comparación por **Material + Lote**")

if f1 and f2:
    try:
        df1 = pd.read_excel(f1)
        df2 = pd.read_excel(f2)
        
        # Limpieza de columnas
        df1.columns = df1.columns.astype(str).str.strip().str.upper()
        df2.columns = df2.columns.astype(str).str.strip().str.upper()

        columnas_req = ['MATERIAL', 'LOTE', 'TOTAL']
        tiene_desc = 'DESCRIPCION' in df1.columns and 'DESCRIPCION' in df2.columns

        if all(col in df1.columns for col in columnas_req) and all(col in df2.columns for col in columnas_req):
            
            # Procesamiento de datos (Ignorando descripción en la suma)
            def procesar(df):
                df['MATERIAL'] = df['MATERIAL'].astype(str).str.strip()
                df['LOTE'] = df['LOTE'].astype(str).str.strip()
                agg = {'TOTAL': 'sum'}
                if tiene_desc: agg['DESCRIPCION'] = 'first'
                return df.groupby(['MATERIAL', 'LOTE']).agg(agg).reset_index()

            d1 = procesar(df1)
            d2 = procesar(df2)

            res = pd.merge(d1, d2, on=['MATERIAL', 'LOTE'], how='outer', suffixes=('_ANT', '_NUEVO')).fillna(0)
            res['DIFERENCIA'] = res['TOTAL_NUEVO'] - res['TOTAL_ANT']

            if tiene_desc:
                res['DESCRIPCION'] = res['DESCRIPCION_NUEVO'].replace(0, '')
                res.loc[res['DESCRIPCION'] == '', 'DESCRIPCION'] = res['DESCRIPCION_ANT']
                res = res.drop(columns=['DESCRIPCION_ANT', 'DESCRIPCION_NUEVO'])

            # --- PANEL DE CONTROL ---
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Items Totales", len(res))
            m2.metric("Sobrantes", len(res[res['DIFERENCIA'] > 0]), delta=int(len(res[res['DIFERENCIA'] > 0])))
            m3.metric("Faltantes", len(res[res['DIFERENCIA'] < 0]), delta=-int(len(res[res['DIFERENCIA'] < 0])), delta_color="inverse")
            m4.metric("Precisión", f"{round((len(res[res['DIFERENCIA'] == 0])/len(res))*100, 1)}%")

            st.divider()

            # Tabla Dinámica
            st.markdown("#### 📋 Detalle de Diferencias Encontradas")
            
            # Reordenar para que se vea bien
            cols = ['MATERIAL', 'LOTE']
            if tiene_desc: cols.append('DESCRIPCION')
            cols += ['TOTAL_ANT', 'TOTAL_NUEVO', 'DIFERENCIA']
            res = res[cols]

            st.dataframe(
                res.style.highlight_between(left=-999999, right=-0.1, color='#ffdadb', subset=['DIFERENCIA'])
                          .highlight_between(left=0.1, right=999999, color='#d4edda', subset=['DIFERENCIA']),
                use_container_width=True
            )

            # Descarga
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                res.to_excel(writer, index=False)
            
            st.download_button(
                label="📥 EXPORTAR REPORTE OFICIAL A EXCEL",
                data=output.getvalue(),
                file_name="CONCILIACION_BAGO.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        else:
            st.error("⚠️ Error: Faltan columnas clave en los archivos.")
    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.warning("👈 Por favor, carga los archivos en el menú de la izquierda para comenzar.")
