"""
Script principal para ejecutar el análisis bursátil completo.
Lee la configuración de configuracion_parametros.py y ejecuta todo el proceso automáticamente.
"""

from datetime import datetime, timedelta
import sys
import os

# Añadir el directorio padre al path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.extractor import DataExtractorFactory, MultiAPIExtractor
    from src.portfolio import Portfolio
    from src.data_classes import PriceSeries
    from src.report import generate_report
    from src.validation import validar_configuracion
    from configuracion_parametros import (
        TICKERS_ACCIONES,
        INDICES,
        FECHA_INICIO_EXTRACCION,
        FECHA_FIN_EXTRACCION,
        DIAS_MONTE_CARLO,
        TIPO_MONTE_CARLO,
        SIMBOLO_MONTE_CARLO,
        SIMBOLOS_MONTE_CARLO,
        NUM_SIMULACIONES_MONTE_CARLO,
        VALOR_INICIAL_CARTERA,
        NIVELES_CONFIANZA,
        NOMBRE_CARTERA,
        PESOS_CARTERA,
        API_POR_DEFECTO,
        MAPEO_SIMBOLO_API,
        ALPHA_VANTAGE_API_KEY,
        TASA_LIBRE_RIESGO,
        INCLUIR_ESTADISTICAS,
        INCLUIR_ADVERTENCIAS,
        RUTA_GUARDADO_GRAFICOS,
        MOSTRAR_GRAFICOS,
        ELIMINAR_DUPLICADOS,
        ELIMINAR_OUTLIERS,
        UMBRAL_OUTLIER,
        MOSTRAR_BANDAS_CONFIANZA,
        EXTRACCION_PARALELA,
        MAX_WORKERS_EXTRACCION,
        EXTRAER_DATOS_FUNDAMENTALES,
        EXTRAER_DIVIDENDOS,
        EXTRAER_INDICADORES_TECNICOS,
        INDICADORES_TECNICOS
    )
except ImportError:
    # Si se ejecuta como módulo
    from .extractor import DataExtractorFactory, MultiAPIExtractor
    from .portfolio import Portfolio
    from .data_classes import PriceSeries
    from .report import generate_report
    from .validation import validar_configuracion
    from .configuracion_parametros import (
        TICKERS_ACCIONES,
        INDICES,
        FECHA_INICIO_EXTRACCION,
        FECHA_FIN_EXTRACCION,
        DIAS_MONTE_CARLO,
        TIPO_MONTE_CARLO,
        SIMBOLO_MONTE_CARLO,
        SIMBOLOS_MONTE_CARLO,
        NUM_SIMULACIONES_MONTE_CARLO,
        VALOR_INICIAL_CARTERA,
        NIVELES_CONFIANZA,
        NOMBRE_CARTERA,
        PESOS_CARTERA,
        API_POR_DEFECTO,
        MAPEO_SIMBOLO_API,
        ALPHA_VANTAGE_API_KEY,
        TASA_LIBRE_RIESGO,
        INCLUIR_ESTADISTICAS,
        INCLUIR_ADVERTENCIAS,
        RUTA_GUARDADO_GRAFICOS,
        MOSTRAR_GRAFICOS,
        ELIMINAR_DUPLICADOS,
        EXTRACCION_PARALELA,
        MAX_WORKERS_EXTRACCION,
        EXTRAER_DATOS_FUNDAMENTALES,
        EXTRAER_DIVIDENDOS,
        EXTRAER_INDICADORES_TECNICOS,
        ELIMINAR_OUTLIERS,
        UMBRAL_OUTLIER,
        MOSTRAR_BANDAS_CONFIANZA
    )


def obtener_fecha_inicio() -> datetime:
    """Retorna la fecha de inicio para extracción."""
    if FECHA_INICIO_EXTRACCION is not None:
        return FECHA_INICIO_EXTRACCION
    fecha_fin = obtener_fecha_fin()
    return fecha_fin - timedelta(days=365)


