from scripts.connect_to_database import get_connection
import pyodbc
import warnings
import pandas as pd
from datetime import timedelta, datetime
import numpy as np
from io import BytesIO

def main(data_inicial_principal, data_final_principal, data_inicial_comparativo, data_final_comparativo):
    # Mantendo o formato do banco de dados
    formato_data = '%Y-%m-%d'
    
    # Adicionando mais um dia na data final devido ai filtro que não considera o dia de hoje porcausa das horas no dataframe    
    data_final_principal = datetime.strptime(data_final_principal, formato_data) + timedelta(days=1)
    data_final_comparativo = datetime.strptime(data_final_comparativo, formato_data) + timedelta(days=1)
    
    warnings.filterwarnings('ignore')
    connection = get_connection()
    conexao = pyodbc.connect(connection)
    
    # Carrega apenas pedidos Netshoes
    comando = '''
    SELECT A.QUANT, A.COD_PEDIDO AS SKU, B.ORIGEM AS ORIGEM_ID , B.DATA
    FROM PEDIDO_MATERIAIS_ITENS_CLIENTE A
    LEFT JOIN PEDIDO_MATERIAIS_CLIENTE B ON A.PEDIDO = B.PEDIDO
    WHERE B.TIPO = 'PEDIDO'
    AND B.POSICAO != 'CANCELADO'
    AND B.ORIGEM IN ('2','3','4')
    '''

    # Preenchendo pedidos
    data_h = pd.read_sql(comando, conexao)
    
    # Limpando valores com espaços vazios
    data_h['SKU'] = data_h['SKU'].str.strip()
    
    # Convertendo quantidade em mais uma linha de pedido
    data_h_aux = data_h[(data_h['QUANT'] > 1)]
    data_h_aux.loc[:, 'QUANT'] -= 1
    for i in range(len(data_h_aux)):
        quantidade = int(data_h_aux['QUANT'].iloc[i])
        sku = data_h_aux['SKU'].iloc[i]
        origem = data_h_aux['ORIGEM_ID'].iloc[i]
        data_venda = data_h_aux['DATA'].iloc[i]
        for j in range(quantidade):
            row1 = pd.Series([1, sku, origem, data_venda], index=data_h.columns)
            data_h = data_h._append(row1, ignore_index=True)
    
    # Renomeando coluna QUANT para VENDAS
    data_h.rename(columns={'QUANT':'VENDAS'}, inplace=True)
    
    # Filtrando a data do usuário e fazendo group by
    df_principal = data_h[(data_h['DATA'] >= data_inicial_principal) & (data_h['DATA'] <= data_final_principal)]
    df_principal_groupby = df_principal.groupby(['SKU','ORIGEM_ID']).count().reset_index().drop(['DATA'], axis=1)
    
    df_comparativo = data_h[(data_h['DATA'] >= data_inicial_comparativo) & (data_h['DATA'] <= data_final_comparativo)]
    df_comparativo_groupby = df_comparativo.groupby(['SKU','ORIGEM_ID']).count().reset_index().drop(['DATA'], axis=1)

    vendas_comparacao = df_principal_groupby.merge(df_comparativo_groupby, on=['SKU', 'ORIGEM_ID'], suffixes=('_PRINCIPAL', '_COMPARATIVO'))
    vendas_comparacao['DIFERENCA_VENDAS'] = vendas_comparacao['VENDAS_PRINCIPAL'] - vendas_comparacao['VENDAS_COMPARATIVO']
    vendas_comparacao['RESULTADO'] = np.where(vendas_comparacao['DIFERENCA_VENDAS'] > 0, 'AUMENTOU', np.where(vendas_comparacao['DIFERENCA_VENDAS'] == 0, 'MANTEVE', 'DIMINUIU'))
    vendas_comparacao['PORCENTAGEM'] = round((vendas_comparacao['DIFERENCA_VENDAS'] / vendas_comparacao['VENDAS_PRINCIPAL']) * 100, 2)
    
    # Alterando nomes da origem
    mapeamento = {2: 'MADZ', 3: 'LEAL', 4: 'PISSTE'}
    vendas_comparacao['ORIGEM_ID'] = vendas_comparacao['ORIGEM_ID'].replace(mapeamento)
    
    excel_bytes = BytesIO()
    vendas_comparacao.to_excel(excel_bytes, index=False)
    excel_bytes.seek(0)
    bytes_data = excel_bytes.getvalue()
    
    return bytes_data