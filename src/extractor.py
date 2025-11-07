"""
Extractor de datos bursátiles desde múltiples fuentes.
Proporciona una interfaz unificada para obtener datos de diferentes APIs.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import requests
import pandas as pd
import time

from .data_classes import PriceSeries, PricePoint


class DataExtractor(ABC):
    """Clase base abstracta para extractores de datos."""
    
    @abstractmethod
    def fetch_historical_prices(self, 
                                symbol: str, 
                                start_date: Optional[datetime] = None,
                                end_date: Optional[datetime] = None) -> PriceSeries:
        """Obtiene precios históricos de un símbolo."""
        pass
    
    @abstractmethod
    def fetch_multiple_series(self, 
                             symbols: List[str],
                             start_date: Optional[datetime] = None,
                             end_date: Optional[datetime] = None,
                             paralelo: bool = True,
                             max_trabajadores: int = 5) -> Dict[str, PriceSeries]:
        """
        Obtiene múltiples series de datos.
        
        Args:
            symbols: Lista de símbolos
            start_date: Fecha de inicio
            end_date: Fecha de fin
            paralelo: Si True, extrae en paralelo (más rápido). Si False, secuencial.
            max_trabajadores: Número máximo de workers paralelos (solo si paralelo=True)
        """
        pass
    
    # Métodos opcionales para datos adicionales (no abstractos)
    
    def fetch_fundamental_data(self, 
                               symbol: str) -> Dict[str, Any]:
        """
        Obtiene datos fundamentales (P/E, P/B, dividendos, etc.)
        Retorna un diccionario con los datos disponibles.
        """
        raise NotImplementedError(f"{self.__class__.__name__} no soporta datos fundamentales")
    
    def fetch_earnings_data(self,
                           symbol: str,
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Obtiene datos de resultados trimestrales/anuales.
        Retorna lista de diccionarios con fecha, EPS, revenue, etc.
        """
        raise NotImplementedError(f"{self.__class__.__name__} no soporta datos de resultados")
    
    def fetch_dividend_data(self,
                           symbol: str,
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Obtiene historial de dividendos.
        Retorna lista de diccionarios con fecha, monto, tipo, etc.
        """
        raise NotImplementedError(f"{self.__class__.__name__} no soporta datos de dividendos")
    
    def fetch_technical_indicators(self,
                                  symbol: str,
                                  indicators: List[str],  # ['RSI', 'MACD', 'SMA_50', etc.]
                                  start_date: Optional[datetime] = None,
                                  end_date: Optional[datetime] = None) -> Dict[str, pd.Series]:
        """
        Obtiene indicadores técnicos calculados.
        Retorna diccionario {nombre_indicador: pd.Series}
        """
        raise NotImplementedError(f"{self.__class__.__name__} no soporta indicadores técnicos")
    
    def fetch_options_data(self,
                          symbol: str,
                          expiration_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Obtiene datos de opciones (calls/puts).
        Retorna lista de diccionarios con strike, premium, etc.
        """
        raise NotImplementedError(f"{self.__class__.__name__} no soporta datos de opciones")


class YahooFinanceExtractor(DataExtractor):
    """
    Extractor de datos de Yahoo Finance.
    Usa la librería yfinance como método principal, con fallback a requests directos.
    Formato de salida estandarizado: PriceSeries
    """
    
    def __init__(self):
        self.base_url = "https://query1.finance.yahoo.com/v8/finance/chart"
        self.source_name = "Yahoo Finance"
        # Headers para evitar bloqueos (usado en método fallback)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self._yfinance_disponible = None
    
    def _verificar_yfinance(self) -> bool:
        """Verifica si yfinance está disponible."""
        if self._yfinance_disponible is None:
            try:
                import yfinance
                self._yfinance_disponible = True
            except ImportError:
                self._yfinance_disponible = False
        return self._yfinance_disponible
    
    def _fetch_con_yfinance(self, 
                            simbolo: str,
                            fecha_inicio: datetime,
                            fecha_fin: datetime) -> PriceSeries:
        """
        Método principal: Obtiene datos usando la librería yfinance.
        
        Args:
            simbolo: Símbolo del valor
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin
        
        Returns:
            PriceSeries con los datos
        """
        import yfinance as yf
        
        try:
            ticker = yf.Ticker(simbolo)
            df = ticker.history(start=fecha_inicio, end=fecha_fin)
            
            if df.empty:
                raise ValueError(f"No se encontraron datos para {simbolo}")
            
            # Obtener información del ticker (puede fallar, usar valores por defecto)
            nombre = simbolo
            moneda = 'USD'
            try:
                info = ticker.info
                nombre = info.get('longName', info.get('shortName', simbolo))
                moneda = info.get('currency', 'USD')
            except Exception:
                # Si falla obtener info, usar valores por defecto
                pass
            
            # Verificar si hay datos ajustados disponibles y válidos
            usar_ajustado = 'Adj Close' in df.columns and df['Adj Close'].notna().any()
            
            # Convertir DataFrame a PriceSeries
            puntos_precio = []
            for fecha, fila in df.iterrows():
                try:
                    # Convertir fecha de pandas Timestamp a datetime
                    if isinstance(fecha, pd.Timestamp):
                        fecha_dt = fecha.to_pydatetime()
                    elif hasattr(fecha, 'to_pydatetime'):
                        fecha_dt = fecha.to_pydatetime()
                    else:
                        fecha_dt = datetime.fromtimestamp(fecha.timestamp())
                    
                    # Usar cierre ajustado si está disponible y es válido, sino usar cierre normal
                    if usar_ajustado and pd.notna(fila.get('Adj Close')):
                        precio_cierre = float(fila['Adj Close'])
                    else:
                        precio_cierre = float(fila['Close'])
                    
                    # Validar que el precio de cierre sea válido
                    if pd.isna(precio_cierre) or precio_cierre <= 0:
                        continue
                    
                    punto = PricePoint(
                        date=fecha_dt,
                        open=float(fila['Open']) if pd.notna(fila['Open']) else None,
                        high=float(fila['High']) if pd.notna(fila['High']) else None,
                        low=float(fila['Low']) if pd.notna(fila['Low']) else None,
                        close=precio_cierre,
                        volume=int(fila['Volume']) if pd.notna(fila['Volume']) else None
                    )
                    puntos_precio.append(punto)
                except (ValueError, KeyError, TypeError) as e:
                    # Saltar filas con datos inválidos
                    continue
            
            if not puntos_precio:
                raise ValueError(f"No se pudieron procesar datos válidos para {simbolo}")
            
            # Añadir información sobre si se usaron datos ajustados
            fuente = f"{self.source_name} (yfinance)"
            if not usar_ajustado:
                fuente += " [cierre sin ajustar]"
            
            return PriceSeries(
                symbol=simbolo,
                name=nombre,
                data=puntos_precio,
                source=fuente,
                currency=moneda
            )
            
        except Exception as e:
            raise ConnectionError(f"Error al obtener datos con yfinance para {simbolo}: {e}")
    
    def _fetch_con_requests(self,
                            simbolo: str,
                            fecha_inicio: datetime,
                            fecha_fin: datetime,
                            max_reintentos: int = 3) -> PriceSeries:
        """
        Método fallback: Obtiene datos usando requests directos a la API.
        
        Args:
            simbolo: Símbolo del valor
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin
            max_reintentos: Número máximo de reintentos
        
        Returns:
            PriceSeries con los datos
        """
        # Convertir a timestamps Unix
        periodo1 = int(fecha_inicio.timestamp())
        periodo2 = int(fecha_fin.timestamp())
        
        url = f"{self.base_url}/{simbolo}"
        params = {
            "period1": periodo1,
            "period2": periodo2,
            "interval": "1d",
            "events": "history"
        }
        
        # Reintentos con backoff exponencial
        for intento in range(max_reintentos):
            try:
                # Pausa progresiva entre intentos
                if intento > 0:
                    tiempo_espera = min(2 ** intento, 10)  # Máximo 10 segundos
                    print(f"  Reintentando en {tiempo_espera} segundos... (intento {intento + 1}/{max_reintentos})")
                    time.sleep(tiempo_espera)
                
                respuesta = requests.get(url, params=params, headers=self.headers, timeout=15)
                
                # Manejo especial para rate limiting
                if respuesta.status_code == 429:
                    tiempo_espera = 30  # Esperar 30 segundos en caso de rate limit
                    if intento < max_reintentos - 1:
                        print(f"  Rate limit alcanzado. Esperando {tiempo_espera} segundos...")
                        time.sleep(tiempo_espera)
                        continue
                    else:
                        raise ConnectionError(f"Rate limit de Yahoo Finance. Intenta más tarde o usa otra fuente de datos.")
                
                respuesta.raise_for_status()
                datos = respuesta.json()
                
                # Parsear datos de Yahoo Finance
                if 'chart' not in datos or 'result' not in datos['chart']:
                    raise ValueError(f"No se encontraron datos para {simbolo}")
                
                resultado = datos['chart']['result'][0]
                
                if 'timestamp' not in resultado or 'indicators' not in resultado:
                    raise ValueError(f"Datos incompletos para {simbolo}")
                
                timestamps = resultado['timestamp']
                quote = resultado['indicators']['quote'][0]
                
                # Intentar obtener datos ajustados (adjclose) si están disponibles
                adjclose_disponible = False
                cierres_ajustados = []
                if 'adjclose' in resultado['indicators'] and len(resultado['indicators']['adjclose']) > 0:
                    adjclose_data = resultado['indicators']['adjclose'][0]
                    if 'adjclose' in adjclose_data:
                        cierres_ajustados = adjclose_data.get('adjclose', [])
                        # Verificar que haya al menos un valor válido (no None, no NaN)
                        adjclose_disponible = len(cierres_ajustados) > 0 and any(
                            c is not None and (isinstance(c, (int, float)) or not pd.isna(c)) 
                            for c in cierres_ajustados
                        )
                
                aperturas = quote.get('open', [])
                maximos = quote.get('high', [])
                minimos = quote.get('low', [])
                cierres = quote.get('close', [])
                volumenes = quote.get('volume', [])
                
                # Crear objeto PriceSeries estandarizado
                puntos_precio = []
                for i, ts in enumerate(timestamps):
                    # Validar que los datos básicos estén disponibles
                    if (i >= len(cierres) or cierres[i] is None or 
                        i >= len(aperturas) or aperturas[i] is None):
                        continue
                    
                    fecha = datetime.fromtimestamp(ts)
                    
                    # Usar cierre ajustado si está disponible y es válido, sino usar cierre normal
                    if (adjclose_disponible and 
                        i < len(cierres_ajustados) and 
                        cierres_ajustados[i] is not None):
                        try:
                            precio_cierre = float(cierres_ajustados[i])
                            # Validar que el precio ajustado sea válido
                            if precio_cierre <= 0 or pd.isna(precio_cierre):
                                precio_cierre = float(cierres[i])
                        except (ValueError, TypeError):
                            precio_cierre = float(cierres[i])
                    else:
                        precio_cierre = float(cierres[i])
                    
                    # Validar que el precio de cierre final sea válido
                    if precio_cierre <= 0 or pd.isna(precio_cierre):
                        continue
                    
                    punto = PricePoint(
                        date=fecha,
                        open=float(aperturas[i]) if aperturas[i] is not None else None,
                        high=float(maximos[i]) if i < len(maximos) and maximos[i] is not None else None,
                        low=float(minimos[i]) if i < len(minimos) and minimos[i] is not None else None,
                        close=precio_cierre,
                        volume=int(volumenes[i]) if i < len(volumenes) and volumenes[i] is not None else None
                    )
                    puntos_precio.append(punto)
                
                # Obtener nombre del activo
                nombre = resultado.get('meta', {}).get('longName', simbolo)
                moneda = resultado.get('meta', {}).get('currency', 'USD')
                
                # Añadir información sobre si se usaron datos ajustados
                fuente = f"{self.source_name} (API directa)"
                if not adjclose_disponible:
                    fuente += " [sin ajustar]"
                
                return PriceSeries(
                    symbol=simbolo,
                    name=nombre,
                    data=puntos_precio,
                    source=fuente,
                    currency=moneda
                )
                
            except requests.Timeout:
                if intento == max_reintentos - 1:
                    raise ConnectionError(f"Timeout al conectar con Yahoo Finance para {simbolo}")
                continue
                
            except requests.RequestException as e:
                if intento == max_reintentos - 1:
                    raise ConnectionError(f"Error al conectar con Yahoo Finance para {simbolo}: {e}")
                continue
                
            except (KeyError, IndexError, ValueError) as e:
                if intento == max_reintentos - 1:
                    raise ValueError(f"Error al procesar datos de Yahoo Finance para {simbolo}: {e}")
                continue
    
    def fetch_historical_prices(self, 
                                simbolo: str, 
                                fecha_inicio: Optional[datetime] = None,
                                fecha_fin: Optional[datetime] = None,
                                max_reintentos: int = 3) -> PriceSeries:
        """
        Obtiene precios históricos de Yahoo Finance.
        Intenta primero con yfinance, si falla usa requests directos como fallback.
        
        Args:
            simbolo: Símbolo del valor (ej: 'AAPL', '^GSPC')
            fecha_inicio: Fecha de inicio (por defecto: 1 año atrás)
            fecha_fin: Fecha de fin (por defecto: hoy)
            max_reintentos: Número máximo de reintentos en caso de error (solo para método fallback)
        """
        if fecha_fin is None:
            fecha_fin = datetime.now()
        if fecha_inicio is None:
            fecha_inicio = fecha_fin - timedelta(days=365)
        
        # Intentar primero con yfinance si está disponible
        if self._verificar_yfinance():
            try:
                return self._fetch_con_yfinance(simbolo, fecha_inicio, fecha_fin)
            except Exception as e:
                # Si falla yfinance, usar método fallback
                print(f"  [ADVERTENCIA] yfinance falló para {simbolo}: {e}")
                print(f"  ↳ Usando método alternativo (requests directos)...")
                return self._fetch_con_requests(simbolo, fecha_inicio, fecha_fin, max_reintentos)
        else:
            # Si yfinance no está disponible, usar método fallback directamente
            print(f"  [INFO] yfinance no disponible, usando método alternativo...")
            return self._fetch_con_requests(simbolo, fecha_inicio, fecha_fin, max_reintentos)
    
    def fetch_multiple_series(self, 
                             simbolos: List[str],
                             fecha_inicio: Optional[datetime] = None,
                             fecha_fin: Optional[datetime] = None,
                             paralelo: bool = True,
                             max_trabajadores: int = 5) -> Dict[str, PriceSeries]:
        """
        Obtiene múltiples series de datos.
        
        Args:
            simbolos: Lista de símbolos
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin
            paralelo: Si True, extrae en paralelo (más rápido). Si False, secuencial.
            max_trabajadores: Número máximo de workers paralelos (solo si paralelo=True)
        """
        if not paralelo:
            # Implementación secuencial (para compatibilidad o cuando se requiere)
            resultados = {}
            for simbolo in simbolos:
                try:
                    resultados[simbolo] = self.fetch_historical_prices(simbolo, fecha_inicio, fecha_fin)
                    # Pausa más larga entre requests para evitar rate limiting
                    time.sleep(1.0)
                except Exception as e:
                    print(f"Error al obtener datos para {simbolo}: {e}")
                    # Pausa adicional antes de continuar con el siguiente símbolo
                    time.sleep(2.0)
                    continue
            return resultados
        
        # Implementación paralela
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        resultados = {}
        
        def obtener_serie(simbolo: str) -> tuple:
            """Función auxiliar para obtener datos de un símbolo."""
            try:
                serie = self.fetch_historical_prices(simbolo, fecha_inicio, fecha_fin)
                return (simbolo, serie, None)
            except Exception as e:
                return (simbolo, None, str(e))
        
        # Ejecutar en paralelo
        with ThreadPoolExecutor(max_workers=max_trabajadores) as ejecutor:
            futuro_a_simbolo = {
                ejecutor.submit(obtener_serie, simbolo): simbolo 
                for simbolo in simbolos
            }
            
            for futuro in as_completed(futuro_a_simbolo):
                simbolo, serie, error = futuro.result()
                
                if serie is not None:
                    resultados[simbolo] = serie
                    try:
                        print(f"[OK] Obtenidos datos de {simbolo}")
                    except UnicodeEncodeError:
                        print(f"[OK] Obtenidos datos de {simbolo}")
                else:
                    try:
                        print(f"[ERROR] Error con {simbolo}: {error}")
                    except UnicodeEncodeError:
                        print(f"[ERROR] Error con {simbolo}: {error}")
        
        return resultados
    
    def fetch_fundamental_data(self, symbol: str) -> Dict[str, Any]:
        """Implementación usando yfinance para datos fundamentales."""
        if not self._verificar_yfinance():
            raise NotImplementedError("yfinance no está disponible para datos fundamentales")
        
        import yfinance as yf
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Extraer datos fundamentales relevantes
            fundamental_data = {
                'symbol': symbol,
                'name': info.get('longName', info.get('shortName', symbol)),
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE'),
                'forward_pe': info.get('forwardPE'),
                'pb_ratio': info.get('priceToBook'),
                'ps_ratio': info.get('priceToSalesTrailing12Months'),
                'dividend_yield': info.get('dividendYield'),
                'dividend_rate': info.get('dividendRate'),
                'payout_ratio': info.get('payoutRatio'),
                'eps': info.get('trailingEps'),
                'forward_eps': info.get('forwardEps'),
                'revenue': info.get('totalRevenue'),
                'revenue_per_share': info.get('revenuePerShare'),
                'profit_margin': info.get('profitMargins'),
                'operating_margin': info.get('operatingMargins'),
                'ebitda': info.get('ebitda'),
                'gross_profit': info.get('grossProfits'),
                'free_cash_flow': info.get('freeCashflow'),
                'debt_to_equity': info.get('debtToEquity'),
                'current_ratio': info.get('currentRatio'),
                'quick_ratio': info.get('quickRatio'),
                'sector': info.get('sector'),
                'industry': info.get('industry'),
                'country': info.get('country'),
                'currency': info.get('currency', 'USD'),
                'exchange': info.get('exchange'),
                '52_week_high': info.get('fiftyTwoWeekHigh'),
                '52_week_low': info.get('fiftyTwoWeekLow'),
                'beta': info.get('beta'),
                'shares_outstanding': info.get('sharesOutstanding'),
                'float_shares': info.get('floatShares'),
                'date_updated': datetime.now()
            }
            
            # Filtrar valores None
            return {k: v for k, v in fundamental_data.items() if v is not None}
        except Exception as e:
            raise ConnectionError(f"Error al obtener datos fundamentales para {symbol}: {e}")
    
    def fetch_dividend_data(self, 
                           symbol: str,
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Implementación usando yfinance para dividendos."""
        if not self._verificar_yfinance():
            raise NotImplementedError("yfinance no está disponible para datos de dividendos")
        
        import yfinance as yf
        import pandas as pd
        
        try:
            ticker = yf.Ticker(symbol)
            
            # Obtener dividendos usando history con acciones específicas
            try:
                # Intentar obtener dividendos directamente
                dividends = ticker.dividends
                
                # Si no hay dividendos o está vacío, intentar con history
                if dividends is None or (hasattr(dividends, 'empty') and dividends.empty):
                    # Intentar obtener desde history
                    hist = ticker.history(start=start_date, end=end_date, actions=True)
                    if hist is not None and not hist.empty and 'Dividends' in hist.columns:
                        dividends = hist['Dividends']
                    else:
                        return []
                
                # Si sigue siendo None o vacío, retornar lista vacía
                if dividends is None or (hasattr(dividends, 'empty') and dividends.empty):
                    return []
                
                # Convertir a Series si es necesario
                if not isinstance(dividends, pd.Series):
                    return []
                
                # Asegurar que el índice sea DatetimeIndex
                if not isinstance(dividends.index, pd.DatetimeIndex):
                    try:
                        dividends.index = pd.to_datetime(dividends.index)
                    except Exception:
                        return []
                
                # Filtrar por fechas si se especifican
                if start_date:
                    try:
                        start_ts = pd.Timestamp(start_date)
                        # Asegurar que start_ts tenga la misma zona horaria que el índice si es necesario
                        if dividends.index.tz is not None:
                            start_ts = start_ts.tz_localize(dividends.index.tz) if start_ts.tz is None else start_ts
                        dividends = dividends[dividends.index >= start_ts]
                    except Exception:
                        # Si hay error en la comparación, continuar sin filtrar por fecha inicio
                        pass
                if end_date:
                    try:
                        end_ts = pd.Timestamp(end_date)
                        # Asegurar que end_ts tenga la misma zona horaria que el índice si es necesario
                        if dividends.index.tz is not None:
                            end_ts = end_ts.tz_localize(dividends.index.tz) if end_ts.tz is None else end_ts
                        dividends = dividends[dividends.index <= end_ts]
                    except Exception:
                        # Si hay error en la comparación, continuar sin filtrar por fecha fin
                        pass
                
                # Filtrar solo valores positivos (dividendos reales)
                dividends = dividends[dividends > 0]
                
                if dividends.empty:
                    return []
                
                # Convertir a lista de diccionarios
                dividend_list = []
                for fecha, monto in dividends.items():
                    try:
                        # Convertir fecha a datetime
                        if isinstance(fecha, pd.Timestamp):
                            fecha_dt = fecha.to_pydatetime()
                        elif hasattr(fecha, 'to_pydatetime'):
                            fecha_dt = fecha.to_pydatetime()
                        else:
                            fecha_dt = pd.to_datetime(fecha).to_pydatetime()
                        
                        dividend_list.append({
                            'date': fecha_dt,
                            'amount': float(monto),
                            'currency': 'USD'
                        })
                    except Exception as e:
                        # Saltar este dividendo si hay error en la conversión
                        continue
                
                return dividend_list
                
            except AttributeError:
                # Si dividends no existe como atributo, retornar lista vacía
                return []
                
        except Exception as e:
            raise ConnectionError(f"Error al obtener dividendos para {symbol}: {e}")
    
    def fetch_earnings_data(self,
                           symbol: str,
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Implementación usando yfinance para resultados."""
        if not self._verificar_yfinance():
            raise NotImplementedError("yfinance no está disponible para datos de resultados")
        
        import yfinance as yf
        import pandas as pd
        
        try:
            ticker = yf.Ticker(symbol)
            
            # Intentar obtener earnings_history
            earnings = None
            try:
                earnings = ticker.earnings_history
            except (AttributeError, KeyError):
                # Si earnings_history no existe, intentar con calendar
                try:
                    earnings = ticker.calendar
                except (AttributeError, KeyError):
                    pass
            
            # Si no hay datos de earnings, retornar lista vacía
            if earnings is None:
                return []
            
            # Verificar si es DataFrame o Series
            if hasattr(earnings, 'empty') and earnings.empty:
                return []
            
            # Si no es DataFrame, intentar convertir
            if not isinstance(earnings, pd.DataFrame):
                # Intentar obtener desde info
                try:
                    info = ticker.info
                    # Buscar datos de earnings en info
                    if 'earningsHistory' in info:
                        earnings = pd.DataFrame(info['earningsHistory'])
                    elif 'earningsQuarterlyGrowth' in info or 'earningsAnnualGrowth' in info:
                        # No hay datos históricos detallados disponibles
                        return []
                    else:
                        return []
                except:
                    return []
            
            # Convertir a formato estandarizado
            earnings_list = []
            for _, row in earnings.iterrows():
                try:
                    # Intentar obtener fecha de diferentes campos posibles
                    fecha = None
                    if 'date' in row:
                        fecha = row['date']
                    elif 'Date' in row:
                        fecha = row['Date']
                    elif 'Earnings Date' in row:
                        fecha = row['Earnings Date']
                    elif row.index[0] if len(row) > 0 else None:
                        # Intentar usar el primer índice como fecha
                        fecha = row.index[0] if isinstance(row.index[0], (pd.Timestamp, datetime)) else None
                    
                    # Convertir fecha a datetime si es necesario
                    fecha_dt = None
                    if fecha:
                        try:
                            if isinstance(fecha, str):
                                fecha_dt = pd.to_datetime(fecha)
                            elif isinstance(fecha, pd.Timestamp):
                                fecha_dt = fecha.to_pydatetime()
                            elif isinstance(fecha, datetime):
                                fecha_dt = fecha
                            else:
                                # Intentar convertir cualquier otro tipo
                                fecha_dt = pd.to_datetime(fecha).to_pydatetime()
                            
                            # Asegurar que fecha_dt sea datetime (no Timestamp)
                            if isinstance(fecha_dt, pd.Timestamp):
                                fecha_dt = fecha_dt.to_pydatetime()
                            
                            # Filtrar por fechas si se especifican
                            if start_date:
                                # Asegurar que start_date sea datetime para comparación
                                if isinstance(start_date, pd.Timestamp):
                                    start_date_dt = start_date.to_pydatetime()
                                elif isinstance(start_date, datetime):
                                    start_date_dt = start_date
                                else:
                                    start_date_dt = pd.to_datetime(start_date).to_pydatetime()
                                
                                # Comparar solo la parte de fecha (sin hora) si es necesario
                                if fecha_dt.date() < start_date_dt.date():
                                    continue
                            
                            if end_date:
                                # Asegurar que end_date sea datetime para comparación
                                if isinstance(end_date, pd.Timestamp):
                                    end_date_dt = end_date.to_pydatetime()
                                elif isinstance(end_date, datetime):
                                    end_date_dt = end_date
                                else:
                                    end_date_dt = pd.to_datetime(end_date).to_pydatetime()
                                
                                # Comparar solo la parte de fecha (sin hora) si es necesario
                                if fecha_dt.date() > end_date_dt.date():
                                    continue
                            
                        except Exception as e:
                            # Si hay error en la conversión de fecha, saltar este registro
                            continue
                    
                    # Obtener valores de EPS
                    eps_actual = row.get('epsActual') or row.get('EpsActual') or row.get('Actual') or None
                    eps_estimate = row.get('epsEstimate') or row.get('EpsEstimate') or row.get('Estimate') or None
                    eps_surprise = row.get('epsSurprise') or row.get('EpsSurprise') or row.get('Surprise') or None
                    eps_surprise_percent = row.get('epsSurprisePercent') or row.get('EpsSurprisePercent') or row.get('SurprisePercent') or None
                    
                    # Convertir a float si es posible
                    if eps_actual is not None:
                        try:
                            eps_actual = float(eps_actual)
                        except (ValueError, TypeError):
                            eps_actual = None
                    if eps_estimate is not None:
                        try:
                            eps_estimate = float(eps_estimate)
                        except (ValueError, TypeError):
                            eps_estimate = None
                    if eps_surprise is not None:
                        try:
                            eps_surprise = float(eps_surprise)
                        except (ValueError, TypeError):
                            eps_surprise = None
                    if eps_surprise_percent is not None:
                        try:
                            eps_surprise_percent = float(eps_surprise_percent)
                        except (ValueError, TypeError):
                            eps_surprise_percent = None
                    
                    # Solo agregar si fecha se convirtió correctamente
                    if fecha_dt and isinstance(fecha_dt, datetime):
                        earnings_list.append({
                            'date': fecha_dt,
                            'eps_actual': eps_actual,
                            'eps_estimate': eps_estimate,
                            'eps_surprise': eps_surprise,
                            'eps_surprise_percent': eps_surprise_percent,
                            'currency': 'USD'
                        })
                    elif fecha:
                        # Si fecha existe pero no se pudo convertir a datetime, agregar sin fecha
                        earnings_list.append({
                            'date': None,
                            'eps_actual': eps_actual,
                            'eps_estimate': eps_estimate,
                            'eps_surprise': eps_surprise,
                            'eps_surprise_percent': eps_surprise_percent,
                            'currency': 'USD'
                        })
                except Exception as e:
                    # Saltar esta fila si hay error
                    continue
            
            return earnings_list
            
        except Exception as e:
            # Si hay un error, retornar lista vacía en lugar de lanzar excepción
            # para que el programa continúe
            return []


class AlphaVantageExtractor(DataExtractor):
    """
    Extractor de datos de Alpha Vantage.
    Requiere API key. Formato de salida estandarizado: PriceSeries
    """
    
    def __init__(self, clave_api: str):
        self.clave_api = clave_api
        self.base_url = "https://www.alphavantage.co/query"
        self.source_name = "Alpha Vantage"
    
    def fetch_historical_prices(self, 
                                simbolo: str, 
                                fecha_inicio: Optional[datetime] = None,
                                fecha_fin: Optional[datetime] = None) -> PriceSeries:
        """
        Obtiene precios históricos de Alpha Vantage.
        Intenta usar datos ajustados primero, si no están disponibles usa datos sin ajustar.
        
        Args:
            simbolo: Símbolo del valor
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin
        """
        # Intentar primero con datos ajustados
        params_ajustado = {
            "function": "TIME_SERIES_DAILY_ADJUSTED",
            "symbol": simbolo,
            "apikey": self.clave_api,
            "outputsize": "full" if fecha_inicio is None or (datetime.now() - fecha_inicio).days > 100 else "compact"
        }
        
        usar_ajustado = False
        datos = None
        
        try:
            respuesta = requests.get(self.base_url, params=params_ajustado, timeout=10)
            respuesta.raise_for_status()
            datos = respuesta.json()
            
            if "Error Message" not in datos and "Note" not in datos:
                serie_temporal = datos.get("Time Series (Daily)", {})
                if serie_temporal:
                    usar_ajustado = True
        except Exception:
            # Si falla, continuar con datos sin ajustar
            pass
        
        # Si no se pudieron obtener datos ajustados, usar datos sin ajustar
        if not usar_ajustado:
            params = {
                "function": "TIME_SERIES_DAILY",
                "symbol": simbolo,
                "apikey": self.clave_api,
                "outputsize": "full" if fecha_inicio is None or (datetime.now() - fecha_inicio).days > 100 else "compact"
            }
            
            try:
                respuesta = requests.get(self.base_url, params=params, timeout=10)
                respuesta.raise_for_status()
                datos = respuesta.json()
            except requests.RequestException as e:
                raise ConnectionError(f"Error al conectar con Alpha Vantage: {e}")
            
            try:
                print(f"  [ADVERTENCIA] {simbolo}: Datos ajustados no disponibles, usando cierre sin ajustar")
            except UnicodeEncodeError:
                print(f"  [!] {simbolo}: Datos ajustados no disponibles, usando cierre sin ajustar")
        
        try:
            if "Error Message" in datos:
                raise ValueError(datos["Error Message"])
            if "Note" in datos:
                raise ValueError("API rate limit exceeded. Please wait.")
            
            serie_temporal = datos.get("Time Series (Daily)", {})
            if not serie_temporal:
                raise ValueError(f"No se encontraron datos para {simbolo}")
            
            puntos_precio = []
            for fecha_str, valores in serie_temporal.items():
                fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
                
                # Filtrar por fechas si se especifican
                if fecha_inicio and fecha < fecha_inicio:
                    continue
                if fecha_fin and fecha > fecha_fin:
                    continue
                
                # Si usamos datos ajustados, usar "5. adjusted close", sino usar "4. close"
                if usar_ajustado and "5. adjusted close" in valores:
                    precio_cierre = float(valores["5. adjusted close"])
                    # En datos ajustados, el volumen está en "6. volume"
                    volumen = int(valores.get("6. volume", 0))
                else:
                    precio_cierre = float(valores["4. close"])
                    # En datos sin ajustar, el volumen está en "5. volume"
                    volumen = int(valores.get("5. volume", 0))
                
                punto = PricePoint(
                    date=fecha,
                    open=float(valores["1. open"]),
                    high=float(valores["2. high"]),
                    low=float(valores["3. low"]),
                    close=precio_cierre,
                    volume=volumen if volumen > 0 else None
                )
                puntos_precio.append(punto)
            
            # Obtener metadata
            metadata = datos.get("Meta Data", {})
            nombre = metadata.get("2. Symbol", simbolo)
            
            return PriceSeries(
                symbol=simbolo,
                name=nombre,
                data=puntos_precio,
                source=self.source_name,
                currency="USD"
            )
            
        except requests.RequestException as e:
            raise ConnectionError(f"Error al conectar con Alpha Vantage: {e}")
        except (KeyError, ValueError) as e:
            raise ValueError(f"Error al procesar datos de Alpha Vantage para {simbolo}: {e}")
    
    def fetch_multiple_series(self, 
                             simbolos: List[str],
                             fecha_inicio: Optional[datetime] = None,
                             fecha_fin: Optional[datetime] = None,
                             paralelo: bool = False,
                             max_trabajadores: int = 1) -> Dict[str, PriceSeries]:
        """
        Obtiene múltiples series de datos.
        
        Args:
            simbolos: Lista de símbolos
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin
            paralelo: Si True, extrae en paralelo. NOTA: Alpha Vantage tiene límites estrictos
                     (5 llamadas/minuto), por lo que paralelo=False es recomendado por defecto.
            max_trabajadores: Número máximo de workers paralelos (solo si paralelo=True)
        """
        # Alpha Vantage tiene límites estrictos (5 llamadas/minuto)
        # Por defecto, usar secuencial para evitar rate limiting
        if not paralelo:
            resultados = {}
            for simbolo in simbolos:
                try:
                    resultados[simbolo] = self.fetch_historical_prices(simbolo, fecha_inicio, fecha_fin)
                    # Alpha Vantage tiene límites estrictos, pausa más larga
                    time.sleep(12)  # 5 llamadas por minuto máximo
                except Exception as e:
                    print(f"Error al obtener datos para {simbolo}: {e}")
                    continue
            
            return resultados
        
        # Implementación paralela (usar con precaución debido a rate limits)
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        resultados = {}
        
        def obtener_serie(simbolo: str) -> tuple:
            """Función auxiliar para obtener datos de un símbolo."""
            try:
                serie = self.fetch_historical_prices(simbolo, fecha_inicio, fecha_fin)
                # Pausa para respetar rate limits incluso en paralelo
                time.sleep(12)
                return (simbolo, serie, None)
            except Exception as e:
                return (simbolo, None, str(e))
        
        # Ejecutar en paralelo (con muy pocos workers debido a rate limits)
        with ThreadPoolExecutor(max_workers=min(max_trabajadores, 1)) as ejecutor:
            futuro_a_simbolo = {
                ejecutor.submit(obtener_serie, simbolo): simbolo 
                for simbolo in simbolos
            }
            
            for futuro in as_completed(futuro_a_simbolo):
                simbolo, serie, error = futuro.result()
                
                if serie is not None:
                    resultados[simbolo] = serie
                    try:
                        print(f"[OK] Obtenidos datos de {simbolo}")
                    except UnicodeEncodeError:
                        print(f"[OK] Obtenidos datos de {simbolo}")
                else:
                    try:
                        print(f"[ERROR] Error con {simbolo}: {error}")
                    except UnicodeEncodeError:
                        print(f"[ERROR] Error con {simbolo}: {error}")
        
        return resultados


class DataExtractorFactory:
    """
    Factory para crear extractores de datos.
    Facilita el cambio entre diferentes fuentes manteniendo la misma interfaz.
    """
    
    @staticmethod
    def create_yahoo_extractor() -> YahooFinanceExtractor:
        """Crea un extractor de Yahoo Finance (sin API key requerida)."""
        return YahooFinanceExtractor()
    
    @staticmethod
    def create_alphavantage_extractor(clave_api: str) -> AlphaVantageExtractor:
        """Crea un extractor de Alpha Vantage (requiere API key)."""
        return AlphaVantageExtractor(clave_api)
    
    @staticmethod
    def get_default_extractor() -> YahooFinanceExtractor:
        """Retorna el extractor por defecto (Yahoo Finance)."""
        return YahooFinanceExtractor()
    
    @staticmethod
    def fetch_index(index_name: str, 
                    fecha_inicio: Optional[datetime] = None,
                    fecha_fin: Optional[datetime] = None) -> PriceSeries:
        """
        Método helper para obtener datos de un índice común.
        
        Args:
            index_name: Nombre del índice (ej: 'sp500', 'S&P 500', '^GSPC')
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin
        
        Returns:
            PriceSeries con los datos del índice
        
        Example:
            >>> extractor = DataExtractorFactory.get_default_extractor()
            >>> sp500 = DataExtractorFactory.fetch_index('sp500')
        """
        from .indices import importar_indice
        extractor = DataExtractorFactory.get_default_extractor()
        serie = importar_indice(index_name, extractor, fecha_inicio, fecha_fin)
        if serie is None:
            raise ValueError(f"No se pudo obtener el índice '{index_name}'")
        return serie


class MultiAPIExtractor:
    """
    Extractor que permite obtener datos de múltiples APIs diferentes simultáneamente.
    Permite especificar qué API usar para cada símbolo.
    """
    
    def __init__(self):
        """Inicializa el extractor multi-API con extractores disponibles."""
        self.extractors: Dict[str, DataExtractor] = {}
        self.default_extractor: Optional[DataExtractor] = None
    
    def register_extractor(self, nombre: str, extractor: DataExtractor, es_por_defecto: bool = False) -> None:
        """
        Registra un extractor con un nombre.
        
        Args:
            nombre: Nombre identificador del extractor (ej: 'yahoo', 'alphavantage')
            extractor: Instancia del extractor
            es_por_defecto: Si es True, se establece como extractor por defecto
        """
        self.extractors[nombre] = extractor
        if es_por_defecto or self.default_extractor is None:
            self.default_extractor = extractor
    
    def fetch_from_multiple_apis(self,
                                 mapeo_simbolo_api: Dict[str, str],
                                 fecha_inicio: Optional[datetime] = None,
                                 fecha_fin: Optional[datetime] = None) -> Dict[str, PriceSeries]:
        """
        Obtiene datos de múltiples símbolos usando diferentes APIs simultáneamente.
        
        Args:
            mapeo_simbolo_api: Diccionario {simbolo: nombre_api} que especifica qué API usar para cada símbolo
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin
        
        Returns:
            Diccionario {simbolo: PriceSeries} con los datos obtenidos
        
        Example:
            >>> extractor = MultiAPIExtractor()
            >>> extractor.register_extractor('yahoo', YahooFinanceExtractor())
            >>> extractor.register_extractor('alphavantage', AlphaVantageExtractor(clave_api))
            >>> resultados = extractor.fetch_from_multiple_apis({
            ...     'AAPL': 'yahoo',
            ...     'MSFT': 'yahoo',
            ...     'SPY': 'alphavantage'
            ... })
        """
        resultados = {}
        
        for simbolo, nombre_api in mapeo_simbolo_api.items():
            extractor = self.extractors.get(nombre_api)
            
            if extractor is None:
                # Si no se encuentra el extractor, usar el por defecto
                if self.default_extractor is None:
                    print(f"[ADVERTENCIA] No se encontró extractor '{nombre_api}' para {simbolo} y no hay extractor por defecto")
                    continue
                extractor = self.default_extractor
                print(f"[INFO] Usando extractor por defecto para {simbolo}")
            
            try:
                serie = extractor.fetch_historical_prices(simbolo, fecha_inicio, fecha_fin)
                resultados[simbolo] = serie
                print(f"[OK] Obtenidos datos de {simbolo} desde {serie.source}")
            except Exception as e:
                print(f"[ERROR] Error al obtener {simbolo} desde {nombre_api}: {e}")
                continue
        
        return resultados
    
    def fetch_multiple_series(self,
                             simbolos: List[str],
                             fecha_inicio: Optional[datetime] = None,
                             fecha_fin: Optional[datetime] = None,
                             paralelo: bool = True,
                             max_trabajadores: int = 5) -> Dict[str, PriceSeries]:
        """
        Obtiene múltiples series usando el extractor por defecto.
        Permite usar MultiAPIExtractor como extractor simple cuando no hay mapeo específico.
        
        Args:
            simbolos: Lista de símbolos a obtener
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin
            paralelo: Si True, extrae en paralelo (más rápido). Si False, secuencial.
            max_trabajadores: Número máximo de workers paralelos (solo si paralelo=True)
        
        Returns:
            Diccionario {simbolo: PriceSeries} con los datos obtenidos
        """
        if self.default_extractor is None:
            raise ValueError("No hay extractor por defecto configurado en MultiAPIExtractor")
        
        return self.default_extractor.fetch_multiple_series(
            simbolos, fecha_inicio, fecha_fin, paralelo, max_trabajadores
        )
    
    def fetch_parallel(self,
                      peticiones: List[Dict[str, Any]],
                      max_trabajadores: int = 3) -> Dict[str, PriceSeries]:
        """
        Obtiene datos de múltiples APIs en paralelo usando threading.
        
        Args:
            peticiones: Lista de diccionarios con formato:
                    [{'symbol': 'AAPL', 'api': 'yahoo'}, {'symbol': 'MSFT', 'api': 'alphavantage'}, ...]
            max_trabajadores: Número máximo de workers paralelos
        
        Returns:
            Diccionario {simbolo: PriceSeries} con los datos obtenidos
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        resultados = {}
        
        def obtener_unico(item_peticion: Dict[str, Any]) -> tuple:
            """Función auxiliar para obtener datos de un símbolo."""
            simbolo = item_peticion['symbol']
            nombre_api = item_peticion.get('api', 'default')
            fecha_inicio = item_peticion.get('start_date')
            fecha_fin = item_peticion.get('end_date')
            
            extractor = self.extractors.get(nombre_api)
            if extractor is None:
                extractor = self.default_extractor
            
            if extractor is None:
                return (simbolo, None, f"No extractor available for {nombre_api}")
            
            try:
                serie = extractor.fetch_historical_prices(simbolo, fecha_inicio, fecha_fin)
                return (simbolo, serie, None)
            except Exception as e:
                return (simbolo, None, str(e))
        
        # Ejecutar en paralelo
        with ThreadPoolExecutor(max_workers=max_trabajadores) as ejecutor:
            futuro_a_peticion = {
                ejecutor.submit(obtener_unico, peticion): peticion 
                for peticion in peticiones
            }
            
            for futuro in as_completed(futuro_a_peticion):
                simbolo, serie, error = futuro.result()
                
                if serie is not None:
                    resultados[simbolo] = serie
                    print(f"[OK] Obtenidos datos de {simbolo}")
                else:
                    print(f"[ERROR] Error con {simbolo}: {error}")
        
        return resultados

