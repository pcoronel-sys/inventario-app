import streamlit as st
import pandas as pd
import io

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Bagó | Sistema Unificado", page_icon="🧪", layout="wide")

# --- IDENTIDAD VISUAL ---
MAGENTA_BAGO = "#C7006A" 
MAGENTA_OSCURO = "#8A004A"

st.markdown(f"""
    <style>
    .main {{ background: #f4f7f9; }}
    
    /* BOTONES COMPACTOS PANTALLA PRINCIPAL */
    div.stButton > button {{
        background-color: white !important;
        color: #444 !important;
        border: 2px solid #eee !important;
        border-radius: 20px !important;
        height: 180px !important;
        width: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05) !important;
        transition: all 0.3s ease-in-out !important;
    }}
    div.stButton > button:hover {{
        background: linear-gradient(135deg, {MAGENTA_BAGO} 0%, {MAGENTA_OSCURO} 100%) !important;
        color: white !important;
        transform: translateY(-5px) !important;
        box-shadow: 0 12px 25px rgba(199, 0, 106, 0.25) !important;
    }}

    /* MÉTRICAS */
    [data-testid="stMetric"] {{
        background: white;
        border-radius: 15px;
        padding: 20px;
        border-left: 6px solid {MAGENTA_BAGO};
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }}

    /* BOTÓN DESCARGA */
    .stDownloadButton button {{
        background: linear-gradient(90deg, {MAGENTA_BAGO} 0%, {MAGENTA_OSCURO} 100%) !important;
        color: white !important;
        height: 3.5em !important;
        border-radius: 12px !important;
        font-weight: bold !important;
    }}
    h1 {{ color: {MAGENTA_BAGO} !important; font-weight: 800; text-align: center; }}
    </style>
    """, unsafe_allow_html=True)

if 'modo' not in st.session_state:
    st.session_state.modo = None

def seleccionar_modo(modo):
    st.session_state.modo = modo

def borrar_todo():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# --- PANTALLA 1: MENÚ ---
if st.session_state.modo is None:
    st.markdown("<br><br><h1>🧪 Laboratorios Bagó</h1><h3 style='text-align:center; color:#666;'>Seleccione el método de trabajo</h3><br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📦 MODO LOTE\n\nCruce por código y lote.", key="btn_lote"):
            seleccionar_modo("con_lote")
            st.rerun()
    with col2:
        if st.button("🔢 MODO MATERIAL\n\nCruce global por código.", key="btn_sin_lote"):
            seleccionar_modo("sin_lote")
            st.rerun()

