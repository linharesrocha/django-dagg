import pandas as pd
import pyodbc
import datetime
import pandas as pd
import warnings
import numpy as np
import os
import sys
from time import sleep
sys.path.append('C:\workspace\cadastro-aton\mordomo\programas')
from scripts.connect_to_database import get_connection

# Esse código pega o primeiro dia do mês anterior até o dia atual e verifica
# qual produto não teve venda nesse período.
# Retorna um arquivo Excel formatado.

warnings.filterwarnings('ignore')
os.system('cls')
connection = get_connection()
conexao = pyodbc.connect(connection)
cursor = conexao.cursor()


today = datetime.date.today()
first_day_last_month = datetime.date(today.year, today.month-1, 1)
first_day_last_month_str = first_day_last_month.strftime('%Y-%d-%m')
last_month = datetime.date(today.year, today.month-1, 1)
month_name = last_month.strftime('%B')
print(f'Verificando produtos que não teve venda entre o periodo {first_day_last_month_str} até hoje.')

path_excel = f'C:/workspace/cadastro-aton/mordomo/programas/excel/produtos-sem-venda-{month_name}.xlsx'
writer = pd.ExcelWriter(path_excel, engine='xlsxwriter')


comando = f'''
SELECT B.CODID, B.COD_INTERNO, B.DESCRICAOPROD, A.PEDIDO, A.DATA
FROM PEDIDO_MATERIAIS_CLIENTE A
LEFT JOIN PEDIDO_MATERIAIS_ITENS_CLIENTE B
ON A.PEDIDO = B.PEDIDO
WHERE A.DATA > '2023-01-02'
'''

data_vendas = pd.read_sql(comando, conexao)


comando = f'''
SELECT CODID, COD_INTERNO, DESCRICAO, B.ESTOQUE, A.INATIVO
FROM MATERIAIS A
LEFT JOIN ESTOQUE_MATERIAIS B ON A.CODID = B.MATERIAL_ID
WHERE COD_INTERNO NOT LIKE '%PAI'
AND INATIVO = 'N'
AND B.ARMAZEM = 1
AND B.ESTOQUE = 0
'''

data_materiais = pd.read_sql(comando, conexao)



not_in_data_vendas = ~data_materiais['CODID'].isin(data_vendas['CODID'])
data = data_materiais.loc[not_in_data_vendas, :]
data['CHECK'] = np.nan * np.empty(len(data))

data.to_excel(writer, sheet_name='Planilha1', index=False)