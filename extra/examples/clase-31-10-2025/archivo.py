import pandas as pd

matriz = [[12, 34, 13], [22, 31,  26]]

# tabla = pd.DataFrame(matriz, columns = ['Temp', 'Irrad', 'Pot'], index = ['10:00', '11:00'])
tabla = pd.read_excel('../clase-24102025/assets/Datos_climatologicos_Santa_Fe_2019.xslx', indesx_col = 0)

print(tabla)

