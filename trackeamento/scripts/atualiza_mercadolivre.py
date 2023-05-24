import requests
from pathlib import Path
import sys
from dotenv import load_dotenv
from datetime import datetime
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import time


BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))
from mercadolivre.scripts.config import reflash


def start_atualiza_mercadolivre():
    main()
    
    
def posicao_produtos_mercadolivre(termo_busca, mlb_anuncio):
    # Teste
    # termo_busca = 'chinelo nuvem'
    # mlb_anuncio = 'MLB2691941243'
    # posicao_anuncio_normal = None
    # pagina_normal = None
    
    print(f'Termo: {termo_busca} - {mlb_anuncio}')
    
    # Controle
    pagina_normal = 1
    posicao_anuncio_normal = None
    mlbs = []
    mlb_found = False
    
    # Primeira página
    start_time = time.time()
    print('BUSCA NORMAL')
    response = requests.get(f'https://lista.mercadolivre.com.br/{termo_busca}')
    print(f'Página: {pagina_normal}')
    print(f'URL: https://lista.mercadolivre.com.br/{termo_busca}')
    print(f'Response: {response.url}')
    
    # Página normal
    while True:
        # Request
        soup = BeautifulSoup(response.content, 'html.parser')
        items = soup.find_all(class_='ui-search-layout__item')
        
        # Armazena mlb dos anúncios
        for item in items:
            try:
                form_class = item.find(class_='ui-search-bookmark')
                item_id = form_class.find('input', {'name':'itemId'})['value']
                mlbs.append(item_id)
            except:
                click1_mercadolivre = item.find(class_='ui-search-result__image').find('a').get('href')
                link = requests.get(click1_mercadolivre).url
                item_id = 'MLB' + link.split("-")[1]
                mlbs.append(item_id)
            
            # Confere se o anúncio é o que está sendo buscado
            if str(item_id) == str(mlb_anuncio):
                posicao_anuncio_normal = mlbs.index(mlb_anuncio) + 1
                mlb_found = True
                break
            
        # Caso o anúncio seja encontrado ou a página ser maior que 20
        if mlb_found or pagina_normal > 20:
            if posicao_anuncio_normal == None:
                pagina_normal = None
            break
        else:
            try:
                pagina_normal += 1
                paginacao = soup.find(class_='andes-pagination__button--next').find('a').get('href')
                response = requests.get(paginacao)
                print(f'Página: {pagina_normal}')
                print(f'URL: {paginacao}')
                print(f'Response: {response.url}')
            except:
                # Não existe mais página
                pagina_normal = None
                break
                
    # Controle
    pagina_full = 1
    posicao_anuncio_full = None
    mlbs = []
    mlb_found = False
    
    # Primeira página
    print('BUSCA FULL')
    response = requests.get(f'https://lista.mercadolivre.com.br/{termo_busca}_Frete_Full_NoIndex_True')
    print(f'Página: {pagina_full}')
    print(f'URL: https://lista.mercadolivre.com.br/{termo_busca}_Frete_Full_NoIndex_True')
    print(f'Response: {response.url}')
    
    # Página Full
    while True:
        # Request
        soup = BeautifulSoup(response.content, 'html.parser')
        items = soup.find_all(class_='ui-search-layout__item')
        
        # Armazena mlb dos anúncios
        for item in items:
            try:
                form_class = item.find(class_='ui-search-bookmark')
                item_id = form_class.find('input', {'name':'itemId'})['value']
                mlbs.append(item_id)
            except:
                click1_mercadolivre = item.find(class_='ui-search-result__image').find('a').get('href')
                link = requests.get(click1_mercadolivre).url
                item_id = 'MLB' + link.split("-")[1]
                mlbs.append(item_id)

            if str(item_id) == str(mlb_anuncio):
                posicao_anuncio_full = mlbs.index(mlb_anuncio) + 1
                mlb_found = True
                break
        
        # Caso o anúncio seja encontrado ou a página ser maior que 20
        if mlb_found or pagina_full > 10:
            if posicao_anuncio_full == None:
                pagina_full = None
            end_time = time.time()
            elapsed_time = end_time - start_time
            mins, secs = divmod(elapsed_time, 60)
            print(f"Tempo de execução: {int(mins)} minutos e {round(secs,2)} segundos")
            return posicao_anuncio_normal, pagina_normal, posicao_anuncio_full, pagina_full
        else:
            try:
                pagina_full += 1
                paginacao = soup.find(class_='andes-pagination__button--next').find('a').get('href') + '_Frete_Full'
                response = requests.get(paginacao)
                print(f'Página: {pagina_full}')
                print(f'URL: {paginacao}')
                print(f'Response: {response.url}')
            except:
                end_time = time.time()
                elapsed_time = end_time - start_time
                mins, secs = divmod(elapsed_time, 60)
                print(f"Tempo de execução: {int(mins)} minutos e {round(secs,2)} segundos")
                # Não existe mais página
                print('Não existe mais página')
                pagina_full = None
                return posicao_anuncio_normal, pagina_normal, posicao_anuncio_full, pagina_full


def slack_notificao(nome, sku, termo, pag_antiga, pag_nova):
    load_dotenv()

    client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])
    SLACK_CHANNEL_ID='C030X3UMR3M'
    
    if int(pag_antiga) > int(pag_nova):
        icon = ':white_check_mark:'
    else:
        icon = ':x:'
    
    message = f'MERCADO LIVRE! {icon}\n{nome} - {sku}\nPesquisa: {termo}\nMudou da página {pag_antiga} para a página {pag_nova}.'
    
    try:
        client.chat_postMessage(channel=SLACK_CHANNEL_ID, text=message)
    except SlackApiError as e:
        print("Error sending message: {}".format(e))
        