def obtener_fecha_fin() -> datetime:
    """Retorna la fecha de fin para extracción."""
    if FECHA_FIN_EXTRACCION is not None:
        return FECHA_FIN_EXTRACCION
    return datetime.now()


def main():
    """Ejecuta el análisis bursátil completo según la configuración."""
    
    # Validar dependencias críticas
    try:
        import pandas as pd
        import numpy as np
        import matplotlib
        import requests
    except ImportError as e:
        print("="*70)
        print("[ERROR] Dependencias faltantes")
        print("="*70)
        print(f"Falta el módulo: {e.name}")
        print("\nPor favor, instala las dependencias:")
        print("  pip install -r requirements.txt")
        print("\nO ejecuta el script de instalación:")
        print("  setup.bat (Windows) o setup.sh (Linux/Mac)")
        return
    
    print("="*70)
    print("ANÁLISIS BURSÁTIL - EJECUCIÓN AUTOMÁTICA")
    print("="*70)
    print(f"Fecha de ejecución: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Validar configuración
    print("Validando configuración...")
    advertencias = validar_configuracion(
        PESOS_CARTERA=PESOS_CARTERA,
        TICKERS_ACCIONES=TICKERS_ACCIONES,
        INDICES=INDICES,
        API_POR_DEFECTO=API_POR_DEFECTO,
        ALPHA_VANTAGE_API_KEY=ALPHA_VANTAGE_API_KEY,
        TIPO_MONTE_CARLO=TIPO_MONTE_CARLO,
        SIMBOLO_MONTE_CARLO=SIMBOLO_MONTE_CARLO,
        SIMBOLOS_MONTE_CARLO=SIMBOLOS_MONTE_CARLO
    )
    if advertencias:
        print("\n[ADVERTENCIA] Advertencias de configuración:")
        for advertencia in advertencias:
            print(f"  {advertencia}")
        print()
    else:
        print("[OK] Configuración válida\n")
    
    # Obtener fechas
    fecha_inicio = obtener_fecha_inicio()
    fecha_fin = obtener_fecha_fin()
    print(f"Período de extracción: {fecha_inicio.strftime('%Y-%m-%d')} a {fecha_fin.strftime('%Y-%m-%d')}")
    print(f"Días de Monte Carlo: {DIAS_MONTE_CARLO}")
    print(f"Simulaciones: {NUM_SIMULACIONES_MONTE_CARLO}\n")
    
    # ============================================
    # CONFIGURAR EXTRACTORES
    # ============================================
    print("="*70)
    print("CONFIGURANDO EXTRACTORES DE DATOS")
    print("="*70)
    
    # Crear extractor multi-API si se especifican múltiples APIs
    usar_multi_api = len(MAPEO_SIMBOLO_API) > 0 or API_POR_DEFECTO != "yahoo"
    
    if usar_multi_api:
        multi_extractor = MultiAPIExtractor()
        
        # Registrar extractores disponibles
        if API_POR_DEFECTO == "yahoo" or "yahoo" in MAPEO_SIMBOLO_API.values():
            yahoo = DataExtractorFactory.create_yahoo_extractor()
            multi_extractor.register_extractor('yahoo', yahoo, es_por_defecto=(API_POR_DEFECTO == "yahoo"))
            print("[OK] Extractor Yahoo Finance registrado")
        
        if ALPHA_VANTAGE_API_KEY:
            if API_POR_DEFECTO == "alphavantage" or "alphavantage" in MAPEO_SIMBOLO_API.values():
                alphavantage = DataExtractorFactory.create_alphavantage_extractor(ALPHA_VANTAGE_API_KEY)
                multi_extractor.register_extractor('alphavantage', alphavantage, 
                                                  es_por_defecto=(API_POR_DEFECTO == "alphavantage"))
                print("[OK] Extractor Alpha Vantage registrado")
        
        extractor = multi_extractor
    else:
        # Usar extractor simple
        if API_POR_DEFECTO == "yahoo":
            extractor = DataExtractorFactory.get_default_extractor()
            print("[OK] Usando extractor Yahoo Finance (por defecto)")
        elif API_POR_DEFECTO == "alphavantage" and ALPHA_VANTAGE_API_KEY:
            extractor = DataExtractorFactory.create_alphavantage_extractor(ALPHA_VANTAGE_API_KEY)
            print("[OK] Usando extractor Alpha Vantage")
        else:
            print("[ADVERTENCIA] API especificada no disponible, usando Yahoo Finance por defecto")
            extractor = DataExtractorFactory.get_default_extractor()
    
    print()
    
    # ============================================
    # EXTRAER ÍNDICES
    # ============================================
    print("="*70)
    print("EXTRAYENDO ÍNDICES BURSÁTILES")
    print("="*70)
    print("Nota: Yahoo Finance puede tener limitaciones de rate. Si hay errores, espera unos minutos.\n")
    
    diccionario_series = {}
    
    if INDICES:
        # Usar importar_indices con paralelismo
        from src.indices import importar_indices
        indices_dict = importar_indices(
            INDICES,
            extractor,
            fecha_inicio,
            fecha_fin,
            paralelo=EXTRACCION_PARALELA,
            max_trabajadores=MAX_WORKERS_EXTRACCION
        )
        
        # Añadir los índices al diccionario de series
        for simbolo, serie in indices_dict.items():
            diccionario_series[simbolo] = serie
        
        print()
    
    # ============================================
    # EXTRAER ACCIONES
    # ============================================
    print("="*70)
    print("EXTRAYENDO ACCIONES")
    print("="*70)
    
    if TICKERS_ACCIONES:
        print(f"Obteniendo datos de {len(TICKERS_ACCIONES)} acción(es)...")
        
        # Si hay mapeo de APIs, usar multi-extractor
        if usar_multi_api and MAPEO_SIMBOLO_API:
            # Crear mapeo para las acciones
            mapeo_acciones = {}
            for ticker in TICKERS_ACCIONES:
                mapeo_acciones[ticker] = MAPEO_SIMBOLO_API.get(ticker, API_POR_DEFECTO)
            
            acciones_dict = multi_extractor.fetch_from_multiple_apis(
                mapeo_acciones, fecha_inicio, fecha_fin
            )
        else:
            acciones_dict = extractor.fetch_multiple_series(
                TICKERS_ACCIONES, 
                fecha_inicio, 
                fecha_fin,
                paralelo=EXTRACCION_PARALELA,
                max_trabajadores=MAX_WORKERS_EXTRACCION
            )
        
        for simbolo, serie in acciones_dict.items():
            diccionario_series[simbolo] = serie
            print(f"  [OK] {simbolo} ({serie.name}) - {len(serie.data)} puntos - Fuente: {serie.source}")
        
        print()
    
    # Verificar que se obtuvieron datos
    if not diccionario_series:
        print("\n Error: No se pudieron obtener datos de ninguna fuente.")
        print("Posibles causas:")
        print("  - Rate limiting de Yahoo Finance (espera unos minutos)")
        print("  - Problemas de conexión a internet")
        print("  - Símbolos incorrectos en la configuración")
        print("  - API keys faltantes o incorrectas")
        return
    
    # ============================================
    # LIMPIAR Y PREPROCESAR DATOS
    # ============================================
    print("="*70)
    print("LIMPIEZA Y PREPROCESADO DE DATOS")
    print("="*70)
    
    for simbolo, serie in diccionario_series.items():
        serie.clean_data(
            eliminar_duplicados=ELIMINAR_DUPLICADOS,
            eliminar_outliers=ELIMINAR_OUTLIERS,
            umbral_outlier=UMBRAL_OUTLIER
        )
        print(f"  [OK] {simbolo}: {len(serie.data)} puntos de datos después de limpieza")
    print()
    
    # ============================================
    # CREAR CARTERA
    # ============================================
    print("="*70)
    print("CREANDO CARTERA")
    print("="*70)
    
    cartera = Portfolio(name=NOMBRE_CARTERA)
    
    tenencias_añadidas = 0
    for simbolo, peso in PESOS_CARTERA.items():
        if simbolo in diccionario_series:
            cartera.add_holding(simbolo=simbolo, peso=peso, serie_precios=diccionario_series[simbolo])
            print(f"  [OK] Añadido {simbolo} con peso {peso:.0%}")
            tenencias_añadidas += 1
        else:
            print(f"  [ADVERTENCIA] {simbolo} no encontrado en los datos extraídos, omitido")
    
    if tenencias_añadidas == 0:
        print("\n[ERROR] No se pudieron añadir holdings a la cartera")
        print("Verifica que los símbolos en PESOS_CARTERA coincidan con los extraídos")
        return
    
    print(f"\n[OK] Cartera creada con {tenencias_añadidas} holding(s)\n")
    
    # ============================================
    # EXTRACCIÓN DE DATOS ADICIONALES (OPCIONAL)
    # ============================================
    
    if EXTRAER_DATOS_FUNDAMENTALES:
        print("="*70)
        print("EXTRACIENDO DATOS FUNDAMENTALES")
        print("="*70)
        
        for simbolo in TICKERS_ACCIONES:
            if simbolo not in diccionario_series:
                continue
            
            try:
                datos_fundamentales = extractor.fetch_fundamental_data(simbolo)
                if datos_fundamentales:
                    try:
                        print(f"\n{simbolo} ({datos_fundamentales.get('name', simbolo)})")
                        if datos_fundamentales.get('pe_ratio'):
                            print(f"  P/E Ratio: {datos_fundamentales['pe_ratio']:.2f}")
                        if datos_fundamentales.get('pb_ratio'):
                            print(f"  P/B Ratio: {datos_fundamentales['pb_ratio']:.2f}")
                        if datos_fundamentales.get('dividend_yield'):
                            print(f"  Dividend Yield: {datos_fundamentales['dividend_yield']:.2%}")
                        if datos_fundamentales.get('market_cap'):
                            print(f"  Market Cap: ${datos_fundamentales['market_cap']:,.0f}")
                        if datos_fundamentales.get('sector'):
                            print(f"  Sector: {datos_fundamentales['sector']}")
                    except UnicodeEncodeError:
                        print(f"\n[INFO] {simbolo}: Datos fundamentales obtenidos")
            except NotImplementedError:
                try:
                    print(f"  [ADVERTENCIA] {simbolo}: Datos fundamentales no disponibles con esta API")
                except UnicodeEncodeError:
                    print(f"  [!] {simbolo}: Datos fundamentales no disponibles con esta API")
            except Exception as e:
                try:
                    print(f"  [ERROR] Error al obtener datos fundamentales para {simbolo}: {e}")
                except UnicodeEncodeError:
                    print(f"  [!] Error al obtener datos fundamentales para {simbolo}: {e}")
        
        print()
    
    if EXTRAER_DIVIDENDOS:
        print("="*70)
        print("EXTRACIENDO HISTORIAL DE DIVIDENDOS")
        print("="*70)
        
        for simbolo in TICKERS_ACCIONES:
            if simbolo not in diccionario_series:
                continue
            
            try:
                dividendos = extractor.fetch_dividend_data(
                    simbolo, 
                    start_date=fecha_inicio,
                    end_date=fecha_fin
                )
                if dividendos:
                    total = sum(d['amount'] for d in dividendos)
                    try:
                        print(f"  {simbolo}: {len(dividendos)} pagos, Total: ${total:.2f}")
                    except UnicodeEncodeError:
                        print(f"  [DIV] {simbolo}: {len(dividendos)} pagos, Total: ${total:.2f}")
                else:
                    try:
                        print(f"  {simbolo}: No hay dividendos en el período especificado")
                    except UnicodeEncodeError:
                        print(f"  {simbolo}: No hay dividendos en el periodo especificado")
            except NotImplementedError:
                try:
                    print(f"  [ADVERTENCIA] {simbolo}: Dividendos no disponibles con esta API")
                except UnicodeEncodeError:
                    print(f"  [!] {simbolo}: Dividendos no disponibles con esta API")
            except Exception as e:
                try:
                    print(f"  [ADVERTENCIA] Error al obtener dividendos para {simbolo}: {str(e)[:100]}")
                except UnicodeEncodeError:
                    print(f"  [!] Error al obtener dividendos para {simbolo}")
        
        print()
    
    # ============================================
    # GENERAR REPORTE
    # ============================================
    print("="*70)
    print("GENERANDO REPORTE")
    print("="*70)
    
    reporte = generate_report(
        cartera,
        tasa_libre_riesgo=TASA_LIBRE_RIESGO,
        incluir_estadisticas=INCLUIR_ESTADISTICAS,
        incluir_advertencias=INCLUIR_ADVERTENCIAS
    )
    
    # Guardar reporte
    with open("portfolio_report.md", "w", encoding="utf-8") as f:
        f.write(reporte)
    
    print("[OK] Reporte generado y guardado en portfolio_report.md")
    
    # Mostrar reporte en consola (si es posible)
    try:
        print("\n" + "-"*70)
        print(reporte)
        print("-"*70)
    except UnicodeEncodeError:
        print("(Reporte guardado en archivo - algunos caracteres no se pueden mostrar en consola)")
    
    print()
    
    # ============================================
    # GENERAR GRÁFICOS
    # ============================================
    print("="*70)
    print("GENERANDO GRÁFICOS")
    print("="*70)
    
    try:
        cartera.plots_report(ruta_guardado=RUTA_GUARDADO_GRAFICOS, mostrar=MOSTRAR_GRAFICOS)
        print(f"[OK] Gráficos guardados en {RUTA_GUARDADO_GRAFICOS}/portfolio_analysis.png")
    except Exception as e:
        print(f"[ERROR] Error al generar gráficos: {e}")
    
    print()
    
    # ============================================
    # SIMULACIÓN DE MONTE CARLO
    # ============================================
    try:
        if TIPO_MONTE_CARLO == "cartera":
            # Simulación de Monte Carlo para la cartera completa
            resultados_mc = cartera.monte_carlo_simulation(
                dias=DIAS_MONTE_CARLO,
                simulaciones=NUM_SIMULACIONES_MONTE_CARLO,
                valor_inicial=VALOR_INICIAL_CARTERA,
                niveles_confianza=NIVELES_CONFIANZA
            )
            
            # Mostrar datos más relevantes de la simulación
            print("\n" + "="*70)
            print("RESULTADOS SIMULACIÓN MONTE CARLO - CARTERA")
            print("="*70)
            print(f"Valor inicial: ${resultados_mc['initial_value']:,.2f}")
            print(f"Valor medio final: ${resultados_mc['mean_final_value']:,.2f}")
            retorno_esperado = (resultados_mc['mean_final_value'] / resultados_mc['initial_value'] - 1) * 100
            print(f"Retorno esperado: {retorno_esperado:.2f}%")
            print(f"Valor mínimo: ${resultados_mc['min_final_value']:,.2f}")
            print(f"Valor máximo: ${resultados_mc['max_final_value']:,.2f}")
            print(f"Desviación estándar: ${resultados_mc['std_final_value']:,.2f}")
            
            # Mostrar todos los percentiles
            if resultados_mc.get('percentiles'):
                print("\nPercentiles:")
                percentiles_ordenados = sorted(
                    [(key, value) for key, value in resultados_mc['percentiles'].items()],
                    key=lambda x: int(x[0][1:])
                )
                for key, value in percentiles_ordenados:
                    nivel = int(key[1:])
                    print(f"  {nivel}%: ${value:,.2f}")
            print("="*70 + "\n")
            
            # Visualizar Monte Carlo de cartera
            cartera.plot_monte_carlo(
                dias=DIAS_MONTE_CARLO,
                simulaciones=NUM_SIMULACIONES_MONTE_CARLO,
                valor_inicial=VALOR_INICIAL_CARTERA,
                mostrar=MOSTRAR_GRAFICOS,
                mostrar_bandas=MOSTRAR_BANDAS_CONFIANZA
            )
            
        elif TIPO_MONTE_CARLO == "accion_individual":
            # Simulación de Monte Carlo para una acción individual
            if SIMBOLO_MONTE_CARLO is None:
                print("[ERROR] TIPO_MONTE_CARLO es 'accion_individual' pero SIMBOLO_MONTE_CARLO no está configurado")
                print("   Por favor, configura SIMBOLO_MONTE_CARLO en configuracion_parametros.py")
            elif SIMBOLO_MONTE_CARLO not in diccionario_series:
                print(f"[ERROR] El símbolo '{SIMBOLO_MONTE_CARLO}' no se encuentra en los datos extraídos")
                print(f"   Símbolos disponibles: {', '.join(diccionario_series.keys())}")
            else:
                serie_accion = diccionario_series[SIMBOLO_MONTE_CARLO]
                
                # Calcular precio inicial basado en el valor inicial de la cartera
                precio_actual = serie_accion.get_latest_price()
                if precio_actual is None:
                    print(f"[ERROR] No se puede obtener el precio actual de {SIMBOLO_MONTE_CARLO}")
                else:
                    # Calcular cuántas acciones se pueden comprar con el valor inicial
                    num_acciones = VALOR_INICIAL_CARTERA / precio_actual
                    precio_inicial_simulacion = precio_actual
                    
                    resultados_mc = serie_accion.monte_carlo_simulation(
                        dias=DIAS_MONTE_CARLO,
                        simulaciones=NUM_SIMULACIONES_MONTE_CARLO,
                        precio_inicial=precio_inicial_simulacion,
                        niveles_confianza=NIVELES_CONFIANZA
                    )
                    
                    # Mostrar datos más relevantes de la simulación
                    print("\n" + "="*70)
                    print(f"RESULTADOS SIMULACIÓN MONTE CARLO - {SIMBOLO_MONTE_CARLO}")
                    print("="*70)
                    print(f"Precio inicial: ${resultados_mc['initial_price']:,.2f}")
                    print(f"Precio medio final: ${resultados_mc['mean_final_price']:,.2f}")
                    print(f"Precio mínimo: ${resultados_mc['min_final_price']:,.2f}")
                    print(f"Precio máximo: ${resultados_mc['max_final_price']:,.2f}")
                    print(f"Desviación estándar: ${resultados_mc['std_final_price']:,.2f}")
                    print(f"Retorno esperado: {resultados_mc['expected_return']:.2%}")
                    
                    valor_inicial_total = num_acciones * resultados_mc['initial_price']
                    valor_final_medio = num_acciones * resultados_mc['mean_final_price']
                    print(f"\nValor inicial total: ${valor_inicial_total:,.2f}")
                    print(f"Valor medio final: ${valor_final_medio:,.2f}")
                    
                    # Mostrar todos los percentiles
                    if resultados_mc.get('percentiles'):
                        print("\nPercentiles (precio / valor total):")
                        percentiles_ordenados = sorted(
                            [(key, value) for key, value in resultados_mc['percentiles'].items()],
                            key=lambda x: int(x[0][1:])
                        )
                        for key, value in percentiles_ordenados:
                            nivel = int(key[1:])
                            valor_percentil = num_acciones * value
                            print(f"  {nivel}%: ${value:,.2f} / ${valor_percentil:,.2f}")
                    print("="*70 + "\n")
                    
                    # Visualizar Monte Carlo de acción individual
                    serie_accion.plot_monte_carlo(
                        dias=DIAS_MONTE_CARLO,
                        simulaciones=NUM_SIMULACIONES_MONTE_CARLO,
                        precio_inicial=precio_inicial_simulacion,
                        mostrar=MOSTRAR_GRAFICOS,
                        mostrar_bandas=MOSTRAR_BANDAS_CONFIANZA
                    )
        
        elif TIPO_MONTE_CARLO == "todos_los_elementos":
            # Simulación de Monte Carlo para todos los holdings de la cartera
            if not cartera.holdings:
                print("[ERROR] La cartera no tiene holdings para simular")
            else:
                # Verificar si hay elementos usando datos sin ajustar
                elementos_sin_ajustar = []
                for simbolo in cartera.holdings.keys():
                    if simbolo in cartera.price_series:
                        serie = cartera.price_series[simbolo]
                        if "[sin ajustar]" in serie.source:
                            elementos_sin_ajustar.append(simbolo)
                
                # Mostrar mensaje general si hay elementos sin ajustar
                if elementos_sin_ajustar:
                    try:
                        print(f"\n[ADVERTENCIA] Nota: Se están usando datos de cierre sin ajustar para algunos tickers")
                        print(f"   (no todos los tickers tienen datos ajustados disponibles)")
                        print(f"   Tickers afectados: {', '.join(elementos_sin_ajustar)}")
                    except UnicodeEncodeError:
                        print(f"\n[!] Nota: Se estan usando datos de cierre sin ajustar para algunos tickers")
                        print(f"   (no todos los tickers tienen datos ajustados disponibles)")
                        print(f"   Tickers afectados: {', '.join(elementos_sin_ajustar)}")
                
                elementos_simulados = 0
                for simbolo, peso in cartera.holdings.items():
                    if simbolo not in cartera.price_series:
                        continue
                    
                    serie_accion = cartera.price_series[simbolo]
                    precio_actual = serie_accion.get_latest_price()
                    if precio_actual is None:
                        continue
                    
                    # Calcular valor inicial proporcional al peso en la cartera
                    valor_inicial_proporcional = VALOR_INICIAL_CARTERA * peso
                    num_acciones = valor_inicial_proporcional / precio_actual
                    precio_inicial_simulacion = precio_actual
                    
                    try:
                        resultados_mc = serie_accion.monte_carlo_simulation(
                            dias=DIAS_MONTE_CARLO,
                            simulaciones=NUM_SIMULACIONES_MONTE_CARLO,
                            precio_inicial=precio_inicial_simulacion,
                            niveles_confianza=NIVELES_CONFIANZA
                        )
                        
                        # Mostrar datos más relevantes de la simulación
                        print(f"\n{simbolo} ({serie_accion.name}) - Peso: {peso:.0%}")
                        print(f"  Precio inicial: ${resultados_mc['initial_price']:,.2f}")
                        print(f"  Precio medio final: ${resultados_mc['mean_final_price']:,.2f}")
                        print(f"  Retorno esperado: {resultados_mc['expected_return']:.2%}")
                        
                        # Mostrar todos los percentiles
                        if resultados_mc.get('percentiles'):
                            percentiles_str = ", ".join([
                                f"{int(k[1:])}%: ${v:,.2f}" 
                                for k, v in sorted(
                                    resultados_mc['percentiles'].items(),
                                    key=lambda x: int(x[0][1:])
                                )
                            ])
                            print(f"  Percentiles: {percentiles_str}")
                        
                        # Visualizar Monte Carlo de cada elemento
                        serie_accion.plot_monte_carlo(
                            dias=DIAS_MONTE_CARLO,
                            simulaciones=NUM_SIMULACIONES_MONTE_CARLO,
                            precio_inicial=precio_inicial_simulacion,
                            mostrar=MOSTRAR_GRAFICOS,
                            mostrar_bandas=MOSTRAR_BANDAS_CONFIANZA
                        )
                        elementos_simulados += 1
                        
                    except Exception as e:
                        print(f"[ERROR] Error al simular {simbolo}: {e}")
        
        elif TIPO_MONTE_CARLO == "seleccion_elementos":
            # Simulación de Monte Carlo para una selección específica de holdings
            if not SIMBOLOS_MONTE_CARLO:
                print("[ERROR] TIPO_MONTE_CARLO es 'seleccion_elementos' pero SIMBOLOS_MONTE_CARLO está vacío")
                print("   Por favor, configura SIMBOLOS_MONTE_CARLO en configuracion_parametros.py con una lista de símbolos")
            else:
                simbolos_validos = []
                simbolos_invalidos = []
                
                for simbolo in SIMBOLOS_MONTE_CARLO:
                    if simbolo not in diccionario_series:
                        simbolos_invalidos.append(simbolo)
                    else:
                        simbolos_validos.append(simbolo)
                
                if simbolos_invalidos:
                    print(f"[ADVERTENCIA] Símbolos no encontrados (omitidos): {', '.join(simbolos_invalidos)}")
                    print(f"  Símbolos disponibles: {', '.join(diccionario_series.keys())}")
                
                if not simbolos_validos:
                    print("[ERROR] No hay símbolos válidos para simular")
                else:
                    for simbolo in simbolos_validos:
                        serie_accion = diccionario_series[simbolo]
                        precio_actual = serie_accion.get_latest_price()
                        if precio_actual is None:
                            continue
                        
                        # Calcular cuántas acciones se pueden comprar con el valor inicial
                        num_acciones = VALOR_INICIAL_CARTERA / precio_actual
                        precio_inicial_simulacion = precio_actual
                        
                        try:
                            resultados_mc = serie_accion.monte_carlo_simulation(
                                dias=DIAS_MONTE_CARLO,
                                simulaciones=NUM_SIMULACIONES_MONTE_CARLO,
                                precio_inicial=precio_inicial_simulacion,
                                niveles_confianza=NIVELES_CONFIANZA
                            )
                            
                            # Mostrar datos más relevantes de la simulación
                            print(f"\n{simbolo} ({serie_accion.name})")
                            print(f"  Precio inicial: ${resultados_mc['initial_price']:,.2f}")
                            print(f"  Precio medio final: ${resultados_mc['mean_final_price']:,.2f}")
                            print(f"  Retorno esperado: {resultados_mc['expected_return']:.2%}")
                            
                            # Mostrar todos los percentiles
                            if resultados_mc.get('percentiles'):
                                percentiles_str = ", ".join([
                                    f"{int(k[1:])}%: ${v:,.2f}" 
                                    for k, v in sorted(
                                        resultados_mc['percentiles'].items(),
                                        key=lambda x: int(x[0][1:])
                                    )
                                ])
                                print(f"  Percentiles: {percentiles_str}")
                            
                            # Visualizar Monte Carlo de cada elemento
                            serie_accion.plot_monte_carlo(
                                dias=DIAS_MONTE_CARLO,
                                simulaciones=NUM_SIMULACIONES_MONTE_CARLO,
                                precio_inicial=precio_inicial_simulacion,
                                mostrar=MOSTRAR_GRAFICOS
                            )
                            
                        except Exception as e:
                            print(f"[ERROR] Error al simular {simbolo}: {e}")
        else:
            print(f"[ERROR] TIPO_MONTE_CARLO debe ser 'cartera', 'accion_individual', 'todos_los_elementos' o 'seleccion_elementos', pero se encontró: '{TIPO_MONTE_CARLO}'")
            print("   Por favor, configura TIPO_MONTE_CARLO correctamente en configuracion_parametros.py")
        
    except Exception as e:
        print(f"[ERROR] Error en simulación de Monte Carlo: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    
    # ============================================
    # RESUMEN FINAL
    # ============================================
    print("="*70)
    print("EJECUCIÓN COMPLETADA")
    print("="*70)
    print(f"[OK] Datos extraídos: {len(diccionario_series)} serie(s)")
    print(f"[OK] Cartera creada: {NOMBRE_CARTERA}")
    print(f"[OK] Reporte: portfolio_report.md")
    print(f"[OK] Gráficos: {RUTA_GUARDADO_GRAFICOS}/portfolio_analysis.png")
    print("\n" + "="*70)


if __name__ == "__main__":
    main()
