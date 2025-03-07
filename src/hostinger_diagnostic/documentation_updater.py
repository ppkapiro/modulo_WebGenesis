import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from ..utils.ui_helper import UIHelper

class DocumentationUpdater:
    def __init__(self, ui: UIHelper):
        self.ui = ui
        self.archivos_doc = [
            'project.md',
            'docs/documentation.txt',
            'wp-documentation.md'
        ]

    def actualizar_documentacion(self, ruta_base: Path, diagnostico: Dict, acciones: List[str]) -> bool:
        """Actualiza la documentación del proyecto con información reciente"""
        try:
            info = self._recopilar_informacion(diagnostico, acciones)
            
            # Actualizar cada archivo de documentación
            for archivo in self.archivos_doc:
                doc_path = ruta_base / archivo
                if doc_path.exists():
                    self._actualizar_archivo(doc_path, info)
                    self.ui.print_success(f"Documentación actualizada: {doc_path}")
                    logging.info(f"Documentación actualizada en {doc_path}")

            return True

        except Exception as e:
            self.ui.print_error(f"Error al actualizar documentación: {str(e)}")
            logging.error(f"Error en actualización de documentación: {str(e)}")
            return False

    def _recopilar_informacion(self, diagnostico: Dict, acciones: List[str]) -> Dict:
        """Recopila y estructura la información para la documentación"""
        return {
            'timestamp': datetime.now().isoformat(),
            'estado_wp': diagnostico.get('estado', 'desconocido'),
            'version_wp': diagnostico.get('wp_version', 'N/A'),
            'version_php': diagnostico.get('php_version', 'N/A'),
            'errores': diagnostico.get('errores', []),
            'advertencias': diagnostico.get('advertencias', []),
            'acciones_remediacion': acciones,
            'recomendaciones': diagnostico.get('recomendaciones', [])
        }

    def _actualizar_archivo(self, ruta: Path, info: Dict):
        """Actualiza un archivo de documentación específico"""
        if ruta.suffix == '.md':
            contenido = self._generar_contenido_markdown(info)
        else:
            contenido = self._generar_contenido_texto(info)

        # Si el archivo existe, actualizar sección WordPress
        if ruta.exists():
            texto_actual = ruta.read_text(encoding='utf-8')
            contenido = self._integrar_contenido(texto_actual, contenido)

        ruta.write_text(contenido, encoding='utf-8')

    def _generar_contenido_markdown(self, info: Dict) -> str:
        """Genera contenido en formato Markdown"""
        return f"""## Estado WordPress
Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

### Información del Sistema
- **Estado**: {info['estado_wp']}
- **Versión WordPress**: {info['version_wp']}
- **Versión PHP**: {info['version_php']}

### Diagnóstico
#### Errores Detectados
{self._formatear_lista_md([e['mensaje'] for e in info['errores']])}

#### Advertencias
{self._formatear_lista_md(info['advertencias'])}

### Acciones de Remediación
{self._formatear_lista_md(info['acciones_remediacion'])}

### Recomendaciones
{self._formatear_lista_md(info['recomendaciones'])}
"""

    def _generar_contenido_texto(self, info: Dict) -> str:
        """Genera contenido en formato texto plano"""
        return f"""ESTADO WORDPRESS
==================
Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Información del Sistema:
- Estado: {info['estado_wp']}
- Versión WordPress: {info['version_wp']}
- Versión PHP: {info['version_php']}

Diagnóstico:
-----------
Errores Detectados:
{self._formatear_lista_txt([e['mensaje'] for e in info['errores']])}

Advertencias:
{self._formatear_lista_txt(info['advertencias'])}

Acciones de Remediación:
{self._formatear_lista_txt(info['acciones_remediacion'])}

Recomendaciones:
{self._formatear_lista_txt(info['recomendaciones'])}
"""

    def _formatear_lista_md(self, items: List[str]) -> str:
        """Formatea una lista para Markdown"""
        if not items:
            return "_Ninguno_"
        return "\n".join(f"- {item}" for item in items)

    def _formatear_lista_txt(self, items: List[str]) -> str:
        """Formatea una lista para texto plano"""
        if not items:
            return "Ninguno"
        return "\n".join(f"* {item}" for item in items)

    def _integrar_contenido(self, texto_actual: str, nuevo_contenido: str) -> str:
        """Integra el nuevo contenido en el texto existente"""
        # Para archivos Markdown
        if "## Estado WordPress" in texto_actual:
            partes = texto_actual.split("## Estado WordPress")
            return partes[0] + nuevo_contenido + \
                   ("\n\n" + "## Estado WordPress".join(partes[1:]) if len(partes) > 1 else "")
        
        # Para archivos de texto
        if "ESTADO WORDPRESS" in texto_actual:
            partes = texto_actual.split("ESTADO WORDPRESS")
            return partes[0] + nuevo_contenido + \
                   ("\n\n" + "ESTADO WORDPRESS".join(partes[1:]) if len(partes) > 1 else "")
        
        # Si no existe la sección, agregar al final
        return texto_actual + "\n\n" + nuevo_contenido
