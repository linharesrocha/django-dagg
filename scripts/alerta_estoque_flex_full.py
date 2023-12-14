from connect_to_database import get_connection
import pyodbc
import pandas as pd
import warnings
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from pathlib import Path
import sys
import requests
import json
from dotenv import load_dotenv

# Settings ML
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
from mercadolivre.scripts.config import reflash
ACCESS_TOKEN = reflash.refreshToken()
header = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

def slack_notificao(cod_interno, sku, prodmktp_id, index):
    load_dotenv()

    client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])
    SLACK_CHANNEL_ID='C030X3UMR3M'

    message = f'INATIVAR FLEX! {index} :warning:\n{cod_interno}!  MLB: {sku} / PRODMKTP_ID: {prodmktp_id}'
    
    try:
        response = client.chat_postMessage(
            channel=SLACK_CHANNEL_ID,
            text=message
        )
    except SlackApiError as e:
        print("Error sending message: {}".format(e))
        

def main():
    warnings.filterwarnings('ignore')
    connection = get_connection()
    conexao = pyodbc.connect(connection)

    comando = f'''
    SELECT A.MATERIAL_ID, C.COD_INTERNO, A.SKU, PRODMKTP_ID, A.FLEX, B.ESTOQUE, C.INATIVO
    FROM ECOM_SKU A
    LEFT JOIN ESTOQUE_MATERIAIS B ON A.MATERIAL_ID = B.MATERIAL_ID
    LEFT JOIN MATERIAIS C ON A.MATERIAL_ID = C.CODID
    WHERE A.FLEX = 'A'
    AND B.ARMAZEM = '1'
    AND C.INATIVO = 'N'
    AND B.ESTOQUE <= '1'
    AND A.FULFILLMENT = 'S'
    ORDER BY MATERIAL_ID
    '''
    
    df_flex = pd.read_sql(comando, conexao)
    
    df_flex['COD_INTERNO'] = df_flex['COD_INTERNO'].str.strip()
    df_flex['SKU'] = df_flex['SKU'].str.strip()
    
    contador = 1
    for index, item in df_flex.iterrows():
        response = requests.get(f"https://api.mercadolibre.com/items/{item['SKU']}", headers=header).json()
        
        if response['variations'] == []:
            if item['PRODMKTP_ID'] == response['inventory_id'] and response['available_quantity'] > 0:
                slack_notificao(item['COD_INTERNO'], item['SKU'], item['PRODMKTP_ID'], contador)
                contador = contador + 1
        else:
            for variacoes in response['variations']:
                if item['PRODMKTP_ID'] == variacoes['inventory_id']:
                    if variacoes['available_quantity'] > 0:
                        slack_notificao(item['COD_INTERNO'], item['SKU'], item['PRODMKTP_ID'], contador)
                        contador = contador + 1

main()