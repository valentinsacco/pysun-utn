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
    