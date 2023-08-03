from django.shortcuts import redirect
from django.contrib.messages import constants
from django.contrib import messages
import random
from scripts.connect_to_database import get_connection
import pyodbc
import pandas as pd
from datetime import datetime

def main(request):
    def calcular_digito_verificador(ean_base):
        soma = 0
        for i, digito in enumerate(reversed(ean_base)):
            multiplicador = 3 if i % 2 == 0 else 1
            soma += int(digito) * multiplicador
        return str((10 - soma % 10) % 10)

    def gerar_ean_brasileiro(codigo_produto):
        if len(codigo_produto) != 9 or not codigo_produto.isdigit():
            raise ValueError("O código do produto deve ter exatamente 9 dígitos numéricos.")

        ean_base = '789' + codigo_produto
        digito_verificador = calcular_digito_verificador(ean_base)

        ean_completo = ean_base + digito_verificador
        
        return ean_completo
    
    connection = get_connection()
    conexao = pyodbc.connect(connection)
    cursor = conexao.cursor()
    
    descricao_codid_2 = None
    descricao_codid_3 = None
    
    DESCRICAO_INICIAL = '''PRONTA ENTREGA - COM NOTA FISCAL - TESTADO - COM GARANTIA

Temos o cuidado de embalar os produtos individualmente, com material de proteção de alta qualidade, certificando que ele chegue até ao seu destino intacto, minimizando possíveis danos durante o transporte.

Todos os produtos são testados, analisados e possuem nota fiscal, garantindo mais confiabilidade com a melhor qualidade e preço, além disso caso haja alguma inconformidade com o produto basta nos acionar que resolveremos.

Nossos produtos estão a pronta entrega e sempre são despachados em até um dia útil, garantindo agilidade no processo de compra e uma boa experiência para o cliente.

Nós somos excelência em atendimentos aos nossos clientes, envie suas dúvidas ou perguntas, de preferência em nosso chat, atenderemos com agilidade e empenho para resolver da melhor maneira.

SOBRE O PRODUTO:'''

    # Coleta CODID's
    codid_1 = request.POST.get('codid1-kit')
    codid_2 = request.POST.get('codid2-kit')
    codid_3 = request.POST.get('codid3-kit')
    
    qtd_codid_1 = request.POST.get('qtd-codid1-kit')
    qtd_codid_2 = request.POST.get('qtd-codid2-kit')
    qtd_codid_3 = request.POST.get('qtd-codid3-kit')

    # Validar se o segundo foi informado
    codid_2_informado = True
    if codid_2 == '' or codid_2 == None:
        codid_2_informado = False
        
    # Validar se o terceiro foi informado
    codid_3_informado = True
    if codid_3 == '' or codid_3 == None:
        codid_3_informado = False
        
    # Valida se o segundo não foi informado mas o primeiro e o terceiro sim
    if not codid_2_informado and codid_3_informado:
        messages.add_message(request, constants.ERROR, 'Passe o CODID3 para o CODID2!')
        return redirect('index-ferramentas')
        
    # Criar lista de CODID
    if codid_3_informado:
        lists_codid = [codid_1, codid_2, codid_3]
    elif codid_2_informado:
        lists_codid = [codid_1, codid_2]
    else:
        lists_codid = [codid_1]
        
    # Validar se o segundo tem quantidade
    if codid_2_informado:
        if qtd_codid_2 == '0' or qtd_codid_2 == '' or qtd_codid_2 == None:
            messages.add_message(request, constants.ERROR, 'Informe a quantidade do CODID 2!')
            return redirect('index-ferramentas')
        
    # Validar se o terceiro tem quantidade
    if codid_3_informado:
        if qtd_codid_3 == '0' or qtd_codid_3 == '' or qtd_codid_3 == None:
            messages.add_message(request, constants.ERROR, 'Informe a quantidade do CODID 3!')
            return redirect('index-ferramentas')  


    # Validar se os CODID são iguais, não podem ser iguais
    elif codid_2_informado:
        if codid_1 == codid_2:
            messages.add_message(request, constants.ERROR, 'CODID não podem ser iguais! Caso queira criar KIT do mesmo produto, aumente apenas a quantidade!')
            return redirect('index-ferramentas')
        
    if codid_3_informado:
        if codid_1 == codid_2 or codid_1 == codid_3 or codid_2 == codid_3:
            messages.add_message(request, constants.ERROR, 'CODID não podem ser iguais! Caso queira criar KIT do mesmo produto, aumente apenas a quantidade!')
            return redirect('index-ferramentas')
    

    # Valida cada CODID e também soma peso 
    peso_kit_list = []
    dimensao_codids_list = []
    vlr_custo_list = []
    contador = 1
    for codid in lists_codid:
        comando = f'''
        SELECT CODID, COD_INTERNO, INATIVO, DESMEMBRA, PESO, DESCRICAO, DESCRITIVO, COMPRIMENTO, LARGURA, ALTURA, VLR_CUSTO
        FROM MATERIAIS
        WHERE CODID = '{codid}'
        AND INATIVO = 'N'
        '''
        
        df = pd.read_sql(comando, conexao)  
        
        # Verifica se existe no banco de dados
        if len(df) <= 0:
            messages.add_message(request, constants.ERROR, f'CODID: {codid} não existe no Aton!')
            return redirect('index-ferramentas')
        
        # Valida se é PAI
        coluna_pai = df['COD_INTERNO'][0]
        if 'PAI' in coluna_pai:
            messages.add_message(request, constants.ERROR, f'CODID: {codid} é PAI!')
            return redirect('index-ferramentas')
        
        # Valida se é KIT
        coluna_desmembra = df['DESMEMBRA'][0].strip()
        if coluna_desmembra == 'S':
            messages.add_message(request, constants.ERROR, f'CODID: {codid} é KIT!')
            return redirect('index-ferramentas')
        
        # Coleta dimensão e armazena como dicionario em uma lista
        dimensao = {'CODID':codid ,'COMPRIMENTO': df['COMPRIMENTO'][0], 'LARGURA': df['LARGURA'][0], 'ALTURA': df['ALTURA'][0]}
        dimensao_codids_list.append(dimensao)
        
        # Soma peso
        if contador == 1:
            peso_kit_list.append(df['PESO'][0] * int(qtd_codid_1))
            vlr_custo_list.append(df['VLR_CUSTO'][0] * int(qtd_codid_1))

        elif contador == 2: 
            peso_kit_list.append(df['PESO'][0] * int(qtd_codid_2))
            vlr_custo_list.append(df['VLR_CUSTO'][0] * int(qtd_codid_2))

        elif contador == 3:
            peso_kit_list.append(df['PESO'][0] * int(qtd_codid_3))
            vlr_custo_list.append(df['VLR_CUSTO'][0] * int(qtd_codid_3))

        contador+= 1

    if len(dimensao_codids_list) == 1:
        dimensao1 = {'CODID':None ,'COMPRIMENTO': None, 'LARGURA': None, 'ALTURA': None}
        dimensao2 = {'CODID':None ,'COMPRIMENTO': None, 'LARGURA': None, 'ALTURA': None}
        dimensao_codids_list.append(dimensao1)
        dimensao_codids_list.append(dimensao2)
    elif len(dimensao_codids_list) == 2:
        dimensao1 = {'CODID':None ,'COMPRIMENTO': None, 'LARGURA': None, 'ALTURA': None}
        dimensao_codids_list.append(dimensao1)
    
    # Peso
    peso_kit = str(round(sum(peso_kit_list), 2))
    
    # Vlr Custo
    valor_custo_kit = str(round(sum(vlr_custo_list), 2))
    
    # EAN
    codigo_produto_aleatorio = ''.join(random.choices('0123456789', k=9))
    ean_valido_brasileiro = str(gerar_ean_brasileiro(codigo_produto_aleatorio))
    print(ean_valido_brasileiro)
    
    # Verifica porcentagem
    valor_agregado_kit1 = None
    valor_agregado_kit2 = None
    valor_agregado_kit3 = None
    if len(vlr_custo_list) == 1:
        valor_agregado_kit1 = 100
    elif len(vlr_custo_list) == 2:
        valor_agregado_kit1 = round((vlr_custo_list[0] / sum(vlr_custo_list)) * 100, 2)
        valor_agregado_kit2 = round((vlr_custo_list[1] / sum(vlr_custo_list)) * 100, 2)
    elif len(vlr_custo_list) == 3:
        valor_agregado_kit1 = round((vlr_custo_list[0] / sum(vlr_custo_list)) * 100, 2)
        valor_agregado_kit2 = round((vlr_custo_list[1] / sum(vlr_custo_list)) * 100, 2)
        valor_agregado_kit3 = round((vlr_custo_list[2] / sum(vlr_custo_list)) * 100, 2)
        
    # DF com os dados dos CODID
    comando = f'''
    SELECT A.CODID, COD_INTERNO, INATIVO, DESMEMBRA, PESO, DESCRICAO, DESCRITIVO, CLASS_FISCAL, ECOM_CATEGORIA, MARCA, B.URL,
    FROM MATERIAIS A
    LEFT JOIN MATERIAIS_IMAGENS B ON A.CODID = B.CODID
    WHERE A.CODID IN ('{codid_1}', '{codid_2}', '{codid_3}')
    '''
    
    df = pd.read_sql(comando, conexao)
    
    # Copiar NCM
    ncm_kit = df['CLASS_FISCAL'][0]
    
    # Marca
    marca_kit = str(df['MARCA'][0]).strip()
    
    ecom_categoria_kit = str(df['ECOM_CATEGORIA'][0]).strip()
    
    # Obter data do cadastro
    data_atual = datetime.now()
    data_alvo = data_atual.replace(hour=0, minute=0, second=0, microsecond=0)
    data_formatada_kit = str(data_alvo.strftime('%Y-%m-%d %H:%M:%S'))


    # Fazer kit cod interno
    while True:
        now = datetime.now()
        DATE_TIME = now.strftime("%Y%m%d")
        RANDOM = random.randint(0, 99)
        INICIAL_KITDG = 'KITDG'
        codigo_kit = INICIAL_KITDG + str(DATE_TIME) + str(RANDOM)
        
        # Verifica se existe no banco de dados
        comando = f'''
        SELECT CODID
        FROM MATERIAIS
        WHERE COD_INTERNO = '{codigo_kit}'
        '''
        
        df_kit_check_cod_interno = pd.read_sql(comando, conexao)
        
        if len(df_kit_check_cod_interno) <= 0:
            break
    
    # Cria nome do kit e descricao
    if codid_3_informado:
        nome_codid_3 = df['DESCRICAO'][2].strip()
        nome_codid_2 = df['DESCRICAO'][1].strip()
        nome_codid_1 = df['DESCRICAO'][0].strip()
        descricao_codid_3 = df['DESCRITIVO'][2].strip()
        descricao_codid_2 = df['DESCRITIVO'][1].strip()
        descricao_codid_1 = df['DESCRITIVO'][0].strip()
        nome_kit = f'KIT {qtd_codid_1} {nome_codid_1} + {qtd_codid_2} {nome_codid_2} + {qtd_codid_3} {nome_codid_3}'
        descritivo_kit = f'''{nome_codid_1.title()} + {nome_codid_2.title()} + {nome_codid_3.title()}

{DESCRICAO_INICIAL}
        '''
    elif codid_2_informado:
        nome_codid_2 = df['DESCRICAO'][1].strip()
        nome_codid_1 = df['DESCRICAO'][0].strip()
        descricao_codid_2 = df['DESCRITIVO'][1].strip()
        descricao_codid_1 = df['DESCRITIVO'][0].strip()
        nome_kit = f'KIT {qtd_codid_1} {nome_codid_1} + {qtd_codid_2} {nome_codid_2}'
        descritivo_kit = f'''{nome_codid_1.title()} + {nome_codid_2.title()}

{DESCRICAO_INICIAL}
        '''
    else:
        nome_codid_1 = df['DESCRICAO'][0].strip()
        descricao_codid_1 = df['DESCRITIVO'][0].strip()
        nome_kit = f'KIT {qtd_codid_1} {nome_codid_1}'
        descritivo_kit = f'''{nome_codid_1.title()}

{DESCRICAO_INICIAL}
        '''

    
    # Cadastrar no aton
    # Defina as colunas e os valores
    colunas = [
        'COD_INTERNO', 'COD_BARRAS', 'COD_FABRICANTE', 'TIPO_MATERIAL',
        'TIPO_ITEM', 'DESCRICAO', 'DESCRICAONF', 'DESCRITIVO', 'LOCACAO', 'UNIDADE_ENT',
        'UNIDADE_SAI', 'EMBALAGEM', 'FORMATO', 'PESO', 'COR', 'MEDIDA', 'TAMANHO',
        'OUTROS', 'GRUPO', 'SUBGRUPO', 'FABRICANTE', 'FORNECEDOR', 'ALIQ_II', 'ALIQ_IPI',
        'ALIQ_ICMS', 'CLASS_FISCAL_ID', 'CLASS_FISCAL', 'IVAD', 'IVAF', 'ESTOQUE_PADRAO',
        'ESTOQUE', 'EST_MIN', 'EST_MAX', 'DESCONTO_MAX', 'VLR_CUSTO', 'VLR_CUSTO_MEDIO',
        'PORC_GARANTIA', 'VLR_IPI', 'REAJ1', 'REAJ2', 'REAJ3', 'VLR_VENDA', 'VLR_VENDA2',
        'VLR_VENDA3', 'SEL', 'MAQ', 'ORIGEM_TRIB', 'SIT_TRIBUTARIA', 'COD_COMISSAO',
        'CENTROCUSTO', 'PA', 'INATIVO', 'OP', 'EXERCITO', 'CIVIL', 'FEDERAL', 'COD_EXERCITO',
        'COD_CIVIL', 'COD_FEDERAL', 'FOTOPATH', 'DESMEMBRA', 'TABELAIMPOSTO', 'EMBQUANT',
        'NAOMOVESTOQUE', 'PISCOFINS', 'CSTPIS', 'CSTCOFINS', 'CSTIPI', 'PIS', 'COFINS',
        'CODANP', 'MOEDA', 'COMPRIMENTO', 'ALTURA', 'LARGURA', 'CEST', 'nFCI', 'OBSI',
        'ID_SKU', 'SKU', 'VLR_SITE1', 'VLR_SITE2', 'TRANSPORTADORA', 'VALIDO', 'SKYHUB',
        'SKYHUB_STATUS', 'GARANTIA', 'CROSSDOCK', 'CATEGORIA', 'EANTRIB', 'OPENHUB', 'SEMGTIN',
        'MARGEM_MIN', 'MARGEM_MAX', 'PAI', 'VLR_BASE', 'VLR_VENDA4', 'LOGISTICA', 'DTCADASTRO',
        'SABOR', 'GENERO', 'IDVARIACAO', 'ARMAZEM', 'VOLUMES', 'PRODUTO_PADRAO', 'MARCA',
        'COD_INTERNO_PAI', 'ECOM_CATEGORIA', 'IMPSKU', 'EMPRESA_FAT', 'CODANVISA', 'EMP',
        'REAJ4', 'REQUER_SERIE'
    ]

    valores = [
        codigo_kit, ean_valido_brasileiro, None, 'VENDA', '00', nome_kit, None, descritivo_kit, None, None,
        'UN', None, 2, peso_kit, None, None, None, None, None, None, None, None, 0, 0, 0, None, ncm_kit, 0, 0,
        1, 0, 0, 0, 0, valor_custo_kit, 0, None, 0, 0, 0, 0, 0, 0, 0, 'False', 0, 0, '00', 0, None, None, 'N', 'N',
        'N', 'N', 'N', None, None, None, None, 'S', 1, 0, 'N', None, None, None, None, 0, 0, None, 1, 0, 0, 0,
        None, None, None, None, None, 0, 0, None, 'N', 'N', 'N', 3, 0, None, ean_valido_brasileiro, 0, 'S', 0, 0, 0,
        0, 0, None, data_formatada_kit, None, None, 0, 0, 0, None, marca_kit, None, ecom_categoria_kit, 0, 0, None,
        0, 0, 'N'
    ]


    # Crie a consulta INSERT
    query = f"INSERT INTO MATERIAIS ({', '.join(colunas)}) VALUES ({', '.join(['?' for _ in colunas])})"
    

    try:
        # Confirmar as alterações e fechar a conexão
        cursor.execute(query, valores)
        conexao.commit()
    except Exception as e:
        print('='*100)
        print(e)
        print('='*100)
        messages.add_message(request, constants.ERROR, 'Erro ao tentar cadastrar o KIT!')
        conexao.close()
        return redirect('index-ferramentas')
    
    # Obtem o ultimo CODID cadastrado
    comando = f'''
    SELECT TOP 1 CODID
    FROM MATERIAIS
    ORDER BY CODID DESC;
    '''
    
    df_codid = pd.read_sql(comando, conexao)
    codid_kit = df_codid['CODID'][0]
    
    
    # Cria os produtos agregagos na composição
    try:
        contador = 1
        for codid in lists_codid:
            if contador == 1:
                valores = [
                    (str(codid), str(codid_kit), str(qtd_codid_1), 0, 'UN', 1, 0, 0, valor_agregado_kit1)
                ]
            elif contador == 2:
                valores = [
                    (str(codid), str(codid_kit), str(qtd_codid_2), 0, 'UN', 1, 0, 0, valor_agregado_kit2)
                ]
            elif contador == 3:
                valores = [
                    (str(codid), str(codid_kit), str(qtd_codid_3), 0, 'UN', 1, 0, 0, valor_agregado_kit3)
                ]

            # Crie a consulta INSERT
            query = """
            INSERT INTO MATERIAIS_AGREGADOS (CODID_AGREG, CODID, QUANT, PERCENTUAL, UNI_CODIGO, FATOR, CALCULO, QUANTNF, VALOR_AGREG)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            # Execute a consulta INSERT com os valores fornecidos
            cursor.executemany(query, valores)

            # Confirme a transação e feche a conexão
            conexao.commit()
            
            contador += 1
        conexao.close()
    except Exception as e:
        print(e)
        messages.add_message(request, constants.ERROR, 'Erro ao tentar cadastrar os produtos agregados na composição!')
        return redirect('index-ferramentas')
    
    
    novo_conteudo = f'''
    COMPRIMENTO | LARGURA | ALTURA - CODID {codid_1}
    CODID {codid_1} | {dimensao_codids_list[0]['COMPRIMENTO']} | {dimensao_codids_list[0]['LARGURA']} | {dimensao_codids_list[0]['ALTURA']}
    
    COMPRIMENTO | LARGURA | ALTURA - CODID {codid_2}
    CODID {codid_2} | {dimensao_codids_list[1]['COMPRIMENTO']} | {dimensao_codids_list[1]['LARGURA']} | {dimensao_codids_list[1]['ALTURA']}
    
    COMPRIMENTO | LARGURA | ALTURA - CODID {codid_3}
    
    CODID {codid_3} | {dimensao_codids_list[2]['COMPRIMENTO']} | {dimensao_codids_list[2]['LARGURA']} | {dimensao_codids_list[2]['ALTURA']}
    
    ------------------------------------------------------------------------------------------------------------------------
    
    DESCRIÇÃO - CODID {codid_1}
    
    {descricao_codid_1}

    ------------------------------------------------------------------------------------------------------------------------
    
    DESCRIÇÃO - CODID {codid_2}
    
    {descricao_codid_2}
    
    ------------------------------------------------------------------------------------------------------------------------
    
    DESCRIÇÃO - CODID {codid_3}
    
    {descricao_codid_3}
    '''
    
    return novo_conteudo