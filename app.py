import streamlit as st
import pandas as pd
from datetime import datetime
import math

# ==========================================
# 1. CONFIGURACIÓN VISUAL (Tamaño y Estilo)
# ==========================================
st.set_page_config(layout="wide", page_title="IBM - Lacostw41")

# Estilo para que se vea profesional
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. CARGA Y PROCESAMIENTO DE DATOS
# ==========================================
@st.cache_data
def load_all_data():
    # Cargamos todos tus archivos CSV
    df_c = pd.read_csv('countries.csv')
    df_o = pd.read_csv('offering.csv')
    df_r = pd.read_csv('risk.csv')
    df_s = pd.read_csv('slc.csv')
    df_mcbr = pd.read_csv('mcbr.csv')
    df_lband = pd.read_csv('lband.csv')
    df_lplat = pd.read_csv('lplat.csv')
    return df_c, df_o, df_r, df_s, df_mcbr, df_lband, df_lplat

df_countries, df_offering, df_risk, df_slc, df_mcbr, df_lband, df_lplat = load_all_data()

# Limpieza rápida de ER (Exchange Rate) de countries.csv
# El ER está en la fila 1 (index 1) y los países empiezan en la columna 2
paises_lista = df_countries.columns[2:].tolist()

def get_er(pais_sel):
    try:
        val = df_countries.loc[1, pais_sel]
        return float(str(val).replace(',', ''))
    except:
        return 1.0

# ==========================================
# 3. BARRA LATERAL (INPUTS GENERALES)
# ==========================================
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/5/51/IBM_logo.svg", width=100)
    st.header("Configuración General")
    
    # --- CAMPOS DE ENTRADA ---
    id_cotiz = st.text_input("ID Cotización", "COT-001")
    pais = st.selectbox("País (Country)", paises_lista)
    moneda = st.radio("Moneda (Currency)", ["USD", "Local"])
    
    # Lógica de Exchange Rate
    er_actual = get_er(pais)
    if pais == "Ecuador": er_actual = 1.0 # Ecuador usa USD
    st.info(f"Exchange Rate aplicado: {er_actual}")

    qa_risk = st.selectbox("QA Risk", df_risk['Risk'])
    # Traemos el valor de contingencia
    cont_str = df_risk[df_risk['Risk'] == qa_risk]['Contingency'].values[0]
    contingencia = float(cont_str.strip('%')) / 100

    st.markdown("---")
    customer = st.text_input("Customer Name")
    quote_date = st.date_input("Quote Date", datetime.now())

# ==========================================
# 4. CUERPO PRINCIPAL (TABS)
# ==========================================
tab1, tab2 = st.tabs(["🛠 TAB 1: Servicios", "📊 TAB 2: Labor (Manage)"])

# --- TAB 1: SERVICIOS ---
with tab1:
    st.subheader("Entrada de Datos de Servicio")
    # [1, 1, 1, 2] crea 3 columnas delgadas y una doble de espacio vacío
    col1, col2, col3, col_espacio = st.columns([1, 1, 1, 2]) 
    
    with col1:
        offering_sel = st.selectbox("Offering", df_offering['Offering'])
        qty = st.number_input("Cantidad (QTY)", min_value=1, value=1)
        # El costo unitario debajo de QTY para ahorrar espacio
        u_cost_usd = st.number_input("Unit Cost USD", min_value=0.0, format="%.2f")
    
    with col2:
        s_start = st.date_input("Service Start", datetime.now())
        s_end = st.date_input("Service End", datetime.now())
        u_cost_local = st.number_input("Unit Cost Local", min_value=0.0, format="%.2f")

    with col3:
        slc_options = df_slc[df_slc['Scope'] == 'only Brazil']['SLC'] if pais == "Brazil" else df_slc[df_slc['Scope'].isna()]['SLC']
        slc_sel = st.selectbox("SLC", slc_options)
        
        # Cálculo de Duración visible
        duration = (s_end.year - s_start.year) * 12 + (s_end.month - s_start.month)
        if duration <= 0: duration = 1
        st.info(f"Duración: {duration} meses")

    # --- Operación Matemática ---
    uplf = df_slc[df_slc['SLC'] == slc_sel]['UPLF'].values[0]
    base_cost = (u_cost_usd + (u_cost_local / er_actual if er_actual != 0 else 0))
    total_service = (base_cost * duration) * qty * uplf
    display_cost = total_service * er_actual if moneda == "Local" else total_service

    st.markdown("---")
    st.metric(f"Total Service Cost ({moneda})", f"{display_cost:,.2f}")
    
# --- TAB 2: LABOR ---
with tab2:
    st.subheader("Cálculos de Labor / Manage")
    # Misma proporción para mantener simetría
    col_l1, col_l2, col_l3, col_espacio_l = st.columns([1, 1, 1, 2])
    
    with col_l1:
        tipo_mcbr = st.selectbox("MachCat/BandRate", df_mcbr['MCBR'])
        mcrr_list = df_lplat['Plat'].unique() if "Machine" in tipo_mcbr else df_lband['Def'].unique()
        col_busqueda = 'Plat' if "Machine" in tipo_mcbr else 'Def'
        df_ref = df_lplat if "Machine" in tipo_mcbr else df_lband
        
        mcrr_sel = st.selectbox("Seleccione MC/RR", mcrr_list)
        
    with col_l2:
        # Búsqueda y Limpieza
        try:
            valor_raw = df_ref[df_ref[col_busqueda] == mcrr_sel][pais].values[0]
            m_cost = float(str(valor_raw).replace(',', '').replace('"', '').strip()) if not pd.isna(valor_raw) else 0.0
        except:
            m_cost = 0.0
            
        st.write(f"Costo Base: **{m_cost:,.2f}**")
        horas = st.number_input("Horas", value=1, min_value=1)

    with col_l3:
        m_start = st.date_input("Manage Start", s_start)
        m_end = st.date_input("Manage End", s_end)
        
    # --- Operación Matemática ---
    dur_manage = (m_end.year - m_start.year) * 12 + (m_end.month - m_start.month)
    if dur_manage <= 0: dur_manage = 1
    
    total_manage_base = (m_cost * horas * dur_manage)
    display_manage = total_manage_base if moneda == "Local" else (total_manage_base / er_actual if er_actual != 0 else total_manage_base)

    st.markdown("---")
    st.metric(f"Total Manage Cost ({moneda})", f"{display_manage:,.2f}")
    
# TOTAL GLOBAL (Al final de los tabs)
st.markdown("---")
total_final_quote = display_cost + display_manage
st.header(f"Total Final Cotización: {total_final_quote:,.2f} {moneda}")

# ==========================================
# 7. TOTAL FINAL (FOOTER)
# ==========================================
st.markdown("---")
total_final = display_cost + display_manage
st.header(f"Total Quote Cost: {total_final:,.2f} {moneda}")
