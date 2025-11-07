"""
Módulo para generar reportes de carteras en formato Markdown.
"""

from datetime import datetime
from typing import TYPE_CHECKING
import pandas as pd
import numpy as np

if TYPE_CHECKING:
    from .portfolio import Portfolio


def generate_report(
    portfolio: 'Portfolio',
    tasa_libre_riesgo: float = 0.02,
    incluir_estadisticas: bool = True,
    incluir_advertencias: bool = True
) -> str:
    """
    Genera un reporte en formato Markdown de la cartera.
    
    Args:
        portfolio: Objeto Portfolio a analizar
        tasa_libre_riesgo: Tasa libre de riesgo para cálculos
        incluir_estadisticas: Incluir estadísticas detalladas
        incluir_advertencias: Incluir advertencias
    
    Returns:
        String con el reporte en formato Markdown
    """
    reporte = []
    reporte.append(f"# Reporte de Cartera: {portfolio.name}\n")
    reporte.append(f"**Fecha de generación:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Composición de la cartera
    reporte.append("## Composición de la Cartera\n")
    reporte.append("| Símbolo | Peso | Nombre |\n")
    reporte.append("|---------|------|--------|\n")
    
    peso_total = 0
    for simbolo, peso in portfolio.holdings.items():
        serie = portfolio.price_series.get(simbolo)
        nombre = serie.name if serie else "N/A"
        reporte.append(f"| {simbolo} | {peso:.2%} | {nombre} |\n")
        peso_total += peso
    
    if abs(peso_total - 1.0) > 0.01:
        if incluir_advertencias:
            reporte.append(f"\n[ADVERTENCIA] **Advertencia:** Los pesos suman {peso_total:.2%}, no 100%.\n")
    
    # Estadísticas de la cartera
    if incluir_estadisticas:
        retornos_cartera = portfolio.get_portfolio_returns()
        if retornos_cartera is not None and len(retornos_cartera) > 0:
            reporte.append("\n## Estadísticas de la Cartera\n")
            
            retorno_medio = retornos_cartera.mean()
            desv_retorno = retornos_cartera.std()
            retorno_anual = retorno_medio * 252
            vol_anual = desv_retorno * np.sqrt(252)
            sharpe = (retorno_anual - tasa_libre_riesgo) / vol_anual if vol_anual > 0 else None
            
            reporte.append(f"- **Retorno medio diario:** {retorno_medio:.4%}\n")
            reporte.append(f"- **Volatilidad diaria:** {desv_retorno:.4%}\n")
            reporte.append(f"- **Retorno anualizado:** {retorno_anual:.2%}\n")
            reporte.append(f"- **Volatilidad anualizada:** {vol_anual:.2%}\n")
            if sharpe is not None:
                reporte.append(f"- **Ratio de Sharpe:** {sharpe:.2f}\n")
            
            # Valor de la cartera
            valor_cartera = portfolio.get_portfolio_value_series()
            if valor_cartera is not None and len(valor_cartera) > 0:
                valor_inicial = valor_cartera.iloc[0]
                valor_final = valor_cartera.iloc[-1]
                retorno_total = (valor_final - valor_inicial) / valor_inicial
                
                reporte.append(f"\n### Valor de la Cartera\n")
                reporte.append(f"- **Valor inicial:** ${valor_inicial:,.2f}\n")
                reporte.append(f"- **Valor final:** ${valor_final:,.2f}\n")
                reporte.append(f"- **Retorno total:** {retorno_total:.2%}\n")
                
                # Máximo drawdown
                pico = valor_inicial
                max_dd = 0.0
                for valor in valor_cartera:
                    if valor > pico:
                        pico = valor
                    dd = (pico - valor) / pico
                    if dd > max_dd:
                        max_dd = dd
                
                reporte.append(f"- **Máximo Drawdown:** {max_dd:.2%}\n")
    
    # Estadísticas individuales
    if incluir_estadisticas:
        reporte.append("\n## Estadísticas por Valor de la Cartera \n")
        reporte.append("| Símbolo | Retorno Anualizado | Volatilidad | Sharpe | Max Drawdown |\n")
        reporte.append("|---------|-------------------|-------------|--------|--------------|\n")
        
        for simbolo, serie in portfolio.price_series.items():
            ret_anual = serie.annualized_return()
            volatilidad = serie.volatility()
            sharpe = serie.sharpe_ratio(tasa_libre_riesgo)
            max_dd = serie.max_drawdown()
            
            ret_anual_str = f"{ret_anual:.2%}" if ret_anual else "N/A"
            vol_str = f"{volatilidad:.2%}" if volatilidad else "N/A"
            sharpe_str = f"{sharpe:.2f}" if sharpe else "N/A"
            max_dd_str = f"{max_dd:.2%}" if max_dd else "N/A"
            
            reporte.append(f"| {simbolo} | {ret_anual_str} | {vol_str} | {sharpe_str} | {max_dd_str} |\n")
    
    # Advertencias
    if incluir_advertencias:
        advertencias = []
        
        # Verificar datos faltantes
        for simbolo, serie in portfolio.price_series.items():
            if not serie.data:
                advertencias.append(f"[ERROR] {simbolo}: No hay datos disponibles")
        
        # Verificar períodos de datos
        periodos = {}
        for simbolo, serie in portfolio.price_series.items():
            periodo = serie.get_period()
            if periodo:
                periodos[simbolo] = periodo
        
        if len(set(periodos.values())) > 1:
            advertencias.append("[ADVERTENCIA] Los valores de la cartera tienen períodos de datos diferentes")
        
        if advertencias:
            reporte.append("\n## Advertencias\n")
            for advertencia in advertencias:
                reporte.append(f"{advertencia}\n")
    
    return "".join(reporte)


