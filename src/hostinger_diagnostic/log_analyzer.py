import re
from pathlib import Path
from typing import Dict, List
from ..utils.ui_helper import UIHelper

class LogAnalyzer:
    def __init__(self, ui: UIHelper):
        self.ui = ui
        self.patrones_error = {
            'php': r'PHP (Fatal|Parse|Warning|Notice|Error)',
            'wordpress': r'WordPress database error',
            'plugin': r'Plugin (.*?) error',
            'tema': r'Theme (.*?) error'
        }

    def obtener_logs_locales(self, ruta: Path) -> Dict[str, str]:
        """Obtiene logs locales de WordPress"""
        logs = {}
        archivos_log = [
            'wp-content/debug.log',
            'error.log',
            'php_error.log'
        ]

        for archivo in archivos_log:
            log_path = ruta / archivo
            if log_path.exists():
                logs[archivo] = log_path.read_text(errors='ignore')

        return logs

    def analizar_logs(self, logs: Dict[str, str]) -> Dict:
        """Analiza los logs buscando errores y patrones"""
        resultados = {
            'errores': [],
            'advertencias': [],
            'recomendaciones': []
        }

        for nombre_log, contenido in logs.items():
            self._analizar_contenido_log(contenido, resultados)

        return resultados

    def _analizar_contenido_log(self, contenido: str, resultados: Dict):
        """Analiza el contenido de un log buscando errores"""
        lineas = contenido.splitlines()
        
        for linea in lineas:
            for tipo, patron in self.patrones_error.items():
                if re.search(patron, linea):
                    error = self._clasificar_error(tipo, linea)
                    if error:
                        resultados['errores'].append(error)
                        resultados['recomendaciones'].extend(
                            self._generar_recomendaciones(error)
                        )

    def _clasificar_error(self, tipo: str, linea: str) -> Dict:
        """Clasifica y estructura un error encontrado"""
        return {
            'tipo': tipo,
            'mensaje': linea,
            'severidad': self._determinar_severidad(linea),
            'timestamp': self._extraer_timestamp(linea)
        }

    def _determinar_severidad(self, linea: str) -> str:
        """Determina la severidad de un error"""
        if 'Fatal' in linea or 'Error' in linea:
            return 'alta'
        elif 'Warning' in linea:
            return 'media'
        return 'baja'

    def _extraer_timestamp(self, linea: str) -> str:
        """Extrae el timestamp de una línea de log"""
        match = re.search(r'\[(.*?)\]', linea)
        return match.group(1) if match else 'desconocido'

    def _generar_recomendaciones(self, error: Dict) -> List[str]:
        """Genera recomendaciones basadas en el error"""
        recomendaciones = []
        
        if error['tipo'] == 'php':
            recomendaciones.append("Verificar versión de PHP y compatibilidad")
        elif error['tipo'] == 'wordpress':
            recomendaciones.append("Ejecutar reparación de base de datos")
        elif error['tipo'] == 'plugin':
            recomendaciones.append("Considerar actualizar o desactivar el plugin")
        elif error['tipo'] == 'tema':
            recomendaciones.append("Verificar compatibilidad del tema")

        return recomendaciones
