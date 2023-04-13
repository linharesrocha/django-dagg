import pyodbc
import pandas as pd
import warnings
from connect_to_database import get_connection
from datetime import datetime, timedelta

# Função para validar o formato da data
def validar_data(data):
    try:
        dia, mes, ano = data.split('-')
        # Verifica se a data possui 3 elementos (dia, mês e ano)
        if len(dia) == len(mes) == 2 and len(ano) == 4:
            # Verifica se dia, mês e ano são inteiros
            dia = int(dia)
            mes = int(mes)
            ano = int(ano)
            # Verifica se o dia está dentro do intervalo válido
            if dia >= 1 and dia <= 31:
                # Verifica se o mês está dentro do intervalo válido
                if mes >= 1 and mes <= 12:
                    return True
        return False
    except ValueError:
        return False


# Loop para solicitar 4 datas ao usuário
# for i in range(4):
#     while True:
#         data = input(f"Digite a data {i+1} (dd-mm-yyyy): ")
#         if validar_data(data):
#             datas.append(data)
#             break
#         else:
#             print("Data inválida! Por favor, digite novamente.")

data_periodo_1_inicial = '01-03-2023'
data_periodo_1_final = '02-03-2023'
data_periodo_2_inicial = '01-04-2023'
data_periodo_2_final = '12-04-2023'

# Converter para datetime e formatar para yyyy-mm-dd
data_periodo_1_inicial = datetime.strptime(data_periodo_1_inicial, '%d-%m-%Y').strftime('%Y-%m-%d')
data_periodo_1_final = datetime.strptime(data_periodo_1_final, '%d-%m-%Y').strftime('%Y-%m-%d')
data_periodo_2_inicial = datetime.strptime(data_periodo_2_inicial, '%d-%m-%Y').strftime('%Y-%m-%d')
data_periodo_2_final = datetime.strptime(data_periodo_2_final, '%d-%m-%Y').strftime('%Y-%m-%d')

