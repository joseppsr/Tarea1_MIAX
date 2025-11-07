"""
Script de verificación del entorno y configuración del proyecto.
Verifica que todo esté correctamente configurado antes de ejecutar el análisis.
"""

import sys
import os
from pathlib import Path

def verificar_python():
    """Verifica la versión de Python."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        try:
            print("[ERROR] Python 3.8 o superior es requerido")
        except UnicodeEncodeError:
            print("[ERROR] Python 3.8 o superior es requerido")
        print(f"   Versión actual: {version.major}.{version.minor}.{version.micro}")
        return False
    
    try:
        print(f"[OK] Python {version.major}.{version.minor}.{version.micro}")
    except UnicodeEncodeError:
        print(f"[OK] Python {version.major}.{version.minor}.{version.micro}")
    return True


def verificar_venv():
    """Verifica si el entorno virtual está activado."""
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    if in_venv:
        try:
            print("[OK] Entorno virtual activado")
        except UnicodeEncodeError:
            print("[OK] Entorno virtual activado")
    else:
        try:
            print("[ADVERTENCIA] Entorno virtual no activado (recomendado pero no obligatorio)")
        except UnicodeEncodeError:
            print("[!] Entorno virtual no activado (recomendado pero no obligatorio)")
    
    return True


def verificar_dependencias():
    """Verifica que las dependencias estén instaladas."""
    dependencias_criticas = [
        'pandas',
        'numpy',
        'matplotlib',
        'requests',
        'python-dotenv'
    ]
    
    dependencias_opcionales = [
        'yfinance'
    ]
    
    faltantes = []
    opcionales_faltantes = []
    
    for dep in dependencias_criticas:
        try:
            __import__(dep.replace('-', '_'))
        except ImportError:
            faltantes.append(dep)
    
    for dep in dependencias_opcionales:
        try:
            __import__(dep)
        except ImportError:
            opcionales_faltantes.append(dep)
    
    if faltantes:
        try:
            print(f"[ERROR] Dependencias faltantes: {', '.join(faltantes)}")
        except UnicodeEncodeError:
            print(f"[ERROR] Dependencias faltantes: {', '.join(faltantes)}")
        print("   Ejecuta: pip install -r requirements.txt")
        return False
    
    try:
        print("[OK] Todas las dependencias críticas instaladas")
    except UnicodeEncodeError:
        print("[OK] Todas las dependencias criticas instaladas")
    
    if opcionales_faltantes:
        try:
            print(f"[ADVERTENCIA] Dependencias opcionales faltantes: {', '.join(opcionales_faltantes)}")
            print("   (yfinance mejora la extracción de Yahoo Finance, pero no es obligatorio)")
        except UnicodeEncodeError:
            print(f"[!] Dependencias opcionales faltantes: {', '.join(opcionales_faltantes)}")
            print("   (yfinance mejora la extraccion de Yahoo Finance, pero no es obligatorio)")
    
    return True


def verificar_archivos():
    """Verifica que los archivos necesarios existan."""
    archivos_requeridos = [
        'configuracion_parametros.py',
        'main.py',
        'requirements.txt',
        'src/__init__.py',
        'src/extractor.py',
        'src/data_classes.py',
        'src/portfolio.py',
        'src/report.py'
    ]
    
    faltantes = []
    for archivo in archivos_requeridos:
        if not Path(archivo).exists():
            faltantes.append(archivo)
    
    if faltantes:
        try:
            print(f"[ERROR] Archivos faltantes: {', '.join(faltantes)}")
        except UnicodeEncodeError:
            print(f"[ERROR] Archivos faltantes: {', '.join(faltantes)}")
        return False
    
    try:
        print("[OK] Todos los archivos necesarios presentes")
    except UnicodeEncodeError:
        print("[OK] Todos los archivos necesarios presentes")
    
    return True


def verificar_configuracion():
    """Verifica la configuración básica."""
    try:
        import configuracion_parametros as config
        
        # Verificar que configuracion_parametros.py tenga las variables necesarias
        variables_requeridas = [
            'TICKERS_ACCIONES',
            'INDICES',
            'API_POR_DEFECTO'
        ]
        
        faltantes = []
        for var in variables_requeridas:
            if not hasattr(config, var):
                faltantes.append(var)
        
        if faltantes:
            try:
                print(f"[ADVERTENCIA] Variables de configuración faltantes: {', '.join(faltantes)}")
            except UnicodeEncodeError:
                print(f"[!] Variables de configuracion faltantes: {', '.join(faltantes)}")
            return False
        
        try:
            print("[OK] Configuración básica válida")
        except UnicodeEncodeError:
            print("[OK] Configuracion basica valida")
        
        return True
        
    except Exception as e:
        try:
            print(f"[ERROR] Error al verificar configuración: {e}")
        except UnicodeEncodeError:
            print(f"[!] Error al verificar configuracion: {e}")
        return False


def main():
    """Ejecuta todas las verificaciones."""
    print("="*70)
    try:
        print("VERIFICACIÓN DEL ENTORNO - Tarea1_MIAX")
    except UnicodeEncodeError:
        print("VERIFICACION DEL ENTORNO - Tarea1_MIAX")
    print("="*70)
    print()
    
    resultados = []
    
    try:
        print("1. Verificando Python...")
        resultados.append(verificar_python())
    except Exception as e:
        print(f"Error: {e}")
        resultados.append(False)
    
    print()
    
    try:
        print("2. Verificando entorno virtual...")
        resultados.append(verificar_venv())
    except Exception as e:
        print(f"Error: {e}")
        resultados.append(False)
    
    print()
    
    try:
        print("3. Verificando dependencias...")
        resultados.append(verificar_dependencias())
    except Exception as e:
        print(f"Error: {e}")
        resultados.append(False)
    
    print()
    
    try:
        print("4. Verificando archivos...")
        resultados.append(verificar_archivos())
    except Exception as e:
        print(f"Error: {e}")
        resultados.append(False)
    
    print()
    
    try:
        print("5. Verificando configuración...")
        resultados.append(verificar_configuracion())
    except Exception as e:
        print(f"Error: {e}")
        resultados.append(False)
    
    print()
    print("="*70)
    
    if all(resultados):
        try:
            print("[OK] ¡Todo está correctamente configurado!")
            print("  Puedes ejecutar: python main.py")
        except UnicodeEncodeError:
            print("[OK] !Todo esta correctamente configurado!")
            print("  Puedes ejecutar: python main.py")
        return 0
    else:
        try:
            print("[ADVERTENCIA] Hay problemas que deben resolverse antes de ejecutar el proyecto")
        except UnicodeEncodeError:
            print("[!] Hay problemas que deben resolverse antes de ejecutar el proyecto")
        return 1


if __name__ == "__main__":
    sys.exit(main())

