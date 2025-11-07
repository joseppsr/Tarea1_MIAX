#!/bin/bash
# Script de instalación automática para Linux/Mac

echo "========================================"
echo "Instalación de Tarea1_MIAX"
echo "========================================"
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python no está instalado o no está en el PATH"
    echo "Por favor, instala Python 3.8 o superior"
    exit 1
fi

echo "[1/4] Python encontrado"
python3 --version

# Crear entorno virtual
echo ""
echo "[2/4] Creando entorno virtual..."
if [ -d "venv" ]; then
    echo "El entorno virtual ya existe. Saltando creación..."
else
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "[ERROR] No se pudo crear el entorno virtual"
        exit 1
    fi
    echo "✓ Entorno virtual creado"
fi

# Activar entorno virtual e instalar dependencias
echo ""
echo "[3/4] Instalando dependencias..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[ERROR] No se pudieron instalar las dependencias"
    exit 1
fi
echo "✓ Dependencias instaladas"

# Crear .env si no existe
echo ""
echo "[4/4] Configurando archivo .env..."
if [ -f ".env" ]; then
    echo "El archivo .env ya existe. Saltando creación..."
else
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✓ Archivo .env creado desde .env.example"
        echo "  IMPORTANTE: Edita .env y añade tus API keys si las necesitas"
    else
        echo "[ERROR] .env.example no encontrado. Creando .env vacío..."
        echo "# Archivo de variables de entorno" > .env
        echo "# Añade tus API keys aquí" >> .env
    fi
fi

echo ""
echo "========================================"
echo "¡Instalación completada!"
echo "========================================"
echo ""
echo "Siguiente paso:"
echo "1. Edita configuracion_parametros.py con tus tickers e índices"
echo "2. (Opcional) Edita .env con tus API keys"
echo "3. Ejecuta: python main.py"
echo ""
echo "Para activar el entorno virtual en el futuro:"
echo "  source venv/bin/activate"
echo ""

