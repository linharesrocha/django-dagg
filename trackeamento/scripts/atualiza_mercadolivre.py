import requests
from pathlib import Path
import sys
from dotenv import load_dotenv
from datetime import datetime
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os
from datetime import datetime, timedelta
from posicao_produtos_mercadolivre import main as posicao_produtos_mercadolivre


BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))
from mercadolivre.scripts.config import reflash


def start_atualiza_mercadolivre():
    slack = True
    main(slack)


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
        pagina = posicao_produtos_mercadolivre(termo_busca, mlb_anuncio)

        # Salvando no banco de dados
        novo_registro_meli = MetricasMercadoLivre()
        novo_registro_meli.nome = titulo
        novo_registro_meli.termo_busca = termo_busca
        novo_registro_meli.mlb_anuncio = mlb_anuncio
        novo_registro_meli.posicao = posicao_anuncio
        novo_registro_meli.pagina = pagina
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