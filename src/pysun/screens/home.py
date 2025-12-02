import streamlit as st

def renderHomeScreen():
    st.set_page_config(layout="centered")
    st.title("Simulador de Generadores Fotovoltaicos")
    st.markdown("""
        <div style="font-size: 16px; margin-bottom: 20px">
            <strong>Proyecto Integrador – Introducción a la Programación Científica en MATLAB y Python</strong><br>
            <strong>UTN Facultad Regional Santa Fe – 2025</strong><br>
            <strong>Docente:</strong> Dr. Ing. Loyarte, Ariel Sebastián<br>
            <strong>Alumnos:</strong> Broggi, Tomás Emanuel • Sacco, Valentin Alejandro
        </div>
                
        <span style='display: block; width: 100%; text-align: justify;'>Este proyecto web permite <strong style='color:#f54a00; font-weight:600;'>modelar</strong> y <strong style='color:#f54a00; font-weight:600;'>simular</strong> la operación de un  generador  fotovoltaico  (GFV)  para  evaluar  el  desempeño  ante  diferentes configuraciones de componentes y condiciones climatológicas. El programa computa distintas variables de interés, las cuáles son visualizadas mediante distintos indicadores y gráficos para distintos periodos de tiempo.</span>
    """, unsafe_allow_html=True)