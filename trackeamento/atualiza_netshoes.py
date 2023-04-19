# Django Utils

import os
import django
import sys

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dagg.settings')
django.setup()

# Importando Modulos do Script
from trackeamento.models import PosicaoNetshoes
import requests
from bs4 import BeautifulSoup

trackeamentos = PosicaoNetshoes.objects.all()

for trackeamento in trackeamentos:
    termo = trackeamento.termo_busca
    sku_netshoes = trackeamento.sku_netshoes
    
    page = '&page=2'
    
    # Configurações
    url = f'https://www.netshoes.com.br/busca?nsCat=Natural&q={termo}'
    user_agent = {'User-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)' 'Chrome/106.0.0.0 Safari/537.36'}
    
    # Requisição
    page = requests.get(url, headers=user_agent)
    site = BeautifulSoup(page.content, "html.parser")

    # Obtendo links
    container = site.find(class_="item-list")