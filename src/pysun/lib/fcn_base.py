import matplotlib.pyplot as plt
from matplotlib import use
import numpy as np

def pot_modelo_GFV(G, T, N, Ppico, eta, kp, Pinv, mu = 2, Gstd = 1000, Tr = 25):
    """
    Calcula la potencia generada por un sistema fotovoltaico bajo condiciones específicas.
    
    Implementa el modelo de cálculo de potencia para una instalación generadora
    fotovoltaica (GFV) considerando la irradiancia, temperatura ambiente,
    coeficiente de temperatura y límites de potencia del inversor.
    
    Args:
        G (float): Irradiancia total incidente (W/m²)
        T (float): Temperatura ambiente (°C)
        N (int): Número de paneles
        Ppico (float): Potencia pico del módulo (W)
        eta (float): Rendimiento de la instalación
        kp (float): Coeficiente de temperatura de potencia (1/°C)
        Pinv (float): Potencia nominal del inversor (kW)
        mu (float): Factor de mínima potencia (%). Default: 2
        Gstd (float): Irradiancia estándar de referencia (W/m²). Default: 1000
        Tr (float): Temperatura de referencia (°C). Default: 25
    
    Returns:
        float: Potencia generada (kW). Devuelve 0 si está por debajo de la
               potencia mínima del inversor, o la potencia nominal si excede
               la capacidad máxima del inversor.
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
    """
    Calcula la potencia generada para múltiples pares de irradiancia y temperatura.
    
    Recibe listas de valores de irradiancia y temperatura ambiente, y devuelve
    una lista con las potencias generadas para cada par de valores.
    
    Args:
        lista_G (list): Lista de valores de irradiancia total incidente (W/m²)
        lista_T (list): Lista de valores de temperatura ambiente (°C)
        N (int): Número de paneles
        Ppico (float): Potencia pico del módulo (W)
        eta (float): Rendimiento de la instalación
        kp (float): Coeficiente de temperatura de potencia (1/°C)
        Pinv (float): Potencia nominal del inversor (kW)
        mu (float): Factor de mínima potencia (%). Default: 2
        Gstd (float): Irradiancia estándar (W/m²). Default: 1000
        Tr (float): Temperatura de referencia (°C). Default: 25
    
    Returns:
        list: Lista de potencias generadas (kW) para cada par de entrada
    """
    
    p = []

    for G, T in zip(lista_G, lista_T):
        p.append(pot_modelo_GFV(G, T, N, Ppico, eta, kp, Pinv, mu, Gstd, Tr))

    return p

def pot_media(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu=2, Gstd=1000,Tr=25):
    """
    Calcula la potencia media generada para múltiples pares de irradiancia y temperatura.
    
    Recibe los mismos argumentos que pot_generada_rango y devuelve el promedio
    de todas las potencias calculadas.
    
    Args:
        lista_G (list): Lista de valores de irradiancia total incidente (W/m²)
        lista_T (list): Lista de valores de temperatura ambiente (°C)
        N (int): Número de paneles
        Ppico (float): Potencia pico del módulo (W)
        eta (float): Rendimiento de la instalación
        kp (float): Coeficiente de temperatura de potencia (1/°C)
        Pinv (float): Potencia nominal del inversor (kW)
        mu (float): Factor de mínima potencia (%). Default: 2
        Gstd (float): Irradiancia estándar (W/m²). Default: 1000
        Tr (float): Temperatura de referencia (°C). Default: 25
    
    Returns:
        float: Potencia promedio generada (kW)
    """

    lista_potencias = pot_generada_rango(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu, Gstd, Tr)
    
    if lista_potencias: 
        return np.mean(lista_potencias)
    else:
        return 0


def energia(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu=2, Gstd=1000, Tr=25):
    """
    Calcula la energía total generada por el sistema fotovoltaico.
    
    Recibe los mismos argumentos que pot_generada_rango y devuelve la energía
    generada por el GFV (en kWh), asumiendo que el intervalo de tiempo entre
    mediciones es de 10 minutos.
    
    Args:
        lista_G (list): Lista de valores de irradiancia total incidente (W/m²)
        lista_T (list): Lista de valores de temperatura ambiente (°C)
        N (int): Número de paneles
        Ppico (float): Potencia pico del módulo (W)
        eta (float): Rendimiento de la instalación
        kp (float): Coeficiente de temperatura de potencia (1/°C)
        Pinv (float): Potencia nominal del inversor (kW)
        mu (float): Factor de mínima potencia (%). Default: 2
        Gstd (float): Irradiancia estándar (W/m²). Default: 1000
        Tr (float): Temperatura de referencia (°C). Default: 25
    
    Returns:
        float: Energía total generada (kWh)
    """

    lista_potencias = pot_generada_rango(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu, Gstd, Tr)
    
    suma_potencias = np.sum(lista_potencias)
    
    intervalo_h = 10 / 60
    
    energia_total = suma_potencias * intervalo_h
    
    return energia_total

def factor_de_utilizacion(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu=2, Gstd=1000, Tr=25):
    """
    Calcula el factor de utilización de la instalación fotovoltaica.
    
    Se calcula como la proporción entre la energía generada y la que se podría
    haber entregado si la instalación hubiera operado a potencia nominal del
    inversor durante todo el período de medición.
    
    Args:
        lista_G (list): Lista de valores de irradiancia total incidente (W/m²)
        lista_T (list): Lista de valores de temperatura ambiente (°C)
        N (int): Número de paneles
        Ppico (float): Potencia pico del módulo (W)
        eta (float): Rendimiento de la instalación
        kp (float): Coeficiente de temperatura de potencia (1/°C)
        Pinv (float): Potencia nominal del inversor (kW)
        mu (float): Factor de mínima potencia (%). Default: 2
        Gstd (float): Irradiancia estándar (W/m²). Default: 1000
        Tr (float): Temperatura de referencia (°C). Default: 25
    
    Returns:
        float: Factor de utilización (proporción entre 0 y 1)
    """

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
    """
    Identifica la potencia máxima generada y su posición temporal.
    
    Devuelve una tupla con la posición (índice) en las listas donde se alcanza
    la potencia máxima y el valor de dicha potencia.
    
    Args:
        lista_G (list): Lista de valores de irradiancia total incidente (W/m²)
        lista_T (list): Lista de valores de temperatura ambiente (°C)
        N (int): Número de paneles
        Ppico (float): Potencia pico del módulo (W)
        eta (float): Rendimiento de la instalación
        kp (float): Coeficiente de temperatura de potencia (1/°C)
        Pinv (float): Potencia nominal del inversor (kW)
        mu (float): Factor de mínima potencia (%). Default: 2
        Gstd (float): Irradiancia estándar (W/m²). Default: 1000
        Tr (float): Temperatura de referencia (°C). Default: 25
    
    Returns:
        tuple: Tupla (posicion, potencia_maxima) donde posicion es el índice
               en las listas y potencia_maxima es el valor en kW
    """

    lista_potencias = pot_generada_rango(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu, Gstd, Tr)
    
    if not lista_potencias: 
        return (0, 0)
        
    valor_maximo = np.max(lista_potencias)
    
    posicion = np.argmax(lista_potencias)
    
    return (posicion, valor_maximo)
    
def graficar_pot(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu = 2, Gstd = 1000, Tr = 25):
    """
    Genera una gráfica de la variación temporal de la potencia generada.
    
    Crea una gráfica con la evolución temporal de la potencia generada
    utilizando Matplotlib. Se asume que el intervalo de tiempo entre
    mediciones es de 10 minutos.
    
    Args:
        lista_G (list): Lista de valores de irradiancia total incidente (W/m²)
        lista_T (list): Lista de valores de temperatura ambiente (°C)
        N (int): Número de paneles
        Ppico (float): Potencia pico del módulo (W)
        eta (float): Rendimiento de la instalación
        kp (float): Coeficiente de temperatura de potencia (1/°C)
        Pinv (float): Potencia nominal del inversor (kW)
        mu (float): Factor de mínima potencia (%). Default: 2
        Gstd (float): Irradiancia estándar (W/m²). Default: 1000
        Tr (float): Temperatura de referencia (°C). Default: 25
    
    Returns:
        matplotlib.figure.Figure: Figura con la gráfica de potencia generada
    """

    p = pot_generada_rango(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu, Gstd, Tr)

    fig, ax = plt.subplots()
    
    ax.plot(p, lw = 3, c = 'r', ls = '--')
    ax.grid()
    ax.set_title("Potencia Generada")
    ax.set_ylabel("(kW)")
    ax.set_xlabel("Tiempo (muestras de 10 min)")
    
    return fig