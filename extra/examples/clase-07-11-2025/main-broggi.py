import streamlit as st
import pandas as pd
import datetime

tabla = pd.read_excel("extra\data\Datos_climatologicos_Santa_Fe_2019.xlsx", index_col=0)
enero = tabla.loc['2019-01', :]

tab1, tab2, tab3 = st.tabs(["Simulación GFV", "Análisis de datos", "Graficación de resultados"])

with tab1:
    st.title("Aplicación de simulación de un GEN. FV")
    st.write("adsadads")
    st.markdown("""
                Esta aplicacion simula el comportomaniento de un GF
                fafafafafe
                """)

with tab2:
        """st.header("Análisis de datos climatológicos")
        st.write("En esta sección se pueden analizar los datos climatológicos de Santa Fe, Argentina, correspondientes al año 2019.")
        st.write("Se cuenta con datos horarios de irradiancia global horizontal (GHI) y temperatura ambiente (Tamb).")
        """
N = st.number_input('Cantidad de paneles FV', min_value=1, max_value=1000, value=12, step=1)

Ppico = st.number_input('Potencia pico del panel FV (W)', min_value=50, max_value=240, value=240, step=10)

eta = st.number_input('Rendimiento del inversor', min_value=0.00, max_value=1.00, value=0.95, step=0.10, format="%.2f")

kp = st.slider('Coeficiente de potencia-temperatura (p.u./°C)', min_value=-0.5, max_value=-0.0044, value=-0.2, step=0.001, format="%.2f")

Tc = enero['Temperatura (°C)'] + 0.031 * enero['Irradiancia (W/m²)']

pot = N * Ppico * enero['Irradiancia (W/m²)'] / 1000 * eta * (1 + kp * (Tc - 25))

with tab3:
    st.dataframe(enero)

    dia = st.date_input("Seleccionar día", min_value = datetime.date(2019, 1, 1), max_value = datetime.date(2019, 1, 31), value = datetime.date(2019, 1, 21))

    if st.button("Graficar Temperaturas de enero", type="primary"):
        y = dia.year
        m = dia.month
        d = dia.day
        tabla_filtrada = enero.loc[f'{y}-{m}-{d}', :]

        col1, col2 = st.columns(2)
        with col1:
            st.line_chart(data=tabla_filtrada, y='Potencia (kW)', use_container_width=True)
        with col2:
            valores_medios= tabla_filtrada['Potencia (kW)'].mean()
            valores_medios.name = 'Valor medio'
            st.dataframe(valores_medios)

            energ_diaria = valores_medios['Potencia (kW)'] * 24 #kWh diarios
            st.success(f"Energía diaria generada: {energ_diaria:.2f} kWh")