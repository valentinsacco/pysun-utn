import streamlit as st
import pandas as pd
import numpy as np
import io
import plotly.express as px
import matplotlib.pyplot as plt # <--- ESTO FALTABA SEGURO

# Importamos tus funciones de cálculo
from lib.fcn_base import pot_generada_rango, energia, factor_de_utilizacion, max_pot

def _df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    return buf.getvalue().encode('utf-8')

def renderSimulatorScreen():
    st.header("Simulador de Generación Fotovoltaica")
    st.markdown("Carga los datos climáticos y ajusta los parámetros en la barra lateral.")

    # --- INICIALIZACIÓN DE VARIABLES DE ESTADO ---
    defaults = {
        "N": 12,
        "Ppico": 240.0,
        "eta": 0.97,
        "kp": -0.0044,
        "Pinv": 2.5,
        "mu": 2.0
    }
    
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

    # --- FUNCIÓN CALLBACK PARA EL BOTÓN ---
    def cargar_datos_utn():
        st.session_state.N = 12
        st.session_state.Ppico = 240.0
        st.session_state.eta = 0.97
        st.session_state.kp = -0.0044
        st.session_state.Pinv = 2.5
        st.session_state.mu = 2.0

    # --- BARRA LATERAL (Sidebar) ---
    st.sidebar.header("1. Configuración del GFV")
    
    st.sidebar.button("Cargar datos GFV UTN Santa Fe", on_click=cargar_datos_utn)
    
    N = st.sidebar.number_input("Cantidad de paneles (N)", min_value=1, key="N")
    Ppico = st.sidebar.number_input("Potencia Pico por panel [W]", min_value=0.0, step=5.0, format="%.1f", key="Ppico")
    eta = st.sidebar.slider("Rendimiento Global (eta)", 0.0, 1.0, step=0.01, key="eta")
    kp = st.sidebar.number_input("Coef. Temperatura (kp) [1/°C]", step=0.0001, format="%.4f", key="kp")
    Pinv = st.sidebar.number_input("Potencia Nominal Inversor [kW]", min_value=0.0, step=0.1, key="Pinv")
    mu = st.sidebar.slider("Umbral mínimo inversor (mu %)", 0.0, 20.0, step=0.5, key="mu")
    
    Gstd = 1000.0
    Tr = 25.0
    st.sidebar.info(f"Parámetros fijos: Gstd={Gstd} W/m², Tr={Tr}°C")

    # --- ZONA PRINCIPAL ---
    
    st.subheader("2. Carga de Datos Meteorológicos")
    uploaded_file = st.file_uploader("Subir archivo (Excel/CSV) con: Fecha, Irradiancia, Temperatura", type=["xlsx", "xls", "csv"])
    
    df = None
    
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            if df.shape[1] < 3:
                st.error("El archivo debe tener al menos 3 columnas: [Fecha, Irradiancia, Temperatura]")
                df = None
            else:
                cols = df.columns
                df = df.rename(columns={cols[0]: 'Fecha', cols[1]: 'G', cols[2]: 'T'})
                df['Fecha'] = pd.to_datetime(df['Fecha'], dayfirst=True, errors='coerce')
                df = df.dropna(subset=['Fecha'])
                
                st.success(f"Archivo cargado correctamente. {len(df)} registros encontrados.")
                
                with st.expander("Ver datos cargados (primeras filas)"):
                    st.dataframe(df.head())

        except Exception as e:
            st.error(f"Error al leer el archivo: {e}")

    # --- SIMULACIÓN ---
    if df is not None:
        st.divider()
        st.subheader("3. Resultados de la Simulación")

        if st.button("Ejecutar Simulación", type="primary"):
            lista_G = df['G'].to_numpy()
            lista_T = df['T'].to_numpy()

            # 1. CÁLCULOS PRINCIPALES
            # Potencia Real (Con limitación Pinv)
            potencias = pot_generada_rango(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu, Gstd, Tr)
            df['Potencia_kW'] = potencias

            # Energía Real (kWh)
            e_real = energia(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu, Gstd, Tr)
            
            # Energía Teórica (Sin limitación): 
            # Pinv infinito y mu=0 para que no suba el umbral mínimo
            Pinv_infinito = 999999.0 
            e_teorica = energia(lista_G, lista_T, N, Ppico, eta, kp, Pinv_infinito, 0.0, Gstd, Tr)
            
            # Pérdida por recorte
            e_perdida = e_teorica - e_real
            
            # Factor de utilización y máximos
            f_util = factor_de_utilizacion(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu, Gstd, Tr)
            idx_max, val_max = max_pot(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu, Gstd, Tr)
            
            # Manejo seguro del índice máximo
            if len(df) > idx_max:
                fecha_max = df.iloc[idx_max]['Fecha']
            else:
                fecha_max = "N/A"

            # 2. MOSTRAR MÉTRICAS (Columnas)
            # Fila 1: Energías
            c1, c2, c3 = st.columns(3)
            c1.metric("Energía REAL (Generada)", f"{e_real:.2f} kWh", help="Energía entregada a la red limitada por el inversor.")
            c2.metric("Energía TEÓRICA (Paneles)", f"{e_teorica:.2f} kWh", help="Energía que podrían haber generado los paneles si el inversor fuera infinito.")
            c3.metric("Pérdida por Inversor", f"{e_perdida:.2f} kWh", delta_color="inverse", help="Diferencia desperdiciada por saturación (clipping).")
            
            # Fila 2: Otros indicadores
            c4, c5 = st.columns(2)
            c4.metric("Potencia Máxima Alcanzada", f"{val_max:.2f} kW", f"Fecha: {fecha_max}")
            c5.metric("Factor de Utilización", f"{f_util*100:.1f} %")

            # 3. GRÁFICO DE LÍNEAS (Con PLOTLY para el ZOOM)
            st.write("### Evolución Temporal de la Potencia")
            fig = px.line(df, x='Fecha', y='Potencia_kW', title='Potencia de Salida del GFV (kW)')
            
            # Fijar eje Y hasta 3 y agregar Zoom
            fig.update_layout(yaxis_range=[0, 3]) 
            fig.update_xaxes(rangeslider_visible=True)
            
            st.plotly_chart(fig, use_container_width=True)

            # 4. GRÁFICO MENSUAL (Con MATPLOTLIB para cumplir requisitos académicos)
            st.write("### Generación Mensual de Energía")
            df['Mes'] = df['Fecha'].dt.month
            
            # Agrupar y convertir potencia instantánea a energía (kWh)
            monthly = df.groupby('Mes')['Potencia_kW'].sum() * (10.0/60.0)
            
            # Mapear números a Nombres
            meses_nombres = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", 
                             "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
            
            # Crear gráfico con MATPLOTLIB
            fig_bar, ax = plt.subplots(figsize=(10, 4))
            # Color 'skyblue' y bordes negros para que quede prolijo
            ax.bar(monthly.index, monthly.values, color='skyblue', edgecolor='white')
            
            # Ajustes visuales
            ax.set_xticks(range(1, 13))
            ax.set_xticklabels(meses_nombres)
            ax.set_ylabel("Energía (kWh)")
            ax.set_title("Energía Generada por Mes")
            ax.grid(axis='y', linestyle='--', alpha=0.3)
            
            # Fondo transparente para que se vea bien en el modo oscuro de tu app
            fig_bar.patch.set_alpha(0.0)
            ax.patch.set_alpha(0.0)
            
            # Cambiar color de textos a blanco/gris claro para que contraste con tu fondo oscuro
            ax.tick_params(colors='white')
            ax.xaxis.label.set_color('white')
            ax.yaxis.label.set_color('white')
            ax.title.set_color('white')
            for spine in ax.spines.values():
                spine.set_edgecolor('white')

            st.pyplot(fig_bar)

            # 5. DESCARGAS
            csv_res = _df_to_csv_bytes(df[['Fecha', 'G', 'T', 'Potencia_kW']])
            st.download_button("Descargar Resultados Detallados (CSV)", csv_res, "simulacion_pysun.csv", "text/csv")