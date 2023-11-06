from pathlib import Path
import sys
from dotenv import load_dotenv
import os
import pandas as pd
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import pyodbc
from connect_to_database import get_connection

def main(): 
    connection = get_connection()
    conexao = pyodbc.connect(connection)
    
    load_dotenv()
    SLACK_CHANNEL_ID='C05FN0ZF0UB'
    client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])
    
    
    comando = f'''
    SELECT A.CODID, B.COD_INTERNO, B.DESCRICAO, SUM(A.QUANT) AS RESERVADOS, C.ESTOQUE
    FROM ESTOQUE_MKTP_WAIT A
    LEFT JOIN MATERIAIS B ON A.CODID = B.CODID
    LEFT JOIN ESTOQUE_MATERIAIS C ON C.MATERIAL_ID = A.CODID
    WHERE C.ARMAZEM = '1'
    GROUP BY A.CODID, B.COD_INTERNO, B.DESCRICAO, C.ESTOQUE
    '''
    
    df_reservados = pd.read_sql_query(comando, conexao)
    
    df_reservados_filtered = df_reservados[(df_reservados['ESTOQUE'] <= 10) & (df_reservados['RESERVADOS'] >= 5)]
    
    if df_reservados_filtered.shape[0] > 0:
        for index, row in df_reservados_filtered.iterrows():
            message = f'OLHAR RESERVADOS!\n{row["COD_INTERNO"]} - {row["DESCRICAO"]} - {row["RESERVADOS"]} reservados'
            
            try:
                response = client.chat_postMessage(
                    channel=SLACK_CHANNEL_ID,
                    text=message
                )
            except Exception as e:
                print(e)
    
main()