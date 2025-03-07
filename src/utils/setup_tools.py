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

def verificar_modulo_hostinger(ruta_base: Path) -> bool:
    """Verifica y corrige el módulo hostinger_diagnostic"""
    try:
        # 1. Verificar directorio
        modulo_path = ruta_base / 'src' / 'hostinger_diagnostic'
        if not modulo_path.exists():
            logging.info("Creando directorio hostinger_diagnostic...")
            modulo_path.mkdir(parents=True, exist_ok=True)

        # 2. Verificar __init__.py
        init_path = modulo_path / '__init__.py'
        if not init_path.exists():
            init_content = '''"""
Módulo de diagnóstico WordPress para Hostinger.
Proporciona herramientas para analizar instalaciones WordPress y plantillas.
"""

from .diagnostic_manager import HostingerDiagnosticManager
'''
            init_path.write_text(init_content, encoding='utf-8')
            logging.info("Archivo __init__.py creado")

        # 3. Verificar diagnostic_manager.py
        manager_path = modulo_path / 'diagnostic_manager.py'
        if not manager_path.exists() or 'run_diagnostics' not in manager_path.read_text(encoding='utf-8'):
            crear_diagnostic_manager(manager_path)
            logging.info("Archivo diagnostic_manager.py actualizado")

        return True

    except Exception as e:
        logging.error(f"Error al verificar módulo hostinger: {str(e)}")
        return False

def crear_diagnostic_manager(path: Path):
    """Crea o actualiza el archivo diagnostic_manager.py"""
    content = '''"""
Módulo principal para diagnósticos de WordPress en Hostinger.
Gestiona la ejecución de diagnósticos y generación de reportes.
"""

import logging
from pathlib import Path
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from ..utils.ui_helper import UIHelper

@dataclass
class DiagnosticConfig:
    """Configuración para el diagnóstico"""
    ruta_local: Optional[Path] = None
    modo: str = 'local'
    host: Optional[str] = None
    usuario: Optional[str] = None
    password: Optional[str] = None

class HostingerDiagnosticManager:
    def __init__(self, ui: UIHelper):
        self.ui = ui
        self.config = None
        logging.info("Inicializando HostingerDiagnosticManager")

    def run_diagnostics(self) -> Tuple[bool, Dict]:
        """Punto de entrada principal para ejecutar diagnósticos"""
        logging.info("Iniciando diagnóstico de WordPress")
        try:
            if not self.config:
                self.config = self._solicitar_configuracion()

            resultados = {
                'estado': 'pendiente',
                'timestamp': None,
                'errores': [],
                'recomendaciones': []
            }

            # TODO: Implementar lógica de diagnóstico
            self.ui.print_step("Ejecutando diagnóstico...")
            
            return True, resultados

        except Exception as e:
            logging.error(f"Error en diagnóstico: {str(e)}")
            return False, {'estado': 'error', 'mensaje': str(e)}

    def _solicitar_configuracion(self) -> DiagnosticConfig:
        """Solicita la configuración necesaria al usuario"""
        try:
            modo = input("¿Analizar WordPress local o remoto? (L/R): ").lower()
            if modo == 'l':
                ruta = input("Ruta de la instalación WordPress: ").strip()
                return DiagnosticConfig(ruta_local=Path(ruta), modo='local')
            else:
                return DiagnosticConfig(
                    modo='remoto',
                    host=input("Host: ").strip(),
                    usuario=input("Usuario: ").strip(),
                    password=input("Contraseña: ").strip()
                )
        except Exception as e:
            logging.error(f"Error al solicitar configuración: {str(e)}")
            raise

if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Prueba del módulo
    from ..utils.ui_helper import UIHelper
    manager = HostingerDiagnosticManager(UIHelper())
    success, results = manager.run_diagnostics()
    print(f"Prueba completada: {'✓' if success else '✗'}")
    print(f"Resultados: {results}")
'''
    path.write_text(content, encoding='utf-8')
