from connect_to_database import get_connection
import pyodbc
import pandas as pd
import warnings
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

def slack_notificao(cod_interno, sku, prodmktp_id, estoque, index, tamanho_df):
    load_dotenv()

    client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])
    SLACK_CHANNEL_ID='C045HEE4G7L'

    message = f'FLEX! {index}/{tamanho_df}\n{cod_interno} está com {estoque} estoque!  MLB: {sku} / PRODMKTP_ID: {prodmktp_id}'
    
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
    ORDER BY MATERIAL_ID
    '''

    df_flex = pd.read_sql(comando, conexao)
    
    df_flex['COD_INTERNO'] = df_flex['COD_INTERNO'].str.strip()
    df_flex['SKU'] = df_flex['SKU'].str.strip()

    for index, item in df_flex.iterrows():
        slack_notificao(item['COD_INTERNO'], item['SKU'], item['PRODMKTP_ID'], int(item['ESTOQUE']), index+1, len(df_flex))
        
main()