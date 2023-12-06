import pyodbc
import pandas as pd
from pathlib import Path
import os
import sys

BASE_DIR = Path(__file__).resolve().parent.parent.parent

def main():
    import django
    sys.path.append(str(BASE_DIR))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dagg.settings')
    django.setup()

    from scripts.connect_to_database import get_connection

    connection = get_connection()
    conexao = pyodbc.connect(connection)
    cursor = conexao.cursor()

    # Pedidos
    comando = '''
    SELECT A.COD_INTERNO, A.QUANT, B.DATA
    FROM PEDIDO_MATERIAIS_ITENS_CLIENTE A
    LEFT JOIN PEDIDO_MATERIAIS_CLIENTE B
    ON A.PEDIDO = B.PEDIDO
    WHERE B.TIPO = 'PEDIDO'
    AND B.POSICAO != 'CANCELADO'
    AND B.DATA >= DATEADD(DAY, -30, GETDATE());
    '''

    # Preenchendo pedidos
    data_h = pd.read_sql(comando, conexao)

    # Limpando valores com espaços vazios
    data_h['COD_INTERNO'] = data_h['COD_INTERNO'].str.strip()


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
        data_venda = data_h_aux['DATA'].iloc[i]
        for j in range(quantidade):
            row1 = pd.Series([cod_interno, 1, data_venda], index=data_h.columns)
            data_h = data_h._append(row1, ignore_index=True)

    # Contabilizando pedidos
    data_h_30 = data_h.groupby('COD_INTERNO').count()
    data_h_30 = data_h_30.reset_index()
    data_h_30.drop(['DATA'], axis=1, inplace=True)

    # Filtra apenas pedidos com quantidade maior que 10
    data_h_30 = data_h_30[data_h_30['QUANT'] >= 10]

    #  Carrega produtos com estoque
    comando = f'''
    SELECT COD_INTERNO, DESCRICAO, B.ESTOQUE
    FROM MATERIAIS A
    LEFT JOIN ESTOQUE_MATERIAIS B ON A.CODID = B.MATERIAL_ID
    WHERE INATIVO = 'N'
    AND B.ARMAZEM = '1'
    '''

    data_produtos = pd.read_sql(comando, conexao)
    data_produtos['COD_INTERNO'] = data_produtos['COD_INTERNO'].str.strip()
    data_produtos['DESCRICAO'] = data_produtos['DESCRICAO'].str.strip()

    # Fazer merge entre os dois dataframes
    data = pd.merge(data_h_30, data_produtos, on='COD_INTERNO', how='left')

    # Se o estoque for menor ou igual as vendas dos ultimos 30 dias ai notifica
    data = data[data['ESTOQUE'] <= data['QUANT']]


    # Reordena colunas
    data = data[['COD_INTERNO', 'DESCRICAO', 'QUANT', 'ESTOQUE']]

    data.to_excel('result.xlsx', index=False)

main()