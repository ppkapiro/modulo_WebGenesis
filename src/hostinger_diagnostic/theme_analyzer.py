import re
from pathlib import Path
from typing import Dict
from ..utils.ui_helper import UIHelper
from ..utils.command_runner import CommandRunner

class ThemeAnalyzer:
    def __init__(self, ui: UIHelper):
        self.ui = ui
        self.required_files = ['style.css', 'index.php', 'functions.php']

    def analizar_tema_local(self, ruta: Path) -> Dict:
        """Analiza un tema WordPress local"""
        try:
            tema_info = {
                'estado': 'pendiente',
                'nombre': None,
                'version': None,
                'wp_version': None,
                'archivos_faltantes': [],
                'errores': [],
                'advertencias': []
            }

            # Obtener información del tema activo
            success, output = CommandRunner.execute_command(
                ['wp', 'theme', 'list', '--status=active', '--format=json'],
                cwd=ruta
            )
            
            if success:
                tema_info.update(self._analizar_archivos_tema(ruta))
                tema_info.update(self._verificar_compatibilidad_php(ruta))
                tema_info['estado'] = 'error' if tema_info['errores'] else 'ok'
                
            return tema_info

        except Exception as e:
            return {'estado': 'error', 'errores': [str(e)]}

    def _analizar_archivos_tema(self, ruta: Path) -> Dict:
        """Verifica archivos requeridos y estructura del tema"""
        resultados = {
            'archivos_faltantes': [],
            'errores': [],
            'advertencias': []
        }

        tema_path = ruta / 'wp-content/themes'
        if not tema_path.exists():
            resultados['errores'].append("Directorio de temas no encontrado")
            return resultados

        # Verificar archivos requeridos
        for archivo in self.required_files:
            if not (tema_path / archivo).exists():
                resultados['archivos_faltantes'].append(archivo)

        return resultados

    def _verificar_compatibilidad_php(self, ruta: Path) -> Dict:
        """Verifica la compatibilidad de PHP en el tema"""
        resultados = {'compatibilidad': [], 'advertencias': []}
        
        # Verificar funciones obsoletas
        deprecated_functions = [
            'create_function',
            'mysql_*',
            'split',
            'ereg',
            'eregi'
        ]

        for php_file in ruta.rglob('*.php'):
            contenido = php_file.read_text(errors='ignore')
            for func in deprecated_functions:
                if re.search(func, contenido):
                    resultados['advertencias'].append(
                        f"Función obsoleta {func} encontrada en {php_file.name}"
                    )

        return resultados

    def verificar_compatibilidad(self, ruta: Path, version_wp: str) -> Dict:
        """Verifica compatibilidad con versión específica de WordPress"""
        try:
            style_css = ruta / 'wp-content/themes/style.css'
            if not style_css.exists():
                return {'compatible': False, 'error': 'style.css no encontrado'}

            contenido = style_css.read_text(encoding='utf-8')
            requires = re.search(r'Requires at least: ([\d.]+)', contenido)
            
            if requires:
                min_version = requires.group(1)
                return {
                    'compatible': self._comparar_versiones(version_wp, min_version),
                    'min_version': min_version,
                    'current_version': version_wp
                }

            return {'compatible': True, 'warning': 'No se encontró requisito de versión'}

        except Exception as e:
            return {'compatible': False, 'error': str(e)}

    def _comparar_versiones(self, version_actual: str, version_minima: str) -> bool:
        """Compara versiones de WordPress"""
        actual = [int(x) for x in version_actual.split('.')]
        minima = [int(x) for x in version_minima.split('.')]
        return actual >= minima
