from scripts.connect_to_database import get_connection
import pyodbc
import pandas as pd
import warnings

def main(codid):
    warnings.filterwarnings('ignore')
    connection = get_connection()
    conexao = pyodbc.connect(connection)
    
    comando = f'''
    SELECT CODID, URL
    FROM MATERIAIS_IMAGENS
    WHERE CODID = {codid}
    '''
    
    df_fotos = pd.read_sql(comando, conexao)
    
    if len(df_fotos) == 0:
        return False
    
    lista_fotos = df_fotos['URL'].to_list()
    
    return lista_fotos