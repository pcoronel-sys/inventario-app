import streamlit as st
import pandas as pd
import io

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Bagó | Intel-Stock", page_icon="🧪", layout="wide")

# --- IDENTIDAD VISUAL Y CSS DINÁMICO ---
MAGENTA_BAGO = "#C7006A" 
MAGENTA_OSCURO = "#8A004A"

st.markdown(f"""
    <style>
    /* Fondo General */
    .main {{ background: #f4f7f9; }}
    
    /* Diseño de las Tarjetas del Menú Principal */
    .menu-card {{
        background: white;
        padding: 40px;
        border-radius: 20px;
        border-bottom: 8px solid {MAGENTA_BAGO};
        text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
        cursor: pointer;
        margin-bottom: 20px;
    }}
    .menu-card:hover {{
        transform: translateY(-10px);
        box-shadow: 0 15px 35px rgba(199, 0, 106, 0.15);
        background: linear-gradient(180deg, #ffffff 0%, #fff0f6 100%);
    }}
    
    /* Botones de Acción (Descarga y Volver) */
    .stDownloadButton button {{
        background: linear-gradient(90deg, {MAGENTA_BAGO} 0%, {MAGENTA_OSCURO} 100%) !important;
        color: white !important;
        border-radius: 12px !important;
        font-weight: bold !important;
        height: 3.8em !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(199, 0, 106, 0.3) !important;
    }}
    
    /* Títulos y Métricas */
    [data-testid="stMetric"] {{
        background: white;
        border-radius: 15px;
        padding: 15px;
        border-left: 5px solid {MAGENTA_BAGO};
    }}
    
    h1 {{ color: {MAGENTA_BAGO} !important; font-weight: 800; text-align: center; letter-spacing: -1px; }}
    h3 {{ color: #444 !important; text-align: center; font-weight: 400; }}
    
    /* Ocultar botones de Streamlit por defecto para los modos */
    .stButton button {{
        width: 100%;
        height: 120px;
        border-radius: 20px !important;
        font-size: 1.2em !important;
        font-weight: bold !important;
    }}
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

# --- PANTALLA 1: MENÚ PRINCIPAL DINÁMICO ---
if st.session_state.modo is None:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h1>🧪 Laboratorios Bagó</h1>", unsafe_allow_html=True)
    st.markdown("<h3>Sistema Inteligente de Conciliación de Inventarios</h3>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col1, col_gap, col2 = st.columns([1, 0.1, 1])
    
    with col1:
        st.markdown('<div class="menu-card">', unsafe_allow_html=True)
        st.write("### 📦 Modo Lote")
        st.write("Análisis detallado por código y número de lote. Ideal para trazabilidad.")
        if st.button("INICIAR CRUCE CON LOTE", key="btn_lote"):
            seleccionar_modo("con_lote")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
            
    with col2:
        st.markdown('<div class="menu-card">', unsafe_allow_html=True)
        st.write("### 🔢 Modo Material")
        st.write("Suma total por código de producto. Ideal para inventarios rápidos.")
        if st.button("INICIAR CRUCE SIN LOTE", key="btn_sin_lote"):
            seleccionar_modo("sin_lote")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- PANTALLA 2: APLICACIÓN DE CONCILIACIÓN ---
else:
    # Encabezado Compacto
    c_head1, c_head2 = st.columns([4, 1])
    with c_head1:
        modo_txt = "Detallado (Lote)" if st.session_state.modo == "con_lote" else "General (Material)"
        st.markdown(f"<h2 style='text-align: left; color:{MAGENTA_BAGO}'>Conciliación: {modo_txt}</h2>", unsafe_allow_html=True)
    with c_head2:
        if st.button("🔄 Volver al Menú"):
            borrar_todo()

    st.divider()

    # Carga de archivos en tarjetas
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        st.markdown("##### 📄 Archivo BASE (Bagó)")
        f1 = st.file_uploader("Subir Excel principal", type=['xlsx'], key="f1", label_visibility="collapsed")
    with col_f2:
        st.markdown("##### 📄 Archivo COMPARAR (FP/QX)")
        f2 = st.file_uploader("Subir Excel comparativo", type=['xlsx'], key="f2", label_visibility="collapsed")

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

            # Lógica de Cruce
            keys = ['MATERIAL', 'LOTE'] if st.session_state.modo == "con_lote" else ['MATERIAL']
            res_base = pd.merge(d1, d2, on=keys, how='left', suffixes=('_BAGO', '_FPQX')).fillna(0)
            
            # Detectar Desconocidos (Solo en FP/QX)
            extra_df = pd.merge(d2, d1, on=keys, how='left', indicator=True)
            solo_en_fpqx = extra_df[extra_df['_merge'] == 'left_only'].drop(columns=['_merge'])

            # --- DASHBOARD DINÁMICO ---
            m1, m2, m3, m4 = st.columns(4)
            diferencias = len(res_base[res_base['TOTAL_BAGO'] != res_base['TOTAL_FPQX']])
            codigos_extra = len(solo_en_fpqx)

            m1.metric("Items Bagó", len(d1))
            m2.metric("Discrepancias", diferencias, delta=f"{diferencias} filas" if diferencias > 0 else "OK", delta_color="inverse")
            m3.metric("Faltan en Maestro", codigos_extra, delta="ALERT" if codigos_extra > 0 else "Limpios", delta_color="inverse")
            m4.metric("Consistencia", f"{round((1 - (codigos_extra/len(d1)))*100,1)}%" if len(d1)>0 else "0%")

            st.divider()

            # --- FILTROS Y TABLA ---
            c_filt1, c_filt2 = st.columns([2, 1])
            with c_filt1:
                busqueda = st.text_input("🔍 Buscar Material o Descripción...")
            with c_filt2:
                vista = st.selectbox("🎯 Filtrar Vista:", ["Reporte Unificado", "Solo Diferencias", "Ver Desconocidos (Solo en FP/QX)"])

            if vista == "Reporte Unificado":
                res_final = res_base.copy()
            elif vista == "Solo Diferencias":
                res_final = res_base[res_base['TOTAL_BAGO'] != res_base['TOTAL_FPQX']]
            else:
                res_final = solo_en_fpqx.copy()

            if busqueda:
                res_final = res_final[res_final.apply(lambda row: row.astype(str).str.contains(busqueda, case=False).any(), axis=1)]

            if not res_final.empty:
                res_final['DIFERENCIA'] = res_final.get('TOTAL_BAGO', 0) - res_final.get('TOTAL_FPQX', 0)
                
                # Columnas finales
                cols_v = ['MATERIAL']
                if 'LOTE' in res_final.columns: cols_v.append('LOTE')
                if 'DESCRIPCION_BAGO' in res_final.columns:
                    res_final = res_final.rename(columns={'DESCRIPCION_BAGO': 'DESCRIPCION'})
                    cols_v.append('DESCRIPCION')
                cols_v += ['TOTAL_BAGO', 'TOTAL_FPQX', 'DIFERENCIA']
                
                st.dataframe(
                    res_final[cols_v].style.highlight_between(left=-999999, right=-0.1, color='#ffdadb', subset=['DIFERENCIA'])
                                           .highlight_between(left=0.1, right=999999, color='#d4edda', subset=['DIFERENCIA']),
                    use_container_width=True
                )

                # Exportar
                st.divider()
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    res_final[cols_v].to_excel(writer, index=False)
                st.download_button("📥 DESCARGAR REPORTE EXCEL", data=output.getvalue(), file_name=f"Bagó_Reporte_{vista}.xlsx")
            else:
                st.warning("No hay datos para mostrar con los filtros seleccionados.")

        except Exception as e:
            st.error(f"Falla crítica: {e}")
