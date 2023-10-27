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
    SELECT A.AUTOID, B.ORIGEM_NOME, A.SKU, A.TITULO, A.VALOR2, A.COD_INTERNO, SKURETORNO, A.ORIGEM_ID
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
    df['SKURETORNO'] = df['SKURETORNO'].str.strip()
        
    # Percorre df com iterrows
    for index, row in df.iterrows():
        mktp = row['ORIGEM_NOME']
        sku = row['SKU']
        titulo = row['TITULO']
        valor = 'R$' + str(row['VALOR2'])
        cod_interno = row['COD_INTERNO']
        origem_id = str(row['ORIGEM_ID'])
        
        if origem_id == '8' or origem_id == '9' or origem_id == '10':
            sku_retorno = row['SKURETORNO']
            message = f'PRODUTO PUBLICADO! :arrow_upper_right:\n{cod_interno} | {mktp} | {sku} | {sku_retorno} | {valor}\n {titulo}'
        else:
            message = f'PRODUTO PUBLICADO! :arrow_upper_right:\n{cod_interno} | {mktp} | {sku} | {valor}\n {titulo}'
        
        try:
            response = client.chat_postMessage(channel=SLACK_CHANNEL_ID, text=message)
        except SlackApiError as e:
            print("Error sending message: {}".format(e))
            
    
    # Atualiza na primeira linha do UltimoProdutoCadastrado o ultimo_autoid
    UltimoProdutoCadastrado.objects.filter(pk=1).update(autoid=ultimo_autoid)
        
    
main()