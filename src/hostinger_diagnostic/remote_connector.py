try:
    import paramiko
except ImportError:
    raise ImportError(
        "El módulo 'paramiko' es necesario para conexiones SSH. "
        "Instálelo con: pip install paramiko"
    )

from pathlib import Path
from typing import Dict, Optional
from ..utils.ui_helper import UIHelper

class HostingerConnector:
    def __init__(self, config: Dict, ui: UIHelper):
        self.config = config
        self.ui = ui
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def test_connection(self) -> bool:
        """Prueba la conexión SSH al servidor"""
        try:
            self.ssh.connect(
                self.config.host,
                username=self.config.usuario,
                password=self.config.password
            )
            self.ui.print_success("Conexión establecida con Hostinger")
            return True
        except Exception as e:
            self.ui.print_error(f"Error de conexión: {str(e)}")
            return False

    def obtener_logs(self) -> Dict[str, str]:
        """Obtiene logs remotos vía SSH"""
        try:
            logs = {}
            archivos = [
                'error.log',
                'wp-content/debug.log',
                '/var/log/php_errors.log'
            ]

            for archivo in archivos:
                ruta_completa = f"{self.config.ruta_remota}/{archivo}"
                stdin, stdout, stderr = self.ssh.exec_command(f"cat {ruta_completa}")
                logs[archivo] = stdout.read().decode('utf-8')

            return logs

        except Exception as e:
            self.ui.print_error(f"Error al obtener logs: {str(e)}")
            return {}

    def obtener_info_tema(self) -> Dict:
        """Obtiene información del tema vía SSH"""
        try:
            cmd = "wp theme list --status=active --format=json --path=" + self.config.ruta_remota
            stdin, stdout, stderr = self.ssh.exec_command(cmd)
            return {'tema_info': stdout.read().decode('utf-8')}
        except Exception as e:
            return {'error': str(e)}

    def cerrar_conexion(self):
        """Cierra la conexión SSH"""
        try:
            self.ssh.close()
        except:
            pass
