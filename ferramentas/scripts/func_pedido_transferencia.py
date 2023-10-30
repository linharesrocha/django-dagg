from scripts.connect_to_database import get_connection
import pyodbc

def main(empresa_origem, empresa_destino, armazem_origem, armazem_destino, df_pedido_transferencia):
    
    connection = get_connection()
    conexao = pyodbc.connect(connection)
    cursor = conexao.cursor()
    
    # Consulta ultimo numero PEDIDO
    comando = '''
    SELECT TOP 1 PEDIDO
    FROM PEDIDO_TRANSFERENCIA
    ORDER BY PEDIDO DESC
    '''
    
    novo_numero_pedido = int(cursor.execute(comando).fetchone()[0]) + 1
    
    # Insere nova transferencia
    comando = f'''
    INSERT INTO PEDIDO_TRANSFERENCIA 
    (PEDIDO, DATA, PEDIDO_ENTRADA, PEDIDO_ORIGEM, TIPO, EMPRESA_ORIGEM, EMPRESA_DESTINO, ARMAZEM_ORIGEM, ARMAZEM_DESTINO, QTDE_ITENS, POSICAO, DTFECHAMENTO, PA, GERA_PEDIDOENTRADA, NOME_LOJA, COD_STATUS, LOGISTICA)
    VALUES ('{novo_numero_pedido}', SYSDATETIME(), '0', '0', 'TRANSFERENCIA', '{empresa_origem}', '{empresa_destino}', '{armazem_origem}', '{armazem_destino}', '0', 'ABERTA', SYSDATETIME(), '239', 'N', NULL, '1', '0');
    '''
    
    cursor.execute(comando)
    conexao.commit()
    
    for index, row in df_pedido_transferencia.iterrows():
        cod_interno = row['COD_INTERNO']
        quant = row['QUANT']
        
        # Seleciona outros dados do produto
        
        comando = f'''
        SELECT CODID, DESCRICAO, A.VLR_CUSTO AS VLRUNIT, B.ESTOQUE AS ESTOQUE_ATUAL, EANTRIB
        FROM MATERIAIS A
        LEFT JOIN ESTOQUE_MATERIAIS B ON A.CODID = B.MATERIAL_ID
        WHERE B.ARMAZEM = '1'
        AND COD_INTERNO = '{cod_interno}'
        '''
        
        dados_produto = cursor.execute(comando).fetchone()
        
        codid = dados_produto[0]
        descricao = dados_produto[1]
        vlrunit = dados_produto[2]
        vlrtotal = vlrunit * quant
        estoque_atual = dados_produto[3]
        eantrib = dados_produto[4]
        
        # Insere novo produto
        comando = f'''
        INSERT INTO PEDIDO_TRANSFERENCIA_ITENS
        (PEDIDO, CODID, COD_INTERNO, DESCRICAO, ESTOQUE_ATUAL, QUANT, VLRUNIT, VLRTOTAL, EAN)
        VALUES ('{novo_numero_pedido}', '{codid}', '{cod_interno}', '{descricao}', '{estoque_atual}', '{quant}', '{vlrunit}', '{vlrtotal}', '{eantrib}')
        '''
        
        cursor.execute(comando)
        conexao.commit()
        
        
        # Debita estoque na origem
        comando = f'''
        SELECT ESTOQUE
        FROM ESTOQUE_MATERIAIS
        WHERE MATERIAL_ID = '{codid}'
        AND ARMAZEM = '{armazem_origem}'
        '''
        
        estoque_atual_origem = cursor.execute(comando).fetchone()[0]
        
        comando = f'''
        UPDATE ESTOQUE_MATERIAIS
        SET ESTOQUE = '{estoque_atual_origem - quant}'
        WHERE MATERIAL_ID = '{codid}'
        AND ARMAZEM = '{armazem_origem}'
        '''
        
        cursor.execute(comando)
        conexao.commit()
        
        # Credita estoque no destino
        comando = f'''
        SELECT ESTOQUE
        FROM ESTOQUE_MATERIAIS
        WHERE MATERIAL_ID = '{codid}'
        AND ARMAZEM = '{armazem_destino}'
        '''
        
        estoque_atual_destino = cursor.execute(comando).fetchone()[0]
        
        comando = f'''
        UPDATE ESTOQUE_MATERIAIS
        SET ESTOQUE = '{estoque_atual_destino + quant}'
        WHERE MATERIAL_ID = '{codid}'
        AND ARMAZEM = '{armazem_destino}'
        '''
        
        cursor.execute(comando)
        conexao.commit()

        
    # Fechar pedido
    comando = f'''
    UPDATE PEDIDO_TRANSFERENCIA
    SET POSICAO = 'FINALIZADA', PA_FECHAMENTO = '239'
    WHERE PEDIDO = '{novo_numero_pedido}'
    '''
    
    cursor.execute(comando)
    conexao.commit()

    
    conexao.close()