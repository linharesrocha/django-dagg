from scripts.connect_to_database import get_connection
import pyodbc
import warnings
import pandas as pd

def main(data_inicial_principal, data_final_principal, data_inicial_comparativo, data_final_comparativo):
    warnings.filterwarnings('ignore')
    connection = get_connection()
    conexao = pyodbc.connect(connection)
    
    # Carrega apenas pedidos Netshoes
    comando = '''
    SELECT A.PEDIDO, A.DESCRICAOPROD, A.COD_INTERNO, A.QUANT, A.COD_PEDIDO AS SKU, B.ORIGEM AS ORIGEM_ID, C.ORIGEM_NOME, B.DATA
    FROM PEDIDO_MATERIAIS_ITENS_CLIENTE A
    LEFT JOIN PEDIDO_MATERIAIS_CLIENTE B ON A.PEDIDO = B.PEDIDO
    LEFT JOIN ECOM_ORIGEM C ON B.ORIGEM = C.ORIGEM_ID
    WHERE B.TIPO = 'PEDIDO'
    AND B.POSICAO != 'CANCELADO'
    AND B.ORIGEM IN ('2','3','4')
    '''

    # Preenchendo pedidos
    data_h = pd.read_sql(comando, conexao)
    data_h.drop('PEDIDO', axis=1, inplace=True)
    
    # Limpando valores com espaços vazios
    data_h['COD_INTERNO'] = data_h['COD_INTERNO'].str.strip()
    data_h['SKU'] = data_h['SKU'].str.strip()
    
    print(sum(data_h['QUANT']))
    print(data_h.columns)
    
    # Convertendo quantidade em mais uma linha de pedido
    data_h_aux = data_h[(data_h['QUANT'] > 1)]
    data_h_aux.loc[:, 'QUANT'] -= 1
    for i in range(len(data_h_aux)):
        descricao_prod = data_h_aux['DESCRICAOPROD'].iloc[i]
        cod_interno = data_h_aux['COD_INTERNO'].iloc[i]
        quantidade = int(data_h_aux['QUANT'].iloc[i])
        sku = data_h_aux['SKU'].iloc[i]
        origem = data_h_aux['ORIGEM_ID'].iloc[i]
        origem_nome = data_h_aux['ORIGEM_NOME'].iloc[i]
        data_venda = data_h_aux['DATA'].iloc[i]
        for j in range(quantidade):
            row1 = pd.Series([descricao_prod, cod_interno, 1, sku, origem, origem_nome, data_venda], index=data_h.columns)
            data_h = data_h._append(row1, ignore_index=True)
            
    