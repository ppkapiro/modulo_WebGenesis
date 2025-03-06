import logging
from pathlib import Path
from .command_runner import CommandRunner
from .user_input import cargar_configuracion

def validar_dependencias():
    """Verifica las herramientas necesarias"""
    config = cargar_configuracion()
    dependencias_ok = True
    
    # Verificar Conda
    if not verificar_conda():
        dependencias_ok = False
    
    # Verificar VS Code
    if not verificar_vscode(config['vscode']['paths']):
        dependencias_ok = False
    
    return dependencias_ok

def verificar_conda():
    success, message = CommandRunner.execute_command(['conda', '--version'])
    if success:
        logging.info(f"Conda encontrado: {message.strip()}")
        return True
    else:
        logging.error("Conda no encontrado")
        print("\nERROR: Conda no está instalado o no está en el PATH")
        return False

def verificar_vscode(vscode_paths):
    for path in vscode_paths:
        if Path(path).exists():
            logging.info(f"VS Code encontrado en: {path}")
            return True
    logging.error("VS Code no encontrado")
    return False
