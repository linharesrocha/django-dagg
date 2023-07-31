import requests
from pathlib import Path
import sys
from datetime import datetime
import pyodbc
import pandas as pd
from io import BytesIO

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

from mercadolivre.scripts.config import reflash
from scripts.connect_to_database import get_connection

def main():
    connection = get_connection()
    conexao = pyodbc.connect(connection)

    # Obtem access token
    ACCESS_TOKEN = reflash.refreshToken()

    # Header
    header = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    
    mlbs_list = []
    names_list = []
    visitas_list = []
    vendas_totais_list = []
    tipo_de_anuncio_list = []
    data_criacao_list = []

    # Obtem lista MLB
    comando = f'''
    SELECT DISTINCT SKU
    FROM ECOM_SKU
    WHERE ORIGEM_ID = '8';
    '''
    
    df_mlbs = pd.read_sql(comando, conexao)
    
    contador = 1
    for mlb in df_mlbs['SKU']:
        print(f'{str(contador)}/{str(len(df_mlbs))}')
        
        # MLB
        mlbs_list.append(mlb)
        
        # Título / Criação Anúncio / Vendas Anúncio
        response = requests.get(f"https://api.mercadolibre.com/items/{mlb}?include_attributes=all", headers=header).json()
        names_list.append(response['title'])
        data_criacao = response['date_created']
        dt = datetime.fromisoformat(data_criacao[:-1])
        data_criacao = dt.strftime("%Y-%m-%d %H:%M:%S")
        data_criacao_list.append(data_criacao)
        vendas_totais_list.append(response['sold_quantity'])
        tipo_de_anuncio_list.append(response['listing_type_id'].replace('gold_pro', 'Premium').replace('gold_special', 'Clássico'))
        
        # Vísitas
        visitas_list.append(requests.get(f"https://api.mercadolibre.com/visits/items?ids={mlb}", headers=header).json().get(mlb))
        
        contador += 1
        
    
    # Transformar listas em um dicionário
    dados = {
        "MLB": mlbs_list,
        "NOME": names_list,
        "VISITAS": visitas_list,
        "V_TOTAIS": vendas_totais_list,
        "TIPO_ANUNCIO": tipo_de_anuncio_list,
        "DATA_CRIACAO": data_criacao_list
    }

    # Criar o DataFrame a partir do dicionário
    df_mlbs_stats = pd.DataFrame(dados)
    
    excel_bytes = BytesIO()
    df_mlbs_stats.to_excel(excel_bytes, index=False)
    excel_bytes.seek(0)
    bytes_data = excel_bytes.getvalue()
    
    return bytes_data