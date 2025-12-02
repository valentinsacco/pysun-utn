import streamlit as st
import pandas as pd
import numpy as np
import io
import plotly.express as px
import matplotlib.pyplot as plt
from datetime import time

# Importamos TODAS las funciones de cálculo y graficado
from lib.fcn_base import (
    pot_generada_rango, energia, factor_de_utilizacion, max_pot,
    graficar_dispersion, graficar_torta, graficar_histograma, graficar_pot
)

# Función para generar EXCEL real (.xlsx)
def _df_to_excel_bytes(df: pd.DataFrame) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Resultados')
    return output.getvalue()

def renderSimulatorScreen():
    # --- CAMBIO 1: TÍTULO CENTRADO ---
    st.markdown("<h1 style='text-align: center;'>Simulador de Generación Fotovoltaica</h1>", unsafe_allow_html=True)
    st.markdown("Carga los datos climáticos y ajusta los parámetros en la barra lateral.")

    # --- INICIALIZACIÓN DE VARIABLES DE ESTADO ---
    defaults = {
        "N": 12, "Ppico": 240.0, "eta": 0.97, "kp": -0.0044, "Pinv": 2.5, "mu": 2.0
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

    # --- FUNCIÓN CALLBACK ---
    def cargar_datos_utn():
        st.session_state.N = 12
        st.session_state.Ppico = 240.0
        st.session_state.eta = 0.97
        st.session_state.kp = -0.0044
        st.session_state.Pinv = 2.5
        st.session_state.mu = 2.0

    # --- BARRA LATERAL ---
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
    
    df_raw = None
    
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.csv'):
                df_raw = pd.read_csv(uploaded_file)
            else:
                df_raw = pd.read_excel(uploaded_file)
            
            if df_raw.shape[1] < 3:
                st.error("El archivo debe tener al menos 3 columnas: [Fecha, Irradiancia, Temperatura]")
                df_raw = None
            else:
                cols = df_raw.columns
                df_raw = df_raw.rename(columns={cols[0]: 'Fecha', cols[1]: 'G', cols[2]: 'T'})
                df_raw['Fecha'] = pd.to_datetime(df_raw['Fecha'], dayfirst=True, errors='coerce')
                df_raw = df_raw.dropna(subset=['Fecha'])
                st.success(f"Archivo cargado correctamente. {len(df_raw)} registros encontrados.")
                
                with st.expander("Ver datos cargados (primeras filas)"):
                    st.dataframe(df_raw.head())

        except Exception as e:
            st.error(f"Error al leer el archivo: {e}")

    # --- SIMULACIÓN ---
    if df_raw is not None:
        st.divider()
        st.subheader("3. Resultados de la Simulación")

        if st.button("Ejecutar Simulación", type="primary"):
            lista_G = df_raw['G'].to_numpy()
            lista_T = df_raw['T'].to_numpy()

            # Cálculos
            potencias = pot_generada_rango(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu, Gstd, Tr)
            df_res = df_raw.copy()
            df_res['Potencia_kW'] = potencias

            e_real = energia(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu, Gstd, Tr)
            
            Pinv_infinito = 999999.0 
            e_teorica = energia(lista_G, lista_T, N, Ppico, eta, kp, Pinv_infinito, 0.0, Gstd, Tr)
            e_perdida = e_teorica - e_real
            
            f_util = factor_de_utilizacion(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu, Gstd, Tr)
            idx_max, val_max = max_pot(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu, Gstd, Tr)
            
            fecha_max = df_res.iloc[idx_max]['Fecha'] if len(df_res) > idx_max else "N/A"

            # GUARDAR EN SESSION_STATE
            st.session_state['sim_results'] = {
                'df': df_res,
                'potencias': potencias,
                'lista_G': lista_G,
                'lista_T': lista_T,
                'e_real': e_real,
                'e_teorica': e_teorica,
                'e_perdida': e_perdida,
                'f_util': f_util,
                'val_max': val_max,
                'fecha_max': fecha_max,
                'N': N, 'Ppico': Ppico, 'Pinv': Pinv, 'mu': mu, 'eta': eta, 'kp': kp
            }

        # VISUALIZACIÓN
        if 'sim_results' in st.session_state:
            res = st.session_state['sim_results']
            df = res['df']

            # --- MÉTRICAS ---
            c1, c2, c3 = st.columns(3)
            c1.metric("Energía REAL", f"{res['e_real']:.2f} kWh", help="Energía entregada a la red limitada por la potencia del inversor.")
            c2.metric("Energía TEÓRICA", f"{res['e_teorica']:.2f} kWh", help="Energía potencial que podrían haber generado los paneles sin limitaciones.")
            # --- CAMBIO 2: TOOLTIP EN PÉRDIDA ---
            c3.metric("Pérdida (Clipping)", f"{res['e_perdida']:.2f} kWh", delta_color="inverse", help="Energía desperdiciada en los momentos donde la producción de los paneles superó la capacidad máxima del inversor (Pinv).")
            
            c4, c5 = st.columns(2)
            c4.metric("Potencia Máxima", f"{res['val_max']:.2f} kW", f"Fecha: {res['fecha_max']}")
            c5.metric("Factor de Utilización", f"{res['f_util']*100:.1f} %")

            # --- FILTRADO ---
            st.divider()
            st.markdown("### 🔎 Filtrar Periodo de Análisis")
            
            min_date = df['Fecha'].dt.date.min()
            max_date = df['Fecha'].dt.date.max()
            
            c_filtro1, c_filtro2 = st.columns(2)
            date_range = c_filtro1.date_input("Rango de Fechas", value=(min_date, max_date), min_value=min_date, max_value=max_date, key="date_filter")
            time_range = c_filtro2.slider("Rango Horario", value=(time(0,0), time(23,59)), step=pd.Timedelta(minutes=60), key="time_filter")

            if len(date_range) == 2:
                start_d, end_d = date_range
                mask = (df['Fecha'].dt.date >= start_d) & (df['Fecha'].dt.date <= end_d) & \
                       (df['Fecha'].dt.time >= time_range[0]) & (df['Fecha'].dt.time <= time_range[1])
                df_filtered = df.loc[mask]
            else:
                df_filtered = df.copy()

            if df_filtered.empty:
                st.warning("No hay datos en el rango seleccionado.")
            else:
                e_periodo = df_filtered['Potencia_kW'].sum() * (10.0/60.0)
                
                c_res1, c_res2 = st.columns([1, 3])
                c_res1.metric(f"Energía en Periodo", f"{e_periodo:.2f} kWh")
                
                fig_line = px.line(df_filtered, x='Fecha', y='Potencia_kW', title='Potencia de Salida (kW) - Periodo Seleccionado')
                fig_line.update_layout(yaxis_range=[0, res['Pinv'] * 1.2]) 
                c_res2.plotly_chart(fig_line, use_container_width=True)

            st.divider()

            # --- GRÁFICOS AVANZADOS ---
            st.markdown("### 📊 Análisis Técnico Anual")
            
            tabs = st.tabs(["Dispersión (Saturación)", "Eficiencia & Frecuencia", "Mensual", "Reporte Estático"])

            with tabs[0]:
                st.markdown("**Correlación Irradiancia vs. Potencia** (Interactivo)")
                st.caption("Usa el zoom para ver el 'codo' de saturación del inversor.")
                df_scatter = df if len(df) < 10000 else df.sample(10000)
                fig_scatter = px.scatter(
                    df_scatter, x='G', y='Potencia_kW', 
                    opacity=0.4, 
                    title="Curva Característica del Sistema",
                    labels={'G': 'Irradiancia (W/m²)', 'Potencia_kW': 'Potencia Salida (kW)'}
                )
                fig_scatter.update_layout(yaxis_range=[0, res['Pinv'] * 1.2])
                st.plotly_chart(fig_scatter, use_container_width=True)

            with tabs[1]:
                col_pie, col_hist = st.columns(2)
                with col_pie:
                    st.markdown("**Pérdidas por Recorte**")
                    fig_pie = graficar_torta(res['e_real'], res['e_perdida'])
                    st.pyplot(fig_pie)
                with col_hist:
                    st.markdown("**Histograma de Potencia**")
                    fig_hist = graficar_histograma(res['potencias'])
                    st.pyplot(fig_hist)

            with tabs[2]:
                st.markdown("**Generación Mensual**")
                df['Mes'] = df['Fecha'].dt.month
                monthly = df.groupby('Mes')['Potencia_kW'].sum() * (10.0/60.0)
                meses_nombres = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
                
                fig_bar, ax = plt.subplots(figsize=(10, 4))
                ax.bar(monthly.index, monthly.values, color='skyblue', edgecolor='white')
                ax.set_xticks(range(1, 13))
                ax.set_xticklabels(meses_nombres)
                ax.set_ylabel("Energía (kWh)")
                ax.grid(axis='y', linestyle='--', alpha=0.3)
                
                fig_bar.patch.set_alpha(0.0); ax.patch.set_alpha(0.0)
                ax.tick_params(colors='white'); ax.xaxis.label.set_color('white'); ax.yaxis.label.set_color('white')
                for spine in ax.spines.values(): spine.set_edgecolor('white')
                st.pyplot(fig_bar)

            with tabs[3]:
                st.markdown("**Gráfico de Potencia Estático**")
                st.caption("Generado con la función `graficar_pot` del módulo base (Requisito PDF).")
                fig_static = graficar_pot(res['lista_G'], res['lista_T'], res['N'], res['Ppico'], res['eta'], res['kp'], res['Pinv'], res['mu'], Gstd, Tr)
                
                fig_static.patch.set_alpha(0.0)
                ax_s = fig_static.gca()
                ax_s.patch.set_alpha(0.0)
                ax_s.tick_params(colors='white'); ax_s.xaxis.label.set_color('white'); ax_s.yaxis.label.set_color('white')
                ax_s.title.set_color('white')
                for spine in ax_s.spines.values(): spine.set_edgecolor('white')
                st.pyplot(fig_static)

            # --- DESCARGAS ---
            st.divider()
            st.subheader("Descargas")
            
            # --- CAMBIO 3: TEXTO EXPLICATIVO ---
            st.markdown("""
            Descargue un archivo Excel con la serie temporal completa de los resultados de la simulación. 
            El archivo incluirá columnas para: **Fecha y Hora, Irradiancia (G), Temperatura (T) y Potencia de Salida Generada**.
            """)
            
            excel_data = _df_to_excel_bytes(df[['Fecha', 'G', 'T', 'Potencia_kW']])
            
            st.download_button(
                label="Descargar Resultados (Excel .xlsx)",
                data=excel_data,
                file_name="simulacion_pysun.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )