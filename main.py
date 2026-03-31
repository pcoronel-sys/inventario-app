import streamlit as st
import pandas as pd
import io

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Inventario Bagó | Alertas Pro", page_icon="🧪", layout="wide")

# --- IDENTIDAD VISUAL ---
MAGENTA_BAGO = "#C7006A" 

st.markdown(f"""
    <style>
    .main {{ background: #f8f9fa; }}
    [data-testid="stMetric"] {{
        background-color: white;
        border-radius: 15px;
        padding: 20px;
        border-left: 6px solid {MAGENTA_BAGO};
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }}
    .stDownloadButton button {{
        background: linear-gradient(90deg, {MAGENTA_BAGO} 0%, #A00055 100%) !important;
        color: white !important;
        border-radius: 10px !important;
        font-weight: bold !important;
        height: 3.5em !important;
        width: 100% !important;
    }}
    h1, h2, h3 {{ color: {MAGENTA_BAGO} !important; text-align: center; font-weight: 800; }}
    </style>
    """, unsafe_allow_html=True)

# --- NAVEGACIÓN ---
if 'modo' not in st.session_state:
    st.session_state.modo = None

def seleccionar_modo(modo):
    st.session_state.modo = modo

def borrar_todo():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# --- MENÚ PRINCIPAL ---
if st.session_state.modo is None:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.title("🧪 Sistema de Conciliación Bagó")
    st.markdown("### Seleccione el método de cruce:")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📦 CRUCE POR MATERIAL + LOTE"):
            seleccionar_modo("con_lote")
            st.rerun()
    with col2:
        if st.button("🔢 CRUCE SOLO POR MATERIAL"):
            seleccionar_modo("sin_lote")
            st.rerun()

# --- APLICACIÓN ---
else:
    modo_txt = "CON LOTE" if st.session_state.modo == "con_lote" else "SIN LOTE"
    st.title(f"🧪 Reporte de Conciliación {modo_txt}")
    
    if st.button("⬅️ Volver al Menú"):
        borrar_todo()

    st.divider()

    c1, c2 = st.columns(2)
    with c1:
        f1 = st.file_uploader("📂 Archivo BASE (Bagó)", type=['xlsx'], key="f1")
    with c2:
        f2 = st.file_uploader("📂 Archivo COMPARATIVO (FP/QX)", type=['xlsx'], key="f2")

    if f1 and f2:
        try:
            df1 = pd.read_excel(f1)
            df2 = pd.read_excel(f2)
            
            def limpiar_y_agrupar(df):
                df.columns = df.columns.astype(str).str.strip().str.upper()
                df['MATERIAL'] = df['MATERIAL'].astype(str).str.strip().str.upper()
                agg = {'TOTAL': 'sum'}
                if 'DESCRIPCION' in df.columns:
                    df['DESCRIPCION'] = df['DESCRIPCION'].astype(str).str.strip().str.upper()
                    agg['DESCRIPCION'] = 'first'
                
                if st.session_state.modo == "con_lote":
                    if 'LOTE' not in df.columns: df['LOTE'] = 'SIN LOTE'
                    df['LOTE'] = df['LOTE'].fillna('SIN LOTE').astype(str).str.strip().str.upper()
                    return df.groupby(['MATERIAL', 'LOTE']).agg(agg).reset_index()
                else:
                    return df.groupby(['MATERIAL']).agg(agg).reset_index()

            d1 = limpiar_y_agrupar(df1)
            d2 = limpiar_y_agrupar(df2)

            # --- CRUCE DOBLE PARA EL DASHBOARD ---
            keys = ['MATERIAL', 'LOTE'] if st.session_state.modo == "con_lote" else ['MATERIAL']
            
            # 1. El reporte que tú quieres (Base Bagó)
            res_base = pd.merge(d1, d2, on=keys, how='left', suffixes=('_BAGO', '_FPQX')).fillna(0)
            
            # 2. Buscamos códigos que están en FP/QX pero NO en Bagó (Los "Desconocidos")
            codigos_bago = d1[keys]
            extra_df = pd.merge(d2, d1, on=keys, how='left', indicator=True)
            solo_en_fpqx = extra_df[extra_df['_merge'] == 'left_only'].drop(columns=['_merge'])

            # --- DASHBOARD DE ALERTAS ---
            st.markdown("### 📊 Dashboard de Consistencia")
            m1, m2, m3, m4 = st.columns(4)
            
            diferencias = len(res_base[res_base['TOTAL_BAGO'] != res_base['TOTAL_FPQX']])
            codigos_faltantes = len(solo_en_fpqx)

            m1.metric("Items en Bagó", len(d1))
            m2.metric("Diferencias Stock", diferencias)
            m3.metric("Faltantes en Bagó", codigos_faltantes, delta="⚠️ DESCONOCIDOS", delta_color="inverse" if codigos_faltantes > 0 else "normal")
            m4.metric("Precisión Catálogo", f"{round((1 - (codigos_faltantes/len(d1)))*100,1)}%" if len(d1)>0 else "0%")

            if codigos_faltantes > 0:
                st.error(f"🚨 **ALERTA:** Se detectaron {codigos_faltantes} códigos en el archivo FP/QX que NO existen en tu archivo de Bagó.")

            st.divider()

            # --- FILTROS ---
            st.markdown("#### 🔍 Filtros de Reporte")
            col_busq, col_ver = st.columns([2, 1])
            with col_busq:
                busqueda = st.text_input("Buscar por código o descripción:")
            with col_ver:
                opcion_vista = st.selectbox("Ver en tabla:", ["Reporte Base (Bagó)", "Solo Diferencias", "Ver Códigos Desconocidos (Solo en FP/QX)"])

            # Lógica de Visualización
            if opcion_vista == "Reporte Base (Bagó)":
                res_final = res_base.copy()
            elif opcion_vista == "Solo Diferencias":
                res_final = res_base[res_base['TOTAL_BAGO'] != res_base['TOTAL_FPQX']]
            else:
                res_final = solo_en_fpqx.copy()

            if busqueda:
                res_final = res_final[res_final.apply(lambda row: row.astype(str).str.contains(busqueda, case=False).any(), axis=1)]

            # Formatear columnas
            if not res_final.empty:
                res_final['DIFERENCIA'] = res_final.get('TOTAL_BAGO', 0) - res_final.get('TOTAL_FPQX', 0)
                
                # Renombrar para que se vea bien
                res_final = res_final.rename(columns={'TOTAL_BAGO': 'TOTAL BAGO', 'TOTAL_FPQX': 'TOTAL FP/QX'})
                
                # Tabla
                st.dataframe(
                    res_final.style.highlight_between(left=-999999, right=-0.1, color='#ffdadb', subset=['DIFERENCIA'] if 'DIFERENCIA' in res_final.columns else [])
                                   .highlight_between(left=0.1, right=999999, color='#d4edda', subset=['DIFERENCIA'] if 'DIFERENCIA' in res_final.columns else []),
                    use_container_width=True
                )

                # Exportar
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    res_final.to_excel(writer, index=False)
                st.download_button("📥 DESCARGAR ESTA VISTA", data=output.getvalue(), file_name=f"Reporte_{opcion_vista}.xlsx")
            else:
                st.info("No hay datos para mostrar con este filtro.")

        except Exception as e:
            st.error(f"Error: {e}")
