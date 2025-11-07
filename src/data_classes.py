"""
DataClasses para representar series de precios históricos y portfolios.
Proporciona un formato estandarizado independiente de la fuente de datos.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
import pandas as pd
import numpy as np
from datetime import timedelta
try:
    from scipy import stats
except ImportError:
    stats = None


@dataclass
class PricePoint:
    """Representa un punto de precio en el tiempo."""
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: Optional[int] = None
    
    def __post_init__(self):
        """Validación de datos después de la inicialización."""
        if self.high < self.low:
            raise ValueError("High price cannot be lower than low price")
        if not (self.low <= self.open <= self.high):
            raise ValueError("Open price must be between low and high")
        if not (self.low <= self.close <= self.high):
            raise ValueError("Close price must be between low and high")


@dataclass
class PriceSeries:
    """
    Serie temporal de precios estandarizada.
    Formato de salida uniforme independiente de la fuente de datos.
    """
    symbol: str
    name: str
    data: List[PricePoint] = field(default_factory=list)
    source: str = "unknown"
    currency: str = "USD"
    
    # Estadísticas calculadas automáticamente
    _mean_return: Optional[float] = field(default=None, init=False, repr=False)
    _std_return: Optional[float] = field(default=None, init=False, repr=False)
    _returns: Optional[pd.Series] = field(default=None, init=False, repr=False)
    
    def __post_init__(self):
        """Calcula estadísticas básicas automáticamente."""
        if self.data:
            self._calculate_statistics()
    
    def _calculate_statistics(self) -> None:
        """Calcula media y desviación típica de los retornos automáticamente."""
        if len(self.data) < 2:
            return
        
        # Calcular retornos logarítmicos
        cierres = [punto.close for punto in sorted(self.data, key=lambda x: x.date)]
        retornos = np.diff(np.log(cierres))
        
        self._returns = pd.Series(retornos)
        self._mean_return = float(np.mean(retornos))
        self._std_return = float(np.std(retornos))
    
    @property
    def mean_return(self) -> Optional[float]:
        """Retorna la media de los retornos."""
        if self._mean_return is None and self.data:
            self._calculate_statistics()
        return self._mean_return
    
    @property
    def std_return(self) -> Optional[float]:
        """Retorna la desviación típica de los retornos."""
        if self._std_return is None and self.data:
            self._calculate_statistics()
        return self._std_return
    
    @property
    def returns(self) -> Optional[pd.Series]:
        """Retorna la serie de retornos."""
        if self._returns is None and self.data:
            self._calculate_statistics()
        return self._returns
    
    def add_data_point(self, punto: PricePoint) -> None:
        """Añade un punto de datos y recalcula estadísticas."""
        self.data.append(punto)
        self._calculate_statistics()
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convierte la serie a un DataFrame de pandas."""
        if not self.data:
            return pd.DataFrame()
        
        datos_ordenados = sorted(self.data, key=lambda x: x.date)
        df = pd.DataFrame([{
            'date': punto.date,
            'open': punto.open,
            'high': punto.high,
            'low': punto.low,
            'close': punto.close,
            'volume': punto.volume
        } for punto in datos_ordenados])
        
        df.set_index('date', inplace=True)
        return df
    
    def get_period(self) -> Optional[tuple]:
        """Retorna la tupla (fecha_inicio, fecha_fin) del período."""
        if not self.data:
            return None
        fechas = [punto.date for punto in self.data]
        return (min(fechas), max(fechas))
    
    def get_latest_price(self) -> Optional[float]:
        """Retorna el precio de cierre más reciente."""
        if not self.data:
            return None
        datos_ordenados = sorted(self.data, key=lambda x: x.date)
        return datos_ordenados[-1].close
    
    def get_price_at_date(self, fecha: datetime) -> Optional[float]:
        """Retorna el precio de cierre en una fecha específica."""
        for punto in self.data:
            if punto.date.date() == fecha.date():
                return punto.close
        return None
    
    def annualized_return(self) -> Optional[float]:
        """Calcula el retorno anualizado."""
        if not self.data or len(self.data) < 2:
            return None
        
        datos_ordenados = sorted(self.data, key=lambda x: x.date)
        precio_inicial = datos_ordenados[0].close
        precio_final = datos_ordenados[-1].close
        dias = (datos_ordenados[-1].date - datos_ordenados[0].date).days
        
        if dias == 0:
            return None
        
        años = dias / 365.25
        retorno_total = np.log(precio_final / precio_inicial)
        return float(retorno_total / años) if años > 0 else None
    
    def volatility(self, anualizado: bool = True) -> Optional[float]:
        """Calcula la volatilidad (desviación típica de retornos)."""
        if self.std_return is None:
            return None
        
        if anualizado:
            # Asumiendo 252 días de trading por año
            return float(self.std_return * np.sqrt(252))
        return self.std_return
    
    def sharpe_ratio(self, tasa_libre_riesgo: float = 0.02) -> Optional[float]:
        """Calcula el ratio de Sharpe."""
        ret_anual = self.annualized_return()
        vol_anual = self.volatility()
        
        if ret_anual is None or vol_anual is None or vol_anual == 0:
            return None
        
        return float((ret_anual - tasa_libre_riesgo) / vol_anual)
    
    def max_drawdown(self) -> Optional[float]:
        """Calcula el máximo drawdown."""
        if not self.data:
            return None
        
        datos_ordenados = sorted(self.data, key=lambda x: x.date)
        cierres = [punto.close for punto in datos_ordenados]
        
        pico = cierres[0]
        max_dd = 0.0
        
        for precio in cierres:
            if precio > pico:
                pico = precio
            dd = (pico - precio) / pico
            if dd > max_dd:
                max_dd = dd
        
        return float(max_dd)
    
    def clean_data(self, eliminar_duplicados: bool = True, 
                   eliminar_outliers: bool = True, 
                   umbral_outlier: float = 3.0) -> 'PriceSeries':
        """
        Limpia y preprocesa los datos.
        
        Args:
            eliminar_duplicados: Eliminar puntos duplicados por fecha
            eliminar_outliers: Eliminar outliers basados en desviaciones estándar
            umbral_outlier: Número de desviaciones estándar para considerar outlier
        """
        if not self.data:
            return self
        
        # Paso 1: Eliminar puntos con valores None o NaN
        datos_validos = []
        puntos_eliminados_nan = 0
        for punto in self.data:
            # Verificar que todos los precios sean válidos (no None, no NaN)
            precios_validos = (
                punto.close is not None and not np.isnan(punto.close) and
                punto.open is not None and not np.isnan(punto.open) and
                punto.high is not None and not np.isnan(punto.high) and
                punto.low is not None and not np.isnan(punto.low) and
                punto.close > 0 and punto.open > 0 and punto.high > 0 and punto.low > 0
            )
            
            if precios_validos:
                datos_validos.append(punto)
            else:
                puntos_eliminados_nan += 1
        
        if puntos_eliminados_nan > 0:
            try:
                print(f"  [!] {puntos_eliminados_nan} punto(s) eliminado(s) por valores None/NaN/inválidos")
            except UnicodeEncodeError:
                print(f"  [!] {puntos_eliminados_nan} punto(s) eliminado(s) por valores None/NaN/invalidos")
        
        self.data = datos_validos
        
        if not self.data:
            try:
                print(f"  [!] Todos los datos fueron eliminados por valores inválidos")
            except UnicodeEncodeError:
                print(f"  [!] Todos los datos fueron eliminados por valores invalidos")
            return self
        
        # Paso 2: Eliminar duplicados
        if eliminar_duplicados:
            fechas_vistas = set()
            datos_unicos = []
            for punto in sorted(self.data, key=lambda x: x.date):
                if punto.date.date() not in fechas_vistas:
                    fechas_vistas.add(punto.date.date())
                    datos_unicos.append(punto)
            self.data = datos_unicos
        
        # Eliminar outliers
        if eliminar_outliers and len(self.data) > 2:
            if self.std_return is not None:
                retornos = self.returns
                if retornos is not None:
                    media = self.mean_return
                    desv = self.std_return
                    
                    if media is not None and desv is not None:
                        # Filtrar puntos cuyos retornos sean outliers
                        indices_validos = []
                        for i, punto in enumerate(sorted(self.data, key=lambda x: x.date)):
                            if i == 0:
                                indices_validos.append(0)
                            else:
                                cierre_previo = sorted(self.data, key=lambda x: x.date)[i-1].close
                                ret = np.log(punto.close / cierre_previo)
                                if abs(ret - media) <= umbral_outlier * desv:
                                    indices_validos.append(i)
                        
                        datos_ordenados = sorted(self.data, key=lambda x: x.date)
                        self.data = [datos_ordenados[i] for i in indices_validos if i < len(datos_ordenados)]
        
        # Recalcular estadísticas
        self._calculate_statistics()
        return self
    
    def monte_carlo_simulation(self, 
                               dias: int = 252, 
                               simulaciones: int = 1000,
                               precio_inicial: Optional[float] = None,
                               niveles_confianza: List[float] = None) -> Dict[str, Any]:
        """
        Simulación de Monte Carlo para la evolución del precio de un valor individual.
        
        Args:
            dias: Días a simular hacia adelante
            simulaciones: Número de simulaciones
            precio_inicial: Precio inicial (por defecto usa el último precio disponible)
            niveles_confianza: Niveles de confianza para percentiles (ej: [0.05, 0.95])
        
        Returns:
            Diccionario con resultados de la simulación
        """
        if niveles_confianza is None:
            niveles_confianza = [0.05, 0.25, 0.50, 0.75, 0.95]
        
        if not self.data or len(self.data) < 2:
            raise ValueError("No hay datos suficientes para la simulación")
        
        if self.mean_return is None or self.std_return is None:
            raise ValueError("No se pueden calcular estadísticas de retornos")
        
        if precio_inicial is None:
            precio_inicial = self.get_latest_price()
            if precio_inicial is None:
                raise ValueError("No se puede determinar el precio inicial")
        
        # Usar retornos logarítmicos para la simulación
        retorno_medio = self.mean_return
        desv_retorno = self.std_return
        
        if desv_retorno == 0 or np.isnan(desv_retorno):
            raise ValueError("No hay suficiente variabilidad en los retornos")
        
        # Simular trayectorias
        trayectorias_simuladas = []
        for _ in range(simulaciones):
            # Generar retornos aleatorios logarítmicos
            retornos_aleatorios = np.random.normal(retorno_medio, desv_retorno, dias)
            
            # Calcular precio final usando retornos logarítmicos
            precio_final = precio_inicial * np.exp(np.sum(retornos_aleatorios))
            trayectorias_simuladas.append(precio_final)
        
        trayectorias_simuladas = np.array(trayectorias_simuladas)
        
        # Calcular estadísticas
        resultados = {
            'simulations': simulaciones,
            'days': dias,
            'initial_price': precio_inicial,
            'mean_final_price': float(np.mean(trayectorias_simuladas)),
            'std_final_price': float(np.std(trayectorias_simuladas)),
            'min_final_price': float(np.min(trayectorias_simuladas)),
            'max_final_price': float(np.max(trayectorias_simuladas)),
            'percentiles': {},
            'simulated_paths': trayectorias_simuladas,
            'expected_return': float((np.mean(trayectorias_simuladas) - precio_inicial) / precio_inicial)
        }
        
        # Calcular percentiles
        for nivel in niveles_confianza:
            valor_percentil = np.percentile(trayectorias_simuladas, nivel * 100)
            resultados['percentiles'][f'p{int(nivel*100)}'] = float(valor_percentil)
        
        return resultados
    
    def plot_monte_carlo(self, 
                        dias: int = 252, 
                        simulaciones: int = 1000,
                        precio_inicial: Optional[float] = None,
                        mostrar: bool = True,
                        mostrar_bandas: bool = False) -> None:
        """
        Muestra visualmente el resultado de la simulación de Monte Carlo para un valor individual.
        """
        try:
            import matplotlib.pyplot as plt
            import matplotlib.dates as mdates
        except ImportError:
            print("matplotlib no está instalado. Instálalo con: pip install matplotlib")
            return
        
        resultados = self.monte_carlo_simulation(dias, simulaciones, precio_inicial)
        
        # Crear figura
        figura, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Gráfico 1: Distribución de precios finales
        ax1.hist(resultados['simulated_paths'], bins=50, alpha=0.7, edgecolor='black')
        ax1.axvline(resultados['mean_final_price'], color='red', linestyle='--', 
                   label=f'Media: ${resultados["mean_final_price"]:,.2f}')
        ax1.axvline(resultados['percentiles']['p50'], color='green', linestyle='--',
                   label=f'Mediana: ${resultados["percentiles"]["p50"]:,.2f}')
        ax1.set_xlabel('Precio Final')
        ax1.set_ylabel('Frecuencia')
        ax1.set_title(f'Distribución de Precios Finales - {self.symbol} ({simulaciones} simulaciones)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Gráfico 2: Trayectorias de muestra
        if self.data:
            datos_ordenados = sorted(self.data, key=lambda x: x.date)
            ultima_fecha = datos_ordenados[-1].date
            
            # Mostrar algunas trayectorias de muestra
            for i in range(min(100, simulaciones)):
                retornos_aleatorios = np.random.normal(
                    self.mean_return,
                    self.std_return,
                    dias
                )
                trayectoria = [resultados['initial_price']]
                for ret in retornos_aleatorios:
                    trayectoria.append(trayectoria[-1] * np.exp(ret))
                
                fechas = pd.date_range(
                    start=ultima_fecha,
                    periods=dias+1,
                    freq='D'
                )
                ax2.plot(fechas, trayectoria, alpha=0.1, color='blue')
            
            # Calcular y mostrar trayectorias de referencia que evolucionan en el tiempo
            if stats is None:
                # Si scipy no está disponible, usar aproximación con numpy
                def norm_ppf(p):
                    return np.sqrt(2) * np.erfinv(2 * p - 1)
            else:
                norm_ppf = stats.norm.ppf
            
            precio_inicial = resultados['initial_price']
            
            # Trayectoria de la media esperada (evoluciona con el tiempo usando retornos logarítmicos)
            trayectoria_media = [precio_inicial]
            for t in range(1, dias + 1):
                # Valor esperado usando retornos logarítmicos: P0 * exp(μ * t)
                # donde μ es el retorno medio logarítmico diario
                valor_esperado = precio_inicial * np.exp(self.mean_return * t)
                trayectoria_media.append(valor_esperado)
            
            ax2.plot(fechas, trayectoria_media, color='red', linestyle='--', linewidth=2.5,
                    label=f'Media esperada', alpha=0.9)
            
            # Diccionario para almacenar trayectorias de percentiles
            trayectorias_percentiles = {}
            
            # Trayectorias de percentiles que evolucionan en el tiempo
            if 'percentiles' in resultados:
                # Calcular percentiles en cada punto del tiempo usando distribución log-normal
                for percentil_key, percentil_valor in resultados['percentiles'].items():
                    nivel = int(percentil_key[1:]) / 100.0
                    
                    # Calcular z-score para este percentil
                    z_score = norm_ppf(nivel)
                    
                    # Calcular trayectoria del percentil
                    trayectoria_percentil = [precio_inicial]
                    for t in range(1, dias + 1):
                        # Valor esperado en tiempo t (log-normal)
                        valor_esperado_t = precio_inicial * np.exp(self.mean_return * t)
                        # Valor del percentil en tiempo t
                        # Para log-normal: P_t = P0 * exp(μ*t + σ*√t*z)
                        valor_percentil_t = precio_inicial * np.exp(self.mean_return * t + self.std_return * np.sqrt(t) * z_score)
                        trayectoria_percentil.append(valor_percentil_t)
                    
                    trayectorias_percentiles[nivel] = trayectoria_percentil
                    
                    # Elegir color y estilo según el percentil
                    if nivel == 0.5:
                        color = 'orange'
                        estilo = '--'
                        grosor = 2
                        etiqueta = f'Mediana (50%)'
                    elif nivel == 0.05:
                        color = 'purple'
                        estilo = ':'
                        grosor = 1.5
                        etiqueta = f'Percentil 5%'
                    elif nivel == 0.95:
                        color = 'brown'
                        estilo = ':'
                        grosor = 1.5
                        etiqueta = f'Percentil 95%'
                    else:
                        color = 'gray'
                        estilo = '-.'
                        grosor = 1
                        etiqueta = f'Percentil {int(nivel*100)}%'
                    
                    ax2.plot(fechas, trayectoria_percentil, color=color, linestyle=estilo, 
                            linewidth=grosor, label=etiqueta, alpha=0.7)
            
            # Añadir trayectorias extremas (1% y 99%) si no están en los percentiles calculados
            if 0.01 not in trayectorias_percentiles:
                z_score_01 = norm_ppf(0.01)
                trayectoria_01 = [precio_inicial]
                for t in range(1, dias + 1):
                    valor_percentil_t = precio_inicial * np.exp(self.mean_return * t + self.std_return * np.sqrt(t) * z_score_01)
                    trayectoria_01.append(valor_percentil_t)
                trayectorias_percentiles[0.01] = trayectoria_01
                ax2.plot(fechas, trayectoria_01, color='darkred', linestyle='-.', linewidth=1.5,
                        label='Peor caso (1%)', alpha=0.6)
            
            if 0.99 not in trayectorias_percentiles:
                z_score_99 = norm_ppf(0.99)
                trayectoria_99 = [precio_inicial]
                for t in range(1, dias + 1):
                    valor_percentil_t = precio_inicial * np.exp(self.mean_return * t + self.std_return * np.sqrt(t) * z_score_99)
                    trayectoria_99.append(valor_percentil_t)
                trayectorias_percentiles[0.99] = trayectoria_99
                ax2.plot(fechas, trayectoria_99, color='darkgreen', linestyle='-.', linewidth=1.5,
                        label='Mejor caso (99%)', alpha=0.6)
            
            # Añadir bandas de confianza (áreas sombreadas) si está habilitado
            if mostrar_bandas:
                # Banda de confianza 90% (entre p5 y p95)
                if 0.05 in trayectorias_percentiles and 0.95 in trayectorias_percentiles:
                    ax2.fill_between(fechas, trayectorias_percentiles[0.05], trayectorias_percentiles[0.95],
                                    alpha=0.15, color='blue', label='Intervalo 90% (5%-95%)')
                
                # Banda de confianza 50% (entre p25 y p75)
                if 0.25 in trayectorias_percentiles and 0.75 in trayectorias_percentiles:
                    ax2.fill_between(fechas, trayectorias_percentiles[0.25], trayectorias_percentiles[0.75],
                                    alpha=0.25, color='orange', label='Intervalo 50% (25%-75%)')
            
            # Línea del precio inicial (horizontal de referencia)
            ax2.axhline(y=precio_inicial, color='green', linestyle=':', linewidth=1.5,
                       label=f'Precio inicial: ${precio_inicial:,.2f}', alpha=0.6)
        
        ax2.set_xlabel('Fecha')
        ax2.set_ylabel('Precio')
        ax2.set_title(f'Trayectorias de Muestra - {self.symbol} (Monte Carlo)')
        ax2.legend(loc='best', fontsize=8)
        ax2.grid(True, alpha=0.3)
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        
        plt.tight_layout()
        
        if mostrar:
            plt.show()
        else:
            # Guardar en la carpeta plots si existe, sino en el directorio actual
            import os
            ruta_guardado = 'plots' if os.path.exists('plots') else '.'
            nombre_archivo = os.path.join(ruta_guardado, f'monte_carlo_{self.symbol}.png')
            plt.savefig(nombre_archivo, dpi=300, bbox_inches='tight')
            plt.close()

