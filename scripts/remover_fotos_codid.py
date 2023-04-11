from scripts.connect_to_database import get_connection
import pyodbc
import pandas as pd
import warnings

def main(codid):
    warnings.filterwarnings('ignore')
    connection = get_connection()
    conexao = pyodbc.connect(connection)
    cursor = conexao.cursor()
    
    comando = f'''
    SELECT *
    FROM MATERIAIS_IMAGENS
    WHERE CODID = {codid}
    '''
    
    df_test = pd.read_sql(comando, conexao)
    if len(df_test) == 0:
        return False
    
    
    comando = f'''
    DELETE
    FROM MATERIAIS_IMAGENS
    WHERE CODID = {codid}
    '''
    
    cursor.execute(comando)
    conexao.commit()
    
    return True