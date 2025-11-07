# Diagrama de Estructura de Clases

## Diagrama de Clases con Herencias

```
┌─────────────────────────────────────────────────────────────────┐
│                        ABC (Abstract Base Class)                │
│                                                                 │
│                    DataExtractor                                │
│  + fetch_historical_prices() : PriceSeries                      │
│  + fetch_multiple_series(paralelo, max_trabajadores) : Dict     │
│  + fetch_fundamental_data() : Dict (opcional)                   │
│  + fetch_dividend_data() : List[Dict] (opcional)                │
│  + fetch_technical_indicators() : Dict (opcional)               │
│  + fetch_options_data() : List[Dict] (opcional)                 │
│  + fetch_earnings_data() : List[Dict] (opcional)                │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ hereda
                              │
                ┌─────────────┼─────────────┐
                │             │             │
                │             │             │
    ┌───────────┴───┐  ┌──────┴──────┐      │
    │               │  │             │      │
┌───┴───────────┐   │  │  ┌──────────┴──┐   │
│               │   │  │  │             │   │
│ YahooFinance  │   │  │  │ AlphaVantage│   │
│ Extractor     │   │  │  │ Extractor   │   │
│               │   │  │  │             │   │
│ (implementa   │   │  │  │ (implementa │   │
│ métodos       │   │  │  │ métodos     │   │
│ opcionales)   │   │  │  │ opcionales) │   │
└───────────────┘   │  │  └─────────────┘   │
                    │  │                    │
                    │  │                    │
┌───────────────────┴──┴────────────────────┴───────────────────┐
│                    DataExtractorFactory                       │
│  + create_yahoo_extractor() : YahooFinanceExtractor           │
│  + create_alphavantage_extractor() : AlphaVantageExtractor    │
│  + get_default_extractor() : YahooFinanceExtractor            │
└───────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    MultiAPIExtractor                            │
│  (NO hereda de DataExtractor - usa composición)                 │
│                                                                 │
│  - extractors: Dict[str, DataExtractor]                         │
│  - default_extractor: Optional[DataExtractor]                   │
│                                                                 │
│  + register_extractor(nombre, extractor, es_por_defecto)        │
│  + fetch_from_multiple_apis(mapeo_simbolo_api) : Dict           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ usa (composición)
                              │
                              ▼
                    ┌──────────────────────────┐
                    │   DataExtractor          │
                    │   (múltiples instancias) │
                    └──────────────────────────┘


┌─────────────────────────────────────────────────────────────────┐
│                        @dataclass                               │
│                                                                 │
│                    PricePoint                                   │
│  - date: datetime                                               │
│  - open: float                                                  │
│  - high: float                                                  │ 
│  - low: float                                                   │
│  - close: float                                                 │
│  - volume: Optional[int]                                        │
│                                                                 │
│  + __post_init__() : void (validación)                          │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │
                              │ composición (1 a muchos)
                              │
                              │
┌─────────────────────────────┴─────────────────────────────────┐
│                        @dataclass                             │
│                                                               │
│                    PriceSeries                                │
│  - symbol: str                                                │
│  - name: str                                                  │
│  - data: List[PricePoint]                                     │
│  - source: str                                                │
│  - currency: str                                              │
│  - _mean_return: Optional[float] (auto)                       │
│  - _std_return: Optional[float] (auto)                        │
│  - _returns: Optional[pd.Series] (auto)                       │
│                                                               │
│  + __post_init__() : void (calc stats)                        │
│  + _calculate_statistics() : void                             │
│  + mean_return : float (property)                             │
│  + std_return : float (property)                              │
│  + returns : pd.Series (property)                             │
│  + add_data_point(point: PricePoint) : void                   │
│  + to_dataframe() : pd.DataFrame                              │
│  + get_period() : Optional[tuple]                             │
│  + get_latest_price() : Optional[float]                       │
│  + annualized_return() : Optional[float]                      │
│  + volatility() : Optional[float]                             │
│  + sharpe_ratio() : Optional[float]                           │
│  + max_drawdown() : Optional[float]                           │
│  + clean_data() : PriceSeries                                 │
│  + monte_carlo_simulation() : Dict[str, Any]                  │
│  + plot_monte_carlo() : void                                  │
└───────────────────────────────────────────────────────────────┘
                              ▲
                              │
                              │ composición (1 a muchos)
                              │
                              │
┌─────────────────────────────┴───────────────────────────────────────┐
│                        @dataclass                                   │
│                                                                     │
│                    Portfolio                                        │ 
│  - name: str                                                        │
│  - holdings: Dict[str, float]  (symbol → weight)                    │
│  - price_series: Dict[str, PriceSeries]                             │
│                                                                     │
│  + add_holding(symbol, weight, series) : void                       │
│  + remove_holding(symbol) : void                                    │
│  + get_portfolio_returns() : Optional[pd.Series]                    │
│  + get_portfolio_value_series(valor_inicial) : Optional[pd.Series]  │
│  + monte_carlo_simulation(dias, simulaciones, ...) : Dict           │
│  + plot_monte_carlo(dias, simulaciones, mostrar_bandas) : void      │
│  + report() : str (Markdown) - DEPRECATED                           │
│  + plots_report(ruta_guardado, mostrar) : void                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Relaciones entre Clases

### 1. Herencia (Extractores)
```
DataExtractor (ABC)
    ├── YahooFinanceExtractor
    ├── AlphaVantageExtractor