# Adicionar mais um dia nas variáveis data_periodo_1_final e data_periodo_2_final
data_periodo_1_final = (datetime.strptime(data_periodo_1_final, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
data_periodo_2_final = (datetime.strptime(data_periodo_2_final, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')


warnings.filterwarnings('ignore')
connection = get_connection()
conexao = pyodbc.connect(connection)

comando = f'''
SELECT A.PEDIDO, A.COD_INTERNO, A.QUANT, A.COD_PEDIDO AS SKU, A.EDICAO AS SKU2, B.ORIGEM AS ORIGEM_ID, B.DATA, A.VLR_TOTAL
FROM PEDIDO_MATERIAIS_ITENS_CLIENTE A
LEFT JOIN PEDIDO_MATERIAIS_CLIENTE B
ON A.PEDIDO = B.PEDIDO
WHERE B.TIPO = 'PEDIDO'
AND B.POSICAO != 'CANCELADO'
'''

# Preenchendo pedidos
df_vendas = pd.read_sql(comando, conexao)
df_vendas.drop('PEDIDO', axis=1, inplace=True)

# Limpando valores com espaços vazios
df_vendas['COD_INTERNO'] = df_vendas['COD_INTERNO'].str.strip()
df_vendas['SKU'] = df_vendas['SKU'].str.strip()
df_vendas['SKU2'] = df_vendas['SKU2'].str.strip()

# Adiciona linhas
df_vendas_aux = df_vendas[(df_vendas['QUANT'] > 1)]
df_vendas_aux.loc[:, 'QUANT'] -= 1
for i in range(len(df_vendas_aux)):
    cod_interno = df_vendas_aux['COD_INTERNO'].iloc[i]
    quantidade = int(df_vendas_aux['QUANT'].iloc[i])
    sku = df_vendas_aux['SKU'].iloc[i]
    sku2 = df_vendas_aux['SKU2'].iloc[i]
    origem = df_vendas_aux['ORIGEM_ID'].iloc[i]
    data_venda = df_vendas_aux['DATA'].iloc[i]
    vlr_total = df_vendas_aux['VLR_TOTAL'].iloc[i]
    for j in range(quantidade):
        row1 = pd.Series([cod_interno, 1, sku, sku2, origem, data_venda, vlr_total], index=df_vendas.columns)
        df_vendas = df_vendas._append(row1, ignore_index=True)
        
df_vendas.loc[df_vendas['ORIGEM_ID'].isin([5,6,7]), 'SKU'] = df_vendas['SKU2'].fillna(df_vendas['SKU'])

# Coloca todos valroes da coluna SKU na coluna SK2 do Mercado Livre
df_vendas.loc[df_vendas['ORIGEM_ID'].isin([8,9,10]), 'SKU2'] = df_vendas['SKU'].fillna(df_vendas['SKU2'])


df_periodo_1 = df_vendas[(df_vendas['DATA'] >= data_periodo_1_inicial) & (df_vendas['DATA'] <= data_periodo_1_final)]
df_periodo_2 = df_vendas[(df_vendas['DATA'] >= data_periodo_2_inicial) & (df_vendas['DATA'] <= data_periodo_2_final)]


# MÉTRICAS MÉTRICAS MÉTRICAS MÉTRICAS

# Vendas Bruta
vendas_bruta_periodo_1 = round(df_periodo_1['VLR_TOTAL'].sum(),2)
vendas_bruta_periodo_2 = round(df_periodo_2['VLR_TOTAL'].sum(),2)
resultado_vendas_bruta = round(vendas_bruta_periodo_1 - vendas_bruta_periodo_2,2)
if vendas_bruta_periodo_2 != 0:
    resultado_vendas_bruta_porcentagem = round((resultado_vendas_bruta / vendas_bruta_periodo_1) * 100,2)
else:
    resultado_vendas_bruta_porcentagem = 0
resultado_vendas_bruta_classificacao = 'AUMENTOU' if vendas_bruta_periodo_1 > vendas_bruta_periodo_2 else 'DIMINUIU'

# Quantidade de Vendas
quantidade_de_vendas_periodo1 = len(df_periodo_1)
quantidade_de_vendas_periodo2 = len(df_periodo_2)
resultado_quantidade_vendas = quantidade_de_vendas_periodo1 - quantidade_de_vendas_periodo2
if quantidade_de_vendas_periodo2 != 0:
    resultado_quantidade_vendas_porcentagem = round((resultado_quantidade_vendas / quantidade_de_vendas_periodo1) * 100,2)
else:
    resultado_quantidade_vendas_porcentagem = 0
resultado_quantidade_vendas_classificacao = 'AUMENTOU' if quantidade_de_vendas_periodo1 > quantidade_de_vendas_periodo2 else 'DIMINUIU'


# Preço Médio
preco_medio_periodo1 = round(df_periodo_1['VLR_TOTAL'].mean(),2)
preco_medio_periodo2 = round(df_periodo_2['VLR_TOTAL'].mean(),2)
resultado_preco_medio = round(preco_medio_periodo1 - preco_medio_periodo2,2)
if preco_medio_periodo2 != 0:
    resultado_preco_medio_porcentagem = round((resultado_preco_medio / preco_medio_periodo1) * 100, 2)
else:
    resultado_preco_medio_porcentagem = 0
resultado_preco_medio_classificacao = 'AUMENTOU' if preco_medio_periodo1 > preco_medio_periodo2 else 'DIMINUIU'

print('Datas Analisádas')
print(f'Periodo 1: {data_periodo_1_inicial} até {data_periodo_1_final}')
print(f'Periodo 2: {data_periodo_2_inicial} até {data_periodo_2_final}\n')
print('Relatório Geral')
print('')
print(f'VENDAS BRUTAS\nPeriodo 1: {vendas_bruta_periodo_1}\nPeriodo 2: {vendas_bruta_periodo_2}\nDiferença: {resultado_vendas_bruta} - {resultado_vendas_bruta_classificacao} {resultado_vendas_bruta_porcentagem}%')
print('')
print(f'QUANTIDADE DE VENDAS\nPeriodo 1: {quantidade_de_vendas_periodo1}\nPeriodo 2: {quantidade_de_vendas_periodo2}\nDiferença: {resultado_quantidade_vendas} - {resultado_quantidade_vendas_classificacao} {resultado_quantidade_vendas_porcentagem}%')
print(' ')
print(f'PREÇO MÉDIO\nPeriodo 1: {preco_medio_periodo1}\nPeriodo 2: {preco_medio_periodo2}\nDiferença: {resultado_preco_medio} - {resultado_preco_medio_classificacao} {resultado_preco_medio_porcentagem}%')



df_periodo_1_groupby = df_periodo_1.groupby(['SKU','ORIGEM_ID']).count().reset_index().drop(['DATA'], axis=1)

df_periodo_2_groupby = df_periodo_2.groupby(['SKU','ORIGEM_ID']).count().reset_index().drop(['DATA'], axis=1)

df_periodos_comparacao = df_periodo_1_groupby.merge(df_periodo_2_groupby, on=['SKU', 'ORIGEM_ID'], how='outer',suffixes=('_PRINCIPAL', '_COMPARATIVO'))

df_periodos_comparacao.drop(columns=['COD_INTERNO_PRINCIPAL', 'QUANT_PRINCIPAL', 'SKU2_PRINCIPAL', 'COD_INTERNO_COMPARATIVO', 'QUANT_COMPARATIVO', 'SKU2_COMPARATIVO'], axis=1, inplace=True)

df_periodos_comparacao.rename(columns={'VLR_TOTAL_PRINCIPAL':'VENDAS_PERIODO_1'}, inplace=True)
df_periodos_comparacao.rename(columns={'VLR_TOTAL_COMPARATIVO':'VENDAS_PERIODO_2'}, inplace=True)

df_periodos_comparacao['VENDAS_PERIODO_1'].fillna(0, inplace=True)
df_periodos_comparacao['VENDAS_PERIODO_2'].fillna(0, inplace=True)

df_periodos_comparacao = df_periodos_comparacao.sort_values(by='VENDAS_PRINCIPAL', ascending=False)



df_periodos_comparacao.to_excel('test.xlsx', index=False)
