# Tarea1_MIAX

Herramienta para la obtención y análisis de acciones e índices.

## Tabla de Contenidos

- [Descripción](#descripción)
- [Arquitectura](#arquitectura)
- [Instalación](#instalación)
  - [Requisitos Previos](#requisitos-previos)
  - [Configuración del Entorno Virtual](#configuración-del-entorno-virtual)
  - [Archivo `.env`](#archivo-env)
  - [Verificación del Entorno](#verificación-del-entorno)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Uso](#uso)
  - [Configuración Rápida](#configuración-rápida)
- [Configuración Detallada](#configuración-detallada)
- [Módulos de `src/` en Orden de Ejecución](#módulos-de-src-en-orden-de-ejecución)
- [Simulación de Monte Carlo](#simulación-de-monte-carlo)
- [Reportes](#reportes)
- [Limpieza y Preprocesado](#limpieza-y-preprocesado)
- [Notas Importantes](#notas-importantes)
- [Licencia](#licencia)
- [Contribuciones](#contribuciones)

## Descripción

Este proyecto proporciona un conjunto completo de herramientas para:
- **Extracción de datos** desde dos fuentes (APIs) con formato estandarizado (Yahoo Finance y Alpha Vantage)
- **Análisis estadístico** automático de series de precios
- **Gestión de carteras** con cálculos estadísticos
- **Simulación de Monte Carlo** para proyecciones
- **Generación de reportes** en Markdown y visualizaciones

## Arquitectura

El proyecto está diseñado con las siguientes características:
- **Estructura**: Organización clara y modular
- **Estandarización**: Formato de salida uniforme independiente de la fuente.
- **Abstracción**: Interfaces claras que permiten extensibilidad.
- **Separación de responsabilidades**: Módulos con funciones bien definidas.
- **Automatización**: Cálculos estadísticos automáticos.
- **Configuración centralizada**: Todos los parámetros se configuran desde `configuracion_parametros.py`.
- **Seguridad**: API keys protegidas en `.env` (no versionado)
- **Plug and play**: Haciendo que tras la instalación sea lo más fácil posible su uso.

## Instalación

### Requisitos Previos
- Python 3.8 o superior

### Configuración del Entorno Virtual

1. **Crear el entorno virtual**:
   ```bash
   python -m venv venv
   ```

2. **Activar el entorno virtual**:
   
   En Windows (PowerShell):
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
   
   En Windows (CMD):
   ```cmd
   venv\Scripts\activate.bat
   ```
   
   En Linux/Mac:
   ```bash
   source venv/bin/activate
   ```

3. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

### Archivo `.env`

Para proteger tus API keys, usa el archivo `.env`:

1. Copia `.env.example` a `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edita `.env` y añade tus API keys:
   ```
   ALPHA_VANTAGE_API_KEY=tu_clave_real_aqui
   ```

3. El archivo `.env` está en `.gitignore` y **NO se subirá a GitHub**.

**Importante**: Las API keys se cargan automáticamente desde `.env` cuando ejecutas `main.py`. No necesitas modificar código.

### Verificación del Entorno

Después de la instalación, puedes verificar que todo esté correcto:

```bash
python check_setup.py
```

Este script verifica:
- Versión de Python.
- Entorno virtual.
- Dependencias instaladas.
- Archivos necesarios.
- Configuración básica.

## Estructura del Proyecto

```
Tarea1_MIAX/
├── src/                    # Código fuente principal
│   ├── __init__.py
│   ├── data_classes.py     # DataClasses para series de precios
│   ├── extractor.py        # Extractores de datos de múltiples APIs
│   ├── portfolio.py        # Clase Portfolio y métodos de análisis
│   ├── report.py           # Generación de reportes del portfolio
│   ├── indices.py          # Utilidades para índices, nomenclatura, etc
│   └── validation.py       # Validación del documento configuración_parametros
├── configuracion_parametros.py  # CONFIGURACIÓN: Tickers, índices, períodos, etc.  (Todos los parametros más importantes para ser plug and play)
├── main.py                  # Script principal (ejecuta todo automáticamente solo con poner 'python main.py' )
├──docs/                    #carpeta de documentación
│   ├──CLASS_DIAGRAM.md     # Descripción detallada del diagrama de flujo, classes, herencias etc
│   ├── Diagrama de flujo.jpg # Mapa conceptual simple del diagrama de flujo
├── .env.example            # Plantilla para API keys (copiar a .env)
├── .env                    # API keys reales (NO se sube a GitHub)
├── .gitignore
├── venv/                   # Entorno virtual
├── requirements.txt        # Dependencias del proyecto
├── check_setup.py    # Script de verificación del entorno
├── LICENSE                 # Licencia del proyecto
└── README.md               # Este archivo
```

## Uso


1. **Configurar API Keys (opcional)**:
   ```bash
   # Copiar el archivo de ejemplo
   cp .env.example .env
   
   # Editar .env y añadir tus API keys
   # ALPHA_VANTAGE_API_KEY=tu_clave_aqui
   ```
   **Nota**: Yahoo Finance no requiere API key. Si solo usas Yahoo Finance, puedes omitir este paso.

2. **Configurar parámetros en `configuracion_parametros.py`**:
   
   Edita `configuracion_parametros.py` y ajusta según tus necesidades:
   - `TICKERS_ACCIONES`: Lista de acciones a analizar
   - `INDICES`: Lista de índices a analizar
   - `PESOS_CARTERA`: Pesos de cada valor/holding en la cartera
   - `FECHA_INICIO_EXTRACCION` / `FECHA_FIN_EXTRACCION`: Período de datos
   - `DIAS_MONTE_CARLO`: Días a simular hacia adelante
   - `NUM_SIMULACIONES_MONTE_CARLO`: Número de simulaciones
   - Y muchos más parámetros así como ejemplo de otras posibles carteras.

3. **Ejecutar**:
   ```bash
   python main.py
   ```

El script ejecutará automáticamente:
- Extracción de datos de las APIs configuradas.
- Limpieza y preprocesado de datos.
- Creación de la cartera con los pesos especificados.
- Generación de reportes en Markdown.
- Visualizaciones (gráficos guardados en `plots/`).
- Simulación de Monte Carlo con gráficos.

## Configuración Detallada

### Archivo `configuracion_parametros.py`

Este es el archivo central de configuración. Aquí puedes especificar:

#### Tickers e Índices
- `TICKERS_ACCIONES`: Lista de símbolos de acciones (ej: `["AAPL", "MSFT"]`)
- `INDICES`: Lista de índices (ej: `["sp500", "dowjones", "nasdaq"]`)

#### Períodos de Tiempo
- `FECHA_INICIO_EXTRACCION`: Fecha de inicio (None = 1 año atrás desde hoy)
- `FECHA_FIN_EXTRACCION`: Fecha de fin (None = hoy)
- `DIAS_MONTE_CARLO`: Días a simular hacia adelante (default: 252, un año de trading)

#### Monte Carlo
- `TIPO_MONTE_CARLO`: Tipo de simulación ("cartera", "accion_individual", "todos_los_elementos", "seleccion_elementos")
- `SIMBOLO_MONTE_CARLO`: Símbolo para simulación individual (si TIPO_MONTE_CARLO="accion_individual")
- `SIMBOLOS_MONTE_CARLO`: Lista de símbolos para simulación seleccionada (si TIPO_MONTE_CARLO="seleccion_elementos")
- `NUM_SIMULACIONES_MONTE_CARLO`: Número de simulaciones (default: 1000)
- `VALOR_INICIAL_CARTERA`: Valor inicial para simulación (default: 10000.0)
- `NIVELES_CONFIANZA`: Percentiles a calcular (default: [0.05, 0.25, 0.50, 0.75, 0.95])
- `MOSTRAR_BANDAS_CONFIANZA`: Mostrar bandas de confianza en gráficos (default: False)

#### Cartera
- `NOMBRE_CARTERA`: Nombre de la cartera
- `PESOS_CARTERA`: Diccionario {símbolo: peso} (deben sumar ≤ 1.0)

#### APIs
- `API_POR_DEFECTO`: API a usar por defecto ('yahoo', 'alphavantage')
- `MAPEO_SIMBOLO_API`: Especificar API para cada símbolo (opcional)

#### Reportes y Visualizaciones
- `TASA_LIBRE_RIESGO`: Tasa libre de riesgo (default: 0.02 = 2%)
- `RUTA_GUARDADO_GRAFICOS`: Carpeta para guardar gráficos (default: "plots")
- `MOSTRAR_GRAFICOS`: Mostrar gráficos en pantalla (default: False)
- `INCLUIR_ESTADISTICAS`: Incluir estadísticas detalladas en el reporte (default: True)
- `INCLUIR_ADVERTENCIAS`: Incluir advertencias en el reporte (default: True)

#### Limpieza de Datos
- `ELIMINAR_DUPLICADOS`: Eliminar puntos duplicados (default: True)
- `ELIMINAR_OUTLIERS`: Eliminar outliers (default: True)
- `UMBRAL_OUTLIER`: Número de desviaciones estándar para considerar outlier (default: 3.0)

#### Extracción Paralela
- `EXTRACCION_PARALELA`: Extraer datos en paralelo (default: True)
- `MAX_WORKERS_EXTRACCION`: Número máximo de workers paralelos (default: 5)

#### Datos Adicionales
- `EXTRAER_DATOS_FUNDAMENTALES`: Extraer datos fundamentales (P/E, P/B, etc.) (default: True)
- `EXTRAER_DIVIDENDOS`: Extraer historial de dividendos (default: False)
- `EXTRAER_INDICADORES_TECNICOS`: Extraer indicadores técnicos (default: False)
- `INDICADORES_TECNICOS`: Lista de indicadores técnicos a calcular si `EXTRAER_INDICADORES_TECNICOS = True` (ej: `["RSI", "MACD", "SMA_50"]`)

**Nota**: Si `EXTRAER_DATOS_FUNDAMENTALES` o `EXTRAER_DIVIDENDOS` son `True`, los datos se imprimirán automáticamente por pantalla.

## Módulos de `src/` en Orden de Ejecución

Los módulos se ejecutan en el siguiente orden cuando se corre `main.py`:

### 1. `validation.py` - Validación de Configuración

**Cuándo se ejecuta**: Al inicio de `main.py`, antes de cualquier extracción de datos.

**Función principal**:
- **`validar_configuracion()`**: Valida que todos los parámetros en `configuracion_parametros.py` sean correctos
- Verifica tipos de datos, rangos válidos, y consistencia entre parámetros
- Retorna lista de advertencias si encuentra problemas

**Ejemplo de validaciones**:
- Verifica que los pesos de la cartera sumen ≤ 1.0
- Comprueba que los símbolos de Monte Carlo existan en los datos extraídos
- Valida que las API keys estén presentes cuando se necesitan

### 2. `extractor.py` - Extractores de Datos Multi-API

**Cuándo se ejecuta**: Después de la validación, se configuran los extractores y luego se usan para extraer datos.

**Clases principales**:

**`DataExtractor`** (clase abstracta):
- Interfaz base: `fetch_historical_prices()` y `fetch_multiple_series()`
- Garantiza que todos los extractores devuelvan `PriceSeries` estandarizado

**`YahooFinanceExtractor`**:
- Método principal: Usa la librería `yfinance` (más robusta y mantenida)
- Fallback: Si `yfinance` falla, usa requests directos a la API de Yahoo Finance
- Preferencia: Prioriza datos ajustados (Adj Close) cuando están disponibles
- No requiere API key
- Soporta extracción paralela

**`AlphaVantageExtractor`**:
- Usa la API REST de Alpha Vantage
- Preferencia: Intenta usar `TIME_SERIES_DAILY_ADJUSTED` (datos ajustados) primero
- Fallback: Si no hay datos ajustados, usa `TIME_SERIES_DAILY`
- Requiere API key (máximo 5 llamadas/minuto en plan free)

**`MultiAPIExtractor`**:
- Permite usar múltiples APIs simultáneamente
- Mapea símbolos específicos a APIs específicas según `MAPEO_SIMBOLO_API`
- Utiliza un extractor por defecto para símbolos no mapeados
- Ideal cuando diferentes APIs tienen mejor cobertura para ciertos activos

**`DataExtractorFactory`**:
- Factory pattern para crear extractores de forma simplificada
- Métodos: `create_yahoo_extractor()`, `create_alphavantage_extractor()`, `get_default_extractor()`

**Métodos opcionales** (si están habilitados en configuración):
- `fetch_fundamental_data()` - Datos fundamentales (P/E, P/B, etc.)
- `fetch_dividend_data()` - Historial de dividendos
- `fetch_technical_indicators()` - Indicadores técnicos (RSI, MACD, etc.)

### 3. `indices.py` - Utilidades para Índices Bursátiles

**Cuándo se ejecuta**: Después de configurar extractores, se usan para extraer índices antes que las acciones.

**Funciones principales**:
- **`INDICES_COMUNES`**: Diccionario con índices populares y sus símbolos en Yahoo Finance
  - Índices de EE.UU.: S&P 500, Dow Jones, NASDAQ, NASDAQ 100, Russell 2000, VIX
  - Índices internacionales: FTSE 100, DAX, CAC 40, Nikkei 225, Shanghai Composite, Hang Seng
  - ETFs de índices: SPY, QQQ, DIA, IWM
- **`get_index_symbol()`**: Obtiene el símbolo de un índice por su nombre
- **`get_index_info()`**: Obtiene información completa (nombre, descripción) de un índice
- **`importar_indice()`**: Importa datos de un índice específico
- **`importar_indices()`**: Importa múltiples índices simultáneamente (con soporte paralelo)

### 4. `data_classes.py` - Estructuras de Datos Estandarizadas

**Cuándo se ejecuta**: Los datos extraídos se convierten a `PriceSeries`, y luego se limpian usando los métodos de esta clase.

**Clases principales**:

**`PricePoint`** (dataclass):
- Representa un punto de precio en el tiempo
- Campos: `date`, `open`, `high`, `low`, `close`, `volume`
- Validación automática: asegura que `high >= low`, `open` y `close` estén dentro del rango

**`PriceSeries`** (dataclass):
- Serie temporal de precios estandarizada (formato uniforme independiente de la fuente)
- Atributos: `symbol`, `name`, `data` (lista de PricePoint), `source`, `currency`
- **Estadísticas automáticas**: Calcula media y desviación típica de retornos logarítmicos al crear/modificar datos
- **Métodos principales**:
  - `annualized_return()` - Retorno anualizado (252 días de trading)
  - `volatility()` - Volatilidad anualizada
  - `sharpe_ratio(tasa_libre_riesgo)` - Ratio de Sharpe
  - `max_drawdown()` - Máximo drawdown histórico
  - `clean_data()` - Limpia datos: elimina None/NaN, duplicados y outliers (umbral: 3 desviaciones estándar)
  - `monte_carlo_simulation()` - Simulación de Monte Carlo para un activo individual
  - `plot_monte_carlo()` - Visualización de la simulación
  - `to_dataframe()` - Conversión a pandas DataFrame

### 5. `portfolio.py` - Gestión de Carteras

**Cuándo se ejecuta**: Después de limpiar los datos, se crea la cartera y se realizan los análisis.

**Clase principal**:

**`Portfolio`** (dataclass):
- Representa una cartera de valores con pesos asignados
- Atributos: `name`, `holdings` (dict: símbolo -> peso), `price_series` (dict: símbolo -> PriceSeries)
- **Métodos principales**:
  - `add_holding()` - Añade un holding con su peso (normaliza automáticamente si suma > 1)
  - `remove_holding()` - Elimina un holding
  - `get_portfolio_returns()` - Calcula retornos de la cartera como combinación ponderada
  - `get_portfolio_value_series()` - Calcula la evolución del valor de la cartera a lo largo del tiempo
  - `monte_carlo_simulation()` - Simulación de Monte Carlo para la cartera completa (considera correlaciones)
  - `plot_monte_carlo()` - Visualiza simulaciones con trayectorias completas, percentiles y estadísticas
  - `plots_report()` - Genera múltiples visualizaciones (valor de cartera, composición, retornos, distribución, correlaciones)

### 6. `report.py` - Generación de Reportes

**Cuándo se ejecuta**: Después de crear la cartera, se genera el reporte en Markdown.

**Función principal**:

**`generate_report()`** (función):
- Genera reportes completos en formato Markdown
- Incluye:
  - Composición de la cartera (símbolos, pesos, nombres)
  - Estadísticas agregadas (retorno, volatilidad, Sharpe, máximo drawdown)
  - Estadísticas por holding individual
  - Advertencias (datos faltantes, períodos diferentes, pesos que no suman 100%)
  - APIs utilizadas para cada símbolo
- Parámetros: `tasa_libre_riesgo`, `incluir_estadisticas`, `incluir_advertencias`
- El reporte se guarda automáticamente en `portfolio_report.md`

### 7. Visualizaciones y Monte Carlo

**Cuándo se ejecuta**: Al final del proceso, después de generar el reporte.

**Visualizaciones** (`portfolio.py`):

- Generan automáticamentelos siguientes gráficos con `plots_report()`:
  - Evolución del valor de la cartera
  - Composición (pie chart)
  - Retornos diarios
  - Distribución de retornos
  - Comparación de holdings
  - Matriz de correlación
- Gráficos guardados en la carpeta especificada en `RUTA_GUARDADO_GRAFICOS`


**Simulación de Monte Carlo**:
- Se ejecuta según `TIPO_MONTE_CARLO` en la configuración
- Puede simular: cartera completa, acción individual, todos los elementos, o selección específica
- Considera correlaciones entre activos para simulaciones de cartera
- Genera gráficos con la distibución obtenida, trayectorias, percentiles y bandas de confianza (si están habilitadas)

### `__init__.py` - Inicialización del Paquete

- Define `src/` como un paquete Python
- Incluye la versión del proyecto: `__version__ = "0.1.0"`




## Limpieza y Preprocesado

El método `clean_data()` de `PriceSeries` realiza una limpieza exhaustiva de datos:

```python
# Limpiar datos de una serie
serie.clean_data(
    eliminar_duplicados=True,    # Eliminar puntos duplicados por fecha
    eliminar_outliers=True,      # Eliminar outliers basados en desviaciones estándar
    umbral_outlier=3.0           # Número de desviaciones estándar para considerar outlier
)
```

**Proceso de limpieza**:
1. **Eliminación de None/NaN**: Elimina puntos donde `open`, `high`, `low` o `close` sean `None`, `NaN` o valores no positivos
2. **Eliminación de duplicados**: Si hay múltiples puntos con la misma fecha, mantiene solo el primero
3. **Eliminación de outliers**: Elimina puntos cuyos retornos logarítmicos estén fuera del umbral (por defecto, 3 desviaciones estándar de la media)

**Criterio de outliers**: Se calculan los retornos logarítmicos entre puntos consecutivos. Un punto se considera outlier si su retorno respecto al punto anterior está fuera del rango `[media - umbral * desviación, media + umbral * desviación]`. Este criterio es estadísticamente robusto y elimina valores anómalos que pueden distorsionar los análisis.

Esto se ejecuta automáticamente en `main.py` según la configuración en `configuracion_parametros.py`.

## Notas Importantes

### Datos Ajustados (Adjusted Close)

**Todos los extractores priorizan datos ajustados** cuando están disponibles:
- Los datos ajustados reflejan el retorno real del inversor, incluyendo dividendos y splits de acciones
- **Yahoo Finance**: Usa `Adj Close` cuando está disponible (siempre con `yfinance`, puede variar con requests directos)
- **Alpha Vantage**: Intenta usar `TIME_SERIES_DAILY_ADJUSTED` primero, luego `TIME_SERIES_DAILY` como fallback

Si un extractor no encuentra datos ajustados, usará datos sin ajustar y mostrará una advertencia en la consola.

### APIs y Limitaciones

- **Yahoo Finance**: 
  - Usa la librería `yfinance` como método principal (más robusto y mantenido)
  - Si `yfinance` falla o no está disponible, automáticamente usa requests directos como fallback
  - No requiere API key
  - Puede tener limitaciones de rate. Si encuentras errores 429, espera unos minutos
- **Alpha Vantage**: 
  - Límite de 5 llamadas por minuto y hasta 25 al dia con la versión gratuita
  - Puede causar errores 429 si se excede el límite

### Otros Aspectos Importantes

- **Formato estandarizado**: Todos los extractores devuelven `PriceSeries` con el mismo formato, independientemente de la fuente
- **Limpieza automática**: Los datos se limpian automáticamente (None/NaN, duplicados, outliers) según la configuración
- **Configuración centralizada**: Todo se configura desde `configuracion_parametros.py`, no necesitas modificar código
- **Ejecución simple**: Solo ejecuta `python main.py` después de configurar
- **Multi-API**: Puedes usar múltiples APIs simultáneamente mapeando símbolos específicos a APIs específicas
- **Extracción paralela**: Soporte para extracción de datos en paralelo para mejorar el rendimiento
- **Validación automática**: El sistema valida automáticamente la configuración antes de ejecutar


## Licencia

Ver [LICENSE](LICENSE) para más detalles.

## Contribuciones

Este es un proyecto educativo. Las mejoras y sugerencias son bienvenidas.


