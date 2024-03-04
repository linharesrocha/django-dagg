from django.utils import timezone
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

def start_match_netshoes():
    print('CRON STARTANDO SCRIPT DE VERIFICAÇÃO DE MATCH NETSHOES')
    main()

def main():
    # Django Utils
    import os
    import django
    import sys

    sys.path.append(str(BASE_DIR))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dagg.settings')
    django.setup()

    # Importando Modulos do Script
    from trackeamento.models import MatchNetshoes
    import requests
    from bs4 import BeautifulSoup
    from django.db.models import Min

    trackeamentos = MatchNetshoes.objects.values('sku_match', 'nome_loja').annotate(sku_min=Min('sku_match'))
    print(f'ATUALIZANDO TRACKEAMENTO DE {len(trackeamentos)} PRODUTOS NETSHOES')

    for indice, trackeamento in enumerate(trackeamentos):
        try:
            print(f'{indice+1}/{len(trackeamentos)} - {trackeamento["sku_match"]}')
            nome_loja = trackeamento['nome_loja']
            sku_match = trackeamento['sku_match']
            
            # Páginas
            url = f'https://www.netshoes.com.br/{sku_match}'
            user_agent = {'User-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)' 'Chrome/106.0.0.0 Safari/537.36'}
            
            # Requisição
            page = requests.get(url, headers=user_agent)
            site = BeautifulSoup(page.content, "html.parser")

            # Verifica indisponibilidade
            try:
                indisponibilidade = site.find(class_="action-buttons").find(class_="title").text.strip()
                if indisponibilidade == 'Produto indisponível':
                    MatchNetshoes.objects.filter(sku_match=sku_match, nome_loja=nome_loja).update(status='Indisponível', ultima_atualizacao=timezone.now())
                    continue
            except:
                print('Produto Disponível')
            
            # Nome da loja em BS4
            nome_loja_bs4 = site.find(class_="product__seller_name").text.strip()

            # Verifica se o anúncio é da loja
            if nome_loja_bs4 == nome_loja:
                loja_mantem_posicao = 'Manteve'
            else:
                loja_mantem_posicao = 'Não Manteve'
            
            # Atualiza o trackeamento
            MatchNetshoes.objects.filter(sku_match=sku_match, nome_loja=nome_loja).update(status=loja_mantem_posicao, ultima_atualizacao=timezone.now())
        except Exception as e:
            print(f'Erro: {e}')
            continue