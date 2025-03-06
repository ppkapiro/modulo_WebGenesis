import os
import logging
from colorama import init, Fore, Style
from typing import Optional, List, Dict
from pathlib import Path

# Inicializar colorama para Windows
init()

class UIHelper:
    @staticmethod
    def print_header(texto: str):
        """Imprime un encabezado formateado"""
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f" {texto}")
        print(f"{'='*80}{Style.RESET_ALL}")

    @staticmethod
    def print_step(texto: str):
        """Imprime un paso del proceso"""
        print(f"\n{Fore.GREEN}➜ {texto}{Style.RESET_ALL}")

    @staticmethod
    def print_warning(texto: str):
        """Imprime una advertencia"""
        print(f"{Fore.YELLOW}⚠ {texto}{Style.RESET_ALL}")

    @staticmethod
    def print_error(texto: str):
        """Imprime un error"""
        print(f"{Fore.RED}✖ ERROR: {texto}{Style.RESET_ALL}")

    @staticmethod
    def print_success(texto: str):
        """Imprime un mensaje de éxito"""
        print(f"{Fore.GREEN}✔ {texto}{Style.RESET_ALL}")

    @staticmethod
    def confirmar_accion(mensaje: str, default: bool = False) -> bool:
        """Solicita confirmación al usuario"""
        opcion = input(f"{Fore.YELLOW}{mensaje} [{'S/n' if default else 's/N'}]: {Style.RESET_ALL}").lower()
        if not opcion:
            return default
        return opcion.startswith('s')

    @staticmethod
    def mostrar_rollback_info(operaciones: List[Dict]):
        """Muestra información sobre las operaciones que se desharán"""
        print(f"\n{Fore.YELLOW}Se desharán las siguientes operaciones:{Style.RESET_ALL}")
        for op in operaciones:
            print(f"- {op['descripcion']}")
        
    @staticmethod
    def solicitar_rollback() -> bool:
        """Pregunta al usuario si desea deshacer los cambios"""
        return UIHelper.confirmar_accion("¿Desea deshacer los cambios realizados?")
