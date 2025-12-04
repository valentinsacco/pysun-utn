import streamlit as st

from screens.home import renderHomeScreen
from screens.docs import renderDocsScreen
from screens.simulator import renderSimulatorScreen

st.set_page_config(
    page_title="Simulador GFV - UTN Santa Fe", 
    page_icon="⚡", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
        * {
            font-family: 'Poppins', sans-serif;
            color: #FFFFFF;
        }
            
        body {
            background-color: #010408;
        }
            
        header { margin-top: -60px !important;}
        #MainMenu {visibility: hidden !important;}
        footer {visibility: hidden !important;}
        .css-1d391kg, .css-1v0mbdj {display: none !important;}
                
        .stMain {
            background-color: #010408;
        }
                
        .block-container {
            padding: 0rem 2rem !important;
        }
                
        .st-emotion-cache-1w723zb {
            padding: 0
        }
            
        .st-emotion-cache-8ezv7j {
            position: relative;
            top: 130px;
            left: 1rem;
            background-color: transparent;
        }
            
        .stSidebar {
            background-color: #010408;    
        }

        .stExpandSidebarButton {
            background-color: #0D1117;
        }
            
        .st-emotion-cache-pd6qx2 {
            color: #FFFFFF;
        }

        [data-testid="stSidebarContent"] {
            background-color: #0D1117;
            color: white;
        }
            
        h1[id], h2[id] h2, h3[id], h4[id], h5[id], h6[id] {
            scroll-margin-top: 90px;
        }
    </style>
""", unsafe_allow_html=True)


header = """
    <div id="header" style="
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 80px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 2rem;
        color: white;
        background-color: #010408;
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        z-index: 1000;
    ">
        <div style="display: flex; align-items: center; gap: 15px;">
            <a href="/" target="_self" style="text-decoration: none; color: white;"><img src="https://www.frsf.utn.edu.ar/utnabierta/imagenes/logo-utn.svg" height="40"/></a>
            <span style="font-size: 20px; font-weight: 600; font-family: 'Poppins', sans-serif; font-style: italic;">x</span>
            <img src="https://raw.githubusercontent.com/valentinsacco/pysun-utn/refs/heads/main/img/pysun-logo.png" height="40"/>
        </div>

        <div style="display: flex; gap: 30px; font-size: 1.1rem;">
            <a href="?page=docs" target="_self" style="text-decoration: none; font-weight: 400; font-size: 14px; color: white;">Documentación</a>
            <a href="?page=simulation" target="_self" style="text-decoration: none; font-weight: 400; font-size: 14px; color: white;">Simulador</a>
        </div>
    </div>

    <div style="height:80px"></div>
"""  
st.html(header)

query_params = st.query_params
page = query_params.get("page", 'home')

if page == "home":
    renderHomeScreen()

elif page == "docs":
    renderDocsScreen()

elif page == "simulation":
    renderSimulatorScreen()

else:
    st.html("""
        <div style='height: calc(100vh - 220px); width: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; gap: 20px;'>
            <span style='font-size: 30px; font-weight: 700; font-style: italic;'>404 - Página no Encontrada</span>
            <a href='/' target='_self' style='text-decoration: underline; color: #f54a00'>Volver al Inicio</a>
        </div>
    """)

st.markdown("""
    <div style="
        text-align: center;
        font-size: 12px;
        margin: 50px 0 30px 0;
        ">
        © 2025 • Dr. Ing. Loyarte / Broggi, Sacco • Proyecto Integrador • UTN FRSF
    </div>
""", unsafe_allow_html=True)
