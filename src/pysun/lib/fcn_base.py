import matplotlib.pyplot as plt
from matplotlib import use
import numpy as np

# use('TgAgg')

def pot_modelo_GFV(G, T, N, Ppico, eta, kp, Pinv, mu = 2, Gstd = 1000, Tr = 25):
    """
    Entradas:
    G: Irradiancia total incidente (W/m2)
    T: Temp. ambiente (°C)
    N:
    Ppico:
    eta: Rendimiento

    Salida:
    Potencia del GFV en kW
    """
    Tc = T + 0.031 * G
    P = N * (G / Gstd) * Ppico * (1 + kp * (Tc - Tr)) * eta * 1e-3

    Pmin = (mu / 100) * Pinv

    if P <= Pmin:
        return 0
    elif Pmin < P <= Pinv:
        return P
    else:
        return Pinv
    
def pot_generada_rango(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu = 2, Gstd = 1000, Tr = 25):
    """"""
    # Simil anterior, pero recibe en lista_G una lista (o vector) con
    # cualquier cantidad de valores de irradiancia, y en lista_T una
    # con igual cantidad de registros de temperatura ambiente.
    # Devuelve otra lista (o contenedor) con las potencias generadas para
    # cada par de valores de irradiancia y temperatura.
    
    p = []

    for G, T in zip(lista_G, lista_T):
        p.append(pot_modelo_GFV(G, T, N, Ppico, eta, kp, Pinv, mu, Gstd, Tr))

    return p

def pot_media(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu=2, Gstd=1000,Tr=25):
    """"""
    # Recibe los mismos argumentos que la función anterior, y devuelve
    # la potencia que resulta de promediar todas las calculadas con
    # cada par de valores de irradiancia y temperatura ambiente.

    lista_potencias = pot_generada_rango(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu, Gstd, Tr)
    
    if lista_potencias: 
        return np.mean(lista_potencias)
    else:
        return 0


def energia(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu=2, Gstd=1000, Tr=25):
    """"""
    # Recibe los mismos argumentos que la función anterior, y devuelve
    # la energía generada por el GFV (en kWh), asumiendo que el intervalo
    # de tiempo transcurrido entre 2 mediciones de irradiancia (o de temp.) es de 10 minutos.

    lista_potencias = pot_generada_rango(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu, Gstd, Tr)
    
    suma_potencias = np.sum(lista_potencias)
    
    intervalo_h = 10 / 60
    
    energia_total = suma_potencias * intervalo_h
    
    return energia_total

def factor_de_utilizacion(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu=2, Gstd=1000, Tr=25):
    """"""
    # Devuelve el factor de utilización de la instalación.
    # Se calcula como la proporción de la energía generada (y calculada
    # igual que en la función anterior),
    # en relación (cociente) a la que podría haber entregado si todo el
    # tiempo hubiera desarrollado la potencia nominal del inversor.

    energia_generada = energia(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu, Gstd, Tr)
    
    numero_de_muestras = len(lista_G)
    intervalo_h = 10 / 60
    tiempo_total_horas = numero_de_muestras * intervalo_h
    
    energia_max_posible = Pinv * tiempo_total_horas
    
    if energia_max_posible > 0:
        factor = energia_generada / energia_max_posible
    else:
        factor = 0
        
    return factor
                          
def max_pot(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu=2, Gstd=1000,Tr=25):
    """"""
    # Devuelve una tupla de 2 elementos. El primero es el la posición
    # (orden) en las listas lista_G y lista_T para el cual se
    # identifica la potencia máxima entregada, y el segundo es el valor
    # de dicha potencia.

    lista_potencias = pot_generada_rango(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu, Gstd, Tr)
    
    if not lista_potencias: 
        return (0, 0)
        
    valor_maximo = np.max(lista_potencias)
    
    posicion = np.argmax(lista_potencias)
    
    return (posicion, valor_maximo)
    
def graficar_pot(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu = 2, Gstd = 1000, Tr = 25):
    """"""
    # Genera una gráfica con la variación temporal de la potencia generada,
    # calculada con los datos de irradiancia y temperatura provistos
    # por lista_G y lista_T, respectivamente. Se asume que el intervalo
    # de tiempo transcurrido entre 2 mediciones de irradiancia (o de temp.)
    # es de 10 minutos. Devuelve una figura de Matplotlib.

    p = pot_generada_rango(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu, Gstd, Tr)

    fig, ax = plt.subplots()
    
    ax.plot(p, lw = 3, c = 'r', ls = '--')
    ax.grid()
    ax.set_title("Potencia Generada")
    ax.set_ylabel("(kW)")
    ax.set_xlabel("Tiempo (muestras de 10 min)")
    
    return fig