"""
Punto de entrada principal de WebGenesis.
Este archivo es el orquestador principal de todos los módulos.
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent
sys.path.append(str(root_dir))

from src.utils.ui_helper import UIHelper
from setup_proyecto import main as setup_main
from src.utils.doc_generator import DocumentacionGenerator  # Cambiar esta importación

def mostrar_menu_principal():
    ui = UIHelper()
    ui.print_header("WEBGENESIS - GENERADOR DE PROYECTOS")
    print("\n1. Crear nuevo proyecto")
    print("2. Configurar WordPress en proyecto existente")
    print("3. Generar documentación")
    print("4. Salir")
    return input("\nSeleccione una opción: ")

def generar_documentacion():
    """Genera y actualiza toda la documentación del proyecto"""
    ui = UIHelper()
    ruta_base = Path.cwd()
    
    try:
        # Obtener configuración del proyecto
        from src.utils.user_input import cargar_configuracion
        config = cargar_configuracion()
        nombre = config['defaults']['project_name']
        version_python = config['defaults']['python_version']
        
        ui.print_step("Generando documentación del proyecto")
        doc_generator = DocumentacionGenerator(ruta_base, nombre, version_python)
        
        # Generar todos los documentos
        doc_path = doc_generator.generar_documentacion_completa()
        design_path = doc_generator.generar_design_doc()
        project_path = doc_generator.actualizar_project_md()
        
        if all([doc_path, design_path, project_path]):
            ui.print_success("Documentación actualizada exitosamente")
            ui.print_step("Archivos generados:")
            print(f"- Documentación: {doc_path}")
            print(f"- Diseño: {design_path}")
            print(f"- Proyecto: {project_path}")
            
            # Preguntar si desea abrir la documentación
            if ui.confirmar_accion("¿Desea abrir la documentación en VS Code?", default=True):
                from setup_proyecto import abrir_vscode
                abrir_vscode(ruta_base, doc_path)
        else:
            ui.print_error("Error al generar algunos archivos de documentación")
            
    except Exception as e:
        ui.print_error(f"Error al generar documentación: {str(e)}")

def main():
    while True:
        opcion = mostrar_menu_principal()
        
        if opcion == "1":
            setup_main()
        elif opcion == "2":
            from src.wordpress.wp_manager import WordPressManager
            # Lógica para configurar WordPress
        elif opcion == "3":
            generar_documentacion()
        elif opcion == "4":
            print("\n¡Hasta luego!")
            break
        else:
            print("\nOpción no válida")

if __name__ == "__main__":
    main()
