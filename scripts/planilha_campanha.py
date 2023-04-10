import os
from pathlib import Path
import pyodbc
import pandas as pd
import warnings
from datetime import datetime, date, timedelta
from io import BytesIO
from dotenv import load_dotenv


def carrega_tabela_produtos(conexao):
    comando = '''
    SELECT DISTINCT
    A.AUTOID, A.VLR_SITE2, A.VLR_SITE1, A.PRODMKTP_ID, A.SKU, A.SKUVARIACAO_MASTER, A.ATIVO, A.TIPO_ANUNCIO, A.ORIGEM_ID,
    B.INATIVO, B.CODID, B.COD_INTERNO,  B.PAI,B.DESCRICAO, B.VLR_CUSTO, B.PESO, B.COMPRIMENTO, B.LARGURA, B.ALTURA,
    C.ESTOQUE, 
    D.ORIGEM_NOME,
    E.DESCRICAO AS GRUPO,
    F.CATEG_MKTP_DESC AS DESCRICAON02, F.PRODUTO_TIPO, F.API,
    G.CATEG_ID, G.CATEG_NOME
    FROM ECOM_SKU A
    LEFT JOIN MATERIAIS B ON A.MATERIAL_ID = B.CODID
    LEFT JOIN ESTOQUE_MATERIAIS C ON B.CODID = C.MATERIAL_ID
    LEFT JOIN ECOM_ORIGEM D ON A.ORIGEM_ID = D.ORIGEM_ID
    LEFT JOIN GRUPO E ON B.GRUPO = E.CODIGO
    LEFT JOIN CATEGORIAS_MKTP F  ON F.CATEG_ATON = B.ECOM_CATEGORIA AND F.API = D.API
    LEFT JOIN ECOM_CATEGORIAS G ON G.CATEG_ID = B.ECOM_CATEGORIA
    WHERE C.ARMAZEM = 1
    AND B.INATIVO = 'N'
    ORDER BY CODID
    '''
    data = pd.read_sql(comando, conexao)
    
    # Limpando valores com espaços vazios
    data['COD_INTERNO'] = data['COD_INTERNO'].str.strip()
    data['DESCRICAO'] = data['DESCRICAO'].str.strip()
    data['ORIGEM_NOME'] = data['ORIGEM_NOME'].str.strip()
    data['SKU'] = data['SKU'].str.strip()

    return data

def carrega_tabela_pedidos(conexao):
    # Pedidos
    comando = '''
    SELECT A.PEDIDO, A.COD_INTERNO, A.QUANT, A.COD_PEDIDO AS SKU, A.EDICAO AS SKU2, B.ORIGEM AS ORIGEM_ID, B.DATA
    FROM PEDIDO_MATERIAIS_ITENS_CLIENTE A
    LEFT JOIN PEDIDO_MATERIAIS_CLIENTE B
    ON A.PEDIDO = B.PEDIDO
    WHERE B.TIPO = 'PEDIDO'
    AND B.POSICAO != 'CANCELADO'
    '''

    # Preenchendo pedidos
    data_h = pd.read_sql(comando, conexao)
    data_h.drop('PEDIDO', axis=1, inplace=True)
    
    # Limpando valores com espaços vazios
    data_h['COD_INTERNO'] = data_h['COD_INTERNO'].str.strip()
    data_h['SKU'] = data_h['SKU'].str.strip()
    data_h['SKU2'] = data_h['SKU2'].str.strip()
    
    return data_h

def manipula_colunas_sku_e_sku_variacao(data):
    # Preenche todos os valores vazios na coluna SKUVARIACAO_MASTER com o valor da mesma linha da coluna SKU
    data['SKUVARIACAO_MASTER'].fillna(data['SKU'], inplace=True)
    linhas_vazias = data.loc[data['SKUVARIACAO_MASTER'] == '']
    data.loc[linhas_vazias.index, 'SKUVARIACAO_MASTER'] = linhas_vazias['SKU']

    # Cria nova coluna com os valores da coluna SKU
    data['SKU_MESCLADO'] = data['SKU']

    # Passa para a coluna SKU_MESCLADO os valores de SKUVARIACAO_MASTER (ML, Shopee, B2W, Tray, Decathlon)
    data.loc[data['ORIGEM_ID'].isin([8,9,10]), 'SKU_MESCLADO'] = data['SKUVARIACAO_MASTER']
    return data

