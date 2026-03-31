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
    .main {{ background: #f4f7f9; }}
    .menu-card {{
        background: white;
        padding: 40px;
        border-radius: 20px;
        border-bottom: 8px solid {MAGENTA_BAGO};
        text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }}
    .menu-card:hover {{
        transform: translateY(-10px);
        box-shadow: 0 15px 35px rgba(199, 0, 106, 0.15);
    }}
    .stDownloadButton button {{
        background: linear-gradient(90deg, {MAGENTA_BAGO} 0%, {MAGENTA_OSCURO} 100%) !important;
        color: white !important;
        border-radius: 12px !important;
        font-weight: bold !important;
        height: 3.8em !important;
        border: none !important;
    }}
    [data-testid="stMetric"] {{
        background: white;
        border-radius: 15px;
        padding: 15px;
        border-left: 5px solid {MAGENTA_BAGO};
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

# --- PANTALLA 1: MENÚ PRINCIPAL ---
if st.session_state.modo is None:
    st.markdown("<br><br><h1>🧪 Laboratorios Bagó</h1><h3>Sistema Inteligente de Conciliación</h3><br>", unsafe_allow_html=True)
    col1, _, col2 = st.columns([1, 0.1, 1])
    with col1:
        st.markdown('<div class="menu-card"><h3>📦 Modo Lote</h3><p>Análisis por código y lote.</p>', unsafe_allow_html=True)
        if st.button("INICIAR CRUCE CON LOTE"): seleccionar_modo("con_lote"); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="menu-card"><h3>🔢 Modo Material</h3><p>Suma total por código.</p>', unsafe_allow_html=True)
        if st.button("INICIAR CRUCE SIN LOTE"): seleccionar_modo("sin_lote"); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- PANTALLA 2: APLICACIÓN ---
else:
    c_head1, c_head2 = st.columns([4, 1])
    with c_head1:
        st.markdown(f"<h2 style='color:{MAGENTA_BAGO}'>Modo: {'Lote' if st.session_state.modo == 'con_lote' else 'Material'}</h2>", unsafe_allow_html=True)
    with c_head2:
        if st.button("🔄 Menú Principal"): borrar_todo()

    st.divider()
    col_f1, col_f2 = st.columns(2)
    with col_f1: f1 = st.file_uploader("📂 Archivo BASE (Bagó)", type=['xlsx'], key="f1")
    with col_f2: f2 = st.file_uploader("📂 Archivo COMPARAR (FP/QX)", type=['xlsx'], key="f2")

    if f1 and f2:
        try:
            df1 = pd.read_excel(f1)
            df2 = pd.read_excel(f2)
            
            def limpiar(df):
                df.columns = df.columns.astype(str).str.strip().str.upper()
                df['MATERIAL'] = df['MATERIAL'].astype(str).str.strip().str.upper()
                agg = {'TOTAL': 'sum'}
                if 'DESCRIPCION' in df.columns:
                    df['DESCRIPCION'] = df['DESCRIPCION'].astype(str).str.strip().str.upper()
                    agg['DESCRIPCION'] = 'first'
                if st.session_state.modo == "con_lote":
                    df['LOTE'] = df['LOTE'].fillna('SIN LOTE').astype(str).str.strip().upper() if 'LOTE' in df.columns else 'SIN LOTE'
                    return df.groupby(['MATERIAL', 'LOTE']).agg(agg).reset_index()
                return df.groupby(['MATERIAL']).agg(agg).reset_index()

            d1, d2 = limpiar(df1), limpiar(df2)
            keys = ['MATERIAL', 'LOTE'] if st.session_state.modo == "con_lote" else ['MATERIAL']
            
            # Cruce Base (Bagó manda)
            res_base = pd.merge(d1, d2, on=keys, how='left', suffixes=('_BAGO', '_FPQX')).fillna(0)
            
            # Detectar Desconocidos
            solo_en_fpqx = pd.merge(d2, d1, on=keys, how='left', indicator=True)
            solo_en_fpqx = solo_en_fpqx[solo_en_fpqx['_merge'] == 'left_only'].drop(columns=['_merge']).fillna(0)

            # Dashboard
            m1, m2, m3, m4 = st.columns(4)
            diffs = len(res_base[res_base['TOTAL_BAGO'] != res_base['TOTAL_FPQX']])
            extra = len(solo_en_fpqx)
            m1.metric("Items Bagó", len(d1))
            m2.metric("Discrepancias", diffs, delta_color="inverse")
            m3.metric("Faltan en Maestro", extra, delta="Alerta" if extra > 0 else "OK", delta_color="inverse")
            m4.metric("Consistencia", f"{round((1 - (extra/len(d1)))*100,1)}%" if len(d1)>0 else "0%")

            st.divider()
            c_bus, c_vis = st.columns([2, 1])
            with c_bus: busq = st.text_input("🔍 Buscar Material...")
            with c_vis: vista = st.selectbox("🎯 Ver:", ["Reporte Unificado", "Solo Diferencias", "Desconocidos (Solo FP/QX)"])

            # Selección de vista con corrección de columnas
            if vista == "Desconocidos (Solo FP/QX)":
                df_final = solo_en_fpqx.copy()
                if 'TOTAL' in df_final.columns: df_final = df_final.rename(columns={'TOTAL': 'TOTAL_FPQX'})
            else:
                df_final = res_base.copy()
                if vista == "Solo Diferencias":
                    df_final = df_final[df_final['TOTAL_BAGO'] != df_final['TOTAL_FPQX']]

            if busq:
                df_final = df_final[df_final.apply(lambda r: r.astype(str).str.contains(busq, case=False).any(), axis=1)]

            if not df_final.empty:
                # Asegurar que todas las columnas existan antes de calcular Diferencia
                if 'TOTAL_BAGO' not in df_final.columns: df_final['TOTAL_BAGO'] = 0
                if 'TOTAL_FPQX' not in df_final.columns: df_final['TOTAL_FPQX'] = 0
                
                df_final['DIFERENCIA'] = df_final['TOTAL_BAGO'] - df_final['TOTAL_FPQX']
                
                # Columnas finales seguras
                final_cols = ['MATERIAL']
                if 'LOTE' in df_final.columns: final_cols.append('LOTE')
                if 'DESCRIPCION' in df_final.columns: final_cols.append('DESCRIPCION')
                final_cols += ['TOTAL_BAGO', 'TOTAL_FPQX', 'DIFERENCIA']
                
                st.dataframe(df_final[final_cols].style.highlight_between(left=-999999, right=-0.1, color='#ffdadb', subset=['DIFERENCIA']), use_container_width=True)
                
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df_final[final_cols].to_excel(writer, index=False)
                st.download_button("📥 DESCARGAR EXCEL", data=output.getvalue(), file_name=f"Bago_{vista}.xlsx")
            else:
                st.warning("No hay registros para mostrar.")
        except Exception as e:
            st.error(f"Falla crítica: {e}")
