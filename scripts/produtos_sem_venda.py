import pandas as pd
import pyodbc
import pandas as pd
import warnings
import numpy as np
from scripts.connect_to_database import get_connection
from io import BytesIO

# Esse código pega o primeiro dia do mês anterior até o dia atual e verifica
# qual produto não teve venda nesse período.
# Retorna um arquivo Excel formatado.
def main():
    warnings.filterwarnings('ignore')
    connection = get_connection()
    conexao = pyodbc.connect(connection)

    comando = f'''
    SELECT B.CODID, B.COD_INTERNO, B.DESCRICAOPROD, A.PEDIDO, A.DATA
    FROM PEDIDO_MATERIAIS_CLIENTE A
    LEFT JOIN PEDIDO_MATERIAIS_ITENS_CLIENTE B
    ON A.PEDIDO = B.PEDIDO
    WHERE A.DATA > '2023-01-02'
    '''

    data_vendas = pd.read_sql(comando, conexao)


    comando = f'''
    SELECT CODID, COD_INTERNO, DESCRICAO, B.ESTOQUE, A.INATIVO
    FROM MATERIAIS A
    LEFT JOIN ESTOQUE_MATERIAIS B ON A.CODID = B.MATERIAL_ID
    WHERE COD_INTERNO NOT LIKE '%PAI'
    AND INATIVO = 'N'
    AND B.ARMAZEM = 1
    AND B.ESTOQUE = 0
    '''

    data_materiais = pd.read_sql(comando, conexao)

    not_in_data_vendas = ~data_materiais['CODID'].isin(data_vendas['CODID'])
    data = data_materiais.loc[not_in_data_vendas, :]
    data['CHECK'] = np.nan * np.empty(len(data))

    excel_bytes = BytesIO()
    data.to_excel(excel_bytes, index=False)
    excel_bytes.seek(0)
    bytes_data = excel_bytes.getvalue()
    
    return bytes_data