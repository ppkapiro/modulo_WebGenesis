"""
Punto de entrada principal de WebGenesis.
Este archivo es el orquestador principal de todos los módulos.
"""

import sys
import logging
from pathlib import Path
from typing import Dict  # Agregar esta línea

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent
sys.path.append(str(root_dir))

from src.utils.ui_helper import UIHelper
from src.utils.doc_generator import DocumentacionGenerator
from src.wordpress.wp_manager import WordPressManager
from setup_proyecto import main as setup_main
from src.utils.setup_tools import validar_dependencias
from src.utils.setup_tools import verificar_modulo_hostinger
from src.hostinger_diagnostic.diagnostic_manager import HostingerDiagnosticManager
from src.utils.notification_manager import NotificationManager

def configurar_logging():
    """Configura el sistema de logging"""
    logging.basicConfig(
        filename='webgenesis.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def mostrar_menu_principal():
    """Muestra el menú principal con todas las opciones disponibles"""
    ui = UIHelper()
    ui.print_header("WEBGENESIS - SUITE DE DESARROLLO WEB")
    
    print("\nOpciones disponibles:")
    print("1. 🔧 Configurar proyecto y entorno")
    print("2. 🌐 Administrar WordPress")
    print("3. 🔍 Ejecutar diagnósticos")
    print("4. 📚 Actualizar documentación")
    print("5. 🏥 Diagnóstico WordPress Hostinger")  # Nueva opción
    print("6. ❌ Salir")
    
    return input("\nSeleccione una opción: ").strip()

def submenu_wordpress(ui: UIHelper):
    """Gestiona el submenú de WordPress"""
    # Solicitar ruta una sola vez al inicio
    ruta_str = input("\nRuta de la instalación WordPress: ").strip()
    ruta_base = Path(ruta_str)
    
    if not ruta_base.exists():
        ui.print_error(f"La ruta {ruta_base} no existe")
        return
        
    wp_manager = WordPressManager(ui, ruta_base)
    if not wp_manager.verificar_wpcli():
        return

    while True:
        print("\nGestión de WordPress:")
        print("1. Analizar instalación existente")
        print("2. Ejecutar diagnóstico completo")
        print("3. Re-ejecutar diagnóstico")
        print("4. Verificar actualizaciones")
        print("5. Regresar al menú principal")
        
        opcion = input("\nSeleccione una opción: ").strip()
        
        if opcion == "1":
            success, info = wp_manager.analizar_instalacion_existente()
            if success:
                wp_manager.mostrar_resumen_analisis(info)
                
        elif opcion == "2":
            success, diagnosticos = wp_manager.ejecutar_diagnostico_completo()
            if success:
                if diagnosticos['estado'] == 'error':
                    if ui.confirmar_accion("¿Desea intentar remediar los problemas?", default=False):
                        wp_manager.remediar_automaticamente(diagnosticos)
                        # Re-ejecutar diagnóstico después de remediar
                        wp_manager.re_ejecutar_diagnostico()
                else:
                    ui.print_success("No se encontraron problemas que requieran remediación")
                    
        elif opcion == "3":
            wp_manager.re_ejecutar_diagnostico()
            
        elif opcion == "4":
            wp_manager.verificar_actualizaciones()
            
        elif opcion == "5":
            break
            
        else:
            ui.print_error("Opción no válida")

def submenu_diagnosticos(ui: UIHelper):
    """Gestiona el submenú de diagnósticos"""
    while True:
        print("\nDiagnósticos del proyecto:")
        print("1. Ejecutar diagnóstico completo")
        print("2. Comparar con diagnóstico anterior")
        print("3. Verificar dependencias")
        print("4. Regresar al menú principal")
        
        opcion = input("\nSeleccione una opción: ").strip()
        
        if opcion == "1":
            ui.print_step("Ejecutando diagnóstico completo...")
            # Aquí irían los diagnósticos generales del proyecto
            pass
        elif opcion == "2":
            ui.print_step("Comparando diagnósticos...")
            # Aquí iría la comparación de diagnósticos
            pass
        elif opcion == "3":
            if validar_dependencias():
                ui.print_success("Todas las dependencias están correctamente instaladas")
            else:
                ui.print_error("Hay dependencias faltantes o mal configuradas")
        elif opcion == "4":
            break

def actualizar_documentacion(ui: UIHelper):
    """Actualiza toda la documentación del proyecto"""
    try:
        ui.print_step("Actualizando documentación del proyecto...")
        
        # Obtener información del proyecto
        from src.utils.user_input import cargar_configuracion
        config = cargar_configuracion()
        nombre = config['defaults']['project_name']
        version = config['defaults']['python_version']
        
        # Generar documentación
        doc_generator = DocumentacionGenerator(Path.cwd(), nombre, version)
        doc_path = doc_generator.generar_documentacion_completa()
        design_doc = doc_generator.generar_design_doc()
        project_md = doc_generator.actualizar_project_md()
        
        if all([doc_path, design_doc, project_md]):
            ui.print_success("Documentación actualizada exitosamente")
            ui.print_step("Documentos generados:")
            print(f"- Documentación: {doc_path}")
            print(f"- Diseño: {design_doc}")
            print(f"- Proyecto: {project_md}")
        else:
            ui.print_error("Hubo errores al actualizar algunos documentos")
            
    except Exception as e:
        ui.print_error(f"Error al actualizar documentación: {str(e)}")
        logging.error(f"Error en actualización de documentación: {str(e)}")

def ejecutar_diagnostico_hostinger(ui: UIHelper):
    """Ejecuta el diagnóstico completo de WordPress Hostinger"""
    try:
        manager = HostingerDiagnosticManager(ui)
        notifier = NotificationManager()

        # Configurar diagnóstico
        if not manager.configurar_diagnostico():
            return

        # Ejecutar diagnóstico completo
        ui.print_step("Iniciando diagnóstico completo...")
        success, diagnostico = manager.ejecutar_diagnostico_completo()

        if not success:
            ui.print_error("Error al ejecutar diagnóstico")
            return

        # Mostrar resultados y ofrecer remediación
        if diagnostico['estado'] == 'error':
            if ui.confirmar_accion("Se encontraron problemas. ¿Desea intentar remediarlos?"):
                success = manager.ejecutar_remediacion_interactiva(diagnostico)
                if success:
                    notifier.enviar_notificacion(
                        "Remediación completada",
                        "Se aplicaron correcciones automáticas"
                    )

        # Mostrar resumen final
        mostrar_resumen_diagnostico(ui, diagnostico)

    except Exception as e:
        ui.print_error(f"Error en diagnóstico Hostinger: {str(e)}")
        logging.error(f"Error en diagnóstico Hostinger: {str(e)}")

def mostrar_resumen_diagnostico(ui: UIHelper, diagnostico: Dict):
    """Muestra un resumen detallado del diagnóstico"""
    ui.print_header("RESUMEN DEL DIAGNÓSTICO")
    
    # Estado general
    estado = "✅ OK" if diagnostico['estado'] == 'ok' else "❌ Error"
    print(f"\nEstado: {estado}")
    
    # Errores encontrados
    if diagnostico.get('errores'):
        print("\nErrores detectados:")
        for error in diagnostico['errores']:
            print(f"- {error['tipo']}: {error['mensaje']}")
    
    # Acciones realizadas
    if diagnostico.get('acciones_ejecutadas'):
        print("\nAcciones de remediación:")
        for accion in diagnostico['acciones_ejecutadas']:
            print(f"✓ {accion}")
    
    # Ubicación de reportes
    print("\nReportes generados:")
    print(f"- Diagnóstico: wp-diagnostics.md")
    print(f"- Remediación: wp-remediation.md")
    
    if diagnostico.get('pendientes'):
        ui.print_warning("\nAcciones pendientes que requieren intervención manual:")
        for pendiente in diagnostico['pendientes']:
            print(f"! {pendiente}")

def main():
    """Función principal que maneja el flujo del programa"""
    configurar_logging()
    ui = UIHelper()
    logging.info("Iniciando WebGenesis")
    
    # Verificar módulo hostinger_diagnostic
    if not verificar_modulo_hostinger(Path(__file__).parent):
        ui.print_warning("Advertencia: Módulo hostinger_diagnostic no pudo ser verificado")
    
    while True:
        try:
            opcion = mostrar_menu_principal()
            
            if opcion == "1":
                logging.info("Iniciando configuración de proyecto")
                setup_main()
            elif opcion == "2":
                logging.info("Accediendo a gestión WordPress")
                submenu_wordpress(ui)
            elif opcion == "3":
                logging.info("Accediendo a diagnósticos")
                submenu_diagnosticos(ui)
            elif opcion == "4":
                logging.info("Actualizando documentación")
                actualizar_documentacion(ui)
            elif opcion == "5":
                logging.info("Iniciando diagnóstico WordPress Hostinger")
                ejecutar_diagnostico_hostinger(ui)
            elif opcion == "6":
                ui.print_success("\n¡Gracias por usar WebGenesis!")
                logging.info("Finalizando WebGenesis")
                break
            else:
                ui.print_error("Opción no válida")
                
        except Exception as e:
            logging.error(f"Error en menú principal: {str(e)}")
            ui.print_error(f"Error inesperado: {str(e)}")
            if ui.confirmar_accion("¿Desea continuar con el programa?", default=True):
                continue
            break

if __name__ == "__main__":
    main()
