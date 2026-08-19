#!/usr/bin/env python3
"""
Setup script para el Plugin Serial de Sugar.
============================================

Script de instalación y configuración del plugin de comunicación serie.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_python_version():
    """Verifica la versión de Python."""
    if sys.version_info < (3, 7):
        print("Error: Se requiere Python 3.7 o superior")
        print(f"   Versión actual: {sys.version}")
        return False
    print(f"Python {sys.version.split()[0]} - OK")
    return True

def check_pyserial():
    """Verifica si pyserial está instalado."""
    try:
        import serial
        print(f"pyserial {serial.__version__} - OK")
        return True
    except ImportError:
        print("pyserial no está instalado")
        return False

def install_pyserial():
    """Instala pyserial."""
    print("Instalando pyserial...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyserial>=3.5"])
        print("pyserial instalado correctamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error instalando pyserial: {e}")
        return False

def check_platform():
    """Verifica la plataforma y permisos."""
    system = platform.system().lower()
    print(f" Plataforma: {system}")
    
    if system == "linux":
        # Verificar permisos en Linux
        try:
            import grp
            user_groups = [g.gr_name for g in grp.getgrall() if os.getlogin() in g.gr_mem]
            if 'dialout' not in user_groups:
                print(" Advertencia: Usuario no está en el grupo 'dialout'")
                print("   Ejecutar: sudo usermod -a -G dialout $USER")
                print("   Luego reiniciar sesión")
        except Exception:
            pass
    
    return True

def test_serial_ports():
    """Prueba la detección de puertos serie."""
    try:
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        print(f"Puertos serie detectados: {len(ports)}")
        
        for port in ports:
            print(f"   - {port.device}: {port.description}")
        
        if len(ports) == 0:
            print(" No se detectaron puertos serie")
            print("   Conecte un dispositivo serie para probar")
        
        return True
    except Exception as e:
        print(f"Error detectando puertos: {e}")
        return False

def run_tests():
    """Ejecuta los tests del plugin."""
    print("Ejecutando tests...")
    
    test_dir = Path(__file__).parent / "tests"
    if not test_dir.exists():
        print(" Directorio de tests no encontrado")
        return True
    
    try:
        # Agregar el directorio del plugin al path
        plugin_dir = Path(__file__).parent
        sys.path.insert(0, str(plugin_dir))
        
        # Ejecutar tests
        import unittest
        loader = unittest.TestLoader()
        suite = loader.discover(str(test_dir), pattern='test_*.py')
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        if result.wasSuccessful():
            print("Todos los tests pasaron")
            return True
        else:
            print(f"{len(result.failures)} tests fallaron")
            for test, traceback in result.failures:
                print(f"   - {test}: {traceback}")
            return False
            
    except Exception as e:
        print(f"Error ejecutando tests: {e}")
        return False

def create_example_script():
    """Crea un script de ejemplo."""
    example_script = """#!/usr/bin/env python3
'''
Ejemplo de uso del Plugin Serial.
================================

Ejemplo básico de comunicación serie usando Sugar.
'''

import json

# Script de ejemplo
example_script = {
    "meta": {
        "serial": {
            "options": {
                "test_device": {
                    "port": "COM3",  # Cambiar por el puerto correcto
                    "baudrate": 115200,
                    "auto_connect": True
                }
            }
        }
    },
    "task": [
        {
            "print": {
                "text": "=== Ejemplo Plugin Serial ==="
            }
        },
        {
            "serial": {
                "operator": "list_ports",
                "result": "ports"
            }
        },
        {
            "print": {
                "text": "Puertos disponibles: {{ports}}"
            }
        },
        {
            "serial": {
                "operator": "write",
                "session": "test_device",
                "data": "HELLO\\r\\n",
                "result": "write_result"
            }
        },
        {
            "print": {
                "text": "Datos enviados: {{write_result}}"
            }
        },
        {
            "serial": {
                "operator": "read_line",
                "session": "test_device",
                "timeout": 2.0,
                "result": "response"
            }
        },
        {
            "print": {
                "text": "Respuesta: {{response}}"
            }
        }
    ]
}

# Guardar script de ejemplo
with open("serial_example.json", "w") as f:
    json.dump(example_script, f, indent=2)

print("Script de ejemplo creado: serial_example.json")
print("   Ejecutar con: virtual/bin/python3 Sugar/Service/SugarConsole.py serial_example.json")
"""

    try:
        with open("serial_example.py", "w") as f:
            f.write(example_script)
        print("Script de ejemplo creado: serial_example.py")
        return True
    except Exception as e:
        print(f"Error creando script de ejemplo: {e}")
        return False

def main():
    """Función principal del setup."""
    print("Setup del Plugin Serial para Sugar")
    print("=" * 40)
    
    # Verificar Python
    if not check_python_version():
        return False
    
    # Verificar/instalar pyserial
    if not check_pyserial():
        if not install_pyserial():
            return False
    
    # Verificar plataforma
    check_platform()
    
    # Probar detección de puertos
    test_serial_ports()
    
    # Ejecutar tests
    if not run_tests():
        print(" Algunos tests fallaron, pero el plugin puede funcionar")
    
    # Crear script de ejemplo
    create_example_script()
    
    print("\n" + "=" * 40)
    print("Setup completado")
    print("\nPróximos pasos:")
    print("1. Conectar un dispositivo serie")
    print("2. Ejecutar: python serial_example.py")
    print("3. Modificar el puerto en el script si es necesario")
    print("4. Ejecutar: virtual/bin/python3 Sugar/Service/SugarConsole.py serial_example.json")
    print("\nDocumentación:")
    print("- README.md: Guía de uso")
    print("- docs/API_REFERENCE.md: Referencia de API")
    print("- docs/TROUBLESHOOTING.md: Solución de problemas")
    print("- examples/: Ejemplos de uso")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)