```

### 2. Dataclasses (Series de Datos)
```
PriceSeries (dataclass)
    └── List[PricePoint] (composición)
```

### 3. Composición
```
PriceSeries
    └── List[PricePoint]  (1 a muchos)
    
Portfolio
    └── Dict[str, PriceSeries]  (1 a muchos)
```

### 4. Multi-API Extraction (Composición)
```
MultiAPIExtractor
    └── Dict[str, DataExtractor] (composición)
    └── NO hereda de DataExtractor
    └── Usa múltiples DataExtractor simultáneamente
```

### 5. Factory Pattern
```
DataExtractorFactory
    └── Crea instancias de diferentes extractores
```

## Flujo de Datos

```
API Externa (Yahoo Finance / Alpha Vantage)
    ↓
DataExtractor (abstracto)
    ├── YahooFinanceExtractor
    ├── AlphaVantageExtractor
    └── MultiAPIExtractor (usa composición)
    ↓
PricePoint (dataclass)
    ↓
PriceSeries (dataclass)
    ├── Estadísticas automáticas
    ├── Limpieza de datos (clean_data)
    └── Monte Carlo individual
    ↓
Portfolio (dataclass)
    ├── Agregación de series
    ├── Monte Carlo de cartera (con correlaciones)
    ├── Visualizaciones (plots_report)
    └── Método report() [usar report.py]
    ↓
report.py (módulo separado)
    └── generate_report() - Genera reporte Markdown
```

## Características de las DataClasses

### PricePoint
- **Tipo**: Dataclass simple
- **Propósito**: Representar un punto OHLCV
- **Validación**: Automática en `__post_init__`

### PriceSeries
- **Tipo**: Dataclass con propiedades calculadas
- **Propósito**: Serie temporal estandarizada
- **Características**:
  - Estadísticas automáticas (media, std)
  - Métodos de análisis financiero
  - Limpieza de datos
  - Simulación Monte Carlo individual

### Portfolio
- **Tipo**: Dataclass con colecciones
- **Propósito**: Gestión de carteras
- **Características**:
  - Agregación de múltiples series
  - Cálculos de cartera
  - Monte Carlo de cartera completa
  - Generación de reportes

## Patrones de Diseño Utilizados

1. **Abstract Factory**: `DataExtractorFactory` - Crea instancias de extractores
2. **Strategy**: Diferentes extractores intercambiables (Yahoo/Alpha Vantage)
3. **Composition**: 
   - Portfolio contiene múltiples PriceSeries
   - MultiAPIExtractor contiene múltiples DataExtractor
   - PriceSeries contiene múltiples PricePoint
4. **Template Method**: Extractores implementan la misma interfaz abstracta
5. **Optional Methods**: Métodos opcionales en DataExtractor (fetch_fundamental_data, etc.)

## Módulos Adicionales

### `report.py` (módulo de funciones, no clase)
- **`generate_report()`**: Función independiente que genera reportes Markdown
- Recibe un objeto Portfolio y parámetros de configuración
- **Nota**: Portfolio.report() existe pero está deprecado, usar `generate_report()` de `report.py`

### `indices.py` (módulo de funciones)
- Funciones utilitarias para trabajar con índices bursátiles
- `importar_indice()`, `importar_indices()`, `get_index_symbol()`, etc.

### `validation.py` (módulo de funciones)
- **`validar_configuracion()`**: Valida parámetros de configuración
- Se ejecuta al inicio de `main.py`

