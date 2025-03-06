import logging
from datetime import datetime
from pathlib import Path
from .user_input import cargar_configuracion

class DocumentacionProyecto:
    def __init__(self, nombre, ubicacion, version_python, estructura):
        self.nombre = nombre
        self.ubicacion = ubicacion
        self.version_python = version_python
        self.estructura = estructura
        self.config = cargar_configuracion()
        self.ruta_doc = Path(ubicacion) / nombre / 'docs'
        
    def generar_documentacion(self):
        """Genera la documentación completa del proyecto"""
        try:
            self.ruta_doc.mkdir(parents=True, exist_ok=True)
            contenido = self._generar_contenido()
            
            # Generar documentation.txt en docs/
            doc_path = self.ruta_doc / 'documentation.txt'
            doc_path.write_text(contenido, encoding='utf-8')
            logging.info(f"Documentación generada en: {doc_path}")
            
            # Generar README.md en la raíz
            readme_path = Path(self.ubicacion) / self.nombre / 'README.md'
            readme_contenido = self._generar_readme()
            readme_path.write_text(readme_contenido, encoding='utf-8')
            
            logging.info("Documentación generada exitosamente")
            return doc_path
        except Exception as e:
            logging.error(f"Error al generar documentación: {str(e)}")
            return None

    def mostrar_documentacion(self):
        """Muestra la documentación en la consola"""
        try:
            doc_path = self.ruta_doc / 'documentation.txt'
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

    def _generar_contenido(self):
        """Genera el contenido detallado de la documentación"""
        return f"""DOCUMENTACION DEL PROYECTO
Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

1. INFORMACION GENERAL
--------------------
Nombre del proyecto: {self.nombre}
Ubicacion: {self.ubicacion}
Version de Python: {self.version_python}

2. ESTRUCTURA DEL PROYECTO
------------------------
Directorio raiz: {self.nombre}/
{self.estructura}

3. DESCRIPCION DE DIRECTORIOS
-------------------------
src/
  - Código fuente principal
  - Módulos y paquetes del proyecto
  - Lógica de negocio

config/
  - Archivos de configuración
  - Settings para diferentes entornos
  - Variables de entorno (.env)

tests/
  - Pruebas unitarias y de integración
  - Fixtures y utilidades de testing
  - Configuración de pytest

docs/
  - Documentación técnica
  - Guías de usuario
  - Documentación de API

public_html/
  - Archivos web públicos
  - Assets estáticos
  - Páginas HTML

themes/
  - Temas y estilos
  - Plantillas
  - Recursos visuales

plugins/
  - Extensiones del proyecto
  - Módulos adicionales
  - Integraciones

.github/
  - Configuración de CI/CD
  - GitHub Actions
  - Templates de PR/Issues

4. CONFIGURACIÓN DEL ENTORNO
-------------------------
1. Activar entorno virtual:
   conda activate {self.nombre}_env

2. Instalar dependencias:
   conda env update -f environment.yml

3. Configurar pre-commit:
   conda install -c conda-forge pre-commit
   pre-commit install

5. HERRAMIENTAS DE CALIDAD
-----------------------
- Black: Formato de código
- Flake8: Linting
- isort: Ordenamiento de imports
- pytest: Testing

6. INTEGRACIÓN CONTINUA
--------------------
Pipeline configurado en .github/workflows/ci.yml
Ejecuta automáticamente:
- Tests
- Verificación de formato
- Linting
- Ordenamiento de imports

7. CONTROL DE VERSIONES
--------------------
- Repositorio Git inicializado
- .gitignore configurado
- Hooks de pre-commit instalados
"""

    def _generar_readme(self):
        """Genera el contenido del README.md"""
        return f"""# {self.nombre}

## Descripción
Proyecto generado automáticamente con estructura modular profesional.

## Requisitos
- Python {self.version_python}
- Conda
- VS Code (recomendado)

## Configuración
1. Clonar el repositorio
2. Crear entorno: `conda env create -f environment.yml`
3. Activar entorno: `conda activate {self.nombre}_env`
4. Configurar pre-commit: `conda install -c conda-forge pre-commit && pre-commit install`

## Estructura
{self.estructura}

## Documentación
Consulte `/docs/documentation.txt` para información detallada.

## Herramientas
- Black (formato)
- Flake8 (linting)
- isort (imports)
- pytest (testing)

## CI/CD
Pipeline configurado con GitHub Actions
"""