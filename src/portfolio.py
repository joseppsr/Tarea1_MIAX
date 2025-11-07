"""
Clase Portfolio para gestionar carteras de valores.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
import pandas as pd
import numpy as np
try:
    from scipy import stats
except ImportError:
    stats = None
from .data_classes import PriceSeries, PricePoint


@dataclass
class Portfolio:
    """
    Representa una cartera de valores.
    Una cartera es una colección de series de precios con pesos asignados.
    """
    name: str
    holdings: Dict[str, float] = field(default_factory=dict)  # symbol -> weight
    price_series: Dict[str, PriceSeries] = field(default_factory=dict)
    
    def add_holding(self, simbolo: str, peso: float, serie_precios: PriceSeries) -> None:
        """
        Añade un holding a la cartera.
        
        Args:
            simbolo: Símbolo del valor
            peso: Peso en la cartera (0-1)
            serie_precios: Serie de precios del valor
        """
        if peso < 0 or peso > 1:
            raise ValueError("Weight must be between 0 and 1")
        
        self.holdings[simbolo] = peso
        self.price_series[simbolo] = serie_precios
    
        # Normalizar pesos si suman más de 1
        peso_total = sum(self.holdings.values())
        if peso_total > 1:
            for simbolo in self.holdings:
                self.holdings[simbolo] /= peso_total
    
    def remove_holding(self, simbolo: str) -> None:
        """Elimina un holding de la cartera."""
        if simbolo in self.holdings:
            del self.holdings[simbolo]
        if simbolo in self.price_series:
            del self.price_series[simbolo]
    
    def get_portfolio_returns(self) -> Optional[pd.Series]:
        """
        Calcula los retornos de la cartera como combinación ponderada.
        """
        if not self.holdings:
            return None
        
        # Obtener el rango de fechas común
        fechas_comunes = None
        for serie in self.price_series.values():
            fechas = {punto.date.date() for punto in serie.data}
            if fechas_comunes is None:
                fechas_comunes = fechas
            else:
                fechas_comunes = fechas_comunes.intersection(fechas)
        
        if not fechas_comunes:
            return None
        
        # Calcular retornos individuales
        diccionario_retornos = {}
        for simbolo, serie in self.price_series.items():
            if simbolo not in self.holdings:
                continue
            
            datos_ordenados = sorted(serie.data, key=lambda x: x.date)
            cierres = pd.Series(
                {punto.date.date(): punto.close 
                 for punto in datos_ordenados if punto.date.date() in fechas_comunes}
            )
            cierres = cierres.sort_index()
            retornos = cierres.pct_change().dropna()
            diccionario_retornos[simbolo] = retornos
        
        # Combinar retornos ponderados
        if not diccionario_retornos:
            return None
        
        retornos_cartera = pd.Series(0.0, index=diccionario_retornos[list(diccionario_retornos.keys())[0]].index)
        
        for simbolo, retornos in diccionario_retornos.items():
            peso = self.holdings[simbolo]
            retornos_cartera += peso * retornos
        
        return retornos_cartera
    
    def get_portfolio_value_series(self, valor_inicial: float = 10000.0) -> Optional[pd.Series]:
        """
        Calcula la serie de valores de la cartera a lo largo del tiempo.
        
        Args:
            valor_inicial: Valor inicial de la cartera
        """
        retornos = self.get_portfolio_returns()
        if retornos is None or len(retornos) == 0:
            return None
        
        # Calcular valor acumulado
        valores = [valor_inicial]
        for ret in retornos:
            valores.append(valores[-1] * (1 + ret))
        
        # Crear serie con fechas
        fechas = list(retornos.index)
        # Añadir fecha inicial (un día antes del primer retorno)
        if len(fechas) > 0:
            primera_fecha = pd.to_datetime(fechas[0])
            fecha_inicial = primera_fecha - pd.Timedelta(days=1)
            fechas = [fecha_inicial] + fechas
        else:
            fechas = [datetime.now()] * (len(valores))
        
        return pd.Series(valores, index=fechas)
    
    def monte_carlo_simulation(self, 
                               dias: int = 252, 
                               simulaciones: int = 1000,
                               valor_inicial: float = 10000.0,
                               niveles_confianza: List[float] = None) -> Dict[str, Any]:
        """
        Simulación de Monte Carlo para la evolución de la cartera.
        
        Args:
            dias: Días a simular hacia adelante
            simulaciones: Número de simulaciones
            valor_inicial: Valor inicial de la cartera
            niveles_confianza: Niveles de confianza para percentiles (ej: [0.05, 0.95])
        
        Returns:
            Diccionario con resultados de la simulación
        """
        if niveles_confianza is None:
            niveles_confianza = [0.05, 0.25, 0.50, 0.75, 0.95]
        
        retornos_cartera = self.get_portfolio_returns()
        if retornos_cartera is None or len(retornos_cartera) == 0:
            raise ValueError("No hay datos suficientes para la simulación")
        
        # Calcular parámetros de la distribución
        retorno_medio = retornos_cartera.mean()
        desv_retorno = retornos_cartera.std()
        
        if desv_retorno == 0 or np.isnan(desv_retorno):
            raise ValueError("No hay suficiente variabilidad en los retornos")
        
        # Simular trayectorias
        trayectorias_simuladas = []
        for _ in range(simulaciones):
            # Generar retornos aleatorios
            retornos_aleatorios = np.random.normal(retorno_medio, desv_retorno, dias)
            
            # Calcular valor final
            valor_final = valor_inicial * np.prod(1 + retornos_aleatorios)
            trayectorias_simuladas.append(valor_final)
        
        trayectorias_simuladas = np.array(trayectorias_simuladas)
        
        # Calcular estadísticas
        resultados = {
            'simulations': simulaciones,
            'days': dias,
            'initial_value': valor_inicial,
            'mean_final_value': float(np.mean(trayectorias_simuladas)),
            'std_final_value': float(np.std(trayectorias_simuladas)),
            'min_final_value': float(np.min(trayectorias_simuladas)),
            'max_final_value': float(np.max(trayectorias_simuladas)),
            'percentiles': {},
            'simulated_paths': trayectorias_simuladas
        }
        
        # Calcular percentiles
        for nivel in niveles_confianza:
            valor_percentil = np.percentile(trayectorias_simuladas, nivel * 100)
            resultados['percentiles'][f'p{int(nivel*100)}'] = float(valor_percentil)
        
        return resultados
    
    def plot_monte_carlo(self, 
                        dias: int = 252, 
                        simulaciones: int = 1000,
                        valor_inicial: float = 10000.0,
                        mostrar: bool = True,
                        show: bool = None,
                        show_plot: bool = None,
                        mostrar_bandas: bool = False) -> None:
        """
        Muestra visualmente el resultado de la simulación de Monte Carlo.
        
        Args:
            dias: Días a simular
            simulaciones: Número de simulaciones
            valor_inicial: Valor inicial
            mostrar: Si mostrar el gráfico (por defecto True)
            show: Alias para 'mostrar' (compatibilidad)
            show_plot: Alias para 'mostrar' (deprecated)
        """
        # Compatibilidad con parámetros antiguos
        if show is not None:
            mostrar = show
        if show_plot is not None:
            mostrar = show_plot
        
        try:
            import matplotlib.pyplot as plt
            import matplotlib.dates as mdates
        except ImportError:
            print("matplotlib no está instalado. Instálalo con: pip install matplotlib")
            return
        
        resultados = self.monte_carlo_simulation(dias, simulaciones, valor_inicial)
        
        # Crear figura
        figura, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Gráfico 1: Distribución de valores finales
        ax1.hist(resultados['simulated_paths'], bins=50, alpha=0.7, edgecolor='black')
        ax1.axvline(resultados['mean_final_value'], color='red', linestyle='--', 
                   label=f'Media: ${resultados["mean_final_value"]:,.2f}')
        ax1.axvline(resultados['percentiles']['p50'], color='green', linestyle='--',
                   label=f'Mediana: ${resultados["percentiles"]["p50"]:,.2f}')
        ax1.set_xlabel('Valor Final de la Cartera')
        ax1.set_ylabel('Frecuencia')
        ax1.set_title(f'Distribución de Valores Finales ({simulaciones} simulaciones)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Gráfico 2: Trayectorias de muestra
        valor_cartera = self.get_portfolio_value_series(valor_inicial)
        retornos_cartera = self.get_portfolio_returns()
        if retornos_cartera is not None and len(retornos_cartera) > 0:
            retorno_medio = retornos_cartera.mean()
            desv_retorno = retornos_cartera.std()
            # Mostrar algunas trayectorias de muestra
            for i in range(min(100, simulaciones)):
                retornos_aleatorios = np.random.normal(retorno_medio, desv_retorno, dias)
                trayectoria = [valor_inicial]
                for ret in retornos_aleatorios:
                    trayectoria.append(trayectoria[-1] * (1 + ret))
                
                if valor_cartera is not None and len(valor_cartera) > 0:
                    fechas = pd.date_range(
                        start=valor_cartera.index[-1],
                        periods=dias+1,
                        freq='D'
                    )
                else:
                    fechas = pd.date_range(
                        start=datetime.now(),
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
            
            # Trayectoria de la media esperada (evoluciona con el tiempo)
            trayectoria_media = [valor_inicial]
            for t in range(1, dias + 1):
                # Valor esperado: V0 * (1 + r)^t donde r es el retorno medio diario
                valor_esperado = valor_inicial * ((1 + retorno_medio) ** t)
                trayectoria_media.append(valor_esperado)
            
            ax2.plot(fechas, trayectoria_media, color='red', linestyle='--', linewidth=2.5,
                    label=f'Media esperada', alpha=0.9)
            
            # Diccionario para almacenar trayectorias de percentiles
            trayectorias_percentiles = {}
            
            # Calcular trayectorias de percentiles que evolucionan en el tiempo
            if 'percentiles' in resultados:
                # Calcular percentiles en cada punto del tiempo usando distribución normal
                for percentil_key, percentil_valor in resultados['percentiles'].items():
                    nivel = int(percentil_key[1:]) / 100.0
                    
                    # Calcular z-score para este percentil
                    z_score = norm_ppf(nivel)
                    
                    # Calcular trayectoria del percentil
                    trayectoria_percentil = [valor_inicial]
                    for t in range(1, dias + 1):
                        # Valor esperado en tiempo t
                        valor_esperado_t = valor_inicial * ((1 + retorno_medio) ** t)
                        # Desviación estándar acumulada hasta tiempo t
                        desv_acumulada = valor_inicial * desv_retorno * np.sqrt(t)
                        # Valor del percentil en tiempo t
                        valor_percentil_t = valor_esperado_t + z_score * desv_acumulada
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
                trayectoria_01 = [valor_inicial]
                for t in range(1, dias + 1):
                    valor_esperado_t = valor_inicial * ((1 + retorno_medio) ** t)
                    desv_acumulada = valor_inicial * desv_retorno * np.sqrt(t)
                    valor_percentil_t = valor_esperado_t + z_score_01 * desv_acumulada
                    trayectoria_01.append(valor_percentil_t)
                trayectorias_percentiles[0.01] = trayectoria_01
                ax2.plot(fechas, trayectoria_01, color='darkred', linestyle='-.', linewidth=1.5,
                        label='Peor caso (1%)', alpha=0.6)
            
            if 0.99 not in trayectorias_percentiles:
                z_score_99 = norm_ppf(0.99)
                trayectoria_99 = [valor_inicial]
                for t in range(1, dias + 1):
                    valor_esperado_t = valor_inicial * ((1 + retorno_medio) ** t)
                    desv_acumulada = valor_inicial * desv_retorno * np.sqrt(t)
                    valor_percentil_t = valor_esperado_t + z_score_99 * desv_acumulada
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
            
            # Línea del valor inicial (horizontal de referencia)
            ax2.axhline(y=valor_inicial, color='green', linestyle=':', linewidth=1.5,
                       label=f'Valor inicial: ${valor_inicial:,.2f}', alpha=0.6)
        
        ax2.set_xlabel('Fecha')
        ax2.set_ylabel('Valor de la Cartera')
        ax2.set_title('Trayectorias de Muestra (Monte Carlo)')
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
            nombre_archivo = os.path.join(ruta_guardado, 'monte_carlo_simulation.png')
            plt.savefig(nombre_archivo, dpi=300, bbox_inches='tight')
            plt.close()
    
    def report(self, 
              tasa_libre_riesgo: float = 0.02,
              incluir_estadisticas: bool = True,
              incluir_advertencias: bool = True) -> str:
        """
        Genera un reporte en formato Markdown de la cartera.
        
        Args:
            tasa_libre_riesgo: Tasa libre de riesgo para cálculos
            incluir_estadisticas: Incluir estadísticas detalladas
            incluir_advertencias: Incluir advertencias
        """
        # Importar aquí para evitar dependencias circulares
        from .report import generate_report
        return generate_report(
            portfolio=self,
            tasa_libre_riesgo=tasa_libre_riesgo,
            incluir_estadisticas=incluir_estadisticas,
            incluir_advertencias=incluir_advertencias
        )
    
    def plots_report(self, ruta_guardado: str = "portfolio_plots", mostrar: bool = True) -> None:
        """
        Genera y muestra visualizaciones útiles de la cartera.
        """
        try:
            import matplotlib.pyplot as plt
            import seaborn as sns
        except ImportError:
            print("matplotlib o seaborn no están instalados. Instálalos con: pip install matplotlib seaborn")
            return
        
        sns.set_style("whitegrid")
        
        # Crear figura con múltiples subplots
        figura = plt.figure(figsize=(16, 12))
        
        # 1. Evolución del valor de la cartera
        ax1 = plt.subplot(3, 2, 1)
        valor_cartera = self.get_portfolio_value_series()
        if valor_cartera is not None:
            ax1.plot(valor_cartera.index, valor_cartera.values, linewidth=2)
            ax1.set_title('Evolución del Valor de la Cartera', fontsize=12, fontweight='bold')
            ax1.set_xlabel('Fecha')
            ax1.set_ylabel('Valor ($)')
            ax1.grid(True, alpha=0.3)
        
        # 2. Composición de la cartera (pie chart)
        ax2 = plt.subplot(3, 2, 2)
        if self.holdings:
            simbolos = list(self.holdings.keys())
            pesos = list(self.holdings.values())
            ax2.pie(pesos, labels=simbolos, autopct='%1.1f%%', startangle=90)
            ax2.set_title('Composición de la Cartera', fontsize=12, fontweight='bold')
        
        # 3. Retornos de la cartera
        ax3 = plt.subplot(3, 2, 3)
        retornos_cartera = self.get_portfolio_returns()
        if retornos_cartera is not None:
            ax3.plot(retornos_cartera.index, retornos_cartera.values, alpha=0.7, linewidth=1)
            ax3.axhline(0, color='red', linestyle='--', alpha=0.5)
            ax3.set_title('Retornos Diarios de la Cartera', fontsize=12, fontweight='bold')
            ax3.set_xlabel('Fecha')
            ax3.set_ylabel('Retorno')
            ax3.grid(True, alpha=0.3)
        
        # 4. Distribución de retornos
        ax4 = plt.subplot(3, 2, 4)
        if retornos_cartera is not None:
            ax4.hist(retornos_cartera.values, bins=50, alpha=0.7, edgecolor='black')
            ax4.axvline(retornos_cartera.mean(), color='red', linestyle='--', 
                       label=f'Media: {retornos_cartera.mean():.4f}')
            ax4.set_title('Distribución de Retornos', fontsize=12, fontweight='bold')
            ax4.set_xlabel('Retorno')
            ax4.set_ylabel('Frecuencia')
            ax4.legend()
            ax4.grid(True, alpha=0.3)
        
        # 5. Comparación de holdings (precios normalizados)
        ax5 = plt.subplot(3, 2, 5)
        for simbolo, serie in self.price_series.items():
            df = serie.to_dataframe()
            if not df.empty and 'close' in df.columns:
                normalizado = df['close'] / df['close'].iloc[0] * 100
                ax5.plot(df.index, normalizado, label=simbolo, linewidth=2)
        ax5.set_title('Evolución de Holdings (Normalizado)', fontsize=12, fontweight='bold')
        ax5.set_xlabel('Fecha')
        ax5.set_ylabel('Precio Normalizado (Base 100)')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
        
        # 6. Matriz de correlación
        ax6 = plt.subplot(3, 2, 6)
        if len(self.price_series) > 1:
            diccionario_retornos = {}
            for simbolo, serie in self.price_series.items():
                retornos = serie.returns
                if retornos is not None:
                    # Convertir a serie con fechas
                    df = serie.to_dataframe()
                    if not df.empty:
                        retornos_precio = df['close'].pct_change().dropna()
                        diccionario_retornos[simbolo] = retornos_precio
            
            if len(diccionario_retornos) > 1:
                # Alinear fechas
                df_retornos = pd.DataFrame(diccionario_retornos)
                df_retornos = df_retornos.dropna()
                
                if not df_retornos.empty:
                    matriz_correlacion = df_retornos.corr()
                    sns.heatmap(matriz_correlacion, annot=True, fmt='.2f', cmap='coolwarm', 
                               center=0, ax=ax6, square=True)
                    ax6.set_title('Matriz de Correlación', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        
        if mostrar:
            plt.show()
        else:
            import os
            os.makedirs(ruta_guardado, exist_ok=True)
            plt.savefig(f'{ruta_guardado}/portfolio_analysis.png', dpi=300, bbox_inches='tight')
            plt.close()
            print(f"Gráficos guardados en {ruta_guardado}/portfolio_analysis.png")

