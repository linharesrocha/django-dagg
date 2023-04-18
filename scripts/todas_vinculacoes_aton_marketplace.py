import pyodbc
import pandas as pd
import warnings
from io import BytesIO
from scripts.connect_to_database import get_connection


def main():
    warnings.filterwarnings('ignore')
    connection = get_connection()
    conexao = pyodbc.connect(connection)

    comando = f'''
    SELECT B.CODID, B.COD_INTERNO, B.DESCRICAO, C.ORIGEM_NOME, B.INATIVO, A.*
    FROM ECOM_SKU A
    LEFT JOIN MATERIAIS B ON A.MATERIAL_ID = B.CODID
    LEFT JOIN ECOM_ORIGEM C ON A.ORIGEM_ID = C.ORIGEM_ID
    ORDER BY CODID
    '''

    df = pd.read_sql(comando, conexao)
    
    df.drop(columns=['MATERIAL_ID'], inplace=True)
    
    excel_bytes = BytesIO()
    df.to_excel(excel_bytes, index=False)
    excel_bytes.seek(0)
    bytes_data = excel_bytes.getvalue()
    return bytes_data