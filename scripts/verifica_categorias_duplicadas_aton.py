import os
from pathlib import Path
import pyodbc
import pandas as pd
import warnings
from dotenv import load_dotenv
from io import BytesIO
from scripts.connect_to_database import get_connection


def main(download):
    warnings.filterwarnings('ignore')
    connection = get_connection()
    conexao = pyodbc.connect(connection)

    comando = f'''
    SELECT AUTOID, API, CATEG_MKTP_DESC, DEPARTAMENTO, PRODUTO_TIPO, CATEG_NOME, CATEG_ATON
    FROM CATEGORIAS_MKTP A
    LEFT JOIN ECOM_CATEGORIAS B ON A.CATEG_ATON = B.CATEG_ID
    '''

    df_categorias = pd.read_sql(comando, conexao).sort_values(by=['CATEG_ATON', 'API'])

    # Verifica duplicatas nas colunas CATEG_ATON e API
    duplicatas = df_categorias.duplicated(subset=['CATEG_ATON', 'API'], keep=False)

    # Retorna as linhas duplicadas que possuem ambos os valores duplicados
    df_linhas_duplicadas = df_categorias.loc[duplicatas]
    num_linhas_duplicadas = len(df_linhas_duplicadas)

    if download == False:
        return num_linhas_duplicadas
    else:
        # Código para retornar o dataframe e o num_linhas_duplicadas
        excel_bytes = BytesIO()
        df_linhas_duplicadas.to_excel(excel_bytes, index=False)
        excel_bytes.seek(0)
        bytes_data = excel_bytes.getvalue()
        return bytes_data