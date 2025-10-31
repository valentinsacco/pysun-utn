# import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from lib.fcn_base import pot_modelo_GFV, pot_generada_rango, graficar_pot
# from lib.data import tabla

# Tratando archivo data.py con numpy y graficándolo
# tabla_matriz = np.array(tabla)
# tabla_transpuesta = tabla_matriz.T
# # fila_G = tabla_transpuesta[0, :107]
# # fila_T = tabla_transpuesta[1, :107]

# # Con paso de 2 (último parámetro)
# fila_G = tabla_transpuesta[0, 0:107:2]
# fila_T = tabla_transpuesta[1, 0:107:2]

# # Desde la 20000 a la última
# fila_G = tabla_transpuesta[0, 20000:]
# fila_T = tabla_transpuesta[1, 20000:]

# graficar_pot(fila_G, fila_T, 12, 240, 0.95, -0.0044, 2.5)

# Leyendo Excel con Pandas
tabla = pd.read_excel('./assets/Datos_climatologicos_Santa_Fe_2019.xlsx', index_col = 0)
# print(tabla)
tabla.plot(x = 'Temperatura (°C)', y = 'Irradiancia (W/m²)', kind='scatter')
plt.show()

# lista_G = [1000, 800, 950]
# lista_T = [25, 30, 28]

# graficar_pot(lista_G, lista_T, 12, 240, 0.95, -0.0044, 2.5)

# p = pot_generada_rango(lista_G, lista_T, 12, 240, 0.95, -0.0044, 2.5)

# p = pot_modelo_GFV(1200, 32, 12, 240, 0.95, -0.0044, 2.5)

# print(p)