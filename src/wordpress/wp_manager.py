import logging
from pathlib import Path
from typing import Optional, Tuple, Dict
from ..utils.command_runner import CommandRunner
from ..utils.ui_helper import UIHelper

class WordPressManager:
    def __init__(self, ui: UIHelper, ruta_base: Path):
        self.ui = ui
        self.ruta_base = ruta_base
        self.wp_path = None
        self.diagnostics = []

    def verificar_wpcli(self) -> bool:
        """Verifica si WP-CLI está instalado y configurado"""
        success, output = CommandRunner.execute_command(['wp', '--info'])
        if success:
            self.ui.print_success("WP-CLI encontrado y funcionando")
            return True
        self.ui.print_error("WP-CLI no encontrado. Por favor, instálelo primero.")
        return False

    def instalar_wordpress(self, config: Dict) -> bool:
        """Instala WordPress usando WP-CLI"""
        try:
            steps = [
                ['wp', 'core', 'download', '--locale=es_ES'],
                ['wp', 'config', 'create',
                 f"--dbname={config['db_name']}",
                 f"--dbuser={config['db_user']}",
                 f"--dbpass={config['db_pass']}",
                 '--dbhost=localhost'
                ],
                ['wp', 'core', 'install',
                 f"--url={config['site_url']}",
                 f"--title={config['site_title']}",
                 f"--admin_user={config['admin_user']}",
                 f"--admin_password={config['admin_pass']}",
                 f"--admin_email={config['admin_email']}"
                ]
            ]

            for step in steps:
                self.ui.print_step(f"Ejecutando: {' '.join(step)}")
                success, output = CommandRunner.execute_command(
                    step, cwd=self.ruta_base, shell=True
                )
                if not success:
                    raise Exception(output)
                
            self.ui.print_success("WordPress instalado correctamente")
            return True

        except Exception as e:
            self.ui.print_error(f"Error al instalar WordPress: {str(e)}")
            return False

    def instalar_tema(self, tema_path: Path) -> bool:
        """Instala y activa un tema de WordPress"""
        try:
            # Instalar tema
            success, output = CommandRunner.execute_command(
                ['wp', 'theme', 'install', str(tema_path), '--activate'],
                cwd=self.ruta_base
            )
            if not success:
                raise Exception(output)

            self.ui.print_success(f"Tema instalado y activado: {tema_path.name}")
            return True

        except Exception as e:
            self.ui.print_error(f"Error al instalar tema: {str(e)}")
            return False

    def ejecutar_diagnostico(self) -> Tuple[bool, str]:
        """Ejecuta diagnósticos en la instalación de WordPress"""
        try:
            diagnostics_path = self.ruta_base / 'wp_diagnostics.txt'
            checks = [
                ['wp', 'core', 'verify-checksums'],
                ['wp', 'theme', 'list', '--status=active'],
                ['wp', 'plugin', 'list'],
                ['wp', 'core', 'check-update'],
                ['wp', 'theme', 'check-update'],
                ['wp', 'plugin', 'check-update']
            ]

            with open(diagnostics_path, 'w', encoding='utf-8') as f:
                f.write("=== DIAGNÓSTICO DE WORDPRESS ===\n\n")
                for check in checks:
                    self.ui.print_step(f"Ejecutando: {' '.join(check)}")
                    success, output = CommandRunner.execute_command(
                        check, cwd=self.ruta_base
                    )
                    f.write(f"\n=== {' '.join(check)} ===\n")
                    f.write(output if success else f"ERROR: {output}")

            self.ui.print_success(f"Diagnóstico completado: {diagnostics_path}")
            return True, str(diagnostics_path)

        except Exception as e:
            self.ui.print_error(f"Error durante el diagnóstico: {str(e)}")
            return False, str(e)

    def generar_reporte(self) -> Optional[Path]:
        """Genera un reporte detallado del estado de WordPress"""
        try:
            report_path = self.ruta_base / 'wp_report.md'
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write("# Reporte de WordPress\n\n")
                f.write("## Información del Sistema\n")
                success, output = CommandRunner.execute_command(['wp', 'system', 'info'])
                f.write(f"```\n{output}\n```\n\n")
                
                f.write("## Estado de Temas\n")
                success, output = CommandRunner.execute_command(['wp', 'theme', 'list'])
                f.write(f"```\n{output}\n```\n\n")
                
                f.write("## Plugins Instalados\n")
                success, output = CommandRunner.execute_command(['wp', 'plugin', 'list'])
                f.write(f"```\n{output}\n```\n\n")

            self.ui.print_success(f"Reporte generado en: {report_path}")
            return report_path

        except Exception as e:
            self.ui.print_error(f"Error al generar reporte: {str(e)}")
            return None