def adiciona_coluna_pai(data, conexao):
    # Juntar código pai
    comando = '''
    SELECT COD_INTERNO AS PAI_COD_INTERNO, CODID AS PAI FROM MATERIAIS
    WHERE PAI = '0'
    '''
    data_pai_aux = pd.read_sql(comando, conexao)
    data = pd.merge(data, data_pai_aux, on=['PAI'], how='left')
    data['PAI_COD_INTERNO'].fillna(data['COD_INTERNO'], inplace=True)
    
    return data

def adiciona_categoria_pai_magalu(data, conexao):
    # Juntar categoria pai da Magalu
    comando = '''
    SELECT A.IDNIVEL01, B.IDNIVEL02, A.API, A.DESCRICAON01, B.DESCRICAON02
    FROM ECOM_CATEGORIAN01 A
    LEFT JOIN ECOM_CATEGORIAN02 B
    ON A.IDNIVEL01 = B.IDNIVEL01
    '''
    data_categoria_magalu_tmp = pd.read_sql(comando, conexao)
    data_categoria_magalu_tmp['API'] = data_categoria_magalu_tmp['API'].str.strip()
    data_categoria_magalu_tmp['API'].replace('Integra', 'IntegraCommerce', inplace=True)
    data = pd.merge(data, data_categoria_magalu_tmp, on=['DESCRICAON02', 'API'], how='left')
    data.rename(columns = {'DESCRICAON02':'CATEGORIAS'}, inplace=True)
    
    return data

def adiciona_entrada_estoque(data, conexao):
    
    # Junta Entrada de Estoque (30, 60, 90)
    comando = '''
    SELECT DATA, COD_MATERIAL AS CODID, QUANT
    FROM KARDEX
    WHERE ES = 'E'
    AND TIPODOC = 'PEF'
    '''

    df_entrada_estoque = pd.read_sql(comando, conexao)
    data['ENTRADA_ESTQ_30'] = pd.to_datetime('today').normalize()
    data['ENTRADA_ESTQ_60'] = pd.to_datetime('today').normalize()
    data['ENTRADA_ESTQ_90'] = pd.to_datetime('today').normalize()
    for index, row in data.iterrows():
        codid = row['CODID']
        data_30 = row['ENTRADA_ESTQ_30']
        data_60 = row['ENTRADA_ESTQ_60']
        data_90 = row['ENTRADA_ESTQ_90']
        data_inicio_30 = data_30 - pd.Timedelta(days=30)
        data_inicio_60 = data_60 - pd.Timedelta(days=60)
        data_inicio_90 = data_90 - pd.Timedelta(days=90)
        df_filtered_30 = df_entrada_estoque[(df_entrada_estoque['CODID'] == codid) & (df_entrada_estoque['DATA'] >= data_inicio_30) & (df_entrada_estoque['DATA'] <= data_30)]
        df_filtered_60 = df_entrada_estoque[(df_entrada_estoque['CODID'] == codid) & (df_entrada_estoque['DATA'] >= data_inicio_60) & (df_entrada_estoque['DATA'] <= data_60)]
        df_filtered_90 = df_entrada_estoque[(df_entrada_estoque['CODID'] == codid) & (df_entrada_estoque['DATA'] >= data_inicio_90) & (df_entrada_estoque['DATA'] <= data_90)]
        data.loc[index, 'ENTRADA_ESTQ_30'] = df_filtered_30['QUANT'].sum()
        data.loc[index, 'ENTRADA_ESTQ_60'] = df_filtered_60['QUANT'].sum()
        data.loc[index, 'ENTRADA_ESTQ_90'] = df_filtered_90['QUANT'].sum()

    return data

