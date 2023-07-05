import requests
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
    
    from trackeamento.models import PedidosCompra
    from scripts.connect_to_database import get_connection
    
    dados = {
        'COD_INTERNO': [],
        'DESCRICAO': [],
        'VLR_CUSTO_ANTIGO': [],
    }
    
    pedidos = PedidosCompra.objects.all()
    
    for pedido in pedidos:
        dados['COD_INTERNO'].append(pedido.cod_interno)
        dados['DESCRICAO'].append(pedido.descricao)
        dados['VLR_CUSTO_ANTIGO'].append(pedido.vlr_custo_antigo)
    
    connection = get_connection()
    conexao = pyodbc.connect(connection)
    cursor = conexao.cursor()
    
    comando = '''
    SELECT B.COD_INTERNO, DESCRICAOPROD AS DESCRICAO, B.VLR_CUSTO AS VLR_CUSTO_ANTIGO
    FROM PEDIDO_MATERIAIS_ITENS A
    LEFT JOIN MATERIAIS B ON A.COD_INTERNO = B.COD_INTERNO
    WHERE STATUS = 'N'
    AND POSENT = 'PENDENTE'
    '''
    
    df_pedidos_compra_pendente = pd.read_sql(comando, conexao)
    df_pedidos_banco_de_dados = pd.DataFrame(dados)
    
    df_interno_nao_presente_no_bd = df_pedidos_compra_pendente[~df_pedidos_compra_pendente['COD_INTERNO'].isin(df_pedidos_banco_de_dados['COD_INTERNO'])]
    
    # Salva no banco de dados
    for index, row in df_interno_nao_presente_no_bd.iterrows():
        PedidosCompra.objects.create(
            cod_interno=row['COD_INTERNO'],
            descricao=row['DESCRICAO'],
            vlr_custo_antigo=row['VLR_CUSTO_ANTIGO']
        )
        

    df_interno_finalizados = df_pedidos_banco_de_dados[~df_pedidos_banco_de_dados['COD_INTERNO'].isin(df_pedidos_compra_pendente['COD_INTERNO'])]
    
    if len(df_interno_finalizados) > 0:
        
        load_dotenv()

        client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])
        SLACK_CHANNEL_ID='C030X3UMR3M'
        
        
        # Envia para o slack
        for index, row in df_interno_finalizados.iterrows():
            cod_interno = row['COD_INTERNO']
            cod_interno_strip = cod_interno.strip()
            descricao = row['DESCRICAO'].strip()
            vlr_custo_antigo = str(row['VLR_CUSTO_ANTIGO']).strip()
            
            comando = f'''
            SELECT VLR_CUSTO
            FROM MATERIAIS
            WHERE COD_INTERNO = '{cod_interno_strip}'
            '''
            
            vlr_custo_novo = str(pd.read_sql(comando, conexao).values[0][0]).strip()
            
            message = f'ALTERAÇÃO DE CUSTO! :currency_exchange:\nDESCRIÇÃO: {descricao}\nCOD_INTERNO: {cod_interno_strip}\nAlterado de R$ {vlr_custo_antigo} para R$ {vlr_custo_novo}\n'
                
            try:
                client.chat_postMessage(channel=SLACK_CHANNEL_ID,text=message)
            except SlackApiError as e:
                print("Error sending message: {}".format(e))
            
            # Envia foto
            comando = f'''
            SELECT TOP 1 URL, B.COD_INTERNO FROM MATERIAIS_IMAGENS A
            LEFT JOIN MATERIAIS B ON A.CODID = B.CODID
            WHERE B.COD_INTERNO = '{cod_interno_strip}'
            '''
                
            df_url_imagem = pd.read_sql(comando, conexao)
            
            if len(df_url_imagem) > 0:
                url_imagem = df_url_imagem['URL'][0]

                if not url_imagem.startswith('http://') and not url_imagem.startswith('https://'):
                    url_imagem = 'https://' + url_imagem
                    
                # Baixa a imagem para upload no slack
                response = requests.get(url_imagem)
                if response.status_code == 200:
                    with open(f'imagem.jpg', 'wb') as arquivo:
                        arquivo.write(response.content)
                    
                    # Envia para o slack
                    try:
                        client.files_upload_v2(channel=SLACK_CHANNEL_ID, file=f'imagem.jpg')
                    except SlackApiError as e:
                        print("Error sending message: {}".format(e))
                        
                    # Remove imagem
                    os.remove('imagem.jpg')


            # Apaga do banco de dados
            PedidosCompra.objects.filter(cod_interno=cod_interno).delete()