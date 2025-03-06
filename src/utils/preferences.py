import json
from pathlib import Path
import logging

def guardar_preferencias(preferencias: dict):
    """Guarda las preferencias del usuario en un archivo JSON"""
    try:
        config_dir = Path.home() / '.modulo_webgenesis'
        config_dir.mkdir(exist_ok=True)
        
        config_file = config_dir / 'preferences.json'
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(preferencias, f, indent=4)
        
        logging.info("Preferencias guardadas exitosamente")
        return True
    except Exception as e:
        logging.error(f"Error al guardar preferencias: {str(e)}")
        return False

def cargar_preferencias() -> dict:
    """Carga las preferencias del usuario desde el archivo JSON"""
    try:
        config_file = Path.home() / '.modulo_webgenesis' / 'preferences.json'
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logging.error(f"Error al cargar preferencias: {str(e)}")
    return {}