def adiciona_pedidos(data_h):
    # A tabela de pedidos contém a coluna QUANT.
    # Esse código adiciona uma linha para cada número no QUANT, ex:
    # Se a linha tem o valor 3 na coluna QUANT, ele vai adicionar mais duas linhas com o mesmo número de pedido, 
    # ficando 3 linhas do mesmo pedido.
    # Servirá para fazer contabilização de pedidos. 
    data_h_aux = data_h[(data_h['QUANT'] > 1)]
    data_h_aux.loc[:, 'QUANT'] -= 1
    for i in range(len(data_h_aux)):
        cod_interno = data_h_aux['COD_INTERNO'].iloc[i]
        quantidade = int(data_h_aux['QUANT'].iloc[i])
        sku = data_h_aux['SKU'].iloc[i]
        sku2 = data_h_aux['SKU2'].iloc[i]
        origem = data_h_aux['ORIGEM_ID'].iloc[i]
        data_venda = data_h_aux['DATA'].iloc[i]
        for j in range(quantidade):
            row1 = pd.Series([cod_interno, 1, sku, sku2, origem, data_venda], index=data_h.columns)
            data_h = data_h._append(row1, ignore_index=True)

    return data_h

def manipula_sku_pedidos(data_h):
    # Colocando todos valores da coluna SKU2 na coluna SKU da Dafiti
    data_h.loc[data_h['ORIGEM_ID'].isin([5,6,7]), 'SKU'] = data_h['SKU2'].fillna(data_h['SKU'])

    # Coloca todos valroes da coluna SKU na coluna SK2 do Mercado Livre
    data_h.loc[data_h['ORIGEM_ID'].isin([8,9,10]), 'SKU2'] = data_h['SKU'].fillna(data_h['SKU2'])
    
    return data_h

def groupby_vendas_aton(data_h, data, date_30, date_90):
    # VENDAS ATON (COD INTERNO)
    # Fazendo o Groupby de 90 e 30 dias
    data_h_30 = data_h[(data_h['DATA'] >= date_30)]
    data_h_30 = data_h_30.groupby('COD_INTERNO').count()
    data_h_30 = data_h_30.reset_index()
    data_h_30.drop(['SKU', 'DATA'], axis=1, inplace=True)

    data_h_90 = data_h[(data_h['DATA'] >= date_90)]
    data_h_90 = data_h_90.groupby('COD_INTERNO').count()
    data_h_90 = data_h_90.reset_index()
    data_h_90.drop(['SKU', 'DATA'], axis=1, inplace=True)

    # Fazendo merge
    data_completo = pd.merge(data, data_h_30, on=['COD_INTERNO'], how='left')
    data_completo = pd.merge(data_completo, data_h_90, on=['COD_INTERNO'], how='left')

    # Renomeando colunas
    data_completo.drop(columns=['ORIGEM_ID'], axis=1, inplace=True)
    data_completo = data_completo.rename(columns={'QUANT_x': '30_ATON', 'QUANT_y': '90_ATON', 'VLR_SITE1': 'PRECO_DE', 'VLR_SITE2': 'PRECO_POR', 'ORIGEM_ID_x':'ORIGEM_ID'})

    # Colocando valor Zero para aqueles produtos Aton que não tiveram vendas
    data_completo['30_ATON'].fillna(0, inplace=True)
    data_completo['90_ATON'].fillna(0, inplace=True)
    
    return data_completo

