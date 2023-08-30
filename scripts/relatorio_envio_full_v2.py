import pyodbc
import pandas as pd
import warnings
from connect_to_database import get_connection
from openpyxl.styles import PatternFill
from collections import Counter
from openpyxl.worksheet.filters import (
    FilterColumn,
    CustomFilter,
    CustomFilters,
    )
from io import BytesIO


warnings.filterwarnings('ignore')
connection = get_connection()
conexao = pyodbc.connect(connection)

comando = f'''
SELECT *
FROM ECOM_SKU A
LEFT JOIN MATERIAIS B ON A.MATERIAL_ID = B.CODID
WHERE ORIGEM_ID = '8'
'''

df_ecom_sku_ml = pd.read_sql(comando, conexao)

df_ecom_sku_ml = df_ecom_sku_ml[['MATERIAL_ID', 'SKU', 'PRODMKTP_ID']]

conexao.close()

