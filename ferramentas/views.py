from django.shortcuts import render, redirect
from django.http import HttpResponse
from scripts import baixar_fotos_codid, remover_fotos_codid
import tempfile
import requests
import zipfile
from ferramentas.scripts import catalogo_requerido
from django.contrib.messages import constants
from django.contrib import messages
import random
from scripts.connect_to_database import get_connection
import pyodbc
import pandas as pd
from datetime import datetime
import os
from io import BytesIO
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv


def index(request):
    return render(request, 'index-ferramentas.html')

def baixar_fotos(request):
    codid = request.POST['input-codid']

    lista_fotos = baixar_fotos_codid.main(codid)
    
    if lista_fotos == False:
        messages.add_message(request, constants.ERROR, 'O CODID fornecido não tem foto!')
        return redirect('index-ferramentas')
    
    # Crie um arquivo temporário para armazenar as fotos baixadas
    temp = tempfile.TemporaryFile()
    with zipfile.ZipFile(temp, 'w') as zip_file:
        for i, foto_url in enumerate(lista_fotos):
            
            # Trata as fotos
            if not foto_url.startswith('http://') and not foto_url.startswith('https://'):
                foto_url = 'https://' + foto_url
            
            # Faça o download da foto
            foto_response = requests.get(foto_url)
            
            # Adicione a foto ao arquivo zip com um nome de arquivo único
            nome_arquivo = f'foto{i+1}-{codid}.jpg'
            zip_file.writestr(nome_arquivo, foto_response.content)
    
    temp.seek(0)
    
    # Crie uma resposta HTTP para o arquivo zip
    response = HttpResponse(temp, content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="fotos-{codid}.zip"'

    return response

def remover_fotos(request):
    codid = request.POST['input-codid']
    
    status = remover_fotos_codid.main(codid)
    if status:
        messages.add_message(request, constants.SUCCESS, 'Fotos deletadas!')
        return redirect('index-ferramentas')
    else:
        messages.add_message(request, constants.ERROR, 'O Produto está sem foto!')
        return redirect('index-ferramentas')
    
def remover_catalogo_requerido(request):
    
    resposta = catalogo_requerido.main()
    
    if resposta:
        messages.add_message(request, constants.SUCCESS, 'Sucesso!')
        return redirect('index-ferramentas')
    else:
        messages.add_message(request, constants.ERROR, 'Erro!')
        return redirect('index-ferramentas')
    
def alterar_ean(request):
    autoid = request.POST.get('autoid')
    ean = request.POST.get('ean')
    
    try:
        connection = get_connection()
        conexao = pyodbc.connect(connection)
        cursor = conexao.cursor()
    
        comando = f'''
        UPDATE PUBLICA_PRODUTO
        SET EAN = '{ean}'
        WHERE AUTOID = '{autoid}'
        '''
    
        cursor.execute(comando)
        conexao.commit()
        
        messages.add_message(request, constants.SUCCESS, 'EAN Alterado!')
        return redirect('index-ferramentas')
    except:
        messages.add_message(request, constants.ERROR, 'Erro!')
        return redirect('index-ferramentas')
    
def remover_mlb(request):    
    valores_textarea = request.POST.get('mlb-remover-aton')
    valores_list = valores_textarea.split('\n')
    valores_list = [valor.strip() for valor in valores_list]
    valores_list = [item for item in valores_list if item != '']
    
    contador = 0
    for mlb_vinculacao in valores_list:
        if not mlb_vinculacao.startswith('MLB'):
            messages.add_message(request, constants.ERROR, f'MLB: {mlb_vinculacao} Inválido!')
            return redirect('index-ferramentas')
        
        try:
            connection = get_connection()
            conexao = pyodbc.connect(connection)
            cursor = conexao.cursor()
        
            comando = f'''
            SELECT * FROM ECOM_SKU
            WHERE ORIGEM_ID IN('8','9','10')
            AND SKU = '{mlb_vinculacao}'
            '''
            
            df = pd.read_sql(comando, conexao)
            
            if len(df) <= 0:
                continue

            
            comando = f'''
            DELETE FROM ECOM_SKU
            WHERE ORIGEM_ID IN('8','9','10')
            AND SKU = '{mlb_vinculacao}'
            '''
            
            cursor.execute(comando)
            conexao.commit()
            
            contador += 1
        except:
            messages.add_message(request, constants.INFO, 'Erro no servidor!')
            return redirect('index-ferramentas')
    
    messages.add_message(request, constants.SUCCESS, f'{str(contador)} MLBs Removidos!')
    return redirect('index-ferramentas')
    
def remover_sku_netshoes(request):
    if request.method == 'POST':
        sku_lojista = str(request.POST.get('sku-netshoes-vinculacao'))
        loja = str(request.POST.get('loja'))
        
        try:
            connection = get_connection()
            conexao = pyodbc.connect(connection)
            cursor = conexao.cursor()
            
            comando = f'''
            SELECT * FROM ECOM_SKU
            WHERE ORIGEM_ID = '{loja}'
            AND SKU = '{sku_lojista}'
            '''
            
            df = pd.read_sql(comando, conexao)
            
            if len(df) <= 0:
                messages.add_message(request, constants.ERROR, 'SKU não encontrado!')
                return redirect('index-ferramentas')
            
            comando = f'''
            DELETE FROM ECOM_SKU
            WHERE ORIGEM_ID = '{loja}'
            AND SKU = '{sku_lojista}'
            '''
            
            cursor.execute(comando)
            cursor.commit()
            
            messages.add_message(request, constants.SUCCESS, 'SKU Removido!')
            return redirect('index-ferramentas')
        except:
            messages.add_message(request, constants.INFO, 'Erro no servidor!')
            return redirect('index-ferramentas')
    
def alterar_custo(request):
    if request.method == 'POST':
        # Coleta id
        codid = request.POST.get('codid-custo')
        
        if str(codid).strip() == '':
            messages.add_message(request, constants.ERROR, 'Campo CODID vazio!')
            return redirect('index-ferramentas')
        
        # Verifica se o produto existe no banco de dados
        connection = get_connection()
        conexao = pyodbc.connect(connection)
        cursor = conexao.cursor()
        
        comando = f'''
        SELECT CODID, VLR_CUSTO FROM MATERIAIS
        WHERE CODID = {codid}
        '''
        check_codid_exists = pd.read_sql(comando, conexao)
        if len(check_codid_exists) <= 0:
            messages.add_message(request, constants.ERROR, 'CODID não existe no Aton!')
            return redirect('index-ferramentas')
        
        custo = str(check_codid_exists['VLR_CUSTO'][0]).replace('.', ',')
        
        comando = f'''
        SELECT TOP 1 URL FROM MATERIAIS_IMAGENS
        WHERE CODID = {codid}
        '''
            
        df_url_imagem = pd.read_sql(comando, conexao)
        
        
        # Retorna imagem
        if 'btn-visualizar' in request.POST:
            # Verifica se tem imagem
            if len(df_url_imagem) <= 0:
                messages.add_message(request, constants.ERROR, 'CODID não tem imagem!')
                return redirect('index-ferramentas')
            
            url_imagem = df_url_imagem['URL'][0]
            
            if not url_imagem.startswith('http://') and not url_imagem.startswith('https://'):
                url_imagem = 'https://' + url_imagem
            
            return render(request, 'index-ferramentas.html', {'url_imagem': url_imagem, 'codid_custo': codid, 'custo': custo})
        
        if 'btn-alterar' in request.POST:
            novo_custo = str(request.POST.get('novo-custo')).strip()
            novo_custo = novo_custo.replace(',', '.')
            
            if novo_custo == '':
                messages.add_message(request, constants.ERROR, 'Campo NOVO CUSTO vazio!')
                return redirect('index-ferramentas')
            
            try:
                comando = f'''
                UPDATE MATERIAIS
                SET VLR_CUSTO = '{novo_custo}'
                WHERE CODID = {codid}
                '''
                
                cursor.execute(comando)
                cursor.commit()
                
                load_dotenv()

                client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])
                SLACK_CHANNEL_ID='C030X3UMR3M'

                novo_custo = str(novo_custo).replace('.', ',')
                message = f'ALTERAÇÃO DE CUSTO! :currency_exchange:\nCODID: {codid} alterado de R$ {custo} para R$ {novo_custo}\n'
                
                try:
                    client.chat_postMessage(channel=SLACK_CHANNEL_ID,text=message)
                except SlackApiError as e:
                    print("Error sending message: {}".format(e))
                    
                    
                # Verifica se tem imagem
                if len(df_url_imagem) > 0:
                    url_imagem = df_url_imagem['URL'][0]
            
                    if not url_imagem.startswith('http://') and not url_imagem.startswith('https://'):
                        url_imagem = 'https://' + url_imagem
                        
                    # Baixa a imagem para upload no slack
                    response = requests.get(url_imagem)
                    if response.status_code == 200:
                        with open(f'imagem.jpg', 'wb') as arquivo:
                            arquivo.write(response.content)
                        
                        # Envia para o slack
                        try:
                            client.files_upload_v2(channel=SLACK_CHANNEL_ID, file=f'imagem.jpg')
                        except SlackApiError as e:
                            print("Error sending message: {}".format(e))
                            
                        # Remove imagem
                        os.remove('imagem.jpg')
                                
                messages.add_message(request, constants.SUCCESS, 'Custo alterado!')
                return render(request, 'index-ferramentas.html', {'codid_custo': codid})
            except:
                messages.add_message(request, constants.INFO, 'Erro no servidor!')
                return redirect('index-ferramentas')
            
