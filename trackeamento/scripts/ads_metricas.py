import requests
from pathlib import Path
import sys
from datetime import datetime
from datetime import datetime, timedelta
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))
from mercadolivre.scripts.config import reflash
ACCESS_TOKEN = reflash.refreshToken()
header = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

# Obter a data de hoje e 7 dias atras
hoje = datetime.now().date()
ontem = hoje - timedelta(days=1)
sete_dias_atras = hoje - timedelta(days=7)
date_from = sete_dias_atras.strftime("%Y-%m-%d")
date_to = ontem.strftime("%Y-%m-%d")
date_from_br = sete_dias_atras.strftime("%d-%m-%Y")
date_to_br = ontem.strftime("%d-%m-%Y")

print(date_from, date_to)

# Consulta as campanhas ativas
response = requests.get(f"https://api.mercadolibre.com/advertising/product_ads_2/campaigns/search?user_id=195279505&status=active&limit=50", headers=header).json()

# Listas para armazenar dados das campanhas
ids_list = []
names_list = []
last_updated_list = []
date_created_list = []
bidding_strategy_list = []
status_list = []
target_take_rate_list = []

# Percorre cada campanha e extrai os dados
for result in response['results']:
    ids_list.append(result['id'])
    names_list.append(result['name'])
    last_updated_list.append(result['last_updated'])
    date_created_list.append(result['date_created'])
    bidding_strategy_list.append(result['bidding_strategy'])
    status_list.append(result['status'])
    target_take_rate_list.append(result['target_take_rate'])
    
# Lista para armazenar os dados dos anúncios
name_campanha = []
acos_campanha = []
mlbs_anuncios = []
titulo_anuncios = []
preco_anuncios = []
link_anuncios = []
clicks_anuncios = []
impressions_anuncios = []
cost_anuncios = []
cpc_anuncios = []
ctr_anuncios = []
cvr_anuncios = []
sold_quantity_total_anuncios = []
amount_total_anuncios = []
advertising_fee_anuncios = []
organic_orders_quantity_anuncios = []
share_anuncios = []




# Percorre cada campanha
for index, id in enumerate(ids_list):
    print(f"Campanha: {names_list[index]} - {index+1}/{len(ids_list)}")
    
    # Consulta os anúncios da campanha
    response = requests.get(f"https://api.mercadolibre.com/advertising/product_ads/ads/search?user_id=195279505&status=active&campaigns={id}", headers=header).json()

    # Percorre cada anúncio da campanha
    for result in response['results']:
        # Dados da campanha desse anúncio
        name_campanha.append(names_list[index])
        acos_campanha.append(target_take_rate_list[index])
 
        # Armazena os dados do anúncio
        mlb_anuncio = result['id']
        mlbs_anuncios.append(mlb_anuncio)
        titulo_anuncios.append(result['title'])
        preco_anuncios.append(result['price'])
        link_anuncios.append(result['permalink'])
        
        # Obtem as metricas do anúncio    
        response = requests.get(f"https://api.mercadolibre.com/advertising/product_ads_2/campaigns/{id}/ads/metrics?date_from={date_from}&date_to={date_to}&ids={mlb_anuncio}", headers=header).json()
        
        # Armazena as métricas do anúncio   
        clicks_anuncios.append(response[0]['clicks'])
        impressions_anuncios.append(response[0]['impressions'])
        cost_anuncios.append(response[0]['cost'])
        cpc_anuncios.append(response[0]['cpc'])
        ctr_anuncios.append(response[0]['ctr'])
        cvr_anuncios.append(round(response[0]['sold_quantity_total'] / response[0]['clicks'] * 100, 1))
        sold_quantity_total_anuncios.append(response[0]['sold_quantity_total'])
        amount_total_anuncios.append(response[0]['amount_total'])
        advertising_fee_anuncios.append(response[0]['advertising_fee'])
        organic_orders_quantity_anuncios.append(response[0]['organic_orders_quantity'])
        share_anuncios.append(response[0]['share'])
        
    

# Criando o dicionário dos dados
data = {
    'DESDE': date_from_br,
    'ATÉ': date_to_br,
    'CAMPANHA': name_campanha,
    'ACOS': acos_campanha,
    'MLB': mlbs_anuncios,
    'TÍTULO': titulo_anuncios,
    'PREÇO': preco_anuncios,
    'IMPRESSÕES': impressions_anuncios,
    'CLIQUES': clicks_anuncios,
    'CTR': ctr_anuncios,
    'CPC': cpc_anuncios,
    'CVR': cvr_anuncios,
    'CUSTO': cost_anuncios,
    'VENDAS_TOTAIS': sold_quantity_total_anuncios,
    'REC_TOTAL': amount_total_anuncios,
    'ACOS2': advertising_fee_anuncios,
    'PED VENDA ORG': organic_orders_quantity_anuncios,
    '% PUB/ORG': share_anuncios,
    'LINK': link_anuncios
}

# Criando o DataFrame
df = pd.DataFrame(data)


df.to_excel('test.xlsx', index=False)