import os
import sys
import logging
import subprocess
from pathlib import Path
from datetime import datetime
import shutil

# Importar módulos propios
from src.utils.user_input import solicitar_parametros
from src.utils.setup_tools import validar_dependencias
from src.utils.command_runner import CommandRunner
from src.utils.ui_helper import UIHelper
from src.utils.env_manager import EnvManager
from src.utils.preferences import guardar_preferencias
from src.utils.doc_generator import DocumentacionGenerator
from src.wordpress import WordPressManager

def configurar_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('project_setup.log'),
            logging.StreamHandler()
        ]
    )

def crear_estructura(ruta_base):
    try:
        directorios = [
            'src', 'config', 'tests', 'docs', 'public_html',
            'themes', 'plugins', '.github/workflows'
        ]
        estructura = []
        for dir in directorios:
            Path(ruta_base / dir).mkdir(parents=True, exist_ok=True)
            estructura.append(f"├── {dir}/")
            logging.info(f"Directorio creado: {dir}")
        return "\n".join(estructura)
    except Exception as e:
        logging.error(f"Error al crear directorios: {str(e)}")
        return ""

def configurar_git(ruta_base):
    try:
        success, message = CommandRunner.execute_command(['git', 'init'], cwd=ruta_base)
        if not success:
            raise Exception(message)
            
        gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.env
.venv
env/
venv/
ENV/
.vscode/
*.code-workspace
.DS_Store
Thumbs.db
*.log
"""
        (ruta_base / '.gitignore').write_text(gitignore_content)
        logging.info("Git inicializado y .gitignore creado")
        return True
    except Exception as e:
        logging.error(f"Error al configurar Git: {str(e)}")
        return False

def configurar_conda(nombre_proyecto, version_python):
    try:
        success, message = CommandRunner.execute_command([
            'conda', 'create', '--yes',
            '--name', f"{nombre_proyecto}_env",
            f"python={version_python}"
        ])
        if success:
            logging.info("Entorno Conda creado exitosamente")
        else:
            raise Exception(message)
    except Exception as e:
        logging.error(f"Error al crear entorno Conda: {str(e)}")

def crear_archivos_base(ruta_base, nombre, version_python):
    try:
        # Crear README.md con UTF-8
        readme_content = f"# {nombre}\n\nProyecto creado con Python {version_python}"
        (ruta_base / 'README.md').write_text(readme_content, encoding='utf-8')

        # Crear environment.yml con todas las dependencias necesarias
        environment_content = f"""name: {nombre}_env
channels:
  - conda-forge
  - defaults
dependencies:
  - python={version_python}
  - pytest
  - black
  - flake8
  - isort
  - pre-commit
  - colorama>=0.4.6
  - pyyaml>=6.0.1
  - pip
