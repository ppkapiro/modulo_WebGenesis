import logging
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple

class CommandRunner:
    @staticmethod
    def execute_command(
        command: List[str],
        cwd: Optional[Path] = None,
        shell: bool = False,
        capture_output: bool = True
    ) -> Tuple[bool, str]:
        """
        Ejecuta un comando externo de manera segura y registra su resultado.
        
        Args:
            command: Lista de argumentos del comando
            cwd: Directorio de trabajo
            shell: Si se debe usar shell
            capture_output: Si se debe capturar la salida
        
        Returns:
            Tupla de (éxito, mensaje)
        """
        cmd_str = ' '.join(command)
        logging.info(f"Ejecutando comando: {cmd_str}")
        
        try:
            result = subprocess.run(
                command,
                cwd=str(cwd) if cwd else None,
                shell=shell,
                capture_output=capture_output,
                text=True,
                encoding='utf-8'
            )
            
            if result.returncode == 0:
                logging.info(f"Comando ejecutado exitosamente: {cmd_str}")
                return True, result.stdout if result.stdout else "Comando ejecutado exitosamente"
            else:
                error_msg = f"Error al ejecutar '{cmd_str}': {result.stderr}"
                logging.error(error_msg)
                return False, error_msg
                
        except Exception as e:
            error_msg = f"Excepción al ejecutar '{cmd_str}': {str(e)}"
            logging.error(error_msg)
            return False, error_msg