# --- PANTALLA 2: REPORTE ---
else:
    c_head1, c_head2 = st.columns([4, 1])
    with c_head1:
        modo_txt = "CON LOTE" if st.session_state.modo == "con_lote" else "SIN LOTE"
        st.markdown(f"<h2 style='text-align: left; color:{MAGENTA_BAGO}; margin:0;'>🧪 Conciliación: {modo_txt}</h2>", unsafe_allow_html=True)
    with c_head2:
        if st.button("🔄 Volver al Menú"): borrar_todo()

    st.divider()

    c_f1, c_f2 = st.columns(2)
    with c_f1:
        st.info("📂 Archivo BASE (Bagó)")
        f1 = st.file_uploader("Subir", type=['xlsx'], key="f1", label_visibility="collapsed")
    with c_f2:
        st.info("📂 Archivo COMPARAR (FP/QX)")
        f2 = st.file_uploader("Subir", type=['xlsx'], key="f2", label_visibility="collapsed")

    if f1 and f2:
        try:
            df1, df2 = pd.read_excel(f1), pd.read_excel(f2)
            
            def limpiar(df):
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
                return df.groupby(['MATERIAL']).agg(agg).reset_index()

            d1, d2 = limpiar(df1), limpiar(df2)
            keys = ['MATERIAL', 'LOTE'] if st.session_state.modo == "con_lote" else ['MATERIAL']
            
            # --- CRUCE MAESTRO (OUTER JOIN) PARA EL CÁLCULO TOTAL ---
            res_maestro = pd.merge(d1, d2, on=keys, how='outer', suffixes=('_BAGO', '_FPQX')).fillna(0)
            res_maestro['DIFERENCIA'] = res_maestro['TOTAL_BAGO'] - res_maestro['TOTAL_FPQX']

            # --- 📊 DASHBOARD ---
            m1, m2, m3, m4 = st.columns(4)
            # Solo los que están en Bagó
            base_bago = res_maestro[res_maestro['TOTAL_BAGO'] > 0]
            # Solo los que NO están en Bagó pero están en FP/QX
            desconocidos = res_maestro[(res_maestro['TOTAL_BAGO'] == 0) & (res_maestro['TOTAL_FPQX'] > 0)]
            # Diferencias reales dentro de los que están en Bagó
            diff_stock = base_bago[base_bago['DIFERENCIA'] != 0]

            m1.metric("Items en Bagó", len(base_bago))
            m2.metric("Discrepancias Stock", len(diff_stock))
            m3.metric("Desconocidos (Extra)", len(desconocidos), delta="Alerta" if len(desconocidos) > 0 else "OK", delta_color="inverse")
            m4.metric("TOTAL DIFERENCIAS", len(diff_stock) + len(desconocidos))

            st.divider()

            # --- FILTROS ---
            col_busq, col_ver = st.columns([2, 1])
            with col_busq:
                busqueda = st.text_input("🔍 Buscar Material o Descripción...")
            with col_ver:
                opcion_vista = st.selectbox("🎯 Filtro de Auditoría:", 
                    ["Reporte Base (Bagó)", 
                     "Solo Diferencias de Stock", 
                     "Solo Desconocidos (FP/QX)", 
                     "TOTAL DIFERENCIAS (Stock + Desconocidos)"])

            # --- LÓGICA DE FILTRADO ---
            if opcion_vista == "Reporte Base (Bagó)":
                res_final = base_bago.copy()
            elif opcion_vista == "Solo Diferencias de Stock":
                res_final = diff_stock.copy()
            elif opcion_vista == "Solo Desconocidos (FP/QX)":
                res_final = desconocidos.copy()
            else: # TOTAL DIFERENCIAS
                res_final = res_maestro[res_maestro['DIFERENCIA'] != 0].copy()

            if busqueda:
                res_final = res_final[res_final.apply(lambda row: row.astype(str).str.contains(busqueda, case=False).any(), axis=1)]

            if not res_final.empty:
                res_final = res_final.rename(columns={'TOTAL_BAGO': 'TOTAL BAGO', 'TOTAL_FPQX': 'TOTAL FP/QX'})
                cols_v = ['MATERIAL']
                if 'LOTE' in res_final.columns: cols_v.append('LOTE')
                if 'DESCRIPCION_BAGO' in res_final.columns:
                    res_final = res_final.rename(columns={'DESCRIPCION_BAGO': 'DESCRIPCION'})
                    cols_v.append('DESCRIPCION')
                cols_v += ['TOTAL BAGO', 'TOTAL FP/QX', 'DIFERENCIA']
                
                st.dataframe(
                    res_final[cols_v].style.highlight_between(left=-999999, right=-0.1, color='#ffdadb', subset=['DIFERENCIA'])
                                           .highlight_between(left=0.1, right=999999, color='#d4edda', subset=['DIFERENCIA']),
                    use_container_width=True
                )

                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    res_final[cols_v].to_excel(writer, index=False)
                st.download_button("📥 DESCARGAR REPORTE FILTRADO", data=output.getvalue(), file_name=f"Reporte_Auditoria.xlsx")
            else:
                st.warning("Sin datos para este filtro.")

        except Exception as e:
            st.error(f"Falla técnica: {e}")
