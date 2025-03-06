import logging
from pathlib import Path
import yaml

def cargar_configuracion():
    """Carga la configuración desde el archivo YAML"""
    config_path = Path(__file__).parent.parent / 'config' / 'settings.yaml'
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def solicitar_parametros():
    """Solicita y valida los parámetros del proyecto"""
    try:
        config = cargar_configuracion()
        defaults = config['defaults']
        
        nombre = input(f"Nombre del proyecto [{defaults['project_name']}]: ").strip() or defaults['project_name']
        
        print(f"\nUbicación sugerida: {defaults['base_location']}")
        ubicacion = (defaults['base_location'] 
                    if input("¿Usar esta ubicación? (s/n): ").strip().lower() in ['s', ''] 
                    else input("Ubicación: ").strip())
        
        print(f"\nVersión de Python sugerida: {defaults['python_version']}")
        version_python = (defaults['python_version']
                        if input("¿Usar esta versión? (s/n): ").strip().lower() in ['s', '']
                        else input("Versión de Python deseada: ").strip())
        
        return nombre, ubicacion, version_python
    except Exception as e:
        logging.error(f"Error al solicitar parámetros: {str(e)}")
        return None, None, None