"""
        (ruta_base / 'environment.yml').write_text(environment_content, encoding='utf-8')

        logging.info("Archivos base creados exitosamente")
    except Exception as e:
        logging.error(f"Error al crear archivos base: {str(e)}")

def abrir_vscode(ruta_base, doc_path=None):
    """Abre VS Code con el proyecto y la documentación"""
    try:
        vscode_path = r"C:\Users\pepec\AppData\Local\Programs\Microsoft VS Code\bin\code.cmd"
        # Abrir el proyecto primero
        success, message = CommandRunner.execute_command(
            [vscode_path, str(ruta_base)],
            shell=True
        )
        if not success:
            raise Exception(message)
            
        # Si hay documentación, abrirla en una nueva pestaña
        if doc_path:
            success, message = CommandRunner.execute_command(
                [vscode_path, '--goto', str(doc_path)],
                shell=True
            )
            if success:
                logging.info(f"Documentación abierta en VS Code: {doc_path}")
            else:
                logging.warning(f"No se pudo abrir la documentación: {message}")
        
        logging.info("VS Code abierto con el proyecto")
        return True
    except Exception as e:
        logging.error(f"Error al abrir VS Code: {str(e)}")
        print("\nPara abrir el proyecto manualmente:")
        print(f"1. Abra VS Code")
        print(f"2. Seleccione File > Open Folder")
        print(f"3. Navegue a: {str(ruta_base)}")
        return False

class SetupManager:
    def __init__(self):
        self.operaciones_realizadas = []
        self.ui = UIHelper()
        self.env_manager = EnvManager(self.ui)

    def registrar_operacion(self, tipo: str, descripcion: str, rollback_fn=None):
        """Registra una operación realizada para posible rollback"""
        self.operaciones_realizadas.append({
            'tipo': tipo,
            'descripcion': descripcion,
            'rollback': rollback_fn
        })

    def rollback(self):
        """Deshace las operaciones realizadas en orden inverso"""
        if not self.operaciones_realizadas:
            return

        self.ui.mostrar_rollback_info(self.operaciones_realizadas)
        if not self.ui.solicitar_rollback():
            return

        for operacion in reversed(self.operaciones_realizadas):
            try:
                if operacion['rollback']:
                    operacion['rollback']()
                    self.ui.print_success(f"Desecha operación: {operacion['descripcion']}")
            except Exception as e:
                self.ui.print_error(f"Error al deshacer {operacion['descripcion']}: {str(e)}")

def main():
    setup = SetupManager()
    setup.ui.print_header("CONFIGURACIÓN DE PROYECTO MODULAR")
    
    configurar_logging()
    logging.info("Iniciando configuración modular del proyecto")
    
    if not validar_dependencias():
        setup.ui.print_error("Dependencias faltantes")
        print("\nPor favor, verifique que tiene instalado:")
        print("1. Conda (https://docs.conda.io/en/latest/miniconda.html)")
        print("2. VS Code (https://code.visualstudio.com/)")
        return

    setup.ui.print_step("Solicitando parámetros del proyecto")
    nombre, ubicacion, version_python = solicitar_parametros()
    if not all([nombre, ubicacion, version_python]):
        setup.ui.print_error("Parámetros incompletos")
        return

    ruta_base = Path(ubicacion) / nombre
    if ruta_base.exists():
        if not setup.ui.confirmar_accion(
            f"El directorio {ruta_base} ya existe. ¿Desea continuar y posiblemente sobrescribir archivos?",
            default=False
        ):
            setup.ui.print_warning("Operación cancelada por el usuario")
            return

    try:
        setup.ui.print_step("Creando estructura de directorios")
        ruta_base.mkdir(parents=True, exist_ok=True)
        estructura = crear_estructura(ruta_base)
        setup.registrar_operacion(
            'directorio', 
            f"Crear estructura en {ruta_base}",
            lambda: shutil.rmtree(ruta_base) if ruta_base.exists() else None
        )

        setup.ui.print_step("Creando archivos base")
        crear_archivos_base(ruta_base, nombre, version_python)
        
        setup.ui.print_step("Configurando Git")
        if configurar_git(ruta_base):
            setup.ui.print_success("Git inicializado correctamente")
        
        setup.ui.print_step("Configurando entorno Conda")
        configurar_conda(nombre, version_python)
        
        setup.ui.print_step("Generando documentación detallada")
        doc_generator = DocumentacionGenerator(ruta_base, nombre, version_python)
        doc_path = doc_generator.generar_documentacion_completa()
        
        if doc_path:
            setup.ui.print_success(f"Documentación actualizada en: {doc_path}")
        
        # Verificar entorno virtual
        if setup.env_manager.verificar_entorno_virtual(nombre):
            setup.ui.print_success("Entorno virtual verificado correctamente")
        
        # Generar configuración Docker si se requiere
        setup.env_manager.generar_docker_config(ruta_base, nombre, version_python)
        
        setup.ui.print_success(f"Proyecto creado exitosamente en: {ruta_base}")
        
        # Guardar preferencias del usuario
        if setup.ui.confirmar_accion("¿Desea guardar estas preferencias para futuras ejecuciones?"):
            guardar_preferencias({
                'abrir_doc_automaticamente': True,
                'verificar_entorno': True,
                'configurar_docker': True
            })
        
        # Abrir VS Code con el proyecto y la documentación
        if setup.ui.confirmar_accion("¿Desea abrir el proyecto en VS Code?", default=True):
            abrir_vscode(ruta_base, doc_path)
            
        # Configuración opcional de WordPress
        if setup.ui.confirmar_accion("¿Desea configurar WordPress?", default=False):
            wp_manager = WordPressManager(setup.ui, ruta_base)
            if wp_manager.verificar_wpcli():
                wp_config = {
                    'db_name': input("Nombre de la base de datos: "),
                    'db_user': input("Usuario de la base de datos: "),
                    'db_pass': input("Contraseña de la base de datos: "),
                    'site_url': input("URL del sitio: "),
                    'site_title': input("Título del sitio: "),
                    'admin_user': input("Usuario administrador: "),
                    'admin_pass': input("Contraseña administrador: "),
                    'admin_email': input("Email administrador: ")
                }
                
                if wp_manager.instalar_wordpress(wp_config):
                    # Preguntar por tema personalizado
                    if setup.ui.confirmar_accion("¿Desea instalar un tema personalizado?"):
                        tema_path = Path(input("Ruta al archivo del tema: "))
                        wp_manager.instalar_tema(tema_path)
                    
                    # Ejecutar diagnóstico
                    success, diagnostics_path = wp_manager.ejecutar_diagnostico()
                    if success:
                        reporte_path = wp_manager.generar_reporte()
                        if reporte_path:
                            setup.ui.print_success("WordPress configurado exitosamente")
            
            # Ejecutar diagnóstico completo
            setup.ui.print_step("Ejecutando diagnóstico de WordPress")
            success, diagnosticos = wp_manager.ejecutar_diagnostico_completo()
            
            if success:
                if diagnosticos['estado'] == 'error':
                    setup.ui.print_warning("Se encontraron problemas en la instalación")
                    if setup.ui.confirmar_accion("¿Desea intentar corregir los problemas automáticamente?"):
                        comandos = wp_manager.sugerir_correcciones(diagnosticos)
                        if comandos and wp_manager.ejecutar_correcciones(comandos):
                            setup.ui.print_success("Correcciones aplicadas exitosamente")
                else:
                    setup.ui.print_success("WordPress configurado y verificado correctamente")
            
            setup.ui.print_step("Consulte el reporte completo en wp-diagnostics.md")

    except Exception as e:
        setup.ui.print_error(f"Error durante la configuración: {str(e)}")
        setup.rollback()

if __name__ == "__main__":
    main()
