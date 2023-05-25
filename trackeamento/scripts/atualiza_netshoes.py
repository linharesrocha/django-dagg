import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent


def start_atualiza_netshoes():
    slack = True
    main(slack)
    
    
def slack_notificao(nome, sku, pag_antiga, pag_nova, concorrente, pesquisa):
    load_dotenv()

    client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])
    SLACK_CHANNEL_ID='C030X3UMR3M'

    if concorrente == True:
        if int(pag_antiga) > int(pag_nova):
            icon = ':x:'
        else:
            icon = ':white_check_mark:'
        concorrente = 'Anúncio Concorrente'
    else:
        if int(pag_antiga) > int(pag_nova):
            icon = ':white_check_mark:'
        else:
            icon = ':x:'
        concorrente = 'Anúncio Dagg'
    
    message = f'NETSHOES! {icon}\n{nome} - {sku} - {concorrente}\nPesquisa: {pesquisa}\nMudou da página {pag_antiga} para a página {pag_nova}.'
    
    try:
        response = client.chat_postMessage(
            channel=SLACK_CHANNEL_ID,
            text=message
        )
    except SlackApiError as e:
        print("Error sending message: {}".format(e))


def main(slack):
    # Django Utils
    import os
    import django
    import sys

    sys.path.append(str(BASE_DIR))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dagg.settings')
    django.setup()

    # Importando Modulos do Script
    from trackeamento.models import PosicaoNetshoes
    import requests
    from bs4 import BeautifulSoup
    from django.db.models import Min

    trackeamentos = PosicaoNetshoes.objects.values('termo_busca', 'sku_netshoes', 'anuncio_concorrente', 'nome').annotate(sku_min=Min('sku_netshoes'))
    print(f'ATUALIZANDO TRACKEAMENTO DE {len(trackeamentos)} PRODUTOS NETSHOES')

    for indice, trackeamento in enumerate(trackeamentos):
        print(f'{indice+1}/{len(trackeamentos)} - {trackeamento["sku_netshoes"]}')
        anuncios_list = []
        termo = trackeamento['termo_busca']
        termo_modificado = termo.replace(' ', '%20')
        sku_netshoes = trackeamento['sku_netshoes']
        sku_netshoes_modificado = sku_netshoes[:-3]
        
        # Páginas
        for i in range(1, 10):
            url = f'https://www.netshoes.com.br/busca?nsCat=Natural&q={termo_modificado}&page={i}'
            user_agent = {'User-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)' 'Chrome/106.0.0.0 Safari/537.36'}
            
            # Requisição
            page = requests.get(url, headers=user_agent)
            site = BeautifulSoup(page.content, "html.parser")
            
            # Anúncios em BS4
            anuncios = site.find_all(class_="item-desktop--3")

            # Armazenando SKU Netshoes
            for anuncio in anuncios:
                anuncios_list.append(anuncio['parent-sku'])
                
        
            # Buscando a posição do anúncio
            if sku_netshoes_modificado in anuncios_list:
                posicao_anuncio = anuncios_list.index(sku_netshoes_modificado)
                posicao_anuncio = posicao_anuncio + 1
                break
            else:
                posicao_anuncio = None
        
        # Atualizando a posição no banco de dados
        anuncio_track_novo = PosicaoNetshoes()
        anuncio_track_novo.termo_busca = termo
        anuncio_track_novo.sku_netshoes = sku_netshoes
        anuncio_track_novo.posicao = posicao_anuncio
        anuncio_track_novo.anuncio_concorrente = trackeamento['anuncio_concorrente']
        anuncio_track_novo.nome = trackeamento['nome'] 
        pagina_atual = (posicao_anuncio - 1) // 42 + 1 if posicao_anuncio else None
        anuncio_track_novo.pagina = pagina_atual
        
        # Atualiza variacao
        ultimo_registro_pagina = PosicaoNetshoes.objects.filter(sku_netshoes=sku_netshoes).last().pagina
        envia_notificacao = False
        if ultimo_registro_pagina == None or pagina_atual == None:
            anuncio_track_novo.variacao = 'Manteve'
        elif pagina_atual < ultimo_registro_pagina:
            anuncio_track_novo.variacao = 'Melhorou' 
            envia_notificacao = True
        elif pagina_atual > ultimo_registro_pagina:
            anuncio_track_novo.variacao = 'Piorou'
            envia_notificacao = True
        else:
            anuncio_track_novo.variacao = 'Manteve'
        
        # Verifica se o script foi rodado a partir do crontab e não do usuário
        if slack == True and envia_notificacao == True:
            slack_notificao(trackeamento['nome'], sku_netshoes, ultimo_registro_pagina, pagina_atual, trackeamento['anuncio_concorrente'], termo)
        
        anuncio_track_novo.save()
        