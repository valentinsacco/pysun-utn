# ![PySun Brand](https://raw.githubusercontent.com/valentinsacco/pysun-utn/refs/heads/main/img/pysun-logo.png)

# Generación Fotovoltaica Interactiva.

### Simula y Analiza Sistemas de Generación Fotovoltáica Distribuida.

## Descripción General

**PySun** es una **aplicación web interactiva desarrollada en Python con Streamlit** que permite **modelar y simular el desempeño de un generador fotovoltaico (GFV)** bajo diferentes configuraciones técnicas y condiciones climatológicas.

La plataforma ofrece un **dashboard intuitivo** con indicadores clave, gráficos interactivos y la posibilidad de cargar datos meteorológicos reales (en formatos .csv, .xls, .xlsx) para estimar con precisión:

- Potencia instantánea generada
- Energía acumulada en periodos configurables
- Rendimiento del sistema según parámetros técnicos

## Objetivos

Desarrollar una herramienta educativa y técnica que permita:

- Configurar sistemas fotovoltaicos con distintos paneles, inversores y condiciones de instalación.
- Analizar el impacto de la irradiación solar, temperatura ambiente e inclinación en la generación.
- Visualizar resultados mediante indicadores (<10) y gráficos interactivos (≤4, con zoom en al menos uno).
- Facilitar la comprensión del modelado físico de GFVs mediante una interfaz clara y documentada.

## Estructura del Repositorio

```
root/
├── src/pysun
│   ├── main.py                 # Aplicación principal Streamlit
│   ├── lib/ 
│   │   └── fcn_base.py         # Funciones base (cálculos FV y graficación)
│   └── screens/
│       ├── docs.py             # Pestaña de documentación técnica
│       ├── home.py             # Pestaña de inicio
│       └── simulator.py        # Pestaña de carga de datos y simulación, con devolución de gráficas y resultados
├── extra/
│   └── examples/...            # Ejemplos de clases de la materia
├── img/
│   ├── pysun-logo.png          # Logo oficial del proyecto
│   └── pysun-logo.svg
├── memoria_descriptiva.pdf     # Documentación del proyecto
├── requirements.txt
└── README.md                   # Este archivo
```

## Bitácora Grupal

### DESARROLLADORES
- Valentín Sacco, vasacco1@gmail.com
- Tomás Broggi, tomasbroggitw@gmail.com

### TAREAS

| Tarea | Desarrollador | Completada |
| --- | --- | --- |
| Implementar fcn_base.py | Tomás Broggi | [x] |
| Modificar README.md del proyecto | Valentin Sacco | [x] |
| Estructurar el estilo de la página de inicio y de la pestaña documentación + creación de pestaña de simulación | Valentín Sacco | [x] |
| Desarrollo de la aplicación | Valentín Sacco y Tomás Broggi | [x] |
| Redesarrollo de la aplicación (vuelta a empezar) | Tomás Broggi | [x] |
| Mejoras de la etapa preliminar 2 sugeridas por el docente | Tomás Broggi | [x] |

### REUNIONES

- Jueves 06/11/25 - 17:00 [hs]
- Jueves 13/11/25 - 20:00 [hs]
- Miércoles 26/11/25 - 22:00 [hs]
- Jueves 27/11/25 - 15:30 [hs]
- Viernes 28/11/25 - 11:00 [hs]