def groupby_vendas_marketplace(data_h, data_completo, date_7, date_14, date_30, date_90):
    # VENDAS MARKETPLACE (SKU ANÚNCIO)
    # Fazendo o Groupby de 7 dias
    data_h_7_mktp = data_h[(data_h['DATA'] >= date_7)]
    data_h_7_mktp.loc[:, 'SKU_MESCLADO'] = data_h_7_mktp.apply(lambda x: x['SKU'] if pd.isnull(x['SKU2']) else x['SKU2'], axis=1).copy()
    data_h_7_mktp = data_h_7_mktp.drop(['SKU', 'SKU2', 'DATA'], axis=1)
    data_h_7_mktp = data_h_7_mktp.groupby(['SKU_MESCLADO','ORIGEM_ID']).count()
    data_h_7_mktp = data_h_7_mktp.reset_index()
    data_h_7_mktp.drop(columns=['COD_INTERNO'], axis=1, inplace=True)

    # Fazendo o Groupby de 14 dias
    data_h_14_mktp = data_h[(data_h['DATA'] >= date_14)]
    data_h_14_mktp.loc[:, 'SKU_MESCLADO'] = data_h_14_mktp.apply(lambda x: x['SKU'] if pd.isnull(x['SKU2']) else x['SKU2'], axis=1).copy()
    data_h_14_mktp = data_h_14_mktp.drop(['SKU', 'SKU2', 'DATA'], axis=1)
    data_h_14_mktp = data_h_14_mktp.groupby(['SKU_MESCLADO','ORIGEM_ID']).count()
    data_h_14_mktp = data_h_14_mktp.reset_index()
    data_h_14_mktp.drop(columns=['COD_INTERNO'], axis=1, inplace=True)

    # Fazendo o Groupby de 30 dias
    data_h_30_mktp = data_h[(data_h['DATA'] >= date_30)]
    data_h_30_mktp.loc[:, 'SKU_MESCLADO'] = data_h_30_mktp.apply(lambda x: x['SKU'] if pd.isnull(x['SKU2']) else x['SKU2'], axis=1).copy()
    data_h_30_mktp = data_h_30_mktp.drop(['SKU', 'SKU2', 'DATA'], axis=1)
    data_h_30_mktp = data_h_30_mktp.groupby(['SKU_MESCLADO','ORIGEM_ID']).count()
    data_h_30_mktp = data_h_30_mktp.reset_index()
    data_h_30_mktp = data_h_30_mktp.drop(columns=['COD_INTERNO'], axis=1)

    # Fazendo o Groupby de 90 dias
    data_h_90_mktp = data_h[(data_h['DATA'] >= date_90)]
    data_h_90_mktp.loc[:, 'SKU_MESCLADO'] = data_h_90_mktp.apply(lambda x: x['SKU'] if pd.isnull(x['SKU2']) else x['SKU2'], axis=1).copy()
    data_h_90_mktp =  data_h_90_mktp.drop(['SKU', 'SKU2', 'DATA'], axis=1)
    data_h_90_mktp = data_h_90_mktp.groupby(['SKU_MESCLADO','ORIGEM_ID']).count()
    data_h_90_mktp = data_h_90_mktp.reset_index()
    data_h_90_mktp.drop(columns=['COD_INTERNO'], axis=1, inplace=True)

    # Fazendo Merge
    data_completo = pd.merge(data_completo, data_h_7_mktp, on=['SKU_MESCLADO', 'ORIGEM_ID'], how='left')
    data_completo = pd.merge(data_completo, data_h_14_mktp, on=['SKU_MESCLADO', 'ORIGEM_ID'], how='left')
    data_completo.rename(columns = {'QUANT_x':'7_MKTP', 'QUANT_y':'14_MKTP'}, inplace=True)
    data_completo = pd.merge(data_completo, data_h_30_mktp, on=['SKU_MESCLADO', 'ORIGEM_ID'], how='left')
    data_completo = pd.merge(data_completo, data_h_90_mktp, on=['SKU_MESCLADO', 'ORIGEM_ID'], how='left')
    data_completo.rename(columns = {'QUANT_x':'30_MKTP', 'QUANT_y':'90_MKTP'}, inplace=True)

    # Preenchendo valores nan por 0
    data_completo['7_MKTP'].fillna(0, inplace=True)
    data_completo['14_MKTP'].fillna(0, inplace=True)
    data_completo['30_MKTP'].fillna(0, inplace=True)
    data_completo['90_MKTP'].fillna(0, inplace=True)
    
    return data_completo

