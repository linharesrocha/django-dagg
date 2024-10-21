from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent

# Set up Django settings
sys.path.append(str(BASE_DIR))

from confere_margem_centauro import main

inicio_data_personalizada = None
fim_data_personalizada = None
personalizado = False

main(inicio_data_personalizada, fim_data_personalizada, personalizado)