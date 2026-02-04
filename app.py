import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA (Tamaño y Título) ---
st.set_page_config(layout="wide", page_title="Lacostw41 - IBM")

st.title("🚀 Lacostw41: Conversor Excel a Web")

# --- CARGA DE DATOS (Tus archivos CSV) ---
@st.cache_data
def load_data():
    countries = pd.read_csv('countries.csv')
    offering = pd.read_csv('offering.csv')
    risk = pd.read_csv('risk.csv')
    slc = pd.read_csv('slc.csv')
    return countries, offering, risk, slc

df_countries, df_offering, df_risk, df_slc = load_data()

# --- BARRA LATERAL (Campos de entrada Izquierda) ---
with st.sidebar:
    st.header("Configuración de Cotización")
    id_cotiz = st.text_input("ID Cotización", "COT-001")
    pais = st.selectbox("País", df_countries.columns[2:]) # Dinámico desde CSV
    moneda = st.selectbox("Moneda", ["USD", "Local"])
    risk_level = st.selectbox("QA Risk", df_risk['Risk'])
    
    # Operación simple: Buscar contingencia
    contingency = df_risk[df_risk['Risk'] == risk_level]['Contingency'].values[0]
    st.write(f"Contingencia aplicada: {contingency}")

# --- CUERPO PRINCIPAL (TABs como pediste) ---
tab1, tab2 = st.tabs(["🛠 Servicios", "📊 Resumen"])

with tab1:
    st.subheader("Entrada de Datos de Servicio")
    col1, col2, col3 = st.columns(3) # Aquí controlas el tamaño/columnas
    
    with col1:
        offering_sel = st.selectbox("Offering", df_offering['Offering'])
        qty = st.number_input("Cantidad (QTY)", min_value=1, value=1)
    
    with col2:
        start_date = st.date_input("Fecha Inicio", datetime.now())
        end_date = st.date_input("Fecha Fin")
        # Operación: Cálculo de duración en meses
        duration = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
        st.info(f"Duración: {duration} meses")

    with col3:
        unit_cost = st.number_input("Costo Unitario USD", min_value=0.0)
        uplf = st.selectbox("SLC (UPLF)", df_slc['SLC'])

    # --- OPERACIONES MATEMÁTICAS (Identificables) ---
    # Aquí puedes ajustar tus fórmulas de Excel
    total_service_cost = (unit_cost * qty * duration)
    
    st.markdown("---")
    st.metric("Total Service Cost", f"{total_service_cost:,.2f} {moneda}")

with tab2:
    st.write("Cálculos Finales de Lacostw41")
    # Aquí irían las tablas comparativas finales