from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent

# Set up Django settings
sys.path.append(str(BASE_DIR))

from cria_planilha_armazem_valor_custo_total import main

send_to_slack = True

main(send_to_slack)