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
    anuncios_list = []
    termo = trackeamento.termo_busca
    sku_netshoes = trackeamento.sku_netshoes
    sku_netshoes_modificado = sku_netshoes[:-3]
    
    # Páginas
    for i in range(1, 6):
        url = f'https://www.netshoes.com.br/busca?nsCat=Natural&q={termo}&page={i}'
        user_agent = {'User-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)' 'Chrome/106.0.0.0 Safari/537.36'}
        
        # Requisição
        page = requests.get(url, headers=user_agent)
        site = BeautifulSoup(page.content, "html.parser")
        container = site.find(class_="item-list")
        
        # Anúncios em BS4
        anuncios = container.find_all(class_="item-desktop--3")

        # Armazenando SKU Netshoes
        for anuncio in anuncios:
            anuncios_list.append(anuncio['parent-sku'])
            
    
    # Buscando a posição do anúncio
    if sku_netshoes_modificado in anuncios_list:
        posicao_anuncio = anuncios_list.index(sku_netshoes_modificado)
        posicao_anuncio = posicao_anuncio + 1
    else:
        posicao_anuncio = None
        
    # Atualizando a posição no banco de dados
    anuncio_track = PosicaoNetshoes.objects.get(sku_netshoes=sku_netshoes)
    anuncio_track.posicao = posicao_anuncio
    anuncio_track.pagina = (posicao_anuncio - 1) // 42 + 1 if posicao_anuncio else None

    anuncio_track.save()