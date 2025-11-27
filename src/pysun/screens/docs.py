import streamlit as st

def renderDocsScreen():
    st.set_page_config(layout="centered")

    # NO ESTÁ ANDANDO
    with st.sidebar:
        st.markdown("<h2 style='color:#00d4ff; text-align:center;'>ÍNDICE</h2>", unsafe_allow_html=True)
        st.markdown("<a href='#modelo' class='sidebar-link'>Modelo Matemático</a>", unsafe_allow_html=True)
        st.markdown("<a href='#temp' class='sidebar-link'>Estimación T° Celda</a>", unsafe_allow_html=True)
        st.markdown("<a href='#inversor' class='sidebar-link'>Límites Inversor</a>", unsafe_allow_html=True)
        st.markdown("<a href='#derivados' class='sidebar-link'>Cálculos Derivados</a>", unsafe_allow_html=True)

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
        | $P$           | Potencia entregada por el sistema                | —                      | kW         |
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

        ### Límites Reales del Inversor

        Se aplican las siguientes restricciones reales del inversor:

        1. **Umbral mínimo de activación:**
    """)
    st.latex(r"P_{min} [kW] = \frac{\mu\%}{100} \cdot P_{inv} \quad \Rightarrow \quad P = 0")
    st.latex(r"(\mu = 2\% \text{ por defecto})")
    st.markdown("""
        2. **Límite superior de potencia:**
    """)
    st.latex(r"\text{Si } P > P_{inv} \quad \Rightarrow \quad P = P_{inv}")
    st.markdown("""
        | Parámetro     | Valor típico (GFV UTN) | Unidad |
        |---------------|------------------------|--------|
        | $P_{inv}$     | 2.5                    | kW     |
        | $\mu$         | 2.0                    | %      |

        ### Cálculos Derivados

        | Magnitud                   | Fórmula                                                  | Unidad  |
        |----------------------------|----------------------------------------------------------|---------|
        | Potencia media             | $\bar{P} = \frac{1}{n} \sum P_i $                        | kW      |
        | Energía diaria total       | $E = \sum P_i \cdot \Delta t$                            | kWh |
        | Factor de utilización      | $FU = \frac{\bar{P}}{N \cdot P_{pico}/1000}$             | %       |
        | Potencia máxima registrada | $P_{máx} = \max(P_i)$                                    | kW      |

        ### Referencias y Condiciones de Uso

        - **Datos meteorológicos:** Archivo Excel con columnas: `Fecha`, `Hora`, `Temperatura (°C)`, `Irradiancia (W/m²)`
    """)