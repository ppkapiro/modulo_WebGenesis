"""
Módulo para conectar y administrar conexiones con servidores Hostinger.
Maneja conexiones SSH y operaciones remotas.
"""

import logging
from pathlib import Path
from typing import Dict, Tuple, List, Optional
from dataclasses import dataclass
import json
from ..utils.ui_helper import UIHelper
from ..utils.command_runner import CommandRunner

try:
    import paramiko
except ImportError:
    raise ImportError(
        "El módulo 'paramiko' es necesario para conexiones SSH. "
        "Instálelo con: pip install paramiko"
    )

class HostingerConnector:
    def __init__(self, config: Dict, ui: UIHelper):
        self.config = config
        self.ui = ui
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.sftp = None
        self.is_connected = False

    def test_connection(self) -> bool:
        """Prueba la conexión SSH al servidor"""
        try:
            self.ui.print_step("Conectando a servidor Hostinger...")
            self.ssh.connect(
                hostname=self.config.host,
                username=self.config.usuario,
                password=self.config.password,
                timeout=10
            )
            self.sftp = self.ssh.open_sftp()
            self.is_connected = True
            self.ui.print_success("Conexión establecida con Hostinger")
            return True

        except Exception as e:
            self.ui.print_error(f"Error de conexión: {str(e)}")
            logging.error(f"Error al conectar con Hostinger: {str(e)}")
            return False

    def ejecutar_comando(self, comando: str) -> Tuple[bool, str]:
        """Ejecuta un comando en el servidor remoto"""
        try:
            if not self.is_connected:
                raise Exception("No hay conexión activa")
                
            stdin, stdout, stderr = self.ssh.exec_command(comando)
            error = stderr.read().decode('utf-8')
            
            if error:
                return False, error
                
            return True, stdout.read().decode('utf-8')
            
        except Exception as e:
            return False, str(e)

    def obtener_logs(self) -> Dict[str, str]:
        """Obtiene logs remotos del servidor"""
        try:
            logs = {}
            archivos_log = [
                'wp-content/debug.log',
                'error.log',
                'php_error.log',
                '/var/log/php_errors.log'
            ]

            for archivo in archivos_log:
                ruta_completa = f"{self.config.ruta_remota}/{archivo}"
                success, contenido = self.ejecutar_comando(f"cat {ruta_completa}")
                if success and contenido.strip():
                    logs[archivo] = contenido
                    self.ui.print_success(f"Log obtenido: {archivo}")

            return logs

        except Exception as e:
            self.ui.print_error(f"Error al obtener logs: {str(e)}")
            return {}

    def obtener_info_tema(self) -> Dict:
        """Obtiene información del tema activo"""
        try:
            cmd = f"cd {self.config.ruta_remota} && wp theme list --status=active --format=json"
            success, output = self.ejecutar_comando(cmd)
            
            if success:
                return {'tema_info': json.loads(output)}
            return {'error': output}
            
        except Exception as e:
            return {'error': str(e)}

    def verificar_permisos(self) -> Dict[str, bool]:
        """Verifica permisos de directorios críticos"""
        directorios = [
            'wp-content',
            'wp-content/themes',
            'wp-content/plugins',
            'wp-content/uploads'
        ]
        
        permisos = {}
        for dir in directorios:
            ruta = f"{self.config.ruta_remota}/{dir}"
            success, output = self.ejecutar_comando(f"test -w {ruta} && echo 'true' || echo 'false'")
            permisos[dir] = output.strip() == 'true'
            
        return permisos

    def cerrar_conexion(self):
        """Cierra las conexiones SSH y SFTP"""
        try:
            if self.sftp:
                self.sftp.close()
            if self.ssh:
                self.ssh.close()
            self.is_connected = False
        except:
            pass

    def __del__(self):
        """Asegura que las conexiones se cierren al destruir el objeto"""
        self.cerrar_conexion()