def main():
    # Django Utils
    import os
    import django
    import sys
    from django.db.models import Min

    sys.path.append(str(BASE_DIR))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dagg.settings')
    django.setup()
    
    from trackeamento.models import MetricasMercadoLivre
    
    # Obtem access token
    ACCESS_TOKEN = reflash.refreshToken()
    
    # Header
    header = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    
    lista_mercadolivre = MetricasMercadoLivre.objects.values('termo_busca', 'mlb_anuncio').annotate(sku_min=Min('mlb_anuncio'))
    print(f'ATUALIZANDO TRACKEAMENTO DE {len(lista_mercadolivre)} PRODUTOS MERCADOLIVRE')
    
    # Obtendo dia de ontem
    ontem = datetime.now() - timedelta(days=1)
    data_ontem = ontem.strftime('%Y-%m-%d')
    
    # Percorrendo cada MLB unicos cadastrado 
    for indice, anuncio in enumerate(lista_mercadolivre):
        print(f'{indice+1}/{len(lista_mercadolivre)} - {anuncio["mlb_anuncio"]}')
        termo_busca = anuncio['termo_busca']
        mlb_anuncio = anuncio['mlb_anuncio']

        # Visitas
        visitas_totais = requests.get(f"https://api.mercadolibre.com/visits/items?ids={mlb_anuncio}", headers=header).json().get(mlb_anuncio)

        # Nome / Pontuação Anúncio / Criação Anúncio
        response = requests.get(f"https://api.mercadolibre.com/items/{mlb_anuncio}?include_attributes=all", headers=header).json()
        titulo = response['title']
        pontuacao_anuncio = response['health']
        criacao_anuncio = response['date_created']
        dt = datetime.fromisoformat(criacao_anuncio[:-1])
        criacao_anuncio = dt.strftime("%Y-%m-%d %H:%M:%S")
        vendas_anuncio = response['sold_quantity']

        # Vende a cada visita / Conversao
        if vendas_anuncio > 0:
            taxa_conversao_total = round((vendas_anuncio / visitas_totais) * 100,2)
            vende_a_cada_visita = round(visitas_totais / vendas_anuncio , 1)
        else:
            taxa_conversao_total = 0
            vende_a_cada_visita = 0
        
            
        # Visita Diaria / Vendas Diaria / Taxa Conversao Diaria
        visitas_diaria = requests.get(f"https://api.mercadolibre.com/items/{mlb_anuncio}/visits/time_window?last=1&unit=day", headers=header).json().get('total_visits')
        vendas_diaria = requests.get(f'https://api.mercadolibre.com/orders/search?seller=195279505&item={mlb_anuncio}&order.status=paid&order.date_created.from={data_ontem}T00:00:00.000-00:00', headers=header).json().get('paging').get('total')
        taxa_conversao_diaria = round((vendas_diaria / visitas_diaria) * 100, 2)

        # Posição do Anúncio
        posicao_anuncio_normal, pagina_normal, posicao_anuncio_full, pagina_full = posicao_produtos_mercadolivre(termo_busca, mlb_anuncio)

        # Salvando no banco de dados
        novo_registro_meli = MetricasMercadoLivre()
        novo_registro_meli.nome = titulo
        novo_registro_meli.termo_busca = termo_busca
        novo_registro_meli.mlb_anuncio = mlb_anuncio
        novo_registro_meli.posicao = posicao_anuncio_normal
        novo_registro_meli.pagina = pagina_normal
        novo_registro_meli.posicao_full = posicao_anuncio_full
        novo_registro_meli.pagina_full = pagina_full
        novo_registro_meli.visita_diaria = visitas_diaria
        novo_registro_meli.visita_total = visitas_totais
        novo_registro_meli.vendas_diaria = vendas_diaria
        novo_registro_meli.vendas_total = vendas_anuncio
        novo_registro_meli.vende_a_cada_visita = vende_a_cada_visita
        novo_registro_meli.taxa_conversao_diaria = taxa_conversao_diaria
        novo_registro_meli.taxa_conversao_total = taxa_conversao_total
        novo_registro_meli.pontuacao_anuncio = pontuacao_anuncio
        novo_registro_meli.criacao_anuncio = criacao_anuncio
        
        # Atualiza variacao
        ultimo_registro_pagina_normal = MetricasMercadoLivre.objects.filter(mlb_anuncio=mlb_anuncio).filter(termo_busca=termo_busca).last().pagina
        ultimo_registro_pagina_full = MetricasMercadoLivre.objects.filter(mlb_anuncio=mlb_anuncio).filter(termo_busca=termo_busca).last().pagina_full
        
        if ultimo_registro_pagina_normal != None and pagina_normal != None:
            if pagina_normal < ultimo_registro_pagina_normal or pagina_normal > ultimo_registro_pagina_normal:
                slack_notificao(titulo, mlb_anuncio, termo_busca, ultimo_registro_pagina_normal, pagina_normal)
        
        if ultimo_registro_pagina_full != None and pagina_full != None:
            if pagina_full < ultimo_registro_pagina_full or pagina_full > ultimo_registro_pagina_full:
                slack_notificao(titulo, mlb_anuncio, termo_busca, ultimo_registro_pagina_full, pagina_full)
        
        novo_registro_meli.save()