def baixar_planilha_via_sql(request):
    if request.method == 'POST':
        sql_comando = str(request.POST.get('sql-comando')).strip()
        
        if not sql_comando.startswith('SELECT'):
            messages.add_message(request, constants.ERROR, 'Comando SQL inválido!')
            return redirect('index-ferramentas')
        
        connection = get_connection()
        conexao = pyodbc.connect(connection)
        
        comando = f'''
        {sql_comando}
        '''

        try:
            df_temp = pd.read_sql(comando, conexao)
        except Exception as e:
            messages.add_message(request, constants.ERROR, f'Erro no comando SQL: {e}')
            return redirect('index-ferramentas')
        
        excel_bytes = BytesIO()
        df_temp.to_excel(excel_bytes, index=False)
        excel_bytes.seek(0)
        bytes_data = excel_bytes.getvalue()
        
        response = HttpResponse(bytes_data, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = f'attachment; filename="nome_temporario.xlsx"'
        return response
    
def gerar_ean_aleatorio(request):
    if request.method == 'POST':
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
        
        try:
            connection = get_connection()
            conexao = pyodbc.connect(connection)
            cursor = conexao.cursor()
    
            comando = f'''
            SELECT EAN
            FROM PUBLICA_PRODUTO
            WHERE FLAG = '-9'
            '''
            
            df_ean = pd.read_sql(comando, conexao)
            df_ean_list = df_ean['EAN'].tolist()
            df_ean_stripped_list = [item.strip() for item in df_ean_list]
            
        except:
            messages.add_message(request, constants.ERROR, 'Erro ao tentar acessar o Banco de Dados!')
            return redirect('index-ferramentas')
        
        while True:
            codigo_produto_aleatorio = ''.join(random.choices('0123456789', k=9))
            ean_valido_brasileiro = gerar_ean_brasileiro(codigo_produto_aleatorio)
            
            if ean_valido_brasileiro not in df_ean_stripped_list:
                break
        
        return render(request, 'index-ferramentas.html', {'ean_gerado': ean_valido_brasileiro})
    
def inativar_produtos_aton(request):    
    valores_textarea = request.POST.get('codid-inativar-produtos')
    valores_list = valores_textarea.split('\n')
    valores_list = [valor.strip() for valor in valores_list]
    valores_list = [item for item in valores_list if item != '']
    
    contador = 0
    for codid in valores_list:
        if not codid.isdigit():
            messages.add_message(request, constants.ERROR, f'CODID: {codid} Inválido!')
            return redirect('index-ferramentas')
        
        try:
            connection = get_connection()
            conexao = pyodbc.connect(connection)
            cursor = conexao.cursor()
        
            comando = f'''
            SELECT CODID
            FROM MATERIAIS
            WHERE CODID = '{codid}'
            AND INATIVO = 'N'
            '''
            
            df = pd.read_sql(comando, conexao)
            
            if len(df) <= 0:
                continue

            
            comando = f'''
            UPDATE MATERIAIS
            SET INATIVO = 'S'
            WHERE CODID = '{codid}'
            '''
            
            cursor.execute(comando)
            conexao.commit()
            
            contador += 1
        except:
            messages.add_message(request, constants.INFO, 'Erro no servidor!')
            return redirect('index-ferramentas')
    
    messages.add_message(request, constants.SUCCESS, f'{str(contador)} CODID inativdos!')
    return redirect('index-ferramentas')

def cadastrar_kit(request):
    connection = get_connection()
    conexao = pyodbc.connect(connection)
    cursor = conexao.cursor()

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
    contador = 1
    for codid in lists_codid:
        
        comando = f'''
        SELECT CODID, COD_INTERNO, INATIVO, DESMEMBRA, PESO, DESCRICAO, DESCRITIVO
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
        
        # Soma peso
        if contador == 1:
            peso_kit_list.append(df['PESO'][0] * int(qtd_codid_1))

        elif contador == 2: 
            peso_kit_list.append(df['PESO'][0] * int(qtd_codid_2))

        elif contador == 3:
            peso_kit_list.append(df['PESO'][0] * int(qtd_codid_3))

        contador+= 1
    
    # Peso
    peso_kit = round(sum(peso_kit_list), 2)
        
    # DF com os dados dos CODID
    comando = f'''
    SELECT CODID, COD_INTERNO, INATIVO, DESMEMBRA, PESO, DESCRICAO, DESCRITIVO
    FROM MATERIAIS
    WHERE CODID IN ('{codid_1}', '{codid_2}', '{codid_3}')
    '''
    
    df = pd.read_sql(comando, conexao)


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
        nome_kit = f'KIT {qtd_codid_1} {nome_codid_1} {qtd_codid_2} {nome_codid_2} {qtd_codid_3} {nome_codid_3}'
        descritivo_kit = f'''
        {nome_codid_1.title()} + {nome_codid_2.title()} + {nome_codid_3.title()}
        
        PRONTA ENTREGA - COM NOTA FISCAL - TESTADO - COM GARANTIA

        Temos o cuidado de embalar os produtos individualmente, com material de proteção de alta qualidade, certificando que ele chegue até ao seu destino intacto, minimizando possíveis danos durante o transporte.

        Todos os produtos são testados, analisados e possuem nota fiscal, garantindo mais confiabilidade com a melhor qualidade e preço, além disso caso haja alguma inconformidade com o produto basta nos acionar que resolveremos.

        Nossos produtos estão a pronta entrega e sempre são despachados em até um dia útil, garantindo agilidade no processo de compra e uma boa experiência para o cliente.

        Nós somos excelência em atendimentos aos nossos clientes, envie suas dúvidas ou perguntas, de preferência em nosso chat, atenderemos com agilidade e empenho para resolver da melhor maneira.

        SOBRE O PRODUTO:
        '''
    elif codid_2_informado:
        nome_codid_2 = df['DESCRICAO'][1].strip()
        nome_codid_1 = df['DESCRICAO'][0].strip()
        descricao_codid_2 = df['DESCRITIVO'][1].strip()
        descricao_codid_1 = df['DESCRITIVO'][0].strip()
        nome_kit = f'KIT {qtd_codid_1} {nome_codid_1} {qtd_codid_2} {nome_codid_2}'
        descritivo_kit = f'''
        {nome_codid_1.title()} + {nome_codid_2.title()}
        
        PRONTA ENTREGA - COM NOTA FISCAL - TESTADO - COM GARANTIA

        Temos o cuidado de embalar os produtos individualmente, com material de proteção de alta qualidade, certificando que ele chegue até ao seu destino intacto, minimizando possíveis danos durante o transporte.

        Todos os produtos são testados, analisados e possuem nota fiscal, garantindo mais confiabilidade com a melhor qualidade e preço, além disso caso haja alguma inconformidade com o produto basta nos acionar que resolveremos.

        Nossos produtos estão a pronta entrega e sempre são despachados em até um dia útil, garantindo agilidade no processo de compra e uma boa experiência para o cliente.

        Nós somos excelência em atendimentos aos nossos clientes, envie suas dúvidas ou perguntas, de preferência em nosso chat, atenderemos com agilidade e empenho para resolver da melhor maneira.

        SOBRE O PRODUTO:
        '''
    else:
        nome_codid_1 = df['DESCRICAO'][0].strip()
        descricao_codid_1 = df['DESCRITIVO'][0].strip()
        nome_kit = f'KIT {qtd_codid_1} {nome_codid_1}'
        descritivo_kit = f'''
        {nome_codid_1.title()}
        
        PRONTA ENTREGA - COM NOTA FISCAL - TESTADO - COM GARANTIA

        Temos o cuidado de embalar os produtos individualmente, com material de proteção de alta qualidade, certificando que ele chegue até ao seu destino intacto, minimizando possíveis danos durante o transporte.

        Todos os produtos são testados, analisados e possuem nota fiscal, garantindo mais confiabilidade com a melhor qualidade e preço, além disso caso haja alguma inconformidade com o produto basta nos acionar que resolveremos.

        Nossos produtos estão a pronta entrega e sempre são despachados em até um dia útil, garantindo agilidade no processo de compra e uma boa experiência para o cliente.

        Nós somos excelência em atendimentos aos nossos clientes, envie suas dúvidas ou perguntas, de preferência em nosso chat, atenderemos com agilidade e empenho para resolver da melhor maneira.

        SOBRE O PRODUTO:
        '''
    
    
        
        
    # Criar descrição
    return redirect('index-ferramentas')