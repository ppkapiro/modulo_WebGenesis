import logging
import os
from pathlib import Path
from typing import Optional, Tuple, Dict, List
from datetime import datetime
import json
from ..utils.command_runner import CommandRunner
from ..utils.ui_helper import UIHelper

class WordPressManager:
    def __init__(self, ui: UIHelper, ruta_base: Path):
        self.ui = ui
        self.ruta_base = ruta_base
        self.wp_path = Path.home() / '.wp-cli'  # Nuevo: directorio para WP-CLI
        self.diagnostics = []

    def verificar_wpcli(self) -> bool:
        """Verifica si WP-CLI está instalado y configurado"""
        # Primero verificar en PATH
        success, _ = CommandRunner.execute_command(['wp', '--info'])
        if success:
            self.ui.print_success("WP-CLI encontrado y funcionando")
            return True
            
        # Verificar en directorio local
        wp_local = self.wp_path / 'wp.bat'
        if wp_local.exists():
            self.ui.print_success("WP-CLI encontrado en directorio local")
            return True
            
        self.ui.print_error("WP-CLI no encontrado")
        self.ui.print_step("\nPasos para instalar WP-CLI:")
        print("Se instalará WP-CLI en su directorio de usuario")
        
        if self.ui.confirmar_accion("\n¿Desea intentar instalar WP-CLI automáticamente?", default=True):
            return self._instalar_wpcli()
        return False

    def _instalar_wpcli(self) -> bool:
        """Instala WP-CLI en el directorio del usuario"""
        try:
            # Crear directorio .wp-cli si no existe
            self.wp_path.mkdir(parents=True, exist_ok=True)
            
            self.ui.print_step("Descargando WP-CLI...")
            success, _ = CommandRunner.execute_command([
                'powershell',
                '-Command',
                f'Invoke-WebRequest -Uri "https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar" -OutFile "{self.wp_path}/wp-cli.phar"'
            ])
            
            if not success:
                raise Exception("Error al descargar WP-CLI")

            # Crear archivo batch para ejecutar wp-cli
            wp_bat = self.wp_path / 'wp.bat'
            bat_content = f"""@echo off
php "{self.wp_path / 'wp-cli.phar'}" %*"""
            wp_bat.write_text(bat_content)

            # Agregar al PATH del usuario
            user_path = os.environ.get('PATH', '')
            if str(self.wp_path) not in user_path:
                os.environ['PATH'] = f"{self.wp_path};{user_path}"
                # Actualizar PATH permanentemente para el usuario
                CommandRunner.execute_command([
                    'powershell',
                    '-Command',
                    f'[Environment]::SetEnvironmentVariable("Path", "{self.wp_path};$env:Path", "User")'
                ])
            
            self.ui.print_success("WP-CLI instalado correctamente")
            self.ui.print_step(f"WP-CLI instalado en: {self.wp_path}")
            return True
                
        except Exception as e:
            self.ui.print_error(f"Error al instalar WP-CLI: {str(e)}")
            self.ui.print_warning("Por favor, intente la instalación manual siguiendo los pasos anteriores")
            return False

    def _verificar_requisitos_sistema(self) -> bool:
        """Verifica y configura los requisitos del sistema"""
        try:
            # 1. Verificar PHP
            success, output = CommandRunner.execute_command(['php', '-v'])
            if not success:
                self.ui.print_error("PHP no encontrado. Por favor, instale PHP primero.")
                return False
                
            # 2. Configurar memoria PHP
            php_ini = Path(os.environ.get('PHPRC', '')) / 'php.ini'
            if php_ini.exists():
                self.ui.print_step("Ajustando configuración de PHP")
                with open(php_ini, 'a', encoding='utf-8') as f:
                    f.write("\n; WP-CLI memory settings\n")
                    f.write("memory_limit = 512M\n")
                    f.write("max_execution_time = 300\n")
                self.ui.print_success("Configuración PHP actualizada")
            
            return True
            
        except Exception as e:
            self.ui.print_error(f"Error al verificar requisitos: {str(e)}")
            return False

    def analizar_instalacion_existente(self) -> Tuple[bool, Dict]:
        """Analiza una instalación existente de WordPress"""
        self.ui.print_step("Analizando instalación de WordPress...")
        try:
            # Primero verificar WP-CLI
            if not self.verificar_wpcli():
                return False, {}

            # Verificar que es una instalación WordPress
            if not (self.ruta_base / 'wp-config.php').exists():
                self.ui.print_error("No se encontró wp-config.php. ¿Es esto una instalación WordPress?")
                return False, {}

            info = {
                'version': None,
                'tema_activo': None,
                'plugins': [],
                'estado_db': None,
                'permisos': [],
                'errores': [],
                'recomendaciones': []
            }

            # Obtener versión y estado
            success, output = CommandRunner.execute_command(
                ['wp', 'core', 'version'], cwd=self.ruta_base
            )
            if success:
                info['version'] = output.strip()
                self.ui.print_success(f"WordPress versión {info['version']} detectada")
            
            # Verificar tema activo
            success, output = CommandRunner.execute_command(
                ['wp', 'theme', 'list', '--status=active', '--format=json'],
                cwd=self.ruta_base
            )
            if success:
                info['tema_activo'] = json.loads(output)
                self.ui.print_step(f"Tema activo: {info['tema_activo']}")

            # Listar plugins
            success, output = CommandRunner.execute_command(
                ['wp', 'plugin', 'list', '--format=json'],
                cwd=self.ruta_base
            )
            if success:
                info['plugins'] = json.loads(output)
                self.ui.print_step(f"Plugins encontrados: {len(info['plugins'])}")

            # Verificar base de datos
            success, output = CommandRunner.execute_command(
                ['wp', 'db', 'check'],
                cwd=self.ruta_base
            )
            info['estado_db'] = 'OK' if success else 'Error'
            
            # Verificar permisos críticos
            for dir in ['wp-content', 'wp-content/uploads']:
                path = self.ruta_base / dir
                if path.exists():
                    permisos = os.stat(path).st_mode
                    info['permisos'].append({
                        'path': dir,
                        'mode': oct(permisos)[-3:],
                        'writeable': os.access(path, os.W_OK)
                    })

            # Generar reporte detallado
            report_path = self.ruta_base / 'wp-analysis.md'
            self._generar_reporte_analisis(report_path, info)
            
            return True, info

        except Exception as e:
            self.ui.print_error(f"Error al analizar WordPress: {str(e)}")
            return False, {}

    def _generar_reporte_analisis(self, report_path: Path, info: Dict):
        """Genera un reporte del análisis de la instalación"""
        content = [
            "# Análisis de Instalación WordPress",
            f"\nFecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"\n## Información General",
            f"- Versión WordPress: {info['version']}",
            f"- Tema Activo: {info['tema_activo']}",
            f"- Estado Base de Datos: {info['estado_db']}",
            
            "\n## Plugins Instalados",
            *[f"- {plugin['name']} ({plugin['status']})" for plugin in info['plugins']],
            
            "\n## Permisos de Directorios",
            *[f"- {p['path']}: {p['mode']} ({'Escritura OK' if p['writeable'] else 'Sin escritura'})"
              for p in info['permisos']],
            
            "\n## Recomendaciones",
            *info['recomendaciones']
        ]
        
        report_path.write_text('\n'.join(content), encoding='utf-8')
        self.ui.print_success(f"Reporte de análisis generado en: {report_path}")

    def analizar_sitio_existente(self):
        """Analiza una instalación WordPress existente"""
        try:
            # Verificar que es una instalación WordPress
            if not (self.ruta_base / 'wp-config.php').exists():
                self.ui.print_error("No se encontró wp-config.php. ¿Es esto una instalación WordPress?")
                return

            if not self.verificar_wpcli():
                return

            while True:
                print("\nAcciones disponibles:")
                print("1. Analizar instalación")
                print("2. Ejecutar diagnóstico completo")
                print("3. Verificar actualizaciones")
                print("4. Volver al menú principal")
                
                opcion = input("\nSeleccione una opción: ")
                
                if opcion == "1":
                    success, info = self.analizar_instalacion_existente()
                    if success:
                        self.ui.print_success("Análisis completado")
                elif opcion == "2":
                    success, diagnosticos = self.ejecutar_diagnostico_completo()
                    if success and diagnosticos['estado'] == 'error':
                        if self.ui.confirmar_accion("¿Desea intentar corregir los problemas?"):
                            comandos = self.sugerir_correcciones(diagnosticos)
                            self.ejecutar_correcciones(comandos)
                elif opcion == "3":
                    self.verificar_actualizaciones()
                elif opcion == "4":
                    break

        except Exception as e:
            self.ui.print_error(f"Error al analizar WordPress: {str(e)}")

    def verificar_actualizaciones(self):
        """Verifica actualizaciones disponibles"""
        try:
            self.ui.print_step("Verificando actualizaciones...")
            
            checks = [
                ('core', ['wp', 'core', 'check-update']),
                ('plugins', ['wp', 'plugin', 'update', '--dry-run']),
                ('temas', ['wp', 'theme', 'update', '--dry-run'])
            ]

            for tipo, comando in checks:
                success, output = CommandRunner.execute_command(comando, cwd=self.ruta_base)
                if success:
                    self.ui.print_step(f"Estado de {tipo}:")
                    print(output)

        except Exception as e:
            self.ui.print_error(f"Error al verificar actualizaciones: {str(e)}")

    def ejecutar_diagnostico_completo(self) -> Tuple[bool, Dict]:
        """Ejecuta un diagnóstico completo de WordPress"""
        try:
            diagnosticos = {
                'estado': 'pendiente',
                'errores': [],
                'advertencias': [],
                'info': {},
                'timestamp': datetime.now().isoformat()
            }

            checks = [
                ('core', ['wp', 'core', 'verify-checksums']),
                ('db', ['wp', 'db', 'check']),
                ('plugins', ['wp', 'plugin', 'status']),
                ('temas', ['wp', 'theme', 'status']),
                ('permisos', ['wp', 'eval', "echo wp_is_writable(ABSPATH)"]),
                ('updates', ['wp', 'core', 'check-update']),
                ('ssl', ['wp', 'eval', "echo is_ssl() ? 'SSL activo' : 'Sin SSL'"])
            ]

            for nombre, comando in checks:
                self.ui.print_step(f"Verificando {nombre}...")
                success, output = CommandRunner.execute_command(
                    comando, cwd=self.ruta_base, shell=True
                )
                
                if not success:
                    diagnosticos['errores'].append({
                        'componente': nombre,
                        'mensaje': output
                    })
                else:
                    diagnosticos['info'][nombre] = output.strip()

            # Analizar resultados
            diagnosticos['estado'] = 'error' if diagnosticos['errores'] else 'ok'

            # Generar reporte
            self._generar_reporte_diagnostico(diagnosticos)
            return True, diagnosticos

        except Exception as e:
            self.ui.print_error(f"Error en diagnóstico: {str(e)}")
            logging.error(f"Error en diagnóstico: {str(e)}")
            return False, {"estado": "error", "mensaje": str(e)}

    def _generar_reporte_diagnostico(self, diagnosticos: Dict):
        """Genera un reporte detallado del diagnóstico"""
        try:
            report_path = self.ruta_base / 'wp-diagnostico.md'
            
            contenido = [
                "# Diagnóstico de WordPress",
                f"\nFecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"\nEstado: {diagnosticos['estado'].upper()}",
                
                "\n## Errores Detectados",
                *[f"- {e['componente']}: {e['mensaje']}" for e in diagnosticos['errores']],
                
                "\n## Información por Componente"
            ]
            
            for componente, info in diagnosticos['info'].items():
                contenido.extend([
                    f"\n### {componente.title()}",
                    f"\n{info}"
                ])
            
            report_path.write_text('\n'.join(contenido), encoding='utf-8')
            self.ui.print_success(f"Reporte de diagnóstico generado en: {report_path}")

        except Exception as e:
            self.ui.print_error(f"Error al generar reporte de diagnóstico: {str(e)}")

    def re_ejecutar_diagnostico(self) -> Tuple[bool, Dict]:
        """Re-ejecuta el diagnóstico y compara con el anterior"""
        try:
            # Guardar diagnóstico anterior
            anterior_path = self.ruta_base / 'wp-diagnostico-anterior.md'
            actual_path = self.ruta_base / 'wp-diagnostico.md'
            if actual_path.exists():
                actual_path.rename(anterior_path)

            # Ejecutar nuevo diagnóstico
            success, nuevo_diagnostico = self.ejecutar_diagnostico_completo()
            if not success:
                return False, {}

            # Comparar y generar reporte de cambios
            self._generar_reporte_cambios(anterior_path, actual_path)
            return True, nuevo_diagnostico

        except Exception as e:
            self.ui.print_error(f"Error al re-ejecutar diagnóstico: {str(e)}")
            return False, {}

    def remediar_automaticamente(self, diagnosticos: Dict) -> bool:
        """Intenta remediar automáticamente problemas detectados"""
        try:
            acciones = []
            for error in diagnosticos['errores']:
                componente = error['componente']
                self.ui.print_step(f"Intentando corregir: {componente}")
                
                if componente == 'db':
                    success, _ = CommandRunner.execute_command(
                        ['wp', 'db', 'repair'], cwd=self.ruta_base
                    )
                    if success:
                        acciones.append("Base de datos reparada")
                
                elif componente == 'plugins':
                    success, _ = CommandRunner.execute_command(
                        ['wp', 'plugin', 'update', '--all'], cwd=self.ruta_base
                    )
                    if success:
                        acciones.append("Plugins actualizados")
                
                elif componente == 'temas':
                    success, _ = CommandRunner.execute_command(
                        ['wp', 'theme', 'update', '--all'], cwd=self.ruta_base
                    )
                    if success:
                        acciones.append("Temas actualizados")
                
                elif componente == 'permisos':
                    self._corregir_permisos()
                    acciones.append("Permisos corregidos")

            # Actualizar documentación con acciones realizadas
            self.actualizar_documentacion_wordpress({
                'estado': 'remediado',
                'acciones_correctivas': acciones
            })
            
            return True
            
        except Exception as e:
            self.ui.print_error(f"Error en remediación: {str(e)}")
            logging.error(f"Error en remediación: {str(e)}")
            return False

    def _corregir_permisos(self):
        """Corrige permisos comunes"""
        directorios = ['wp-content', 'wp-content/uploads', 'wp-content/plugins']
        for dir in directorios:
            CommandRunner.execute_command(['chmod', '-R', '755', dir], cwd=self.ruta_base)

    def _actualizar_plugins(self):
        """Actualiza plugins con problemas"""
        CommandRunner.execute_command(['wp', 'plugin', 'update', '--all'], cwd=self.ruta_base)

    def _actualizar_temas(self):
        """Actualiza temas con problemas"""
        CommandRunner.execute_command(['wp', 'theme', 'update', '--all'], cwd=self.ruta_base)

    def _limpiar_cache(self):
        """Limpia cachés de WordPress"""
        CommandRunner.execute_command(['wp', 'cache', 'flush'], cwd=self.ruta_base)

    def _optimizar_db(self):
        """Optimiza la base de datos"""
        CommandRunner.execute_command(['wp', 'db', 'optimize'], cwd=self.ruta_base)

    def actualizar_documentacion_wordpress(self, diagnosticos: Dict):
        """Actualiza la documentación del proyecto con resultados de WordPress"""
        try:
            project_md = self.ruta_base / 'project.md'
            if not project_md.exists():
                return

            contenido = project_md.read_text(encoding='utf-8')
            
            # Actualizar sección WordPress
            wp_section = [
                "\n## Estado WordPress",
                f"Última verificación: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                f"Estado: {diagnosticos['estado']}",
                "\n### Errores Detectados",
                *[f"- {e['componente']}: {e['mensaje']}" for e in diagnosticos['errores']],
                "\n### Acciones Correctivas",
                *[f"- {a}" for a in diagnosticos.get('acciones_correctivas', [])]
            ]

            # Insertar o actualizar sección
            if "## Estado WordPress" in contenido:
                # Actualizar sección existente
                pass
            else:
                # Agregar nueva sección
                contenido += "\n" + "\n".join(wp_section)

            project_md.write_text(contenido, encoding='utf-8')
            self.ui.print_success("Documentación actualizada con estado de WordPress")

        except Exception as e:
            self.ui.print_error(f"Error al actualizar documentación: {str(e)}")

    def mostrar_resumen_analisis(self, info: Dict):
        """Muestra un resumen del análisis en consola"""
        self.ui.print_header("RESUMEN DE ANÁLISIS WORDPRESS")
        print(f"\nVersión WordPress: {info['version']}")
        print(f"Tema Activo: {info['tema_activo']}")
        print(f"Estado DB: {info['estado_db']}")
        
        print("\nPlugins instalados:")
        for plugin in info['plugins']:
            estado = "✔" if plugin['status'] == 'active' else "✖"
            print(f"{estado} {plugin['name']}")

        print("\nEstado de permisos:")
        for permiso in info['permisos']:
            estado = "✔" if permiso['writeable'] else "⚠"
            print(f"{estado} {permiso['path']}: {permiso['mode']}")
