import requests
import json
import pandas as pd
from datetime import datetime, date
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))
from mercadolivre.scripts.config import reflash

# Variáveis
ACCESS_TOKEN = reflash.refreshToken()
ITEM_ID = 'MLB-2762322359'
ITEM_ID = ITEM_ID.replace('-','').replace('/', '')
SER_ID_DAGG = '195279505'
NICKNAME_SELLER = 'DAGG SPORT'

# Header
header = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

# Visitas
visitas = requests.get(f"https://api.mercadolibre.com/visits/items?ids={ITEM_ID}", headers=header).json().get(ITEM_ID)

# Nome / Pontuação Anúncio / Criação Anúncio
response = requests.get(f"https://api.mercadolibre.com/items/{ITEM_ID}?include_attributes=all", headers=header).json()
titulo = response['title']
pontuacao_anuncio = response['health']
criacao_anuncio = response['date_created']
vendas_anuncio = response['sold_quantity']

# Vende a cada visita / Conversao
if vendas_anuncio > 0:
    taxa_conversao_total = round((vendas_anuncio / visitas) * 100,2)
    vende_a_cada_visita = round(visitas / vendas_anuncio , 1)
else:
    taxa_conversao = 0
    vende_a_cada_visita = 0