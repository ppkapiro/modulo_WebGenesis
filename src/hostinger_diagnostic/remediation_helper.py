import logging
from typing import Dict, List, Tuple
from pathlib import Path
from ..utils.command_runner import CommandRunner
from ..utils.ui_helper import UIHelper

class RemediationHelper:
    def __init__(self, ui: UIHelper, ruta_base: Path):
        self.ui = ui
        self.ruta_base = ruta_base
        self.acciones_ejecutadas = []

    def analizar_errores(self, diagnostico: Dict) -> Dict[str, List[str]]:
        """Analiza errores y genera sugerencias de remediación"""
        sugerencias = {
            'criticas': [],
            'importantes': [],
            'recomendadas': []
        }

        for error in diagnostico.get('errores', []):
            severity = self._determinar_severidad(error)
            accion = self._generar_sugerencia(error)
            if accion:
                sugerencias[severity].append(accion)
                
        return sugerencias

    def _determinar_severidad(self, error: Dict) -> str:
        """Determina la severidad de un error"""
        criterios = {
            'criticas': ['db_error', 'core_corrupt', 'security'],
            'importantes': ['plugin_conflict', 'theme_error', 'php_error'],
            'recomendadas': ['performance', 'updates', 'warnings']
        }

        for nivel, tipos in criterios.items():
            if error.get('tipo') in tipos:
                return nivel
        return 'recomendadas'

    def _generar_sugerencia(self, error: Dict) -> str:
        """Genera una sugerencia de remediación"""
        sugerencias = {
            'db_error': "Reparar y optimizar base de datos",
            'plugin_conflict': "Desactivar y actualizar plugins conflictivos",
            'theme_error': "Verificar y actualizar tema",
            'core_corrupt': "Verificar integridad de archivos core",
            'php_error': "Actualizar versión de PHP o ajustar límites",
            'security': "Aplicar correcciones de seguridad recomendadas"
        }
        return sugerencias.get(error.get('tipo', ''), '')

    def ejecutar_remediacion(self, tipo_error: str) -> Tuple[bool, str]:
        """Ejecuta acciones de remediación según el tipo de error"""
        acciones = {
            'db_error': self._reparar_base_datos,
            'plugin_conflict': self._resolver_conflicto_plugins,
            'theme_error': self._corregir_tema,
            'core_corrupt': self._verificar_core,
            'security': self._aplicar_seguridad
        }

        if tipo_error in acciones:
            self.ui.print_step(f"Ejecutando remediación para: {tipo_error}")
            success, msg = acciones[tipo_error]()
            if success:
                self.acciones_ejecutadas.append(f"Remediación {tipo_error}: {msg}")
            return success, msg
        
        return False, "Tipo de error no soportado para remediación"

    def _reparar_base_datos(self) -> Tuple[bool, str]:
        """Repara y optimiza la base de datos"""
        try:
            commands = [
                ['wp', 'db', 'repair'],
                ['wp', 'db', 'optimize']
            ]
            
            for cmd in commands:
                success, output = CommandRunner.execute_command(
                    cmd, cwd=self.ruta_base
                )
                if not success:
                    return False, f"Error en {cmd[1]}: {output}"
                    
            return True, "Base de datos reparada y optimizada"
            
        except Exception as e:
            return False, str(e)

    def _resolver_conflicto_plugins(self) -> Tuple[bool, str]:
        """Resuelve conflictos de plugins"""
        try:
            # 1. Listar plugins activos
            success, output = CommandRunner.execute_command(
                ['wp', 'plugin', 'list', '--status=active', '--format=json'],
                cwd=self.ruta_base
            )
            if not success:
                return False, "No se pudo obtener lista de plugins"

            # 2. Desactivar plugins problemáticos
            success, _ = CommandRunner.execute_command(
                ['wp', 'plugin', 'deactivate', '--all'],
                cwd=self.ruta_base
            )
            if not success:
                return False, "No se pudieron desactivar los plugins"

            # 3. Actualizar plugins
            success, _ = CommandRunner.execute_command(
                ['wp', 'plugin', 'update', '--all'],
                cwd=self.ruta_base
            )

            return True, "Plugins desactivados y actualizados"
            
        except Exception as e:
            return False, str(e)

    def _corregir_tema(self) -> Tuple[bool, str]:
        """Corrige problemas del tema"""
        try:
            # 1. Verificar tema activo
            success, output = CommandRunner.execute_command(
                ['wp', 'theme', 'list', '--status=active', '--format=json'],
                cwd=self.ruta_base
            )
            if not success:
                return False, "No se pudo verificar el tema activo"

            # 2. Actualizar tema
            success, _ = CommandRunner.execute_command(
                ['wp', 'theme', 'update', '--all'],
                cwd=self.ruta_base
            )

            return True, "Tema actualizado correctamente"
            
        except Exception as e:
            return False, str(e)

    def _verificar_core(self) -> Tuple[bool, str]:
        """Verifica y corrige archivos del core"""
        try:
            commands = [
                ['wp', 'core', 'verify-checksums'],
                ['wp', 'core', 'update']
            ]
            
            for cmd in commands:
                success, output = CommandRunner.execute_command(
                    cmd, cwd=self.ruta_base
                )
                if not success:
                    return False, f"Error en {cmd[1]}: {output}"
                    
            return True, "Core verificado y actualizado"
            
        except Exception as e:
            return False, str(e)

    def _aplicar_seguridad(self) -> Tuple[bool, str]:
        """Aplica correcciones de seguridad básicas"""
        try:
            # 1. Verificar permisos
            success, _ = CommandRunner.execute_command(
                ['chmod', '755', 'wp-content'],
                cwd=self.ruta_base
            )
            
            # 2. Actualizar salts
            success, _ = CommandRunner.execute_command(
                ['wp', 'config', 'shuffle-salts'],
                cwd=self.ruta_base
            )

            return True, "Correcciones de seguridad aplicadas"
            
        except Exception as e:
            return False, str(e)

    def generar_reporte_remediacion(self) -> str:
        """Genera un reporte de las acciones de remediación"""
        if not self.acciones_ejecutadas:
            return "No se ejecutaron acciones de remediación"
            
        return "\n".join([
            "# Reporte de Remediación",
            "## Acciones Ejecutadas:",
            *[f"- {accion}" for accion in self.acciones_ejecutadas]
        ])
