"""
Punto de entrada principal del módulo WebGenesis.
Este archivo permite ejecutar el módulo directamente usando:
python -m src
"""

from pathlib import Path
import sys

# Agregar el directorio raíz al path para importaciones
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from setup_proyecto import main

if __name__ == "__main__":
    main()
