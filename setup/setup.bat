@echo off
echo ========================================
echo Instalacion de Tarea1_MIAX
echo ========================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado o no esta en el PATH
    echo Por favor, instala Python 3.8 o superior 
    pause
    exit /b 1
)

echo [1/4] Python encontrado
python --version

REM Crear entorno virtual
echo.
echo [2/4] Creando entorno virtual...
if exist venv (
    echo El entorno virtual ya existe. Saltando creacion...
) else (
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] No se pudo crear el entorno virtual
        pause
        exit /b 1
    )
    echo ✓ Entorno virtual creado
)

REM Activar entorno virtual e instalar dependencias
echo.
echo [3/4] Instalando dependencias...
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] No se pudieron instalar las dependencias
    pause
    exit /b 1
)
echo ✓ Dependencias instaladas

REM Crear .env si no existe
echo.
echo [4/4] Configurando archivo .env...
if exist .env (
    echo El archivo .env ya existe. Saltando creacion...
) else (
    if exist .env.example (
        copy .env.example .env >nul
        echo ✓ Archivo .env creado desde .env.example
        echo   IMPORTANTE: Edita .env y añade tus API keys si las necesitas
    ) else (
        echo [ERROR] .env.example no encontrado. Creando .env vacio...
        echo # Archivo de variables de entorno > .env
        echo # Añade tus API keys aqui >> .env
    )
)

echo.
echo ========================================
echo ¡Instalacion completada!
echo ========================================
echo.
echo Siguiente paso:
echo 1. Edita configuracion_parametros.py con tus tickers e indices
echo 2. (Opcional) Edita .env con tus API keys
echo 3. Ejecuta: python main.py
echo.
echo Para activar el entorno virtual en el futuro:
echo   venv\Scripts\activate.bat
echo.
pause

