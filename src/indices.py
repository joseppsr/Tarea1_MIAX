"""
Módulo para facilitar la importación de índices bursátiles comunes.
Proporciona funciones helper y diccionarios con índices populares.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from .extractor import DataExtractor
from .data_classes import PriceSeries


# Diccionario de índices comunes con sus símbolos en Yahoo Finance
INDICES_COMUNES = {
    # Índices de EE.UU.
    'sp500': {
        'symbol': '^GSPC',
        'name': 'S&P 500',
        'description': 'Índice de las 500 mayores empresas de EE.UU.'
    },
    'dow_jones': {
        'symbol': '^DJI',
        'name': 'Dow Jones Industrial Average',
        'description': 'Índice de 30 empresas industriales líderes'
    },
    'nasdaq': {
        'symbol': '^IXIC',
        'name': 'NASDAQ Composite',
        'description': 'Índice de todas las acciones listadas en NASDAQ'
    },
    'nasdaq100': {
        'symbol': '^NDX',
        'name': 'NASDAQ 100',
        'description': 'Índice de las 100 mayores empresas no financieras de NASDAQ'
    },
    'russell2000': {
        'symbol': '^RUT',
        'name': 'Russell 2000',
        'description': 'Índice de pequeñas capitalizaciones de EE.UU.'
    },
    'vix': {
        'symbol': '^VIX',
        'name': 'CBOE Volatility Index',
        'description': 'Índice de volatilidad del mercado (miedo)'
    },
    
    # Índices internacionales
    'ftse100': {
        'symbol': '^FTSE',
        'name': 'FTSE 100',
        'description': 'Índice de las 100 mayores empresas del Reino Unido'
    },
    'dax': {
        'symbol': '^GDAXI',
        'name': 'DAX',
        'description': 'Índice de las 40 mayores empresas de Alemania'
    },
    'cac40': {
        'symbol': '^FCHI',
        'name': 'CAC 40',
        'description': 'Índice de las 40 mayores empresas de Francia'
    },
    'nikkei225': {
        'symbol': '^N225',
        'name': 'Nikkei 225',
        'description': 'Índice de las 225 mayores empresas de Japón'
    },
    'shanghai': {
        'symbol': '000001.SS',
        'name': 'Shanghai Composite',
        'description': 'Índice principal de la bolsa de Shanghai'
    },
    'hang_seng': {
        'symbol': '^HSI',
        'name': 'Hang Seng Index',
        'description': 'Índice principal de la bolsa de Hong Kong'
    },
    
    # ETFs de índices (alternativas)
    'spy': {
        'symbol': 'SPY',
        'name': 'SPDR S&P 500 ETF',
        'description': 'ETF que replica el S&P 500'
    },
    'qqq': {
        'symbol': 'QQQ',
        'name': 'Invesco QQQ Trust',
        'description': 'ETF que replica el NASDAQ 100'
    },
    'dia': {
        'symbol': 'DIA',
        'name': 'SPDR Dow Jones Industrial Average ETF',
        'description': 'ETF que replica el Dow Jones'
    },
    'iwm': {
        'symbol': 'IWM',
        'name': 'iShares Russell 2000 ETF',
        'description': 'ETF que replica el Russell 2000'
    }
}


def obtener_simbolo_indice(nombre_indice: str) -> Optional[str]:
    """
    Obtiene el símbolo de un índice por su nombre o clave.
    
    Args:
        nombre_indice: Nombre del índice (ej: 'sp500', 'S&P 500', '^GSPC')
    
    Returns:
        Símbolo del índice o None si no se encuentra
    
    Examples:
        >>> obtener_simbolo_indice('sp500')
        '^GSPC'
        >>> obtener_simbolo_indice('S&P 500')
        '^GSPC'
        >>> obtener_simbolo_indice('^GSPC')
        '^GSPC'
    """
    nombre_lower = nombre_indice.lower().strip()
    
    # Si ya es un símbolo (empieza con ^ o es un ticker conocido), devolverlo
    if nombre_indice.startswith('^') or nombre_indice in [idx['symbol'] for idx in INDICES_COMUNES.values()]:
        return nombre_indice
    
    # Buscar por clave
    if nombre_lower in INDICES_COMUNES:
        return INDICES_COMUNES[nombre_lower]['symbol']
    
    # Buscar por nombre
    for clave, info in INDICES_COMUNES.items():
        if nombre_lower in info['name'].lower() or info['name'].lower() in nombre_lower:
            return info['symbol']
    
    return None


def obtener_info_indice(nombre_indice: str) -> Optional[Dict]:
    """
    Obtiene información completa de un índice.
    
    Args:
        nombre_indice: Nombre o clave del índice
    
    Returns:
        Diccionario con información del índice o None
    """
    simbolo = obtener_simbolo_indice(nombre_indice)
    if simbolo is None:
        return None
    
    for clave, info in INDICES_COMUNES.items():
        if info['symbol'] == simbolo:
            return {
                'key': clave,
                **info
            }
    
    return None


def listar_indices_disponibles() -> List[Dict]:
    """
    Lista todos los índices disponibles.
    
    Returns:
        Lista de diccionarios con información de cada índice
    """
    return [
        {
            'key': clave,
            **info
        }
        for clave, info in INDICES_COMUNES.items()
    ]


def importar_indice(
    nombre_indice: str,
    extractor: DataExtractor,
    fecha_inicio: Optional[datetime] = None,
    fecha_fin: Optional[datetime] = None
) -> Optional[PriceSeries]:
    """
    Importa datos históricos de un índice.
    
    Args:
        nombre_indice: Nombre o clave del índice (ej: 'sp500', 'S&P 500', '^GSPC')
        extractor: Extractor de datos a usar
        fecha_inicio: Fecha de inicio (por defecto: 1 año atrás)
        fecha_fin: Fecha de fin (por defecto: hoy)
    
    Returns:
        PriceSeries con los datos del índice o None si hay error
    
    Examples:
        >>> from src.extractor import DataExtractorFactory
        >>> extractor = DataExtractorFactory.get_default_extractor()
        >>> sp500 = importar_indice('sp500', extractor)
        >>> print(f"S&P 500: {len(sp500.data)} puntos de datos")
    """
    simbolo = obtener_simbolo_indice(nombre_indice)
    
    if simbolo is None:
        print(f"[ERROR] No se encontró el índice '{nombre_indice}'")
        print(f"   Índices disponibles: {', '.join(INDICES_COMUNES.keys())}")
        return None
    
    try:
        info = obtener_info_indice(nombre_indice)
        nombre_completo = info['name'] if info else simbolo
        
        print(f"Importando {nombre_completo} ({simbolo})...")
        serie = extractor.fetch_historical_prices(simbolo, fecha_inicio, fecha_fin)
        
        # Actualizar el nombre con el nombre completo del índice
        if info:
            serie.name = info['name']
        
        print(f"[OK] {nombre_completo} importado: {len(serie.data)} puntos de datos")
        return serie
        
    except Exception as e:
        print(f"[ERROR] Error al importar {simbolo}: {e}")
        return None


def importar_indices(
    nombres_indices: List[str],
    extractor: DataExtractor,
    fecha_inicio: Optional[datetime] = None,
    fecha_fin: Optional[datetime] = None,
    paralelo: bool = True,
    max_trabajadores: int = 5
) -> Dict[str, PriceSeries]:
    """
    Importa múltiples índices simultáneamente.
    
    Args:
        nombres_indices: Lista de nombres o claves de índices
        extractor: Extractor de datos a usar
        fecha_inicio: Fecha de inicio
        fecha_fin: Fecha de fin
        paralelo: Si True, importa en paralelo (más rápido). Si False, secuencial.
        max_trabajadores: Número máximo de workers paralelos (solo si paralelo=True)
    
    Returns:
        Diccionario {nombre_indice: PriceSeries} con los datos
    
    Examples:
        >>> extractor = DataExtractorFactory.get_default_extractor()
        >>> indices = importar_indices(['sp500', 'nasdaq', 'dow_jones'], extractor)
        >>> print(f"Índices importados: {list(indices.keys())}")
    """
    resultados = {}
    
    try:
        print(f"\nImportando {len(nombres_indices)} índice(s)...")
    except UnicodeEncodeError:
        print(f"\n[INFO] Importando {len(nombres_indices)} indice(s)...")
    
    if not paralelo:
        # Implementación secuencial
        for nombre in nombres_indices:
            serie = importar_indice(nombre, extractor, fecha_inicio, fecha_fin)
            if serie is not None:
                # Usar el símbolo como clave
                resultados[serie.symbol] = serie
        
        try:
            print(f"\n[OK] {len(resultados)} de {len(nombres_indices)} índices importados exitosamente")
        except UnicodeEncodeError:
            print(f"\n[OK] {len(resultados)} de {len(nombres_indices)} indices importados exitosamente")
        
        return resultados
    
    # Implementación paralela
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    def importar_un_indice(nombre: str) -> tuple:
        """Función auxiliar para importar un índice."""
        try:
            serie = importar_indice(nombre, extractor, fecha_inicio, fecha_fin)
            if serie is not None:
                return (nombre, serie.symbol, serie, None)
            else:
                return (nombre, None, None, f"No se pudo importar {nombre}")
        except Exception as e:
            return (nombre, None, None, str(e))
    
    # Ejecutar en paralelo
    with ThreadPoolExecutor(max_workers=max_trabajadores) as ejecutor:
        futuro_a_nombre = {
            ejecutor.submit(importar_un_indice, nombre): nombre 
            for nombre in nombres_indices
        }
        
        for futuro in as_completed(futuro_a_nombre):
            nombre, simbolo, serie, error = futuro.result()
            
            if serie is not None:
                resultados[simbolo] = serie
                try:
                    print(f"  [OK] {simbolo} ({serie.name}) - {len(serie.data)} puntos")
                except UnicodeEncodeError:
                    print(f"  [OK] {simbolo} ({serie.name}) - {len(serie.data)} puntos")
            else:
                try:
                    print(f"  [ERROR] Error con {nombre}: {error}")
                except UnicodeEncodeError:
                    print(f"  [ERROR] Error con {nombre}: {error}")
    
    try:
        print(f"\n[OK] {len(resultados)} de {len(nombres_indices)} índices importados exitosamente")
    except UnicodeEncodeError:
        print(f"\n[OK] {len(resultados)} de {len(nombres_indices)} indices importados exitosamente")
    
    return resultados


