import pyodbc
import pandas as pd
import warnings
from datetime import date, timedelta
from dotenv import load_dotenv
from connect_to_database import get_connection
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

# Filtrando Warnings
warnings.filterwarnings('ignore')

connection = get_connection()
conexao = pyodbc.connect(connection)
cursor = conexao.cursor()

# DAGG
DAGG_COMISSAO_PADRAO = 21
DAGG_ACRESCIMO_COMISSAO = 6
DAGG_DESCONTO_CAMPANHA = 6

# RED PLACE
RED_COMISSAO_PADRAO = 21
RED_ACRESCIMO_COMISSAO = 0
RED_DESCONTO_CAMPANHA = 6

# PISSTE
PISSTE_COMISSAO_PADRAO = 21
PISSTE_ACRESCIMO_COMISSAO = 6
PISSTE_DESCONTO_CAMPANHA = 6

# PADRAO
TARIFA_FIXA = 3 # PEDIDO ACIMA DE R$10,00
OPERACAO = 10
IMPOSTO = 10

comando = f'''
SELECT A.CODID, A.COD_INTERNO, B.SEUPEDIDO AS PEDIDO, A.EMPRESA, A.DESCRICAOPROD AS TITULO, VLR_CUSTO, VLR_UNIT AS VLR_PEDIDO, B.VLRFRETE AS VLR_FRETE, DATA
FROM PEDIDO_MATERIAIS_ITENS_CLIENTE A
LEFT JOIN PEDIDO_MATERIAIS_CLIENTE B ON A.PEDIDO = B.PEDIDO
WHERE B.TIPO = 'PEDIDO'
AND B.POSICAO != 'CANCELADO'
AND B.ORIGEM IN ('2', '3', '4')
AND B.DATA >= DATEADD(DAY, DATEDIFF(DAY, 0, GETDATE()) - 1, 0)
AND B.DATA < DATEADD(DAY, DATEDIFF(DAY, 0, GETDATE()), 0)
ORDER BY A.EMPRESA, DATA
'''

df = pd.read_sql(comando, conexao)

# Remove espaço da coluna TITULO
df['TITULO'] = df['TITULO'].str.strip()
df['COD_INTERNO'] = df['COD_INTERNO'].str.strip()
df['PEDIDO'] = df['PEDIDO'].str.strip()

df['QUANTIDADE_PED'] = df.groupby(['EMPRESA', 'PEDIDO'])['PEDIDO'].transform('count')

# Arrendonda coluna VLR_PEDIDO para 2 casas decimais
df['VLR_PEDIDO'] = round(df['VLR_PEDIDO'], 2)

# Adiciona coluna VLR_TOTAL
df['VLR_TOTAL'] = df['VLR_PEDIDO'] + df['VLR_FRETE']

# Coloca a coluna VLR_TOTAL depois do VLR_FRETE
df = df[['CODID', 'COD_INTERNO', 'PEDIDO', 'EMPRESA', 'TITULO', 'VLR_CUSTO', 'VLR_PEDIDO', 'VLR_FRETE', 'VLR_TOTAL', 'DATA', 'QUANTIDADE_PED']]

# Modifica VLR_FRETE
df['VLR_FRETE'] = (df['VLR_FRETE'] / df['QUANTIDADE_PED']).round(2)

# Adiciona coluna TARIFA FIXA para apenas os valores da coluna VLR_PEDIDO acima de R$10,00 se não 0
df['TARIFA_FIXA'] = df['VLR_PEDIDO'].apply(lambda x: TARIFA_FIXA if x > 10 else 0)

# Modifica TARIFICA_FIXA
df['TARIFA_FIXA'] = (df['TARIFA_FIXA'] / df['QUANTIDADE_PED']).round(2)

# Imposto Frete que sigifnica aba IMPOSSTO * VALOR DO FRETE
df['IMPOSTO_FRETE'] = (df['VLR_FRETE'] * (IMPOSTO / 100)).round(2)

# Adiciona coluna OPERACAO
df['OPERACAO'] = OPERACAO

# Adiciona coluna IMPOSTO
df['IMPOSTO'] = IMPOSTO

# Adiciona coluna COMISSAO_PADRAO mas diferenciando por empresa
df['COMISSAO_PADRAO'] = df['EMPRESA'].apply(lambda x: DAGG_COMISSAO_PADRAO if x == 1 else RED_COMISSAO_PADRAO if x == 2 else PISSTE_COMISSAO_PADRAO)

# Adiciona coluna ACRESCIMO_COMISSAO mas diferenciando por empresa
df['ACRESCIMO_COMISSAO'] = df['EMPRESA'].apply(lambda x: DAGG_ACRESCIMO_COMISSAO if x == 1 else RED_ACRESCIMO_COMISSAO if x == 2 else PISSTE_ACRESCIMO_COMISSAO)

# Adiciona coluna DESCONTO_CAMPANHA mas diferenciando por empresa
df['DESCONTO_CAMPANHA'] = df['EMPRESA'].apply(lambda x: DAGG_DESCONTO_CAMPANHA if x == 1 else RED_DESCONTO_CAMPANHA if x == 2 else PISSTE_DESCONTO_CAMPANHA)

# Adiciona coluna PORC_TOTAL que soma as colunas
df['PORC_TOTAL'] = df['OPERACAO'] + df['IMPOSTO'] + df['COMISSAO_PADRAO'] + df['ACRESCIMO_COMISSAO'] - df['DESCONTO_CAMPANHA']

# Calculo resto
df['PORC_TOTAL2'] = round(df['VLR_PEDIDO'] * (df['PORC_TOTAL'] / 100), 2)

# Lucro
df['LUCRO'] = round(df['VLR_PEDIDO'] - df['PORC_TOTAL2'] - df['TARIFA_FIXA'] - df['VLR_CUSTO'] - df['IMPOSTO_FRETE'], 2)

# Margem
df['MARGEM'] = round(df['LUCRO'] / df['VLR_PEDIDO'] * 100, 2)

# Altera coluna EMPRESA para nomes
df['EMPRESA'] = df['EMPRESA'].replace(1, 'DAGG')
df['EMPRESA'] = df['EMPRESA'].replace(2, 'RED PLACE')
df['EMPRESA'] = df['EMPRESA'].replace(3, 'PISSTE')

# Salve em excel com a data de ontem
name_file_excel = 'margem_netshoes_' + str(date.today() - timedelta(days=1)) + '.xlsx'


writer = pd.ExcelWriter(name_file_excel, engine='openpyxl')
df.to_excel(writer, sheet_name='NETSHOES', index=False)
#df.to_excel('teste-margem.xlsx', index=False)

worksheet = writer.sheets['NETSHOES']

# Adicionando filtros
worksheet.auto_filter.ref = "A1:T1"

# Congelando painel
worksheet.freeze_panes = 'A2'

writer._save()

# Envia slack
load_dotenv()

client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])
SLACK_CHANNEL_ID='C05FN0ZF0UB'

message = f'NETSHOES MARGEM! :heavy_division_sign:'

# Send message
try:
    client.chat_postMessage(channel=SLACK_CHANNEL_ID, text=message)
except SlackApiError as e:
    print("Error sending message: {}".format(e))
    
# Send file
try:
    client.files_upload_v2(channel=SLACK_CHANNEL_ID, file=name_file_excel, filename=name_file_excel)
except SlackApiError as e:
    print("Error sending message: {}".format(e))
    
writer.close()
    
# Remove arquivo
try:
    os.remove(name_file_excel)
except Exception as e:
    print(e)