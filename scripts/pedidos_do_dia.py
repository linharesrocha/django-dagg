import pyodbc
import pandas as pd
import warnings
from io import BytesIO
from scripts.connect_to_database import get_connection
from openpyxl.utils import get_column_letter
import datetime

def main():
    hoje = datetime.datetime.now()
    ontem = hoje - datetime.timedelta(days=1)
    data_ontem_formatada = ontem.strftime('%Y-%d-%m')
    data_hoje_formatada = hoje.strftime('%Y-%d-%m')
    
    warnings.filterwarnings('ignore')
    connection = get_connection()
    conexao = pyodbc.connect(connection)

    comando = f'''
    SELECT A.PEDIDO, A.COD_INTERNO, A.QUANT, A.EMPRESA, B.DATA
    FROM PEDIDO_MATERIAIS_ITENS_CLIENTE A
    LEFT JOIN PEDIDO_MATERIAIS_CLIENTE B
    ON A.PEDIDO = B.PEDIDO
    WHERE B.TIPO = 'PEDIDO'
    AND B.POSICAO != 'CANCELADO'
    AND DATA >= '{data_ontem_formatada}'
    AND B.POSICAO_PRINT = 1
    AND A.EMPRESA != 4
    ORDER BY DATA
    '''

    df_vendas = pd.read_sql(comando, conexao)
    df_vendas['COD_INTERNO'] = df_vendas['COD_INTERNO'].str.strip()
    
    
    # Adicionando pedidos
    data_h_aux = df_vendas[(df_vendas['QUANT'] > 1)]
    data_h_aux.loc[:, 'QUANT'] -= 1
    for i in range(len(data_h_aux)):
        pedido = data_h_aux['PEDIDO'].iloc[i]
        cod_interno = data_h_aux['COD_INTERNO'].iloc[i]
        quantidade = int(data_h_aux['QUANT'].iloc[i])
        empresa = data_h_aux['EMPRESA'].iloc[i]
        data_venda = data_h_aux['DATA'].iloc[i]
        for j in range(quantidade):
            row1 = pd.Series([pedido, cod_interno, 1, empresa, data_venda], index=df_vendas.columns)
            df_vendas = df_vendas._append(row1, ignore_index=True)
    
    comando = f'''
    SELECT *
    FROM PEDIDO_CLIENTE_LOG
    WHERE DATAHR >= '{data_ontem_formatada}'
    AND DATAHR < '{data_hoje_formatada}'
    ORDER BY DATAHR
    '''
    
    df_feitos_expedicao = pd.read_sql(comando, conexao)
    df_vendas_excluido_feitos = df_vendas[~df_vendas['PEDIDO'].isin(df_feitos_expedicao['PEDIDO'])]
    df_vendas_excluidos_feitos_groupby = df_vendas_excluido_feitos.groupby(['COD_INTERNO', 'EMPRESA']).count()
    df_vendas_excluidos_feitos_groupby.drop(columns=['DATA', 'PEDIDO'], inplace=True)
    df_vendas_excluidos_feitos_groupby.reset_index(inplace=True)
   
    
    comando = f'''
    SELECT COD_INTERNO, DESCRICAO
    FROM MATERIAIS A
    '''
    
    df_materiais = pd.read_sql(comando, conexao)
    df_materiais['COD_INTERNO'] = df_materiais['COD_INTERNO'].str.strip()
    df_materiais['DESCRICAO'] = df_materiais['DESCRICAO'].str.strip()
    
    df_completo = pd.merge(df_vendas_excluidos_feitos_groupby, df_materiais, on='COD_INTERNO', how='left')
    
    comando = f'''
    SELECT DIAG_EMPRESA, FANTASIA
    FROM EMPRESA
    '''
    
    df_completo = pd.merge(df_completo, pd.read_sql(comando, conexao), left_on='EMPRESA', right_on='DIAG_EMPRESA', how='left')
    
    df_completo.drop(columns=['EMPRESA'], inplace=True)
    df_completo.rename(columns={'FANTASIA':'EMPRESA'}, inplace=True)
    df_completo = df_completo[['COD_INTERNO', 'DESCRICAO', 'QUANT', 'EMPRESA']]
    
    # Criar um novo arquivo Excel
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')

    # Loop pelos valores únicos na coluna 'EMPRESA'
    for empresa in df_completo['EMPRESA'].unique():
        # Filtrar o DataFrame para a empresa atual
        df_empresa = df_completo[df_completo['EMPRESA'] == empresa]
        # Criar uma nova aba no arquivo Excel com o nome da empresa
        df_empresa.to_excel(writer, sheet_name=empresa, index=False)
        # Ajustar o tamanho das colunas na aba
        ws = writer.sheets[empresa]
        for col in ws.columns:
            max_length = 0
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except TypeError:
                    pass
            adjusted_width = (max_length + 2) * 1.2
            col_letter = get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = adjusted_width

    # Salvar e fechar o arquivo Excel
    writer._save()
    output.seek(0)
    
    return output