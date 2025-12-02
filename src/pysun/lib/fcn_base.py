import matplotlib.pyplot as plt
import numpy as np

def pot_modelo_GFV(G, T, N, Ppico, eta, kp, Pinv, mu = 2, Gstd = 1000, Tr = 25):
    """
    Calcula la potencia generada por un sistema fotovoltaico bajo condiciones específicas.
    """
    Tc = T + 0.031 * G
    P = N * (G / Gstd) * Ppico * (1 + kp * (Tc - Tr)) * eta * 1e-3

    Pmin = (mu / 100) * Pinv

    if P <= Pmin:
        return 0.0
    elif Pmin < P <= Pinv:
        return P
    else:
        return Pinv
    
def pot_generada_rango(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu = 2, Gstd = 1000, Tr = 25):
    """
    Calcula la potencia generada para múltiples pares de irradiancia y temperatura.
    """
    p = []
    # Vectorizamos la operación con zip para eficiencia básica
    for G, T in zip(lista_G, lista_T):
        p.append(pot_modelo_GFV(G, T, N, Ppico, eta, kp, Pinv, mu, Gstd, Tr))
    return np.array(p)

def pot_media(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu=2, Gstd=1000,Tr=25):
    """
    Calcula la potencia media generada.
    """
    lista_potencias = pot_generada_rango(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu, Gstd, Tr)
    if len(lista_potencias) > 0: 
        return np.mean(lista_potencias)
    else:
        return 0.0

def energia(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu=2, Gstd=1000, Tr=25):
    """
    Calcula la energía total generada (kWh).
    """
    lista_potencias = pot_generada_rango(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu, Gstd, Tr)
    suma_potencias = np.sum(lista_potencias)
    intervalo_h = 10.0 / 60.0 # 10 minutos en horas
    energia_total = suma_potencias * intervalo_h
    return energia_total

def factor_de_utilizacion(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu=2, Gstd=1000, Tr=25):
    """
    Calcula el factor de utilización.
    """
    energia_generada = energia(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu, Gstd, Tr)
    numero_de_muestras = len(lista_G)
    intervalo_h = 10.0 / 60.0
    tiempo_total_horas = numero_de_muestras * intervalo_h
    energia_max_posible = Pinv * tiempo_total_horas
    
    if energia_max_posible > 0:
        return energia_generada / energia_max_posible
    else:
        return 0.0
                          
def max_pot(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu=2, Gstd=1000,Tr=25):
    """
    Identifica la potencia máxima generada y su posición.
    """
    lista_potencias = pot_generada_rango(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu, Gstd, Tr)
    
    if len(lista_potencias) == 0: 
        return (0, 0.0)
        
    valor_maximo = np.max(lista_potencias)
    posicion = np.argmax(lista_potencias)
    return (int(posicion), float(valor_maximo))

# --- FUNCIONES DE GRAFICADO ---

def graficar_pot(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu = 2, Gstd = 1000, Tr = 25):
    """
    Genera una gráfica de la variación temporal de la potencia generada (Estático Matplotlib).
    MEJORADO: Usa gráfico de área (fill_between) para evitar saturación visual.
    """
    p = pot_generada_rango(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu, Gstd, Tr)

    fig, ax = plt.subplots(figsize=(10, 4))
    
    # Creamos un índice numérico para el eje X
    x = np.arange(len(p))
    
    # CAMBIO IMPORTANTE: Usamos fill_between en lugar de plot grueso
    # Esto crea una silueta suave de color rojo semitransparente
    ax.fill_between(x, p, color='#ff4b4b', alpha=0.7, label='Potencia AC')
    
    # Dibujamos una línea muy fina en el borde para definición
    ax.plot(x, p, color='#ff4b4b', lw=0.2)
    
    ax.grid(True, linestyle='--', alpha=0.3)
    ax.set_title("Potencia Generada (Serie Completa)")
    ax.set_ylabel("Potencia (kW)")
    ax.set_xlabel("Tiempo (muestras de 10 min)")
    
    # Ajustamos límites verticales para que se vea prolijo
    ax.set_ylim(bottom=0, top=max(np.max(p)*1.1, Pinv*1.1))

    return fig

def graficar_dispersion(lista_G, lista_potencia):
    """
    Gráfico de Dispersión: Irradiancia vs Potencia.
    """
    fig, ax = plt.subplots(figsize=(6, 4))
    # Puntos más pequeños (s=2) y transparentes para ver densidad
    ax.scatter(lista_G, lista_potencia, color='lime', s=2, alpha=0.3, label='Puntos')
    
    ax.set_title("Curva Característica: Irradiancia vs Potencia")
    ax.set_xlabel("Irradiancia Global ($W/m^2$)")
    ax.set_ylabel("Potencia de Salida (kW)")
    ax.grid(True, linestyle='--', alpha=0.3)
    
    # Estilo transparente para modo oscuro
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)
    ax.tick_params(colors='white')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    ax.title.set_color('white')
    for spine in ax.spines.values():
        spine.set_edgecolor('white')
        
    return fig

def graficar_torta(e_real, e_perdida):
    """
    Gráfico de Torta: Energía Aprovechada vs Perdida.
    """
    labels = ['Energía Generada', 'Pérdida por Recorte']
    sizes = [e_real, e_perdida]
    colors = ['#4CAF50', '#F44336'] 
    explode = (0, 0.1) 

    fig, ax = plt.subplots(figsize=(6, 4))
    
    if e_perdida <= 0:
        sizes = [100, 0]
        
    wedges, texts, autotexts = ax.pie(sizes, explode=explode, labels=labels, colors=colors,
                                      autopct='%1.1f%%', shadow=True, startangle=90,
                                      textprops={'color':"white"})
    
    ax.axis('equal')
    ax.set_title("Eficiencia de Conversión (Clipping)")
    
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)
    ax.title.set_color('white')
    
    return fig

def graficar_histograma(lista_potencia):
    """
    Histograma: Distribución de frecuencias de potencia.
    """
    fig, ax = plt.subplots(figsize=(6, 4))
    
    potencias_activas = [p for p in lista_potencia if p > 0.01]
    if not potencias_activas:
        potencias_activas = [0]

    ax.hist(potencias_activas, bins=30, color='orange', edgecolor='white', alpha=0.7)
    
    ax.set_title("Distribución de Potencia (Horas activas)")
    ax.set_xlabel("Potencia (kW)")
    ax.set_ylabel("Frecuencia")
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)
    ax.tick_params(colors='white')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    ax.title.set_color('white')
    for spine in ax.spines.values():
        spine.set_edgecolor('white')

    return fig