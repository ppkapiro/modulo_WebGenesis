import os
import logging
import platform
from pathlib import Path
from .command_runner import CommandRunner
from .ui_helper import UIHelper

class EnvManager:
    def __init__(self, ui: UIHelper):
        self.ui = ui
        self.sistema = platform.system()

    def verificar_entorno_virtual(self, nombre_proyecto: str) -> bool:
        """Verifica si el entorno virtual está activado"""
        env_actual = os.environ.get('CONDA_DEFAULT_ENV')
        env_esperado = f"{nombre_proyecto}_env"
        
        if env_actual == env_esperado:
            self.ui.print_success(f"Entorno virtual '{env_esperado}' activo")
            return True
        
        self.ui.print_warning(f"Entorno virtual '{env_esperado}' no está activo")
        if self.ui.confirmar_accion("¿Desea activar el entorno automáticamente?"):
            return self.activar_entorno(nombre_proyecto)
        return False

    def activar_entorno(self, nombre_proyecto: str) -> bool:
        """Intenta activar el entorno virtual"""
        try:
            if self.sistema == 'Windows':
                success, _ = CommandRunner.execute_command(
                    ['conda', 'activate', f"{nombre_proyecto}_env"],
                    shell=True
                )
            else:
                success, _ = CommandRunner.execute_command(
                    ['conda', 'activate', f"{nombre_proyecto}_env"],
                    shell=True
                )
            
            if success:
                self.ui.print_success(f"Entorno '{nombre_proyecto}_env' activado")
                return True
            else:
                self.ui.print_error("No se pudo activar el entorno")
                self.mostrar_instrucciones_activacion(nombre_proyecto)
                return False
        except Exception as e:
            logging.error(f"Error al activar entorno: {str(e)}")
            self.mostrar_instrucciones_activacion(nombre_proyecto)
            return False

    def mostrar_instrucciones_activacion(self, nombre_proyecto: str):
        """Muestra instrucciones para activar el entorno manualmente"""
        self.ui.print_step("Para activar el entorno manualmente:")
        if self.sistema == 'Windows':
            print(f"  conda activate {nombre_proyecto}_env")
        else:
            print(f"  source activate {nombre_proyecto}_env")

    def generar_docker_config(self, ruta_base: Path, nombre_proyecto: str, version_python: str):
        """Genera archivos de configuración Docker si se requiere"""
        if self.ui.confirmar_accion("¿Desea configurar Docker para el proyecto?"):
            try:
                self._crear_dockerfile(ruta_base, version_python)
                self._crear_docker_compose(ruta_base, nombre_proyecto)
                self._crear_dockerignore(ruta_base)
                self.ui.print_success("Configuración Docker generada exitosamente")
            except Exception as e:
                logging.error(f"Error al generar configuración Docker: {str(e)}")
                self.ui.print_error("No se pudo generar la configuración Docker")

    def _crear_dockerfile(self, ruta_base: Path, version_python: str):
        contenido = f"""FROM continuumio/miniconda3

WORKDIR /app

COPY environment.yml .
RUN conda env create -f environment.yml

SHELL ["conda", "run", "-n", "myenv", "/bin/bash", "-c"]

COPY . .

CMD ["conda", "run", "-n", "myenv", "python", "src/main.py"]
"""
        (ruta_base / 'Dockerfile').write_text(contenido)

    def _crear_docker_compose(self, ruta_base: Path, nombre_proyecto: str):
        contenido = f"""version: '3.8'

services:
  web:
    build: .
    container_name: {nombre_proyecto}
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    environment:
      - PYTHONPATH=/app
"""
        (ruta_base / 'docker-compose.yml').write_text(contenido)

    def _crear_dockerignore(self, ruta_base: Path):
        contenido = """__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.env
.venv
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.pytest_cache/
.env
.venv
"""
        (ruta_base / '.dockerignore').write_text(contenido)
