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


BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))
from mercadolivre.scripts.config import reflash


def start_atualiza_mercadolivre():
    slack = True
    main(slack)
    
    
def posicao_produtos_mercadolivre(termo_busca, mlb_anuncio):
    # Global
    user_agent = 'Mozilla/5.0 (Windows; 10) Gecko/20100101 Firefox/88.0'
    
    termo_busca = 'joelheira ortopédica'
    mlb = 'MLB3278981070'
    
    # Controle
    pagina_normal = 1
    posicao_anuncio_normal = None
    mlbs = []
    mlb_found = False
    
    # Primeira página
    response = requests.get(f'https://lista.mercadolivre.com.br/{termo_busca}')
    
    # Página normal
    while True:
        print(pagina_normal)
        # Request
        soup = BeautifulSoup(response.content, 'html.parser')
        items = soup.find_all(class_='ui-search-layout__item')
        
        # Armazena mlb dos anúncios
        for item in items:
            form_class = item.find(class_='ui-search-bookmark')
            item_id = form_class.find('input', {'name': 'itemId'})['value']
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
            pagina_normal += 1
            paginacao = soup.find(class_='shops__pagination-link').get('href')
            response = requests.get(paginacao)
                
    # Controle
    pagina_full = 1
    posicao_anuncio_full = None
    mlbs = []
    mlb_found = False
    
    # Primeira página
    response = requests.get(f'https://lista.mercadolivre.com.br/{termo_busca}_Frete_Full')
    
    # Página Full
    while True:
        # Request
        soup = BeautifulSoup(response.content, 'html.parser')
        items = soup.find_all(class_='ui-search-layout__item')
        
        # Armazena mlb dos anúncios
        for item in items:
            form_class = item.find(class_='ui-search-bookmark')
            item_id = form_class.find('input', {'name': 'itemId'})['value']
            mlbs.append(item_id)

         
            if str(item_id) == str(mlb_anuncio):
                posicao_anuncio_full = mlbs.index(mlb_anuncio) + 1
                mlb_found = True
                break
        
        # Stop
        if mlb_found or pagina_full > 10:
            if posicao_anuncio_full == None:
                pagina_full = None
            return posicao_anuncio_normal, pagina_normal, posicao_anuncio_full, pagina_full
        else:
            pagina_full += 1
            paginacao = soup.find(class_='shops__pagination-link').get('href')
            response = requests.get(paginacao)


def slack_notificao(nome, sku, pag_antiga, pag_nova, concorrente):
    load_dotenv()

    client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])
    SLACK_CHANNEL_ID='C030X3UMR3M'

    if str(concorrente) == '1':
        concorrente = 'Anúncio Concorrente'
    else:
        concorrente = 'Anúncio Dagg'
    
    message = f'{nome} - {sku} - {concorrente}\nMudou da página {pag_antiga} para a página {pag_nova}.'
    
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
        # ultimo_registro_pagina = MetricasMercadoLivre.objects.filter(mlb_anuncio=mlb_anuncio).last().pagina
        
        # envia_notificacao = False
        # if ultimo_registro_pagina == None:
        #     novo_registro_meli.variacao = 'Manteve'
        # elif pagina < ultimo_registro_pagina:
        #     novo_registro_meli.variacao = 'Melhorou' 
        #     envia_notificacao = True
        # elif pagina > ultimo_registro_pagina:
        #     novo_registro_meli.variacao = 'Piorou'
        #     envia_notificacao = True
        # else:
        #     novo_registro_meli.variacao = 'Manteve'
        
        # # Verifica se o script foi rodado a partir do crontab e não do usuário
        # if slack == True:
        #     # Verifica se houve mudança de página
        #     if envia_notificacao == True:
        #         pass
        
        
        novo_registro_meli.save()