def adiciona_horario(data_completo):
    # Colocando horário
    data_completo['HORARIO'] = datetime.now()
    
    return data_completo

def filtra_colunas(data_completo):
    data = data_completo
    data = data_completo[['CODID', 'COD_INTERNO', 'PAI_COD_INTERNO', 'SKU', 'SKUVARIACAO_MASTER', 'SKU_MESCLADO',
                        'PRODMKTP_ID', 'DESCRICAO', 'GRUPO', 'VLR_CUSTO', 'PESO',
                        'ESTOQUE', 'ENTRADA_ESTQ_30', 'ENTRADA_ESTQ_60', 'ENTRADA_ESTQ_90','30_ATON', '90_ATON', '7_MKTP','14_MKTP','30_MKTP','90_MKTP','ORIGEM_NOME', 'CATEGORIAS', 'PRODUTO_TIPO',
                        'COMPRIMENTO', 'LARGURA', 'ALTURA', 'TIPO_ANUNCIO', 'CATEG_ID', 'CATEG_NOME',
                        'PRECO_DE', 'PRECO_POR', 'HORARIO']]

    return data

def obtem_colunas_filtradas(data_completo, data):
    # Obtenha os nomes das colunas de cada DataFrame como conjuntos
    cols1 = set(data_completo.columns)
    cols2 = set(data.columns)
    diff_cols1 = cols1 - cols2
    #print('Colunas filtradas (não excluidas, apenas filtradas)')
    #print(diff_cols1)

def gerar_excel(data):
    
    excel_bytes = BytesIO()
    data.to_excel(excel_bytes, index=False)
  
    excel_bytes.seek(0)
    bytes_data = excel_bytes.getvalue()
    return bytes_data

def main_gerar_excel():
    load_dotenv()

    # Filtrando Warnings
    warnings.filterwarnings('ignore')

    # Banco de Dados
    env_path = Path('.') / '.env'
    load_dotenv(dotenv_path=env_path)
    DATABASE = os.environ['DATABASE']
    UID = os.environ['UID']
    PWD = os.environ['PWD']
    dados_conexao = ("Driver={SQL Server};"
                    "Server=erp.ambarxcall.com.br;"
                    "Database=" + DATABASE + ";"
                    "UID=" + UID + ";"
                    "PWD=" + PWD + ";")

    conexao = pyodbc.connect(dados_conexao)

    # Horário
    today = date.today()
    dt = date.today()
    datetime_midnight = datetime.combine(dt, datetime.min.time())
    date_7 = datetime_midnight - timedelta(7)
    date_14 = datetime_midnight - timedelta(14)
    date_30 = datetime_midnight - timedelta(30)
    date_90 = datetime_midnight - timedelta(90)

    #print('\n7 Dias: ' + str(date_7.strftime("%d-%m-%Y")))
    #print('14 Dias: ' + str(date_14.strftime("%d-%m-%Y")))
    #print('30 Dias: ' + str(date_30.strftime("%d-%m-%Y")))
    #print('90 Dias: ' + str(date_90.strftime("%d-%m-%Y")))

    #print('\nCarregando...')

    data = carrega_tabela_produtos(conexao)
    data_h = carrega_tabela_pedidos(conexao)
    data = manipula_colunas_sku_e_sku_variacao(data)
    data = adiciona_coluna_pai(data, conexao)
    data = adiciona_categoria_pai_magalu(data, conexao)
    data = adiciona_entrada_estoque(data, conexao)
    data_h = adiciona_pedidos(data_h)
    data_h = manipula_sku_pedidos(data_h)
    data_completo = groupby_vendas_aton(data_h, data, date_30, date_90)
    data_completo = groupby_vendas_marketplace(data_h, data_completo, date_7, date_14, date_30, date_90)
    data_completo = adiciona_horario(data_completo)
    data = filtra_colunas(data_completo)
    #obtem_colunas_filtradas(data_completo, data)
    bytes_data = gerar_excel(data)
    return bytes_data