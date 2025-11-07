"""
Archivo de configuración centralizado para el análisis bursátil.
Aquí se especifican todos los parámetros necesarios para la ejecución.
Las variables están organizadas según el orden de ejecución del programa.
"""

from datetime import datetime
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()


# ============================================
# 1. CONFIGURACIÓN DE APIs
# ============================================

# API por defecto a usar (opciones: 'yahoo', 'alphavantage')
API_POR_DEFECTO: str = "yahoo"

# Mapeo de símbolos a APIs específicas (opcional)
# Si un símbolo no está aquí, se usará la API por defecto
MAPEO_SIMBOLO_API: Dict[str, str] = {
    # Ejemplo:
    # "AAPL": "yahoo",
    # "MSFT": "alphavantage",
}

# API Keys (desde variables de entorno)
# Las API keys se cargan desde el archivo .env para no exponerlas en GitHub
# Ver .env.example para el formato
ALPHA_VANTAGE_API_KEY: Optional[str] = os.getenv("ALPHA_VANTAGE_API_KEY")


# ============================================
# 2. CONFIGURACIÓN DE TICKERS E ÍNDICES
# ============================================

# Tickers de acciones a extraer
TICKERS_ACCIONES: List[str] = [
    "AAPL",   # Apple 
    "MSFT",   # Microsoft 
    "GOOGL",  # Alphabet 
    "AMZN",   # Amazon
    "TSLA",   # Tesla 
]

# Índices a extraer (usar nombres de src/indices.py o símbolos de Yahoo Finance según la API seleccionada)
INDICES: List[str] = [
    "sp500",      # S&P 500
    "dow_jones",   # Dow Jones Industrial Average
    "nasdaq",     # NASDAQ Composite
    # También se pueden usar símbolos directos de Yahoo Finance:
    #"^GSPC",    # S&P 500
    # "^DJI",     # Dow Jones
    # "^IXIC",    # NASDAQ
    #"GDAXI",     # DAX
    #"^FTSE",     # FTSE 100
    #"^N225",     # Nikkei 225
    #"^HSI",     # Hang Seng Index
    #"SPY",     # SPDR S&P 500 ETF
    #"QQQ",     # Invesco QQQ Trust
    #"^DIA",     # SPDR Dow Jones Industrial Average ETF
    #"^IWM",     # iShares Russell 2000 ETF
]


# ============================================
# 3. CONFIGURACIÓN DE PERÍODOS DE TIEMPO
# ============================================

# Período para extracción de datos históricos
FECHA_INICIO_EXTRACCION: Optional[datetime] = None  # None = 1 año atrás desde hoy
FECHA_FIN_EXTRACCION: Optional[datetime] = None    # None = hoy

# O especificar fechas concretas:
# FECHA_INICIO_EXTRACCION = datetime(2023, 1, 1)
# FECHA_FIN_EXTRACCION = datetime(2024, 12, 31)

# Período para simulación de Monte Carlo (días hacia adelante)
DIAS_MONTE_CARLO: int = 252  # 1 año de trading (252 días hábiles)


# ============================================
# 4. CONFIGURACIÓN DE LIMPIEZA DE DATOS
# ============================================

# Eliminar puntos duplicados por fecha
ELIMINAR_DUPLICADOS: bool = True

# Eliminar outliers basados en desviaciones estándar
ELIMINAR_OUTLIERS: bool = True

# Número de desviaciones estándar para considerar outlier
UMBRAL_OUTLIER: float = 3.0


# ============================================
# 5. CONFIGURACIÓN DE CARTERA
# ============================================

# Nombre de la cartera
NOMBRE_CARTERA: str = "Mi Cartera de Análisis"

# Pesos de cada holding en la cartera (deben sumar 1.0 o menos)
# Si un ticker/índice no está aquí, no se añadirá a la cartera
PESOS_CARTERA: Dict[str, float] = {
    "AAPL": 0.25,
    "MSFT": 0.25,
    "GOOGL": 0.20,
    "AMZN": 0.1,
    "TSLA": 0.10,
    "^GSPC": 0.05,
    "^^IXIC": 0.05,
}


# ============================================
# 6. CONFIGURACIÓN DE MONTE CARLO
# ============================================

# Tipo de simulación de Monte Carlo
# Opciones: 
#   - 'cartera' (simula la cartera completa)
#   - 'accion_individual' (simula una acción específica)
#   - 'todos_los_elementos' (simula todos los holdings de la cartera)
#   - 'seleccion_elementos' (simula una selección específica de holdings)
TIPO_MONTE_CARLO: str = "cartera"

# Símbolo de la acción a simular si TIPO_MONTE_CARLO = 'accion_individual'
# Debe estar en TICKERS_ACCIONES o ser un símbolo válido extraído
SIMBOLO_MONTE_CARLO: Optional[str] = None  # Ejemplo: "AAPL"

