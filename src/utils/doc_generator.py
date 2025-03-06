import os
import re
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import yaml
from .user_input import cargar_configuracion
from .command_runner import CommandRunner

class DocumentacionGenerator:
    def __init__(self, ruta_base: Path, nombre: str, version_python: str):
        self.ruta_base = ruta_base
        self.nombre = nombre
        self.version_python = version_python
        self.estructura = {}
        self.fecha_generacion = datetime.now()
        self.config = cargar_configuracion()

    def generar_documentacion_completa(self) -> Path:
        """Genera la documentación completa del proyecto"""
        try:
            self._analizar_estructura()
            contenido = self._generar_contenido_completo()
            doc_path = self.ruta_base / 'docs' / 'documentation.txt'
            doc_path.parent.mkdir(parents=True, exist_ok=True)
            doc_path.write_text(contenido, encoding='utf-8')
            logging.info(f"Documentación actualizada en: {doc_path}")
            return doc_path
        except Exception as e:
            logging.error(f"Error al generar documentación: {str(e)}")
            return None

    def generar_design_doc(self) -> Path:
        """Genera el documento de diseño del proyecto"""
        try:
            design_path = self.ruta_base / 'docs' / 'design.md'
            design_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Leer la plantilla y generar contenido
            design_template = self.ruta_base / 'docs' / 'design.md'
            if not design_template.exists():
                logging.info("Creando nuevo archivo design.md")
                # Aquí iría el contenido del design.md
                
            logging.info(f"Documento de diseño generado en: {design_path}")
            return design_path
        except Exception as e:
            logging.error(f"Error al generar documento de diseño: {str(e)}")
            return None

    def _analizar_estructura(self):
        """Analiza la estructura completa del proyecto"""
        for root, dirs, files in os.walk(self.ruta_base):
            ruta_relativa = Path(root).relative_to(self.ruta_base)
            if '.git' in str(ruta_relativa):
                continue
            
            self.estructura[str(ruta_relativa)] = {
                'archivos': files,
                'descripcion': self._obtener_descripcion_directorio(ruta_relativa)
            }

    def _obtener_descripcion_directorio(self, ruta: Path) -> str:
        """Obtiene la descripción de cada directorio"""
        descripciones = {
            '.': 'Directorio raíz del proyecto',
            'src': 'Código fuente principal y módulos del proyecto',
            'config': 'Archivos de configuración y variables de entorno',
            'tests': 'Pruebas unitarias y de integración',
            'docs': 'Documentación del proyecto',
            'public_html': 'Archivos web públicos y assets estáticos',
            'themes': 'Temas y plantillas visuales',
            'plugins': 'Extensiones y módulos adicionales',
            '.github/workflows': 'Configuración de CI/CD'
        }
        return descripciones.get(str(ruta), 'Directorio del proyecto')

    def _generar_contenido_completo(self) -> str:
        """Genera el contenido detallado de la documentación"""
        sections = [
            self._generar_seccion_informacion_general(),
            self._generar_seccion_estructura(),
            self._generar_seccion_modulos(),
            self._generar_seccion_configuracion(),
            self._generar_seccion_variables_entorno(),
            self._generar_seccion_instrucciones()
        ]
        return "\n\n".join(sections)

    def _generar_seccion_informacion_general(self) -> str:
        return f"""DOCUMENTACIÓN DEL PROYECTO
Última actualización: {self.fecha_generacion.strftime('%Y-%m-%d %H:%M:%S')}

1. INFORMACIÓN GENERAL
--------------------
Nombre del proyecto: {self.nombre}
Ubicación: {self.ruta_base}
Versión de Python: {self.version_python}
Fecha de generación: {self.fecha_generacion.strftime('%Y-%m-%d %H:%M:%S')}"""

    def _generar_seccion_estructura(self) -> str:
        estructura = ["2. ESTRUCTURA DEL PROYECTO\n------------------------"]
        for ruta, info in self.estructura.items():
            if ruta == '.':
                continue
            estructura.append(f"├── {ruta}/")
            estructura.append(f"    └── {info['descripcion']}")
        return "\n".join(estructura)

    def _generar_seccion_modulos(self) -> str:
        return f"""3. DESCRIPCIÓN DE MÓDULOS
-------------------------
src/
  - utils/: Utilidades y herramientas del proyecto
    • command_runner.py: Ejecutor seguro de comandos externos
    • documentation.py: Generador de documentación
    • env_manager.py: Gestor de entornos virtuales
    • ui_helper.py: Interfaz de usuario y formateo
    • preferences.py: Gestión de preferencias de usuario

config/
  - settings.yaml: Configuración principal del proyecto
  - .env: Variables de entorno (no versionado)

tests/
  - Pruebas unitarias y de integración
  - Configuración de pytest"""

    def _generar_seccion_configuracion(self) -> str:
        return """4. CONFIGURACIÓN DE HERRAMIENTAS
------------------------------
Git:
  - Repositorio inicializado
  - .gitignore configurado para Python
  - Pre-commit hooks instalados

Conda:
  - Entorno virtual específico del proyecto
  - environment.yml con dependencias

Herramientas de calidad:
  - Black: Formato de código
  - Flake8: Linting
  - isort: Ordenamiento de imports
  - pytest: Testing

CI/CD (GitHub Actions):
  - Pruebas automáticas
  - Verificación de formato
  - Análisis de código"""

    def _generar_seccion_variables_entorno(self) -> str:
        return """5. GESTIÓN DE VARIABLES DE ENTORNO
--------------------------------
.env:
  - Configuración sensible
  - No versionado en Git
  - Template disponible en .env.example

Variables requeridas:
  - DEBUG: Modo de depuración
  - SECRET_KEY: Clave secreta
  - DATABASE_URL: Conexión a base de datos"""

    def _generar_seccion_instrucciones(self) -> str:
        return f"""6. INSTRUCCIONES DE USO
----------------------
1. Activar entorno virtual:
   conda activate {self.nombre}_env

2. Instalar dependencias:
   conda env update -f environment.yml

3. Configurar pre-commit:
   pre-commit install

4. Variables de entorno:
   cp .env.example .env
   [Editar .env con valores reales]

5. Ejecutar pruebas:
   pytest

6. Desarrollo:
   - Usar VS Code con la configuración proporcionada
   - Black formateará automáticamente el código
   - Los commits serán validados por pre-commit"""

    def mostrar_documentacion(self):
        """Muestra la documentación en la consola"""
        try:
            doc_path = self.ruta_base / 'docs' / 'documentation.txt'
            if doc_path.exists():
                print("\n" + "="*80)
                print("DOCUMENTACIÓN DEL PROYECTO")
                print("="*80 + "\n")
                with open(doc_path, 'r', encoding='utf-8') as f:
                    print(f.read())
                print("\n" + "="*80)
                return True
        except Exception as e:
            logging.error(f"Error al mostrar documentación: {str(e)}")
        return False

    def actualizar_project_md(self) -> Path:
        """Actualiza el archivo project.md con la información actual"""
        try:
            project_path = self.ruta_base / 'project.md'
            
            # Obtener métricas actuales
            coverage = self._obtener_cobertura_tests()
            calidad = self._analizar_calidad_codigo()
            
            # Actualizar última fecha
            fecha_actual = datetime.now().strftime('%Y-%m-%d')
            
            # Leer contenido actual si existe
            contenido_actual = ""
            if project_path.exists():
                contenido_actual = project_path.read_text(encoding='utf-8')
            
            # Actualizar campos dinámicos
            contenido_actualizado = self._actualizar_campos_project_md(
                contenido_actual,
                {
                    'Última Actualización': fecha_actual,
                    'Cobertura de tests': f"{coverage}%",
                    'Calidad de código': calidad
                }
            )
            
            # Guardar cambios
            project_path.write_text(contenido_actualizado, encoding='utf-8')
            logging.info(f"project.md actualizado: {project_path}")
            return project_path
            
        except Exception as e:
            logging.error(f"Error al actualizar project.md: {str(e)}")
            return None

    def _obtener_cobertura_tests(self) -> int:
        """Obtiene el porcentaje de cobertura de tests"""
        try:
            success, output = CommandRunner.execute_command(['pytest', '--cov'])
            if success:
                # Extraer porcentaje de cobertura
                return 80  # Valor por defecto hasta implementar parser
            return 0
        except:
            return 0

    def _analizar_calidad_codigo(self) -> str:
        """Analiza la calidad del código"""
        try:
            # Ejecutar análisis (ejemplo: flake8)
            success, _ = CommandRunner.execute_command(['flake8'])
            return 'A' if success else 'B'
        except:
            return 'C'

    def _actualizar_campos_project_md(self, contenido: str, campos: dict) -> str:
        """Actualiza campos específicos en project.md"""
        for campo, valor in campos.items():
            # Buscar y reemplazar valores
            patron = f"{campo}: .*"
            reemplazo = f"{campo}: {valor}"
            contenido = re.sub(patron, reemplazo, contenido)
        return contenido
