import pyodbc
import pandas as pd
import warnings
from openpyxl.styles import PatternFill
from collections import Counter
from openpyxl.worksheet.filters import (
    FilterColumn,
    CustomFilter,
    CustomFilters,
    )
from pathlib import Path
import sys
from io import BytesIO
import requests
import json

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
from mercadolivre.scripts.config import reflash
from scripts.connect_to_database import get_connection

def main():    
    # Banco de dados Aton
    warnings.filterwarnings('ignore')
    connection = get_connection()
    conexao = pyodbc.connect(connection)
    
    # Obtem access token ML
    ACCESS_TOKEN = reflash.refreshToken()
    
    # Header
    header = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    
    comando = f'''
    SELECT C.DESCRICAO, B.ESTOQUE, A.PRODMKTP_ID AS COD_ML
    FROM ECOM_SKU A
    LEFT JOIN ESTOQUE_MATERIAIS B ON A.MATERIAL_ID = B.MATERIAL_ID
    LEFT JOIN MATERIAIS C ON A.MATERIAL_ID = C.CODID
    WHERE B.ARMAZEM = 1
    AND A.ORIGEM_ID IN('8')
    AND A.PRODMKTP_ID NOT IN('', 'null')
    ORDER BY C.CODID
    '''
    
    df_produtos_full = pd.read_sql(comando, conexao)
    
    # Percorre coluna COD_ML
    for index, row in df_produtos_full.iterrows():
        cod_ml = row['COD_ML']
        cod_ml = 'EADY83926'
        
        data = requests.get(f"https://api.mercadolibre.com/items/MLB2835251564", headers=header).json()
        data = requests.get(f"https://api.mercadolibre.com/inventories/{cod_ml}/stock/fulfillment?include_attributes=conditions", headers=header).json()
        
        # Txt
        # subtracao = data['total']
        # estoque = data['available_quantity']
        
        with open("pasta/resposta_api2.json", "w") as arquivo:
            json.dump(data, arquivo, indent=4)
            
        break
            
main()