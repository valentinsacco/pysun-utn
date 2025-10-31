import numpy as np
import matplotlib.pyplot as plt
from matplotlib import use

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

    p = []

    for G, T in zip(lista_G, lista_T):
        p.append(pot_modelo_GFV(G, T, N, Ppico, eta, kp, Pinv, mu, Gstd, Tr))

    return p

def pot_media(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu = 2, Gstd = 1000, Tr = 25):
    """"""
    return np.mean(pot_generada_rango(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu, Gstd, Tr))

def energia(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu = 2, Gstd = 1000, Tr = 25):
    """
    Retorna la energía (en kWh) promedio generada por un panel solar
    asumiendo que el tiempo transcurrido entre mediciones es de 10 minutos
    """
    return pot_media(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu, Gstd, Tr) * 10 / 3600
    

def graficar_pot(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu = 2, Gstd = 1000, Tr = 25):
    """"""

    p = pot_generada_rango(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu, Gstd, Tr)

    plt.plot(p, lw = 3, c = 'r', ls = '--')
    plt.grid()
    plt.title("Potencia Generada")
    plt.ylabel('(kW)')
    plt.xlabel('Tiempo')
    plt.show()