import io
import streamlit as st
import pandas as pd

from lib.fcn_base import graficar_pot, energia, factor_de_utilizacion, max_pot, pot_generada_rango

def _df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    return buf.getvalue().encode('utf-8')


def renderSimulatorScreen():
    st.header("Simulación")

    st.sidebar.header("Parámetros del modelo")

    defaults = {
        "N": 12,
        "Ppico": 240.0,
        "eta": 0.97,
        "kp": -0.0044,
        "Pinv": 2.5,
        "mu": 2.0,
        "Gstd": 1000.0,
        "Tr": 25.0,
        "G_slider": 1000.0,
    }

    if st.sidebar.button("Datos del generador UTN"):
        for k, v in defaults.items():
            st.session_state[k] = v

    N = st.sidebar.number_input("N (número de paneles)", value=st.session_state.get("N", defaults["N"]), min_value=1, step=1, format="%d", key="N")
   
    st.sidebar.markdown('<p style="color:white; margin-bottom:6px;">Ppico (W)</p>', unsafe_allow_html=True)
    
    Ppico = st.sidebar.number_input(
        "",
        value=st.session_state.get("Ppico", defaults["Ppico"]),
        min_value=0.0,
        step=0.05,
        format="%.2f",
        key="Ppico",
    )
    
    eta = st.sidebar.slider("Eficiencia (0-1)", min_value=0.0, max_value=1.0, value=st.session_state.get("eta", defaults["eta"]), step=0.01, key="eta")
    
    st.sidebar.markdown('<p style="color:white; margin-bottom:6px;">kp (1/°C)</p>', unsafe_allow_html=True)
    
    kp_raw = st.sidebar.slider("", min_value=-0.0100, max_value=0.0000, value=st.session_state.get("kp", defaults["kp"]), step=0.0001, key="kp", format="%0.4f")
    
    kp = round(kp_raw, 4)
    
    Pinv = st.sidebar.slider("Pinv (kW)", min_value=0.0, max_value=3.0, value=st.session_state.get("Pinv", defaults["Pinv"]), step=0.01, key="Pinv")
    
    mu = st.sidebar.slider("mu (%)", min_value=0.0, max_value=100.0, value=st.session_state.get("mu", defaults["mu"]), step=0.5, key="mu")
    
    Gstd = defaults["Gstd"]

    st.sidebar.markdown(f'<p style="color:white; margin-bottom:6px;">Gstd (W/m²) — fijo: {int(Gstd)}</p>', unsafe_allow_html=True)
    
    Tr = 25.0
    st.sidebar.markdown(f'<p style="color:white; margin-bottom:6px;">Tr (°C) — fijo: {Tr}</p>', unsafe_allow_html=True)

    st.sidebar.markdown('<p style="color:white; margin-top:8px; margin-bottom:6px;">G - Irradiancia (W/m²)</p>', unsafe_allow_html=True)
    G_slider = st.sidebar.slider("", min_value=0.0, max_value=2000.0, value=st.session_state.get("G_slider", defaults["G_slider"]), step=0.05, key="G_slider")

    df = None

    # Drag and Drop
    st.subheader("Cargar datos")
    uploaded_file_body = st.file_uploader(
        "Arrastra o selecciona un archivo Excel (xls/xlsx) o CSV",
        type=["xls", "xlsx", "csv"],
        key="body_uploader",
    )

    if df is None and uploaded_file_body is not None:
        try:
            if uploaded_file_body.name.lower().endswith(".csv"):
                df = pd.read_csv(uploaded_file_body)
            else:
                df = pd.read_excel(uploaded_file_body)
            st.success(f"Archivo cargado: {uploaded_file_body.name} — columnas: {', '.join(df.columns.astype(str))}")
        except Exception as e:
            st.error(f"Error al leer el archivo: {e}")

    

    if df is not None:
        st.subheader("Datos cargados / mapeo de columnas")
        cols = list(df.columns)
        st.markdown('<p style="color:black; margin-bottom:6px;">Columna de irradiancia (W/m²)</p>', unsafe_allow_html=True)
        colG = st.selectbox("", options=cols, index=0, key="colG")
        st.markdown('<p style="color:black; margin-top:6px; margin-bottom:6px;">Columna de temperatura (°C)</p>', unsafe_allow_html=True)
        colT = st.selectbox("", options=cols, index=1 if len(cols) > 1 else 0, key="colT")
        preview = st.checkbox("Mostrar vista previa (primeras filas)", value=True)
        if preview:
            st.dataframe(df[[colG, colT]].head(10))

        if st.button("Calcular y graficar potencia"):
            lista_G = df[colG].to_numpy()
            lista_T = df[colT].to_numpy()
            fig = graficar_pot(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu, Gstd, Tr)
            st.pyplot(fig)

            energia = energia(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu, Gstd, Tr)
            factor = factor_de_utilizacion(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu, Gstd, Tr)
            pos_max, valor_max = max_pot(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu, Gstd, Tr)

            st.markdown("*Métricas resumen*")
            st.write(f"- Energía total (kWh): {energia:.2f}")
            st.write(f"- Factor de utilización: {factor:.4f}")
            st.write(f"- Potencia máxima (kW): {valor_max:.2f} en muestra {pos_max}")

            pot_df = pd.DataFrame({"pot_kW": pot_generada_rango(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu, Gstd, Tr)})
            csv_bytes = _df_to_csv_bytes(pot_df)
            st.download_button("Descargar potencias (CSV)", data=csv_bytes, file_name="potencias.csv", mime="text/csv")