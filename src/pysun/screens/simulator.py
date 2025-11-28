import io
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import calendar
import numpy as np

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
            # Limpiar resultados previos al cargar nuevo archivo
            for k in list(st.session_state.keys()):
                if k.startswith("pv_"):
                    del st.session_state[k]
        except Exception as e:
            st.error(f"Error al leer el archivo: {e}")

    

    if df is not None:
        st.subheader("Datos cargados / mapeo de columnas")
        cols = list(df.columns)
        # Asumir que la primera columna del Excel contiene timestamps (fecha+hora)
        date_col = cols[0]

        # Asumir que la 2ª columna es irradiancia y la 3ª es temperatura
        if len(cols) < 3:
            st.error("El archivo debe contener al menos 3 columnas: fecha/hora, irradiancia y temperatura (en ese orden).")
        else:
            colG = cols[1]
            colT = cols[2]

            preview = st.checkbox("Mostrar vista previa (primeras filas)", value=True)
            if preview:
                # Mostrar fecha + columnas detectadas
                st.dataframe(df[[date_col, colG, colT]].head(10))

            # Botón para calcular energía mensual
            if st.button("Calcular y graficar energía generada mensualmente"):
                lista_G = df[colG].to_numpy()
                lista_T = df[colT].to_numpy()

                # Calcular potencia por muestra
                pot_array = pot_generada_rango(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu, Gstd, Tr)

                # Parsear la primera columna como timestamps (fecha+hora)
                dates = pd.to_datetime(df[date_col], errors='coerce', dayfirst=True)
                if dates.isna().all():
                    st.error(f"No se pudieron parsear las fechas en la primera columna ('{date_col}'). Revise el formato (debe incluir fecha y hora).")
                else:
                    plot_df = pd.DataFrame({"date": dates, "pot_kW": pot_array})
                    plot_df = plot_df.dropna(subset=["date"]).copy()
                    if plot_df.shape[0] < 2:
                        st.error("Se requieren al menos 2 muestras con timestamps válidos para calcular energía.")
                    else:
                        # Ordenar por fecha y asegurar tipo numérico
                        plot_df = plot_df.sort_values("date").reset_index(drop=True)
                        plot_df["pot_kW"] = plot_df["pot_kW"].astype(float)

                        # Calcular intervalos en horas entre muestras (dt para la integración)
                        plot_df["dt_hours"] = plot_df["date"].diff().dt.total_seconds() / 3600.0

                        # Integración trapezoidal: energía por intervalo = 0.5*(p_i + p_{i-1}) * dt_hours
                        plot_df["pot_prev"] = plot_df["pot_kW"].shift(1)
                        plot_df["energy_kWh_interval"] = 0.5 * (plot_df["pot_kW"] + plot_df["pot_prev"]) * plot_df["dt_hours"]

                        # El primer registro tendrá NaN en energy_kWh_interval (sin intervalo previo), descartarlo
                        plot_df = plot_df.dropna(subset=["energy_kWh_interval"]).copy()
                        if plot_df.empty:
                            st.error("No hay intervalos válidos para integrar energía. Revise los timestamps.")
                        else:
                            plot_df["month"] = plot_df["date"].dt.month

                            # Sumar energía por mes (kWh)
                            monthly = plot_df.groupby("month")["energy_kWh_interval"].sum().reindex(range(1,13), fill_value=0)

                            # Guardar resultados en session_state para mantener la visualización
                            st.session_state["pv_plot_df"] = plot_df
                            st.session_state["pv_monthly"] = monthly
                            st.session_state["pv_pot_array"] = pot_array
                            # Guardar también las series de G y T para cálculos teóricos
                            st.session_state["pv_G_array"] = lista_G
                            st.session_state["pv_T_array"] = lista_T

                            # Métricas generales (siempre calculables a partir de las series)
                            energia_total = energia(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu, Gstd, Tr)
                            factor_val = factor_de_utilizacion(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu, Gstd, Tr)
                            pos_max, valor_max = max_pot(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu, Gstd, Tr)

                            st.session_state["pv_metrics"] = {
                                "energia_total": energia_total,
                                "factor_val": factor_val,
                                "pos_max": pos_max,
                                "valor_max": valor_max,
                            }

                            # También guardar meta-información de columnas
                            st.session_state["pv_date_col"] = date_col
                            st.session_state["pv_colG"] = colG
                            st.session_state["pv_colT"] = colT

            # Si ya hay resultados de cálculo mensual, mostrarlos aquí (persistente)
            if "pv_monthly" in st.session_state:
                monthly = st.session_state["pv_monthly"]
                months_es = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]
                fig, ax = plt.subplots(figsize=(10, 4))
                ax.bar(range(1,13), monthly.values, color='tab:blue')
                ax.set_xticks(range(1,13))
                ax.set_xticklabels(months_es)
                ax.set_xlabel("Mes")
                ax.set_ylabel("Energía (kWh)")
                ax.set_title("Energía generada por mes (kWh)")
                # Mostrar etiquetas de valor encima de cada barra
                for i, v in enumerate(monthly.values, start=1):
                    ax.text(i, v + max(monthly.max() * 0.01, 1e-6), f"{v:.2f}", ha='center', va='bottom', fontsize=8)
                st.pyplot(fig)

                # Métricas y descargas
                energia_total = st.session_state.get("pv_metrics", {}).get("energia_total", 0.0)
                factor_val = st.session_state.get("pv_metrics", {}).get("factor_val", 0.0)
                pos_max = st.session_state.get("pv_metrics", {}).get("pos_max", 0)
                valor_max = st.session_state.get("pv_metrics", {}).get("valor_max", 0.0)

                st.markdown("**Métricas resumen**")
                st.write(f"- Energía total (kWh): {energia_total:.2f}")
                st.write(f"- Factor de utilización: {factor_val:.4f}")
                st.write(f"- Potencia máxima (kW): {valor_max:.2f} en muestra {pos_max}")

                pot_df = pd.DataFrame({"pot_kW": st.session_state.get("pv_pot_array", [])})
                csv_bytes = _df_to_csv_bytes(pot_df)
                st.download_button("Descargar potencias (CSV)", data=csv_bytes, file_name="potencias.csv", mime="text/csv")

                monthly_df = pd.DataFrame({"month": range(1,13), "energy_kWh": st.session_state.get("pv_monthly", monthly).values})
                monthly_csv = _df_to_csv_bytes(monthly_df)
                st.download_button("Descargar energía mensual (CSV)", data=monthly_csv, file_name="energia_mensual.csv", mime="text/csv")

            # Botón independiente para calcular y graficar energía diaria del mes seleccionado
            sel_month = st.session_state.get("sel_month", st.selectbox("Seleccionar mes para detalle diario", options=list(range(1,13)), format_func=lambda i: ["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"][i-1], index=0, key="sel_month"))
            if st.button("Calcular y graficar energía del mes seleccionado"):
                # Calcular potencias/plot_df si no existen
                if "pv_plot_df" in st.session_state:
                    plot_df_saved = st.session_state["pv_plot_df"]
                else:
                    lista_G = df[colG].to_numpy()
                    lista_T = df[colT].to_numpy()
                    pot_array = pot_generada_rango(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu, Gstd, Tr)
                    dates = pd.to_datetime(df[date_col], errors='coerce', dayfirst=True)
                    plot_df_saved = pd.DataFrame({"date": dates, "pot_kW": pot_array}).dropna(subset=["date"]).copy()
                    plot_df_saved = plot_df_saved.sort_values("date").reset_index(drop=True)
                    plot_df_saved["pot_kW"] = plot_df_saved["pot_kW"].astype(float)
                    plot_df_saved["dt_hours"] = plot_df_saved["date"].diff().dt.total_seconds() / 3600.0
                    plot_df_saved["pot_prev"] = plot_df_saved["pot_kW"].shift(1)
                    plot_df_saved["energy_kWh_interval"] = 0.5 * (plot_df_saved["pot_kW"] + plot_df_saved["pot_prev"]) * plot_df_saved["dt_hours"]
                    plot_df_saved = plot_df_saved.dropna(subset=["energy_kWh_interval"]).copy()

                sel_month_int = int(st.session_state.get("sel_month", sel_month))
                daily_intervals = plot_df_saved[plot_df_saved["date"].dt.month == sel_month_int].copy()
                if daily_intervals.empty:
                    st.warning("No hay datos para el mes seleccionado.")
                else:
                    daily = daily_intervals.groupby(daily_intervals["date"].dt.day)["energy_kWh_interval"].sum()
                    year_for_days = int(plot_df_saved["date"].dt.year.min())
                    days_in_month = calendar.monthrange(year_for_days, sel_month_int)[1]
                    daily = daily.reindex(range(1, days_in_month + 1), fill_value=0)

                    fig2, ax2 = plt.subplots(figsize=(10, 3))
                    ax2.bar(daily.index, daily.values, color='tab:green')
                    ax2.set_xticks(range(1, days_in_month + 1))
                    ax2.set_xlabel("Día del mes")
                    ax2.set_ylabel("Energía diaria (kWh)")
                    months_full = ["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]
                    ax2.set_title(f"Energía diaria para {months_full[sel_month_int-1]}")
                    if days_in_month > 16:
                        step = 2
                        ax2.set_xticks(range(1, days_in_month + 1, step))
                    st.pyplot(fig2)

                    daily_df = pd.DataFrame({"day": list(daily.index), "energy_kWh": daily.values})
                    daily_csv = _df_to_csv_bytes(daily_df)
                    st.download_button("Descargar energía diaria (CSV)", data=daily_csv, file_name=f"energia_diaria_{sel_month_int}.csv", mime="text/csv")

            # Tercer botón: energía total actual y teórica (sin límite de inversor)
            if st.button("Calcular la energía generada total y la teórica"):
                # Asegurar que tenemos plot_df con energy_kWh_interval
                if "pv_plot_df" in st.session_state:
                    plot_df_tot = st.session_state["pv_plot_df"].copy()
                else:
                    # Reconstruir a partir del dataframe
                    lista_G = df[colG].to_numpy()
                    lista_T = df[colT].to_numpy()
                    pot_array = pot_generada_rango(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu, Gstd, Tr)
                    dates = pd.to_datetime(df[date_col], errors='coerce', dayfirst=True)
                    plot_df_tot = pd.DataFrame({"date": dates, "pot_kW": pot_array}).dropna(subset=["date"]).copy()
                    plot_df_tot = plot_df_tot.sort_values("date").reset_index(drop=True)
                    plot_df_tot["pot_kW"] = plot_df_tot["pot_kW"].astype(float)
                    plot_df_tot["dt_hours"] = plot_df_tot["date"].diff().dt.total_seconds() / 3600.0
                    plot_df_tot["pot_prev"] = plot_df_tot["pot_kW"].shift(1)
                    plot_df_tot["energy_kWh_interval"] = 0.5 * (plot_df_tot["pot_kW"] + plot_df_tot["pot_prev"]) * plot_df_tot["dt_hours"]
                    plot_df_tot = plot_df_tot.dropna(subset=["energy_kWh_interval"]).copy()

                if plot_df_tot.empty:
                    st.error("No hay intervalos válidos para calcular la energía total. Revise los timestamps o el archivo cargado.")
                else:
                    # Energía actual (considerando límite del inversor ya aplicado en pot_kW)
                    energia_actual_kwh = plot_df_tot["energy_kWh_interval"].sum()

                    # Obtener G y T para cálculo teórico (sin límite superior)
                    if "pv_G_array" in st.session_state and "pv_T_array" in st.session_state:
                        G_arr = np.array(st.session_state["pv_G_array"])
                        T_arr = np.array(st.session_state["pv_T_array"])
                        # Alinear longitud con plot_df_tot (por si hay NaNs en dates)
                        # Usamos the same indices as plot_df_tot
                        dates_all = pd.to_datetime(df[date_col], errors='coerce', dayfirst=True)
                        mask = ~dates_all.isna()
                        G_valid = G_arr[mask]
                        T_valid = T_arr[mask]
                        # In case plot_df_tot dropped first row, align lengths
                        if len(G_valid) != plot_df_tot.shape[0]:
                            # Try to align by index intersection
                            G_valid = G_valid[: plot_df_tot.shape[0]]
                            T_valid = T_valid[: plot_df_tot.shape[0]]
                    else:
                        # Fallback: read columns directly from df and align
                        dates_all = pd.to_datetime(df[date_col], errors='coerce', dayfirst=True)
                        valid_idx = dates_all.dropna().index
                        G_valid = df.loc[valid_idx, colG].to_numpy()
                        T_valid = df.loc[valid_idx, colT].to_numpy()
                        if len(G_valid) != plot_df_tot.shape[0]:
                            G_valid = G_valid[: plot_df_tot.shape[0]]
                            T_valid = T_valid[: plot_df_tot.shape[0]]

                    # Cálculo teórico sin tope del inversor: fórmula directa sin clip superior ni mínimo
                    Tc = T_valid + 0.031 * G_valid
                    P_raw_W = N * (G_valid / Gstd) * Ppico * (1 + kp * (Tc - Tr)) * eta
                    P_raw_kW = P_raw_W * 1e-3

                    # Conservar umbral mínimo (mu% de Pinv) pero sin aplicar el tope superior del inversor
                    Pmin_kW = (mu / 100.0) * Pinv
                    P_theo_kW = np.where(P_raw_kW <= Pmin_kW, 0.0, P_raw_kW)

                    # Integración trapezoidal para la serie teórica (usar dt de plot_df_tot)
                    dt_hours = plot_df_tot["dt_hours"].to_numpy()
                    p_curr = P_theo_kW
                    p_prev = np.concatenate(([np.nan], p_curr[:-1]))
                    energy_intervals_theo = 0.5 * (p_curr + p_prev) * dt_hours
                    energy_intervals_theo = energy_intervals_theo[~np.isnan(energy_intervals_theo)]
                    energia_teorica_kwh = np.sum(energy_intervals_theo)

                    # Mostrar resultados
                    st.markdown("**Energía generada (resumen total)**")
                    st.write(f"- Energía real (considerando límite del inversor) (kWh): {energia_actual_kwh:.3f}")
                    st.write(f"- Energía teórica sin límite superior (kWh): {energia_teorica_kwh:.3f}")
                    diff = energia_teorica_kwh - energia_actual_kwh
                    pct = (diff / energia_teorica_kwh * 100) if energia_teorica_kwh > 0 else 0
                    st.write(f"- Diferencia (kWh): {diff:.3f} — ({pct:.2f}% de la teórica)")

                    # Descarga resumen
                    resumen_df = pd.DataFrame({
                        "tipo": ["actual_kWh", "teorica_kWh", "diferencia_kWh", "pct_sobre_teorica"],
                        "valor": [energia_actual_kwh, energia_teorica_kwh, diff, pct],
                    })
                    st.download_button("Descargar resumen energía (CSV)", data=_df_to_csv_bytes(resumen_df), file_name="resumen_energia.csv", mime="text/csv")