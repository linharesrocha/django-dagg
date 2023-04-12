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
    SELECT B.CODID, B.DESCRICAO, A.SKU, A.PRODMKTP_ID, A.SKUVARIACAO_MASTER,C.ORIGEM_NOME, A.VLR_SITE1, A.VLR_SITE2, A.TITULO, A.ATIVO, A.EXISTE, A.ORIGEM_ID
    FROM ECOM_SKU A
    LEFT JOIN MATERIAIS B ON A.MATERIAL_ID = B.CODID
    LEFT JOIN ECOM_ORIGEM C ON A.ORIGEM_ID = C.ORIGEM_ID
    WHERE A.EXISTE = 'N'
    AND B.INATIVO = 'N'
    '''

    df_n_existe = pd.read_sql(comando, conexao)
    
    comando = f'''
    SELECT B.CODID, B.DESCRICAO, A.SKU, A.PRODMKTP_ID, A.SKUVARIACAO_MASTER,C.ORIGEM_NOME, A.VLR_SITE1, A.VLR_SITE2, A.TITULO, A.ATIVO, A.EXISTE, A.ORIGEM_ID
    FROM ECOM_SKU A
    LEFT JOIN MATERIAIS B ON A.MATERIAL_ID = B.CODID
    LEFT JOIN ECOM_ORIGEM C ON A.ORIGEM_ID = C.ORIGEM_ID
    WHERE A.ATIVO = 'N'
    AND B.INATIVO = 'N'
    '''
    
    df_n_ativo = pd.read_sql(comando, conexao)
    
    df_completo = pd.concat([df_n_existe, df_n_ativo], ignore_index=True)
    
    df_sem_duplicadas = df_completo.drop_duplicates(subset=['CODID', 'SKU', 'ORIGEM_ID']).sort_values('CODID')
    num_linhas = len(df_sem_duplicadas)
    
    if download == False:
        return num_linhas
    else:
        excel_bytes = BytesIO()
        df_sem_duplicadas.to_excel(excel_bytes, index=False)
        excel_bytes.seek(0)
        bytes_data = excel_bytes.getvalue()
        return bytes_data