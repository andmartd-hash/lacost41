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
    col_a, col_b = st.columns(6)
    
    with col_a:
        st.subheader("Configuración de Servicio")
        offering_sel = st.selectbox("Offering", df_offering['Offering'])
        l40 = df_offering[df_offering['Offering'] == offering_sel]['L40'].values[0]
        st.caption(f"L40: {l40}")
        
        qty = st.number_input("Cantidad (QTY)", min_value=1, value=1)
        
        # Filtrado de SLC (Si es Brasil, mostrar específicos)
        if pais == "Brazil":
            slc_options = df_slc[df_slc['Scope'] == 'only Brazil']['SLC']
        else:
            slc_options = df_slc[df_slc['Scope'].isna()]['SLC']
        
        slc_sel = st.selectbox("SLC", slc_options)
        uplf = df_slc[df_slc['SLC'] == slc_sel]['UPLF'].values[0]

    with col_b:
        st.subheader("Costos y Fechas")
        s_start = st.date_input("Service Start", datetime.now())
        s_end = st.date_input("Service End", datetime.now())
        # Cálculo de Duración (Meses)
        duration = (s_end.year - s_start.year) * 12 + (s_end.month - s_start.month)
        if duration <= 0: duration = 1
        st.write(f"Duración: {duration} meses")

        u_cost_usd = st.number_input("Unit Cost USD", min_value=0.0, format="%.2f")
        u_cost_local = st.number_input("Unit Cost Local", min_value=0.0, format="%.2f")

    # ==========================================
    # 5. OPERACIONES MATEMÁTICAS (SERVICIOS)
    # ==========================================
    # Fórmula según UI_CONFIG: ((USD + Local)*Duration)*QTY*UPLF
    # Ajustado: Si moneda es Local, el resultado se multiplica/divide por ER
    base_cost = (u_cost_usd + (u_cost_local / er_actual if er_actual != 0 else 0))
    total_service = (base_cost * duration) * qty * uplf
    
    # Si el usuario eligió ver en Local
    display_cost = total_service * er_actual if moneda == "Local" else total_service

    st.markdown("---")
    st.metric(f"Total Service Cost ({moneda})", f"{display_cost:,.2f}")

# --- TAB 2: LABOR ---
with tab2:
    st.subheader("Cálculos de Labor / Manage (Lacostw41)")
    col_l1, col_l2 = st.columns(6)
    
    with col_l1:
        # Seleccionamos si es Machine Category o Brand Rate Full
        tipo_mcbr = st.selectbox("MachCat/BandRate", df_mcbr['MCBR'])
        
        # Filtramos qué tabla usar y qué columna mostrar en el desplegable
        if "Machine" in tipo_mcbr:
            mcrr_list = df_lplat['Plat'].unique()
            df_ref = df_lplat
            col_busqueda = 'Plat'
        else:
            # Aquí corregimos para Band Rate Full
            mcrr_list = df_lband['Def'].unique()
            df_ref = df_lband
            col_busqueda = 'Def'
            
        mcrr_sel = st.selectbox("Seleccione MC/RR (Plataforma o Banda)", mcrr_list)
        
    with col_l2:
        # BUSCANDO EL COSTO EN EL ARCHIVO CSV (Optimizado para Lacostw41)
        try:
            # Buscamos la fila y extraemos el valor del país
            fila_seleccionada = df_ref[df_ref[col_busqueda] == mcrr_sel]
            valor_raw = fila_seleccionada[pais].values[0]
            
            # --- LIMPIADOR DE TEXTO A NÚMERO ---
            if pd.isna(valor_raw) or str(valor_raw).strip() in ['', '-']:
                m_cost = 0.0
            else:
                # Quitamos comas, espacios y convertimos a número flotante
                limpio = str(valor_raw).replace(',', '').replace('"', '').strip()
                m_cost = float(limpio)
        except Exception:
            m_cost = 0.0
            
        st.write(f"Costo Mensual Base detectado: **{m_cost:,.2f}**")
        
        # Inputs adicionales
        horas = st.number_input("Horas / QTY Labor", value=1, min_value=1)
        m_start = st.date_input("Manage Start", s_start)
        m_end = st.date_input("Manage End", s_end)
        
        # Duración Labor
        dur_manage = (m_end.year - m_start.year) * 12 + (m_end.month - m_start.month)
        if dur_manage <= 0: dur_manage = 1

    # ==========================================
    # CÁLCULO MATEMÁTICO LABOR (SEGÚN UI_CONFIG)
    # ==========================================
    # Fórmula: Costo * Horas * Duración
    total_manage_base = (m_cost * horas * dur_manage)
    
    # Ajuste por moneda (Si es USD y el archivo está en Local, divide. Si es Local y está en Local, mantiene)
    if moneda == "USD":
        display_manage = total_manage_base / er_actual if er_actual != 0 else total_manage_base
    else:
        display_manage = total_manage_base

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
