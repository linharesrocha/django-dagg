import pyodbc
import pandas as pd
import warnings
from io import BytesIO
from scripts.connect_to_database import get_connection


def main(download):
    warnings.filterwarnings('ignore')
    connection = get_connection()
    conexao = pyodbc.connect(connection)

    comando = f'''
    SELECT A.CODID, A.COD_INTERNO, A.DESCRICAO, D.ORIGEM_NOME, C.SKU, SKUVARIACAO_MASTER, B.ESTOQUE AS ESTQ_ATON, C.ESTOQUE AS ESTQ_MKTP
    FROM MATERIAIS A
    LEFT JOIN ESTOQUE_MATERIAIS B ON A.CODID = B.MATERIAL_ID
    LEFT JOIN ECOM_SKU C ON A.CODID = C.MATERIAL_ID
    LEFT JOIN ECOM_ORIGEM D ON C.ORIGEM_ID = D.ORIGEM_ID
    WHERE B.ARMAZEM = 1
    AND A.INATIVO = 'S'
    AND C.ESTOQUE > 0
    ORDER BY CODID
    '''

    df = pd.read_sql(comando, conexao)
    num_linhas = len(df)
    
    if download == False:
        return num_linhas
    else:
        excel_bytes = BytesIO()
        df.to_excel(excel_bytes, index=False)
        excel_bytes.seek(0)
        bytes_data = excel_bytes.getvalue()
        return bytes_data