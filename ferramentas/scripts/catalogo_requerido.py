from scripts.connect_to_database import get_connection
import pyodbc

def main():
    connection = get_connection()
    conexao = pyodbc.connect(connection)
    cursor = conexao.cursor()
    
    comando = f'''
    UPDATE PUBLICA_PRODUTO
    SET CATALOGO_REQUERIDO = 'N'
    WHERE FLAG = '-9'
    '''
    
    try:
        cursor.execute(comando)
        conexao.commit()
        return True
    except:
        return False