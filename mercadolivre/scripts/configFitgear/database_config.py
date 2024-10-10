import sys
import os
import django
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dagg.settings')
django.setup()

from mercadolivre.models import TokenMercadoLivreFitGearAPI

first_row = TokenMercadoLivreFitGearAPI.objects.first()

try:
    refresh_token_inicial = first_row.refresh_token_inicial
    access_token = first_row.access_token
    client_id = first_row.client_id
    client_secret = first_row.client_secret
except:
    print('Nenhum token encontrado')