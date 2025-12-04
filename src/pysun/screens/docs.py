import streamlit as st

def renderDocsScreen():
    st.session_state.sidebar_state = "collapsed"
    st.set_page_config(layout="centered")

    # query_params = st.query_params
    # page = query_params.get("page", 'home')

    # js = f"""
    # <script>
    #     const sidebarState = parent.document.querySelector('.stSidebar')?.getAttribute('aria-expanded')
    
    #     const isDocs = {str(page == "docs").lower()}
        
    #     document.querySelector("header").style.left = (isDocs && sidebarState === "expanded") ? "256px" : "0px"
    # </script>
    # """

    # st.markdown(js, unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("""
            <h2 style='color: #f54a00; text-align: left;'>ÍNDICE</h2>
            <ul style='list-style: none; padding-left: 10px; font-size: 14px; color: #FFFFFF; display: flex; flex-direction: column; gap: 10px; cursor: pointer;'>
                <li><a href="#modelo-matematico" style="color:#FFFFFF; text-decoration:none;">Modelo Matemático</a></li>
                <li><a href="#estimacion-de-la-temperatura-de-celda" style="color:#FFFFFF; text-decoration:none;">Estimación de la Temperatura de Celda</a></li>
                <li><a href="#limites-del-inversor" style="color:#FFFFFF; text-decoration:none;">Límites del Inversor</a></li>
                <li><a href="#calculos-derivados" style="color:#FFFFFF; text-decoration:none;">Cálculos Derivados</a></li>
                <li><a href="#referencias-y-condiciones-de-uso" style="color:#FFFFFF; text-decoration:none;">Límites y Restricciones</a></li>                    
            </ul>
            <script>
                document.querySelectorAll('a[href^="#"]').forEach(anchor => {
                    anchor.addEventListener('click', function (e) {
                        e.preventDefault();
                        parent.document.querySelector(this.getAttribute('href'))?.scrollIntoView({
                            behavior: 'smooth'
                        });
                    });
                });
            </script>
        """, unsafe_allow_html=True)

    st.markdown("""
        # Documentación Técnica
        El simulador trabaja con modelos matemáticos inexactos pero que aproximan con gran precisión a los valores reales generados por un sistema de generación fotovoltáica. A continuación, se explicará y detallará como es el algoritmo interno del simulador que permite modelar distintos sistemas.
                
        ### Modelo Matemático
        La potencia generada por el sistema fotovoltaico se calcula mediante la siguiente expresión: 
    """)
    
    # Por un problema para renderizar esta ecuación con LATEX en markdown,
    # tuvimos que separar la ecuación y renderizarla con el método ".latex"  
    st.latex(r"P [kW] = N \cdot \frac{G}{1000} \cdot P_{pico} \cdot [1 + k_p (T_c - 25)] \cdot \eta \cdot 10^{-3}")
    
    st.markdown("""
        De donde:

        | Símbolo       | Descripción                                      | Valor típico (GFV UTN) | Unidad     |
        |---------------|--------------------------------------------------|------------------------|------------|
        | $P$     | Potencia entregada por el sistema                | —                      | kW         |
        | $N$           | Número de paneles fotovoltaicos                  | 12                     | —          |
        | $G$           | Irradiancia global horizontal                    | Variable               | W/m²       |
        | $G_{std}$     | Irradiancia en condiciones estándar             | 1000                   | W/m²       |
        | $P_{pico}$    | Potencia pico nominal de cada panel             | 240                    | W          |
        | $k_p$         | Coeficiente de temperatura-potencia          | – 0.0044                | 1/°C       |
        | $T_c$         | Temperatura de la celda fotovoltaica             | Calculada              | °C         |
        | $T_r$         | Temperatura de referencia utilizada por el fabricante                  | 25                     | °C         |
        | $\eta$        | Rendimiento global del sistema (inversor, cableado, etc.) | 0.97        | —          |

        ### Estimación de la Temperatura de Celda

        $$
            T_c [ºC] = T_{amb} + 0.031 \cdot G
        $$

        Donde:
        - $T_{amb}$: Temperatura ambiente (°C)
        - $G$: Irradiancia global (W/m²)

        ### Límites del Inversor

        Se aplican las siguientes restricciones del inversor:

        1. **Umbral mínimo de activación:**
                
        La potencia generada debe superar un umbral mínimo para que el inversor funcione correctamente:
    """)
    st.latex(r"P_{min} [kW] = \frac{\mu\%}{100} \cdot P_{inv}")
    st.markdown("""
        2. **Límite superior de potencia:**
                
        La potencia máxima está limitada por la capacidad nominal del inversor. La potencia entregada **Pr** se calcula como:
    """)
    st.latex(r"""
        P_r =
        \begin{cases}
        0 & \text{si } P \leq P_{\text{mín}} \\
        P & \text{si } P_{\text{mín}} < P \leq P_{\text{inv}} \\
        P_{\text{inv}} & \text{si } P > P_{\text{inv}}
        \end{cases}
    """)
    st.markdown("""
        | Parámetro     | Valor típico (GFV UTN) | Unidad |
        |---------------|------------------------|--------|
        | $P_{inv}$     | 2.5                    | kW     |
        | $\mu$         | 2.0                    | %      |

        ### Cálculos Derivados

        | Magnitud                   | Fórmula                                                  | Unidad  |
        |----------------------------|----------------------------------------------------------|---------|
        | Potencia media             | $\\bar{P} = \\frac{1}{n} \sum P_i $                      | kW      |
        | Energía diaria total       | $E = \sum P_i \cdot \Delta t$                            | kWh     |
        | Factor de utilización      | $FU = \\frac{\\bar{P}}{P_{inv}} \\cdot 100$              | %       |
        | Potencia máxima registrada | $P_{máx} = \max(P_i)$                                    | kW      |

        ### Referencias y Condiciones de Uso

        - **Datos meteorológicos:** Archivo Excel con columnas: `Fecha`, `Hora`, `Temperatura (°C)`, `Irradiancia (W/m²)`
    """)
