import requests
from pathlib import Path
import sys
from dotenv import load_dotenv
import pyodbc
import os
from datetime import datetime
from datetime import datetime, timedelta
import pandas as pd
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from openpyxl.styles import Alignment, PatternFill, Font
from openpyxl.utils import get_column_letter
import json



BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

from mercadolivre.scripts.config import reflash
from scripts.connect_to_database import get_connection

def main():
    ACCESS_TOKEN = reflash.refreshToken()
    header = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

    list_id = []
    list_sale_fee = []
    list_pack_id = []
    list_unit_price = []
    list_paid_amount = []
    list_full_unit_price = []
    list_date_created = []
    list_mlb = []
    list_coupon_amount_divided = []
    list_shipping_cost_divided = []
    list_title = []
    list_category = []
    list_quantity_unit = []
    list_listing_type_id = []
    list_hiperlink = []
    list_campanha_bool = []

    # Cria a data
    hoje = datetime.now().date()
    debito_dias = hoje - timedelta(days=7)
    date_from_strf = debito_dias.strftime("%Y-%m-%d")

    # Get total orders
    response = requests.get(f"https://api.mercadolibre.com/orders/search?seller=195279505&order.status=paid&order.date_created.from={date_from_strf}T00:00:00.000-00:00&offset=0", headers=header).json()
    total_orders = response['paging']['total']

    offset = 0
    # Obtem todos os pedidos
    while offset < total_orders:
        
        # Consulta pedido
        for result in response['results']:
            
            # Settings variables
            quantity_itens = len(result['order_items'])
    
            # Consulta itens
            for item in result['order_items']:
                

                # Geral
                id_order = result['id']
                pack_id = result['pack_id']
                date_created = result['date_created']
                paid_amount = result['paid_amount']
                coupon_amount = result['coupon']['amount']
                coupon_amount_divided = coupon_amount / quantity_itens
                shipping_cost = result['shipping_cost']
                if shipping_cost is not None:
                    shipping_cost_divided = shipping_cost / quantity_itens
                else:
                    shipping_cost_divided = 0

                # Cria hiperlink
                hiperlink = f'https://www.mercadolivre.com.br/vendas/{id_order}/detalhe'
                list_hiperlink.append(hiperlink)
                
                # Item especifico
                sale_fee = item['sale_fee'] * quantity_itens
                mlb = item['item']['id']
                title = item['item']['title']
                category = item['item']['category_id']
                quantity = item['quantity']
                unit_price = item['unit_price']
                full_unit_price = item['full_unit_price']
                listing_type_id = item['listing_type_id']

                # Verifica se está em campanha
                if unit_price == full_unit_price:
                    list_campanha_bool.append('NÃO')
                else:
                    list_campanha_bool.append('SIM')

                list_id.append(id_order)
                list_sale_fee.append(sale_fee)
                list_pack_id.append(pack_id)
                list_unit_price.append(unit_price)
                list_full_unit_price.append(full_unit_price)
                list_date_created.append(date_created)
                list_mlb.append(mlb)
                list_paid_amount.append(paid_amount)
                list_coupon_amount_divided.append(coupon_amount_divided)
                list_shipping_cost_divided.append(shipping_cost_divided)
                list_title.append(title)
                list_category.append(category)
                list_quantity_unit.append(quantity)
                list_listing_type_id.append(listing_type_id)


        # Consulta todos os pedidos e consulta
        offset += 50
        response = requests.get(f"https://api.mercadolibre.com/orders/search?seller=195279505&order.status=paid&order.date_created.from={date_from_strf}T00:00:00.000-00:00&offset={offset}", headers=header).json()
    
    # Transforma em lista de strings
    list_id = [str(i) for i in list_id]
    list_pack_id = [str(i) for i in list_pack_id]

    # Replace palavra None por vazio em list_pack_id
    list_pack_id = [i.replace('None', '') for i in list_pack_id]

    # Adiciona as listas em DF
    df = pd.DataFrame({
                       'DATA': list_date_created,
                       'ID': list_id, 
                       'PACK_ID': list_pack_id, 
                       'MLB': list_mlb,
                       'TITULO': list_title,
                       'QUANTIDADE': list_quantity_unit,
                       'CATEGORIA': list_category,
                       'TIPO ANUNCIO': list_listing_type_id,
                       'PREÇO': list_full_unit_price,
                       'PREÇO CAMPANHA': list_unit_price,
                       'CAMPANHA': list_campanha_bool,
                       'VLR TOTAL NOTA': list_paid_amount,
                       'TAXA': list_sale_fee, 
                       'CUPOM': list_coupon_amount_divided,
                       'FRETE': list_shipping_cost_divided,
                       'LINK': list_hiperlink
                       })
    

    # Format the DATA column to the desired format
    df['DATA'] = pd.to_datetime(df['DATA'])
    df['DATA'] = df['DATA'].dt.strftime('%d-%m-%Y %H:%M:%S')

    # Renomeia valores TIPO ANUNCIO
    df.loc[df['TIPO ANUNCIO'] == 'gold_especial', 'TIPO ANUNCIO'] = 'CLÁSSICO'
    df.loc[df['TIPO ANUNCIO'] == 'gold_pro', 'TIPO ANUNCIO'] = 'PREMIUM'

    # Planilha aton
    connection = get_connection()
    conexao = pyodbc.connect(connection)
    cursor = conexao.cursor()

    comando = f'''
    SELECT B.CODID, B.COD_INTERNO, B.DESCRICAO, B.VLR_CUSTO, A.SKU AS MLB
    FROM ECOM_SKU A
    LEFT JOIN MATERIAIS B ON A.MATERIAL_ID = B.CODID
    LEFT JOIN ECOM_ORIGEM C ON A.ORIGEM_ID = C.ORIGEM_ID
    WHERE C.API = 'Mercado Livre'
    ORDER BY CODID
    '''

    df_aton = pd.read_sql(comando, conexao)

    # Limpa valores com espaços vazios
    df_aton['MLB'] = df_aton['MLB'].str.strip()
    df_aton['COD_INTERNO'] = df_aton['COD_INTERNO'].str.strip()
    df_aton['DESCRICAO'] = df_aton['DESCRICAO'].str.strip()

    # fecha conexão
    cursor.close()
    conexao.close()

    # merge
    df_completo = pd.merge(df, df_aton, on=['MLB'], how='left')

    # Adiciona coluna IMPOSTO e OPERAÇÃO com valor 10
    df_completo['IMPOSTO'] = 10
    df_completo['OPERAÇÃO'] = 10

    # altera ordem das colunas
    df_completo = df_completo[['CODID', 'COD_INTERNO', 'ID', 'PACK_ID', 'MLB', 'DESCRICAO', 'TITULO', 'VLR_CUSTO', 'PREÇO', 'PREÇO CAMPANHA', 'CAMPANHA', 'VLR TOTAL NOTA',
                                'FRETE', 'DATA', 'QUANTIDADE', 'CATEGORIA', 'TIPO ANUNCIO', 'IMPOSTO', 'OPERACAO', 'TAXA', 'CUPOM', 'LINK']]

    # Exporta em excel
    df_completo.to_excel('margem_mercadolivre.xlsx', index=False)
            
# def envia_slack():
#     hoje = datetime.now().date()
#     hoje_formatado = hoje.strftime("%d-%m-%Y")
        
#     # Envia slack
#     load_dotenv()

#     client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])
#     SLACK_CHANNEL_ID='C05FN11JCUB'
#     #SLACK_CHANNEL_ID='C045HEE4G7L'
    
#     message = f'MERCADO ADS! :money_mouth_face:'
    
#     # Send message
#     try:
#         client.chat_postMessage(channel=SLACK_CHANNEL_ID, text=message)
#     except SlackApiError as e:
#         print("Error sending message: {}".format(e))
        
#     # Send file
#     try:
#         client.files_upload_v2(channel=SLACK_CHANNEL_ID, file=path_metricas, filename=path_metricas)
#     except SlackApiError as e:
#         print("Error sending message: {}".format(e))
        
#     # Remove arquivo
#     try:
#         os.remove(path_metricas)
#     except Exception as e:
#         print(e)


main()