import streamlit as st
import pandas as pd

table = pd.read_excel("extra\data\Datos_climatologicos_Santa_Fe_2019.xlsx", index_col = 0)
enero = table.loc['2019-01', :]


st.title("Aplicación de Simulación de un GEN. FV")
st.html("""
    <header style="background-color: red">
    </header>
""")
st.write("sdfsdf")
st.markdown("""
    # HOLA
""")

st.dataframe(enero)
if st.button("Graficar Temperaturas"):
    st.line_chart(data=enero, y="Temperatura (°C)")

n = st.number_input("Cantidad de paneles FV", min_value=1, max_value=100, value=10, step=1)
n = st.number_input("Potencia pico del FV (W)", min_value=50, max_value=240, value=240, step=10)
n = st.number_input("Rendimiento", min_value=0.0, max_value=1.0, value=0.95, step=0.1, format="%.2f")
