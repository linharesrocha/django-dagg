from pathlib import Path
import sys
from dotenv import load_dotenv
import os
import pandas as pd
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import pyodbc


BASE_DIR = Path(__file__).resolve().parent.parent.parent



def main():
    import django
    
    sys.path.append(str(BASE_DIR))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dagg.settings')
    django.setup()
    
    from trackeamento.models import UltimoProdutoCadastrado
    from scripts.connect_to_database import get_connection
    
    connection = get_connection()
    conexao = pyodbc.connect(connection)
    
    # Slack
    load_dotenv()
    SLACK_CHANNEL_ID='C030X3UMR3M'
    client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])
    autoid, mktp, sku, titulo, valor, cod_interno, message = None, None, None, None, None, None, None
    message = f'PRODUTO CADASTRADO!'
    
    # Obtem a primeira linha do UltimoProdutoCadastrado
    ultimo_produto_cadastrado = UltimoProdutoCadastrado.objects.first().autoid
    
    comando = f'''
    SELECT A.AUTOID, B.ORIGEM_NOME, A.SKU, A.TITULO, A.VALOR2, A.COD_INTERNO
    FROM PUBLICA_PRODUTO A
    LEFT JOIN ECOM_ORIGEM B ON A.ORIGEM_ID = B.ORIGEM_ID
    WHERE A.AUTOID > '{ultimo_produto_cadastrado}'
    '''
    
    df = pd.read_sql_query(comando, conexao)
    
    # Para programa caso nao tenha novos produtos cadastrados
    if df.empty:
        sys.exit()
    
    # Obtem o ultimo autoid
    ultimo_autoid = df['AUTOID'].max()
    
    # Remove com strip
    df['ORIGEM_NOME'] = df['ORIGEM_NOME'].str.strip()
    df['SKU'] = df['SKU'].str.strip()
    df['TITULO'] = df['TITULO'].str.strip()
    df['COD_INTERNO'] = df['COD_INTERNO'].str.strip()
        
    # Percorre df com iterrows
    for index, row in df.iterrows():
        mktp = row['ORIGEM_NOME']
        sku = row['SKU']
        titulo = row['TITULO']
        valor = 'R$' + str(row['VALOR2'])
        cod_interno = row['COD_INTERNO']
        
        message = f'PRODUTO CADASTRADO! :gear:\n{cod_interno} | {mktp} | {sku} | {valor}\n {titulo}'
        
        try:
            response = client.chat_postMessage(channel=SLACK_CHANNEL_ID, text=message)
        except SlackApiError as e:
            print("Error sending message: {}".format(e))
            
    
    # Atualiza na primeira linha do UltimoProdutoCadastrado o ultimo_autoid
    UltimoProdutoCadastrado.objects.filter(pk=1).update(autoid=ultimo_autoid)
        
    
main()