import pyodbc
import pandas as pd
import warnings
from io import BytesIO
from connect_to_database import get_connection
#from scripts.connect_to_database import get_connection
import datetime

def main():
    hoje = datetime.datetime.now()
    ontem = hoje - datetime.timedelta(days=1)
    data_ontem_formatada = ontem.strftime('%Y-%d-%m')
    
    warnings.filterwarnings('ignore')
    connection = get_connection()
    conexao = pyodbc.connect(connection)

    comando = f'''
    SELECT A.PEDIDO, A.COD_INTERNO, A.DESCRICAOPROD, A.QUANT, B.ORIGEM AS ORIGEM_ID, A.EMPRESA, B.DATA
    FROM PEDIDO_MATERIAIS_ITENS_CLIENTE A
    LEFT JOIN PEDIDO_MATERIAIS_CLIENTE B
    ON A.PEDIDO = B.PEDIDO
    WHERE B.TIPO = 'PEDIDO'
    AND B.POSICAO != 'CANCELADO'
    AND DATA >= '{data_ontem_formatada}'
    ORDER BY DATA
    '''

    df = pd.read_sql(comando, conexao)
    print(len(df))


    # excel_bytes = BytesIO()
    # df.to_excel(excel_bytes, index=False)
    # excel_bytes.seek(0)
    # bytes_data = excel_bytes.getvalue()
    # return bytes_data
    
main()