from datetime import datetime
from pathlib import Path
from typing import Dict
from ..utils.ui_helper import UIHelper

class ReportGenerator:
    def __init__(self, ui: UIHelper):
        self.ui = ui

    def generar_reporte(self, ruta: Path, diagnostico: Dict) -> Path:
        """Genera un reporte detallado del diagnóstico"""
        try:
            report_path = ruta / 'hostinger-diagnostico.md'
            
            contenido = [
                "# Diagnóstico WordPress en Hostinger",
                f"\nFecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"\nEstado: {diagnostico['estado'].upper()}",
                
                "\n## Información del Sistema",
                f"- WordPress: {diagnostico.get('wp_version', 'No detectado')}",
                f"- PHP: {diagnostico.get('php_version', 'No detectado')}",
                
                "\n## Errores en Logs",
                *[f"- {e['tipo']}: {e['mensaje']}" for e in diagnostico.get('errores_log', [])],
                
                "\n## Problemas del Tema",
                *[f"- {e}" for e in diagnostico.get('errores_tema', [])],
                
                "\n## Recomendaciones",
                *[f"- {r}" for r in diagnostico.get('recomendaciones', [])]
            ]
            
            report_path.write_text('\n'.join(contenido), encoding='utf-8')
            self.ui.print_success(f"Reporte generado en: {report_path}")
            return report_path

        except Exception as e:
            self.ui.print_error(f"Error al generar reporte: {str(e)}")
            return None
