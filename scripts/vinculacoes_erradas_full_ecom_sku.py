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
    SELECT B.CODID, B.DESCRICAO, A.SKU, A.PRODMKTP_ID, A.SKUVARIACAO_MASTER,C.ORIGEM_NOME, A.VLR_SITE1, A.VLR_SITE2, A.TITULO, A.ATIVO, A.EXISTE, A.ORIGEM_ID, A.FULFIlLMENT
    FROM ECOM_SKU A
    LEFT JOIN MATERIAIS B ON A.MATERIAL_ID = B.CODID
    LEFT JOIN ECOM_ORIGEM C ON A.ORIGEM_ID = C.ORIGEM_ID
    WHERE A.FULFILLMENT = 'S'
    AND A.ORIGEM_ID NOT IN('8', '9', '10')
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