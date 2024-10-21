from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent

# Set up Django settings
sys.path.append(str(BASE_DIR))

from confere_margem_decathlon import main

inicio_data_personalizada = None
fim_data_personalizada = None
empresa_personalizada = None
personalizado = False

main(inicio_data_personalizada, fim_data_personalizada, empresa_personalizada, personalizado)