# Lista de símbolos a simular si TIPO_MONTE_CARLO = 'seleccion_elementos'
# Deben estar en los datos extraídos
SIMBOLOS_MONTE_CARLO: List[str] = []  # Ejemplo: ["AAPL", "MSFT", "GOOGL"]

# Número de simulaciones de Monte Carlo
NUM_SIMULACIONES_MONTE_CARLO: int = 1000

# Valor inicial para la simulación de Monte Carlo
VALOR_INICIAL_CARTERA: float = 10000.0

# Niveles de confianza para percentiles en Monte Carlo
NIVELES_CONFIANZA: List[float] = [0.05, 0.25, 0.50, 0.75, 0.95]

# Mostrar bandas de confianza en los gráficos de Monte Carlo
MOSTRAR_BANDAS_CONFIANZA: bool = False


# ============================================
# 7. CONFIGURACIÓN DE REPORTES
# ============================================

# Tasa libre de riesgo para cálculos (ej: 0.02 = 2%)
TASA_LIBRE_RIESGO: float = 0.02

# Incluir estadísticas detalladas en el reporte
INCLUIR_ESTADISTICAS: bool = True

# Incluir advertencias en el reporte
INCLUIR_ADVERTENCIAS: bool = True

# Ruta donde guardar los gráficos
RUTA_GUARDADO_GRAFICOS: str = "plots"

# Mostrar gráficos en pantalla (True) o solo guardarlos (False)
MOSTRAR_GRAFICOS: bool = False


# ============================================
# 8. CONFIGURACIÓN DE EXTRACCIÓN PARALELA
# ============================================

# Extraer datos en paralelo (más rápido, pero puede causar rate limiting en algunas APIs)
EXTRACCION_PARALELA: bool = True

# Número máximo de workers paralelos para extracción
# Recomendado: 5 para Yahoo Finance, 1 para Alpha Vantage (debido a rate limits)
MAX_WORKERS_EXTRACCION: int = 5


# ============================================
# 9. CONFIGURACIÓN DE DATOS ADICIONALES
# ============================================

# Tipos de datos adicionales a extraer
EXTRAER_DATOS_FUNDAMENTALES: bool = True
EXTRAER_DIVIDENDOS: bool = False
EXTRAER_INDICADORES_TECNICOS: bool = False

# Indicadores técnicos a calcular (si EXTRAER_INDICADORES_TECNICOS = True)
INDICADORES_TECNICOS: List[str] = [
    "RSI",      # Relative Strength Index
    "MACD",     # Moving Average Convergence Divergence
    "SMA_50",   # Simple Moving Average 50 días
    "SMA_200",  # Simple Moving Average 200 días
    "BB",       # Bollinger Bands
]


# ============================================
# CONFIGURACIONES PREDEFINIDAS (EJEMPLOS)
# ============================================

# Puedes descomentar una de estas configuraciones como punto de partida y añadir los indices y tickets arriba:

# CONFIGURACIÓN CONSERVADORA (Índices y blue chips)
# TICKERS_ACCIONES = ["AAPL", "MSFT", "JNJ", "PG", "KO"]
# INDICES = ["sp500", "dowjones"]
# PESOS_CARTERA = {
#     "AAPL": 0.20, "MSFT": 0.20, "JNJ": 0.15, "PG": 0.15, "KO": 0.10,
#     "^GSPC": 0.20  # S&P 500
# }

# CONFIGURACIÓN TECNOLÓGICA (Sector tech)
# NOMBRE_CARTERA: str = "Mi Cartera de Sector Tech"
# TICKERS_ACCIONES = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA"]
# INDICES = ["nasdaq", "nasdaq100"]
# PESOS_CARTERA = {
#     "AAPL": 0.20, "MSFT": 0.20, "GOOGL": 0.15, "AMZN": 0.15,
#     "META": 0.10, "NVDA": 0.10, "TSLA": 0.10
# }

# CONFIGURACIÓN DIVERSIFICADA (Múltiples sectores)
# NOMBRE_CARTERA: str = "Mi Cartera de Multisectorial"
# TICKERS_ACCIONES = ["AAPL", "JPM", "JNJ", "WMT", "XOM", "TSLA"]
# INDICES = ["sp500", "dowjones", "nasdaq"]
# PESOS_CARTERA = {
#     "AAPL": 0.15, "JPM": 0.15, "JNJ": 0.15, "WMT": 0.15,
#     "XOM": 0.15, "TSLA": 0.10, "^GSPC": 0.15
# }

# CONFIGURACIÓN INTERNACIONAL (Índices globales)
# NOMBRE_CARTERA: str = "Mi Cartera de Indices Globales"
# TICKERS_ACCIONES = ["AAPL", "MSFT"]  # Acciones globales
# INDICES = ["sp500", "ftse100", "dax", "nikkei225"]
# PESOS_CARTERA = {
#     "AAPL": 0.30, "MSFT": 0.30,
#     "^GSPC": 0.20, "^FTSE": 0.10, "^GDAXI": 0.05, "^N225": 0.05
# }



