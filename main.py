import streamlit as st
import pandas as pd
import io

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Bagó | Intel-Stock", page_icon="🧪", layout="wide")

# --- IDENTIDAD VISUAL Y CSS DINÁMICO (EFECTO HOVER AVANZADO) ---
MAGENTA_BAGO = "#C7006A" 
MAGENTA_OSCURO = "#8A004A"

st.markdown(f"""
    <style>
    /* Fondo General */
    .main {{ background: #f4f7f9; }}
    
    /* Contenedor de las Tarjetas */
    .menu-container {{
        display: flex;
        justify-content: center;
        gap: 30px;
        padding: 50px;
    }}

    /* Tarjeta de Menú con Animación */
    .menu-card {{
        background: white;
        padding: 40px;
        border-radius: 25px;
        border: 2px solid transparent;
        text-align: center;
        box-shadow: 0 10px 20px rgba(0,0,0,0.05);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        cursor: pointer;
        width: 100%;
    }}

    /* EFECTO CUANDO EL RATÓN ESTÁ ENCIMA */
    .menu-card:hover {{
        transform: translateY(-15px) scale(1.02);
        border-color: {MAGENTA_BAGO};
        box-shadow: 0 20px 40px rgba(199, 0, 106, 0.2);
        background: linear-gradient(180deg, #ffffff 0%, #fff5f9 100%);
    }}

    /* Estilo del texto dentro de la tarjeta al hacer hover */
    .menu-card:hover h3 {{
        color: {MAGENTA_BAGO} !important;
        transform: scale(1.1);
        transition: 0.3s;
    }}

    /* Botón de Selección que reacciona al movimiento */
    .stButton > button {{
        width: 100%;
        border-radius: 15px !important;
        font-weight: bold !important;
        height: 60px !important;
        transition: all 0.3s ease !important;
        background: #f8f9fa !important;
        color: #444 !important;
        border: 1px solid #ddd !important;
    }}

    /* Botón cambia a Magenta cuando el ratón entra a la tarjeta o al botón */
    .menu-card:hover .stButton > button, .stButton > button:hover {{
        background: {MAGENTA_BAGO} !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 5px 15px rgba(199, 0, 106, 0.3);
    }}

    /* Botón de Descarga Premium */
    .stDownloadButton button {{
        background: linear-gradient(90deg, {MAGENTA_BAGO} 0%, {MAGENTA_OSCURO} 100%) !important;
        color: white !important;
        border-radius: 12px !important;
        font-weight: bold !important;
        height: 3.8em !important;
        box-shadow: 0 4px 15px rgba(199, 0, 106, 0.3) !important;
    }}

    h1 {{ color: {MAGENTA_BAGO} !important; font-weight: 800; text-align: center; }}
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
    st.markdown("<h3 style='text-align:center; color:#666;'>Seleccione el método de trabajo</h3>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="menu-card">', unsafe_allow_html=True)
        st.markdown("<h3 style='margin-bottom:10px;'>📦 Modo Lote</h3>", unsafe_allow_html=True)
        st.write("Análisis quirúrgico por código y lote.")
        if st.button("CONFIGURAR LOTE", key="btn_lote"):
            seleccionar_modo("con_lote")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
            
    with col2:
        st.markdown('<div class="menu-card">', unsafe_allow_html=True)
        st.markdown("<h3 style='margin-bottom:10px;'>🔢 Modo Material</h3>", unsafe_allow_html=True)
        st.write("Cruce global por código de producto.")
        if st.button("CONFIGURAR MATERIAL", key="btn_sin_lote"):
            seleccionar_modo("sin_lote")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- PANTALLA 2: APLICACIÓN (EL RESTO DEL CÓDIGO SE MANTIENE IGUAL) ---
else:
    c_head1, c_head2 = st.columns([4, 1])
    with c_head1:
        modo_txt = "CON LOTE" if st.session_state.modo == "con_lote" else "SIN LOTE"
        st.markdown(f"<h2 style='text-align: left; color:{MAGENTA_BAGO}; margin:0;'>🧪 Reporte: {modo_txt}</h2>", unsafe_allow_html=True)
    with c_head2:
        if st.button("🔄 Volver al Menú"):
            borrar_todo()

    st.divider()

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        st.info("📂 Archivo BASE (Bagó)")
        f1 = st.file_uploader("Cargar", type=['xlsx'], key="f1", label_visibility="collapsed")
    with col_f2:
        st.info("📂 Archivo COMPARAR (FP/QX)")
        f2 = st.file_uploader("Cargar", type=['xlsx'], key="f2", label_visibility="collapsed")

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

            keys = ['MATERIAL', 'LOTE'] if st.session_state.modo == "con_lote" else ['MATERIAL']
            res_base = pd.merge(d1, d2, on=keys, how='left', suffixes=('_BAGO', '_FPQX')).fillna(0)
            
            extra_df = pd.merge(d2, d1, on=keys, how='left', indicator=True)
            solo_en_fpqx = extra_df[extra_df['_merge'] == 'left_only'].drop(columns=['_merge'])

            # --- DASHBOARD ---
            m1, m2, m3, m4 = st.columns(4)
            diferencias = len(res_base[res_base['TOTAL_BAGO'] != res_base['TOTAL_FPQX']])
            codigos_faltantes = len(solo_en_fpqx)

            m1.metric("Items en Bagó", len(d1))
            m2.metric("Discrepancias", diferencias, delta_color="inverse")
            m3.metric("Faltantes en Bagó", codigos_faltantes, delta="⚠️ EXTRA", delta_color="inverse" if codigos_faltantes > 0 else "normal")
            m4.metric("Precisión", f"{round((1 - (codigos_faltantes/len(d1)))*100,1)}%" if len(d1)>0 else "0%")

            st.divider()

            # --- FILTROS ---
            col_busq, col_ver = st.columns([2, 1])
            with col_busq:
                busqueda = st.text_input("🔍 Buscar Material o Descripción...")
            with col_ver:
                opcion_vista = st.selectbox("🎯 Vista:", ["Reporte Base (Bagó)", "Solo Diferencias", "Ver Desconocidos (Solo FP/QX)"])

            if opcion_vista == "Reporte Base (Bagó)":
                res_final = res_base.copy()
            elif opcion_vista == "Solo Diferencias":
                res_final = res_base[res_base['TOTAL_BAGO'] != res_base['TOTAL_FPQX']]
            else:
                res_final = solo_en_fpqx.copy()

            if busqueda:
                res_final = res_final[res_final.apply(lambda row: row.astype(str).str.contains(busqueda, case=False).any(), axis=1)]

            if not res_final.empty:
                if 'TOTAL_BAGO' not in res_final.columns: res_final['TOTAL_BAGO'] = 0
                if 'TOTAL_FPQX' not in res_final.columns: res_final['TOTAL_FPQX'] = 0
                res_final['DIFERENCIA'] = res_final['TOTAL_BAGO'] - res_final['TOTAL_FPQX']
                res_final = res_final.rename(columns={'TOTAL_BAGO': 'TOTAL BAGO', 'TOTAL_FPQX': 'TOTAL FP/QX'})
                
                st.dataframe(
                    res_final.style.highlight_between(left=-999999, right=-0.1, color='#ffdadb', subset=['DIFERENCIA'] if 'DIFERENCIA' in res_final.columns else [])
                                   .highlight_between(left=0.1, right=999999, color='#d4edda', subset=['DIFERENCIA'] if 'DIFERENCIA' in res_final.columns else []),
                    use_container_width=True
                )

                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    res_final.to_excel(writer, index=False)
                st.download_button("📥 DESCARGAR EXCEL", data=output.getvalue(), file_name=f"Bago_{opcion_vista}.xlsx")
            else:
                st.info("No hay datos para esta selección.")

        except Exception as e:
            st.error(f"Falla técnica: {e}")
