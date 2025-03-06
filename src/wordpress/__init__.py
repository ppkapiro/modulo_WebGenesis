"""
Módulo de integración con WordPress para WebGenesis.
Proporciona herramientas para gestionar instalaciones de WordPress locales.

Dependencias:
- WP-CLI instalado y accesible en el PATH
- WordPress Engine Local instalado
- Permisos de escritura en el directorio de trabajo
"""

from .wp_manager import WordPressManager
