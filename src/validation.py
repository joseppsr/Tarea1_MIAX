"""
Módulo de validación de configuración.
Valida que la configuración del proyecto sea correcta antes de ejecutar.
"""

from typing import List


def validar_configuracion(
    PESOS_CARTERA: dict,
    TICKERS_ACCIONES: List[str],
    INDICES: List[str],
    API_POR_DEFECTO: str,
    ALPHA_VANTAGE_API_KEY: str,
    TIPO_MONTE_CARLO: str,
    SIMBOLO_MONTE_CARLO: str,
    SIMBOLOS_MONTE_CARLO: List[str]
) -> List[str]:
    """
    Valida la configuración y retorna lista de advertencias.
    
    Args:
        PESOS_CARTERA: Diccionario con los pesos de la cartera
        TICKERS_ACCIONES: Lista de tickers de acciones
        INDICES: Lista de índices
        API_POR_DEFECTO: API por defecto a usar
        ALPHA_VANTAGE_API_KEY: API key de Alpha Vantage (puede ser None)
        TIPO_MONTE_CARLO: Tipo de simulación de Monte Carlo
        SIMBOLO_MONTE_CARLO: Símbolo para simulación individual (puede ser None)
        SIMBOLOS_MONTE_CARLO: Lista de símbolos para simulación de selección
    
    Returns:
        Lista de mensajes de advertencia (vacía si todo está bien)
    """
    advertencias = []
    
    # Validar que los pesos sumen <= 1.0
    suma_pesos = sum(PESOS_CARTERA.values())
    if suma_pesos > 1.0:
        advertencias.append(f"[ALERTA] Los pesos de la cartera suman {suma_pesos:.2%}, se normalizarán a 1.0")
    elif suma_pesos < 0.99:
        advertencias.append("[ALERTA] Los pesos de la cartera suman menos del 99%, no es una cartera completa")
    
    # Validar que haya al menos un ticker o índice
    if not TICKERS_ACCIONES and not INDICES:
        advertencias.append("[ALERTA] No se han especificado tickers ni índices para extraer")
    
    # Validar API keys si se usan APIs que las requieren
    if API_POR_DEFECTO == "alphavantage" and not ALPHA_VANTAGE_API_KEY:
        advertencias.append(" [ALERTA] Se usa Alpha Vantage pero no se ha configurado ALPHA_VANTAGE_API_KEY")
    
    # Validar configuración de Monte Carlo
    if TIPO_MONTE_CARLO not in ["cartera", "accion_individual", "todos_los_elementos", "seleccion_elementos"]:
        advertencias.append(f"[ALERTA] TIPO_MONTE_CARLO debe ser 'cartera', 'accion_individual', 'todos_los_elementos' o 'seleccion_elementos', pero se encontró: '{TIPO_MONTE_CARLO}'")
    
    if TIPO_MONTE_CARLO == "accion_individual" and SIMBOLO_MONTE_CARLO is None:
        advertencias.append("[ALERTA] TIPO_MONTE_CARLO es 'accion_individual' pero SIMBOLO_MONTE_CARLO no está configurado")
    
    if TIPO_MONTE_CARLO == "accion_individual" and SIMBOLO_MONTE_CARLO is not None:
        simbolos_disponibles = set(TICKERS_ACCIONES) | set(INDICES)
        if SIMBOLO_MONTE_CARLO not in simbolos_disponibles:
            advertencias.append(f" [ALERTA] SIMBOLO_MONTE_CARLO '{SIMBOLO_MONTE_CARLO}' no está en TICKERS_ACCIONES ni INDICES")
    
    if TIPO_MONTE_CARLO == "seleccion_elementos" and not SIMBOLOS_MONTE_CARLO:
        advertencias.append("[ALERTA] TIPO_MONTE_CARLO es 'seleccion_elementos' pero SIMBOLOS_MONTE_CARLO está vacío")
    
    if TIPO_MONTE_CARLO == "seleccion_elementos" and SIMBOLOS_MONTE_CARLO:
        simbolos_disponibles = set(TICKERS_ACCIONES) | set(INDICES)
        simbolos_invalidos = [s for s in SIMBOLOS_MONTE_CARLO if s not in simbolos_disponibles]
        if simbolos_invalidos:
            advertencias.append(f"[ALERTA] Algunos símbolos en SIMBOLOS_MONTE_CARLO no están disponibles: {', '.join(simbolos_invalidos)}")
    
    # Validar que los símbolos en PESOS_CARTERA existan en TICKERS_ACCIONES o INDICES
    simbolos_configurados = set(TICKERS_ACCIONES) | set(INDICES)
    simbolos_cartera = set(PESOS_CARTERA.keys())
    simbolos_no_encontrados = simbolos_cartera - simbolos_configurados
    
    if simbolos_no_encontrados:
        advertencias.append(
            f"[ALERTA] Los siguientes símbolos están en PESOS_CARTERA pero no en TICKERS_ACCIONES ni INDICES: "
            f"{', '.join(simbolos_no_encontrados)}"
        )
    
    return advertencias

