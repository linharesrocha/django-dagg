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
    
    from trackeamento.models import UltimoProdutoCadastradoAton
    from scripts.connect_to_database import get_connection
    
    connection = get_connection()
    conexao = pyodbc.connect(connection)
    
    # Slack
    load_dotenv()
    SLACK_CHANNEL_ID='C030X3UMR3M'
    client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])
    codid, descricao, cod_interno = None, None, None
    
    # Obtem a primeira linha do UltimoProdutoCadastrado
    ultimo_produto_cadastrado = UltimoProdutoCadastradoAton.objects.first().codid
    
    comando = f'''
    SELECT CODID, DESCRICAO, COD_INTERNO, PAI
    FROM MATERIAIS
    WHERE CODID > '{ultimo_produto_cadastrado}'
    '''
    
    df = pd.read_sql_query(comando, conexao)
    
    # Para programa caso nao tenha novos produtos cadastrados
    if df.empty:
        sys.exit()
    
    # Obtem o ultimo autoid
    ultimo_codid = df['CODID'].max()
    
    # Remove com strip
    df['DESCRICAO'] = df['DESCRICAO'].str.strip()
    df['COD_INTERNO'] = df['COD_INTERNO'].str.strip()
        
    # Percorre df com iterrows
    for index, row in df.iterrows():
        codid = row['CODID']
        descricao = row['DESCRICAO']
        cod_interno = row['COD_INTERNO']
        pai = row['PAI']
        
        if pai == 0:
            message = f'PRODUTO CADASTRADO NO ATON! :gear:\n{codid} | {cod_interno}\n{descricao}'
        else:
            message = f'PRODUTO CADASTRADO NO ATON! :gear:\n{codid} | {cod_interno} | PAI: {pai}\n{descricao}'
        
        try:
            response = client.chat_postMessage(channel=SLACK_CHANNEL_ID, text=message)
        except SlackApiError as e:
            print("Error sending message: {}".format(e))
            
    
    # Atualiza na primeira linha do UltimoProdutoCadastrado o ultimo_autoid
    UltimoProdutoCadastradoAton.objects.filter(pk=1).update(codid=ultimo_codid)
        
    
main()