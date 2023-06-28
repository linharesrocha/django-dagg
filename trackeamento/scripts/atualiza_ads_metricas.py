import requests
from pathlib import Path
import sys
from datetime import datetime
from datetime import datetime, timedelta
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

from mercadolivre.scripts.config import reflash
from trackeamento.models import MetricasAds

def main():
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
        

    # Percorre cada campanha
    for index, id in enumerate(ids_list):
        print(f"Campanha: {names_list[index]} - {index+1}/{len(ids_list)}")
        
        # Consulta os anúncios da campanha
        response = requests.get(f"https://api.mercadolibre.com/advertising/product_ads/ads/search?user_id=195279505&status=active&campaigns={id}", headers=header).json()

        # Percorre cada anúncio da campanha
        for result in response['results']:
            # Dados da campanha desse anúncio
            name_campanha = names_list[index]
            acos_campanha = target_take_rate_list[index]
    
            # Armazena os dados do anúncio
            mlb_anuncio = result['id']
            titulo = result['title']
            price = result['price']
            link = result['permalink']
            
            # Obtem as metricas do anúncio    
            response = requests.get(f"https://api.mercadolibre.com/advertising/product_ads_2/campaigns/{id}/ads/metrics?date_from={date_from}&date_to={date_to}&ids={mlb_anuncio}", headers=header).json()
            
            # Armazena as métricas do anúncio   
            clicks = response[0]['clicks']
            impressions = response[0]['impressions']
            cost = response[0]['cost']
            cpc = response[0]['cpc']
            ctr = response[0]['ctr']
            
            try:
                cvr = round(response[0]['sold_quantity_total'] / response[0]['clicks'] * 100, 1)
            except ZeroDivisionError:
                cvr = 0
                
            sold_quantity_total = response[0]['sold_quantity_total']
            amount_total = response[0]['amount_total']
            advertising_fee = response[0]['advertising_fee']
            organic_orders_quantity = response[0]['organic_orders_quantity']
            share = response[0]['share']
            
            # Armazena os dados no banco de dados
            novo_registro_ads = MetricasAds()
            novo_registro_ads.desde = date_from
            novo_registro_ads.ate = date_to
            novo_registro_ads.nome_campanha = name_campanha
            novo_registro_ads.acos_campanha = acos_campanha
            novo_registro_ads.mlb_anuncio = mlb_anuncio
            novo_registro_ads.titulo_anuncio = titulo
            novo_registro_ads.preco_anuncio = price
            novo_registro_ads.link_anuncio = link
            novo_registro_ads.clicks_anuncio = clicks
            novo_registro_ads.impressions_anuncio = impressions
            novo_registro_ads.cost_anuncio = cost
            novo_registro_ads.cpc_anuncio = cpc
            novo_registro_ads.ctr_anuncio = ctr
            novo_registro_ads.cvr_anuncio = cvr
            novo_registro_ads.sold_quantity_total_anuncio = sold_quantity_total
            novo_registro_ads.amount_total_anuncio = amount_total
            novo_registro_ads.advertising_fee_anuncio = advertising_fee
            novo_registro_ads.organic_orders_quantity_anuncio = organic_orders_quantity
            novo_registro_ads.share_anuncio = share
            novo_registro_ads.save()
            
            
main()