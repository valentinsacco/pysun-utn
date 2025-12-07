import matplotlib.pyplot as plt
import numpy as np
import pandas as pd 

# --- MODELO MATEMÁTICO ---

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
    # Calculamos la potencia media usando la función que ya tenemos
    potencia_promedio = pot_media(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu, Gstd, Tr)
    
    if Pinv > 0:
        return potencia_promedio / Pinv
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
    """
    p = pot_generada_rango(lista_G, lista_T, N, Ppico, eta, kp, Pinv, mu, Gstd, Tr)

    fig, ax = plt.subplots(figsize=(10, 4))
    x = np.arange(len(p))
    
    # Gráfico de área suave
    ax.fill_between(x, p, color='#ff4b4b', alpha=0.7, label='Potencia AC')
    ax.plot(x, p, color='#ff4b4b', lw=0.2)
    
    ax.grid(True, linestyle='--', alpha=0.3)
    ax.set_title("Potencia Generada (Serie Completa)")
    ax.set_ylabel("Potencia (kW)")
    ax.set_xlabel("Tiempo (muestras de 10 min)")
    
    ax.set_ylim(bottom=0, top=max(np.max(p)*1.1, Pinv*1.1))

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
    Histograma con Doble Eje Y (Horas Reales y Porcentaje).
    """
    fig, ax1 = plt.subplots(figsize=(6, 4))
    
    potencias_activas = [p for p in lista_potencia if p > 0.01]
    if not potencias_activas:
        potencias_activas = [0]
    
    # Pesos para horas reales
    pesos = np.ones_like(potencias_activas) * (10.0 / 60.0)
    total_horas = np.sum(pesos)
    
    # Eje Izquierdo
    counts, bins, patches = ax1.hist(potencias_activas, bins=30, weights=pesos, 
                                     color='#b87d0f', edgecolor='white', alpha=0.9)
    
    ax1.set_xlabel("Potencia (kW)")
    ax1.set_ylabel("Horas Activas (Tiempo Real)", color='white')
    ax1.grid(axis='y', linestyle='--', alpha=0.3)

    # Eje Derecho
    ax2 = ax1.twinx() 
    y1_max = ax1.get_ylim()[1]
    
    if total_horas > 0:
        y2_max = (y1_max / total_horas) * 100
    else:
        y2_max = 100

    ax2.set_ylim(0, y2_max)
    ax2.set_ylabel("Frecuencia Relativa (%)", color='white')
    
    plt.title("Distribución de Potencia")
    
    fig.patch.set_alpha(0.0); ax1.patch.set_alpha(0.0); ax2.patch.set_alpha(0.0)
    ax1.tick_params(axis='x', colors='white'); ax1.tick_params(axis='y', colors='white'); ax2.tick_params(axis='y', colors='white') 
    ax1.xaxis.label.set_color('white'); ax1.title.set_color('white')
    for spine in ax1.spines.values(): spine.set_edgecolor('white')
    ax2.spines['top'].set_visible(False); ax2.spines['left'].set_visible(False); ax2.spines['bottom'].set_visible(False); ax2.spines['right'].set_edgecolor('white')

    return fig

def graficar_impacto_ambiental(lista_potencia, fechas):
    """
    Gráfico de Impacto Ambiental Acumulado (CO2 Evitado).
    """
    fig, ax = plt.subplots(figsize=(10, 4))

    energia_intervalo = np.array(lista_potencia) * (10.0 / 60.0)
    energia_acumulada = np.cumsum(energia_intervalo)
    factor_emision_kg_kwh = 0.45
    co2_acumulado_ton = (energia_acumulada * factor_emision_kg_kwh) / 1000.0

    ax.fill_between(fechas, co2_acumulado_ton, color='#2ecc71', alpha=0.4, label='CO2 Evitado')
    ax.plot(fechas, co2_acumulado_ton, color='#27ae60', lw=2)

    ax.set_title("Impacto Ambiental Acumulado ($CO_2$ Evitado)")
    ax.set_ylabel("Toneladas de $CO_2$")
    ax.set_xlabel("Fecha")
    ax.grid(True, linestyle='--', alpha=0.3)

    fig.patch.set_alpha(0.0); ax.patch.set_alpha(0.0)
    ax.tick_params(colors='white'); ax.xaxis.label.set_color('white'); ax.yaxis.label.set_color('white'); ax.title.set_color('white')
    for spine in ax.spines.values(): spine.set_edgecolor('white')

    total_co2 = co2_acumulado_ton[-1] if len(co2_acumulado_ton) > 0 else 0
    return fig, total_co2

def graficar_mapa_calor(dates, potencias):
    """
    Mapa de Calor (Heatmap): Eje X=Día del año, Eje Y=Hora del día, Color=Potencia.
    """
    fig, ax = plt.subplots(figsize=(10, 5))
    
    df_temp = pd.DataFrame({'Fecha': dates, 'Potencia': potencias})
    df_temp['Hora'] = df_temp['Fecha'].dt.hour
    df_temp['Fecha_Solo'] = df_temp['Fecha'].dt.date
    
    pivot_table = df_temp.pivot_table(index='Hora', columns='Fecha_Solo', values='Potencia', fill_value=0)
    
    cax = ax.imshow(pivot_table, cmap='inferno', aspect='auto', interpolation='nearest')
    
    cbar = fig.colorbar(cax)
    cbar.set_label('Potencia (kW)', color='white')
    cbar.ax.yaxis.set_tick_params(color='white')
    plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='white')

    ax.set_title("Mapa de Calor: Perfil de Generación Anual")
    ax.set_ylabel("Hora del Día")
    ax.set_xlabel("Día del Año")
    ax.invert_yaxis() 

    fig.patch.set_alpha(0.0); ax.patch.set_alpha(0.0)
    ax.tick_params(colors='white'); ax.xaxis.label.set_color('white'); ax.yaxis.label.set_color('white'); ax.title.set_color('white')
    for spine in ax.spines.values(): spine.set_edgecolor('white')

    return fig
