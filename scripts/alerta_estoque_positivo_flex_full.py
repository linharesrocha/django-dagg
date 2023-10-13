from connect_to_database import get_connection
import pyodbc
import pandas as pd
import warnings
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
from pathlib import Path
import requests
import sys
import json

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

    message = f'ATIVAR FLEX! {index} :white_check_mark:\n{cod_interno}!  MLB: {sku} / PRODMKTP_ID: {prodmktp_id}'
    
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
    SELECT A.MATERIAL_ID, C.DESCRICAO, C.COD_INTERNO, A.SKU, PRODMKTP_ID, A.FLEX, B.ESTOQUE, C.INATIVO, C.PAI
    FROM ECOM_SKU A
    LEFT JOIN ESTOQUE_MATERIAIS B ON A.MATERIAL_ID = B.MATERIAL_ID
    LEFT JOIN MATERIAIS C ON A.MATERIAL_ID = C.CODID
    WHERE A.FLEX = 'S'
    AND B.ARMAZEM = '1'
    AND C.INATIVO = 'N'
    AND B.ESTOQUE > '1'
    AND A.FULFILLMENT = 'S'
    ORDER BY MATERIAL_ID
    '''

    df_flex = pd.read_sql(comando, conexao)
    
    df_flex['COD_INTERNO'] = df_flex['COD_INTERNO'].str.strip()
    df_flex['SKU'] = df_flex['SKU'].str.strip()
    df_flex.drop_duplicates(subset="SKU", keep="first", inplace=True)

    
    contador = 1
    for index, item in df_flex.iterrows():

        # Consulta estoque de todos os filhos
        comando = f'''
        SELECT DESCRICAO, CODID, B.ESTOQUE, PRODMKTP_ID
        FROM MATERIAIS A
        LEFT JOIN ESTOQUE_MATERIAIS B ON A.CODID = B.MATERIAL_ID
        LEFT JOIN ECOM_SKU C ON A.CODID = C.MATERIAL_ID
        WHERE PAI = '{item['PAI']}'
        AND B.ARMAZEM = '1'
        AND A.INATIVO = 'N'
        AND ORIGEM_ID = '8'
        AND C.FLEX = 'S'
        AND C.FULFILLMENT = 'S'
        '''
        
        df_all_variations = pd.read_sql(comando, conexao)
        
        response = requests.get(f"https://api.mercadolibre.com/items/{item['SKU']}", headers=header).json()
        
        # Verifica se cada variação, o estoque do Full é maior que 0 e se o estoque principal é menor ou igual a 0, caso verdadeiro break caso falso envia slack
        envia_notificacao = True
        for variacao in response['variations']:
            
            # Coleta inventory_id
            inventory_id = variacao['inventory_id']
            
            # Coleta estoque do df_all_variations baseado no inventory_id
            estoque_principal = int(df_all_variations[df_all_variations['PRODMKTP_ID'] == inventory_id]['ESTOQUE'].values[0])
            
            # Coleta estoque do Full
            estoque_full = int(variacao['available_quantity'])
            
            if estoque_full > 0 and estoque_principal <= 1:
                envia_notificacao = False
                break
                
        if envia_notificacao == True:
            slack_notificao(item['COD_INTERNO'], item['SKU'], item['PRODMKTP_ID'], contador)
            contador = contador + 1

main()