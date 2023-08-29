import pyodbc
import pandas as pd
import warnings
from connect_to_database import get_connection


warnings.filterwarnings('ignore')
connection = get_connection()
conexao = pyodbc.connect(connection)
cursor = conexao.cursor()

df_amazon = pd.read_excel('C:\\workspace\\django-dagg\\scripts\\amazon_skus.xlsx')

# obtem codid  e sku do df
for index, row in df_amazon.iterrows():
    codid = row['MATERIAL_iD']
    sku_amazon = row['SKU'] + '_FBA'

    # Valores a serem inseridos
    valores = [
        [codid, 8, sku_amazon, None, None, None, None, None, 0, None,  None, None, 35, None, None, None, None, None, None, None, 'S', None, None, 0, None, 0, 0, 'N', 0, 0, 0, 0, None, 0, 0, None, None, 0, None, 0, None, 0, 0, None, None, None, None, 0, None, None]
    ]

    # Colunas
    colunas = [
        'MATERIAL_ID', 'ECOM_ID', 'SKU', 'ID_SKU', 'VLR_SITE1', 'VLR_SITE2', 'TITULO', 'TEXTO', 'ESTOQUE', 'EAN', 'ATIVO', 'EXISTE',
        'ORIGEM_ID', 'TIPO_ANUNCIO', 'TIPO_ENVIO', 'STCODE', 'RETORNO', 'LINKURL', 'PRODMKTP_ID', 'BUYBOX', 'ATUALIZA',
        'CROSSDOCKING', 'SKUVARIACAO_MASTER', 'MARGEM', 'UPDT', 'CUSTO_ADICIONAL', 'ARMAZEM', 'FULFILLMENT', 'COMISSAO_SKU',
        'VLR_CUSTO', 'CUSTO_FRETE', 'MARGEM_MAX', 'DESCARTE', 'DESCONTO_VLR', 'IMPOUTRAS', 'CD_TIPO', 'CD_MODELO', 'LEVELSKU',
        'CD_ID', 'ESTOQUE_ND', 'CATALOGO', 'PRICE_BEST', 'REBATE', 'MSHOPS', 'DTCRIACAO', 'UPDSTOCKFULL', 'FLEX', 'VLR_SITE3',
        'DT_GET', 'SKUMKTP_ID'
    ]

    # Montar a instrução de inserção
    insert_query = f"INSERT INTO ECOM_SKU ({', '.join(colunas)}) VALUES ({', '.join(['?' for _ in colunas])})"

    # Executar a instrução de inserção para cada conjunto de valores
    cursor = conexao.cursor()
    for valor in valores:
        cursor.execute(insert_query, valor)
        conexao.commit()


    print(f"{str(index+1)}/{str(len(df_amazon))} - {str(codid)} - {str(sku_amazon)} - Inserção concluída com sucesso!")


# Fechar a conexão
cursor.close()
conexao.close()