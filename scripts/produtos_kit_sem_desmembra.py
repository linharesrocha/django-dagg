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
    SELECT * 
    FROM MATERIAIS
    WHERE COD_INTERNO LIKE '%KIT%'
    AND INATIVO = 'N'
    AND DESMEMBRA = 'N'
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