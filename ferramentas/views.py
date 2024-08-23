from django.shortcuts import render, redirect
from django.http import HttpResponse
from scripts import baixar_fotos_codid, remover_fotos_codid
import tempfile
import requests
import zipfile
from ferramentas.scripts import catalogo_requerido, func_pedido_transferencia
from django.contrib.messages import constants
from django.contrib import messages
import random
from scripts.connect_to_database import get_connection
import pyodbc
import pandas as pd
from datetime import datetime
import os
from io import BytesIO
import io
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from .models import ArquivoAton, RegistroClique, DataUltimoBalanco
from dotenv import load_dotenv
from django.http import JsonResponse
from django.utils import timezone



def index(request):
    return render(request, 'index-ferramentas.html')

def obter_data_hora_clique(request):
    ultimo_clique = RegistroClique.objects.latest('data_hora')
    data_hora_clique = ultimo_clique.data_hora.strftime('%d-%m-%Y %H:%M:%S')
    return JsonResponse({'data_hora': data_hora_clique})

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
    
    messages.add_message(request, constants.SUCCESS, f'{str(contador)} CODID inativados!')
    return redirect('index-ferramentas')

def cadastrar_kit(request):
    
    from ferramentas.scripts.func_cadastrar_kit import main
    
    response = main(request=request)
    
    if not isinstance(response, str):
        return redirect('index-ferramentas')
    
    
    arquivo_txt = "arquivo-kit-tmp.txt"

    try:
        with open(arquivo_txt, 'w') as file:
            file.write(response)
            
        with open(arquivo_txt, 'rb') as file:
            response = HttpResponse(file.read(), content_type='text/plain')
            response['Content-Disposition'] = 'attachment; filename="TMP-KIT-CADASTRADO-SUCESSO.txt"'

        os.remove(arquivo_txt)
        return response
    except Exception as e:
        print(e)
        messages.add_message(request, constants.ERROR, 'Erro ao tentar enviar o arquivo com as descrições e dimensões! Mas o KIT foi cadastrado!')
        return redirect('index-ferramentas')
    
def copiar_atributos(request):    
    if request.method == 'POST':
        connection = get_connection()
        conexao = pyodbc.connect(connection)
        cursor = conexao.cursor()
        
        codid_1 = str(request.POST.get('codid1-atributo'))
        codid_2 = str(request.POST.get('codid2-atributo'))
        marketplace = str(request.POST.get('marketplace'))
        list_codid = [codid_1, codid_2]
        
        # Verifica se os CODID são os mesmos
        if codid_1 == codid_2:
            messages.add_message(request, constants.ERROR, 'CODID não podem ser iguais!')
            return redirect('index-ferramentas')
        
        # Verifica se os CODID são válidos
        for codid in list_codid:
            comando = f'''
            SELECT CODID
            FROM MATERIAIS
            WHERE CODID = '{codid}'
            AND INATIVO = 'N'
            '''
            
            df = pd.read_sql(comando, conexao)  
            
            # Verifica se existe no banco de dados
            if len(df) <= 0:
                messages.add_message(request, constants.ERROR, f'CODID: {codid} não existe no Aton!')
                return redirect('index-ferramentas')
            
        # Válida se o CODID1 tem atributos no marketplace
        comando = f'''
        SELECT * 
        FROM MATERIAIS_ESPECIFICACOES
        WHERE CODID = '{codid_1}'
        AND API = '{marketplace}'
        '''
        
        df_check_codid_1 = pd.read_sql(comando, conexao)
        if len(df_check_codid_1) <= 0:
            messages.add_message(request, constants.ERROR, f'CODID: {codid_1} não tem atributos no marketplace {marketplace}!')
            return redirect('index-ferramentas')
        else:
            cursor.execute(comando)
            resultados = cursor.fetchall()
            

        # Inserir os resultados copiados na tabela com CODID = 11
        for resultado in resultados:
            # Adaptar a inserção de acordo com a estrutura da sua tabela
            insercao = f"""
            INSERT INTO MATERIAIS_ESPECIFICACOES (CODID, TIPO, VALOR, PRODUTO, SKU, API, IDTIPO, TIPODADO, ALLOW_VARIATIONS, VALOR_ID, QTY_UNID)
            VALUES ('{str(codid_2)}', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(insercao, resultado.TIPO, resultado.VALOR, resultado.PRODUTO, resultado.SKU, resultado.API, resultado.IDTIPO, resultado.TIPODADO, resultado.ALLOW_VARIATIONS, resultado.VALOR_ID, resultado.QTY_UNID)

        # Confirmar as alterações e fechar a conexão
        conexao.commit()
        conexao.close()
        
        messages.add_message(request, constants.SUCCESS, f'Atributos do CODID {codid_1} [{marketplace}] copiados para o CODID {codid_2}!')
        return redirect('index-ferramentas')
    
def atualizar_aton(request):
    if request.method == 'POST':
        # Caso a requisição seja para enviar arquivo
        if 'btn-enviar-arquivos-aton' in request.POST:
            arquivos_enviados = request.FILES.getlist('formFile')
            
            # Confere se tem 3 itens
            if len(arquivos_enviados) != 3:
                messages.add_message(request, constants.ERROR, 'Erro! Você deve enviar 3 arquivos! Ambar.exe, AtonECom.exe, AtonPublica.exe')
                return redirect('index-ferramentas')

            list_upload_check = ['Ambar.exe', 'AtonECom.exe', 'AtonPublica.exe']
            pasta_atualizacao = os.path.join('ferramentas', 'atualizacao-aton')
            
            for arquivo_enviado in arquivos_enviados:
                if arquivo_enviado.name not in list_upload_check:
                    messages.add_message(request, constants.ERROR, f'Arquivo {arquivo_enviado.name} não permitido! Arquivos permitidos: Ambar.exe, AtonECom.exe, AtonPublica.exe')
                    return redirect('index-ferramentas')
                else:
                    list_upload_check.remove(arquivo_enviado.name)
                    
                    # Remove caso o arquivo já exista
                    caminho_arquivo = os.path.join(pasta_atualizacao, arquivo_enviado.name)
                    if os.path.exists(caminho_arquivo):
                        os.remove(caminho_arquivo)
                    
                
                novo_arquivo = ArquivoAton(arquivo=arquivo_enviado)
                novo_arquivo.save()
            
            # Registra a hora do envio
            data_hora_clique = RegistroClique.objects.create()
            messages.add_message(request, constants.SUCCESS, 'Arquivos enviados com sucesso!')
            return render(request, 'index-ferramentas.html', {'Message': 'Nova data salva, atualize a página para ver a data e hora do último envio!'})
        
        elif 'btn-baixar-arquivos-aton' in request.POST:
            # Lista de arquivos permitidos
            list_upload_check = ['Ambar.exe', 'AtonECom.exe', 'AtonPublica.exe']
            pasta_atualizacao = os.path.join('ferramentas', 'atualizacao-aton')
            print(pasta_atualizacao)

            # Verificar se os arquivos permitidos existem
            arquivos_faltantes = [arquivo for arquivo in list_upload_check if not os.path.exists(os.path.join(pasta_atualizacao, arquivo))]
            print(os.path.exists(os.path.join(pasta_atualizacao)))
            print(arquivos_faltantes)
            if arquivos_faltantes:
                messages.add_message(request, constants.ERROR, f'Alguns arquivos estão faltando: {", ".join(arquivos_faltantes)}')
                return redirect('index-ferramentas')

            # Criação do arquivo ZIP em memória
            buffer = io.BytesIO()
            with zipfile.ZipFile(buffer, 'w') as zip_file:
                for arquivo in list_upload_check:
                    caminho_arquivo = os.path.join(pasta_atualizacao, arquivo)
                    zip_file.write(caminho_arquivo, arquivo)

            # Preparar a resposta HTTP com o arquivo ZIP
            response = HttpResponse(content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename="arquivos_aton.zip"'
            response.write(buffer.getvalue())

            return response
    return redirect('index-ferramentas')


def consulta_mlb_vinculado(request):
    if request.method == 'POST':
        connection = get_connection()
        conexao = pyodbc.connect(connection)
        cursor = conexao.cursor()
            
        mlb = str(request.POST.get('mlb-vinculacao'))
        marketplace = str(request.POST.get('marketplace'))
    
        
        if 'consultar-vinculacao' in request.POST:
            try:
                comando = f'''
                SELECT AUTOID, API, CATEG_MKTP_DESC, DEPARTAMENTO, PRODUTO_TIPO, CATEG_NOME, CATEG_ATON
                FROM CATEGORIAS_MKTP A
                LEFT JOIN ECOM_CATEGORIAS B ON A.CATEG_ATON = B.CATEG_ID
                WHERE CATEG_ATON = '{mlb}'
                AND API != 'Cnova'
                '''
                
                # Verifica se houve resultado
                df = pd.read_sql(comando, conexao)
                if len(df) <= 0:
                    messages.add_message(request, constants.ERROR, 'Nenhuma vinculação foi encontrada!')
                    return redirect('index-ferramentas')
                
                # Retorna o resultado para template como tabela
                df_dict_ori = df.to_dict(orient='records')
                df_dict = {'df_dict': df_dict_ori}
                return render(request, 'index-ferramentas.html', df_dict)
                
            except:
                messages.add_message(request, constants.ERROR, 'Erro no servidor!')
                return redirect('index-ferramentas')
        elif 'remover-vinculacao' in request.POST:
            autoid_list = request.POST.getlist('autoid-checkbox')    
            for autoid in autoid_list:
                try:
                    # Deleta
                    comando = f'''
                    DELETE FROM CATEGORIAS_MKTP
                    WHERE AUTOID = '{autoid}'
                    '''
                    
                    cursor.execute(comando)
                    conexao.commit()
                except:
                    messages.add_message(request, constants.ERROR, f'Erro no servidor! Erro ao tentar deleta o AUTOID {autoid}')
                    return redirect('index-ferramentas')
                
            messages.add_message(request, constants.SUCCESS, f'{str(len(autoid_list))} Vinculações removidas!')
            return redirect('index-ferramentas')
        else:
            messages.add_message(request, constants.ERROR, 'Erro no servidor!')
            return redirect('index-ferramentas')
        
        
def criar_pedido_transferencia(request):
    if request.method == 'POST':
        # Obtem os quatro valores do formulario
        empresa_origem = str(request.POST.get('empresa-origem'))
        empresa_destino = str(request.POST.get('empresa-destino'))
        armazem_origem = str(request.POST.get('armazem-origem'))
        armazem_destino = str(request.POST.get('armazem-destino'))
        
        # Le o arquivo xlsx
        try:
            file_transferencia = request.FILES['file']
            df_pedido_transferencia = pd.read_excel(file_transferencia)
        except Exception as e:
            messages.add_message(request, constants.ERROR, f'Erro ao tentar ler o arquivo! {e}')
            return redirect('index-ferramentas')
        
        try:
            df_pedido_transferencia['COD_INTERNO'] = df_pedido_transferencia['COD_INTERNO'].str.strip()
        except:
            messages.add_message(request, constants.ERROR, 'Erro ao ler planilha! Verifique se a primeira coluna se chama "COD_INTERNO" e a segunda coluna se chama "QUANT" ou "Quant."')
            return redirect('index-relatorios')
        
        # Verifica se a primeira coluna se chama COD_INTERNO
        if str(df_pedido_transferencia.columns[0]).upper() != 'COD_INTERNO':
            messages.add_message(request, constants.ERROR, 'A primeira coluna deve se chamar "COD_INTERNO"')
            return redirect('index-relatorios')
        
        # Verifica se a segunda coluna se chama QUANT
        if df_pedido_transferencia.columns[1].upper() != 'QUANT' and str(df_pedido_transferencia.columns[1]) != 'Quant.':
            messages.add_message(request, constants.ERROR, 'A segunda coluna deve se chamar "QUANT" ou "Quant."')
            return redirect('index-relatorios')
        
        df_pedido_transferencia.rename(columns={'quant': 'QUANT', 'Quant.': 'QUANT'}, inplace=True)
        
        func_pedido_transferencia.main(empresa_origem=empresa_origem, empresa_destino=empresa_destino, armazem_origem=armazem_origem, armazem_destino=armazem_destino, df_pedido_transferencia=df_pedido_transferencia)
        
        messages.add_message(request, constants.SUCCESS, 'Pedido de transferência criado com sucesso!')
        return redirect('index-ferramentas')
    

def balanco_estoque(request):
    if request.method == 'POST':
        connection = get_connection()
        conexao = pyodbc.connect(connection)
        cursor = conexao.cursor()
            
        if 'baixar-balanco-produto' in request.POST:
            comando = f'''
            SELECT A.CODID, A.COD_INTERNO, A.DESCRICAO, B.ESTOQUE AS ESTOQUE_ATON
            FROM MATERIAIS A
            LEFT JOIN ESTOQUE_MATERIAIS B ON A.CODID = B.MATERIAL_ID
            WHERE B.ARMAZEM = '1'
            AND A.INATIVO = 'N'
            AND B.ESTOQUE > 0
            AND COD_INTERNO NOT LIKE '%PAI'
            AND DESMEMBRA = 'N'
            AND A.GRUPO != '7'
            ORDER BY DESCRICAO
            '''
            
            df_balanco = pd.read_sql(comando, conexao)
            df_balanco['ESTOQUE_REAL'] = None
            
            # Acessa o banco de dados DataUltimoBalanco
            try:
                queryset = DataUltimoBalanco.objects.all()
                df_data_ultimo_balanco = pd.DataFrame(list(queryset.values()))
                df_balanco = pd.merge(df_balanco, df_data_ultimo_balanco, how='left', left_on='CODID', right_on='codid')
                df_balanco.drop(columns=['codid', 'id'], inplace=True)
                df_balanco.rename(columns={'data_e_hora': 'DT_ULTIMA_CONF'}, inplace=True)
                df_balanco['DT_ULTIMA_CONF'] = df_balanco['DT_ULTIMA_CONF'].dt.strftime('%d-%m-%Y %H:%M:%S')
            except:
                df_balanco['DT_ULTIMA_CONF'] = None    
            
            
            # Formata para bytes
            excel_bytes = BytesIO()
            df_balanco.to_excel(excel_bytes, index=False)
            excel_bytes.seek(0)
            bytes_data = excel_bytes.getvalue()
            
            # Cria data atual
            data_hoje = datetime.today()
            data_formatada = data_hoje.strftime("%Y-%m-%d")

            # Retorna
            response = HttpResponse(bytes_data, content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = f'attachment; filename="{data_formatada}-balanco.xlsx"'
            return response
        
        elif 'importar-balanco-produto' in request.POST:
            try:
                file_balanco = request.FILES['formFile']
            except:
                messages.add_message(request, constants.ERROR, 'Erro ao tentar ler o arquivo!')
                return redirect('index-ferramentas')
            
            df_balanco = pd.read_excel(file_balanco)
            
            # Confere se existe a coluna CODID
            if 'CODID' not in df_balanco.columns:
                messages.add_message(request, constants.ERROR, 'A coluna CODID não existe!')
                return redirect('index-ferramentas')
            
            # Confere se existe a coluna ESTOQUE_REAL
            if 'ESTOQUE_REAL' not in df_balanco.columns:
                messages.add_message(request, constants.ERROR, 'A coluna ESTOQUE_REAL não existe!')
                return redirect('index-ferramentas')
            
            # Deleta o resto das colunas
            df_balanco = df_balanco[['CODID', 'ESTOQUE_REAL']]
            
            # Deixa apenas as linhas que contem numero na coluna ESTOQUE_REAL
            df_balanco = df_balanco[df_balanco['ESTOQUE_REAL'].notnull()]
            
            # Confere se existe string  na coluna ESTOQUE_REAL caso sim retorne
            if df_balanco['ESTOQUE_REAL'].dtype == 'O':
                messages.add_message(request, constants.ERROR, 'A coluna ESTOQUE_REAL não pode conter letras ou caracteres, apenas números!')
                return redirect('index-ferramentas')
            
            # Converte ESTOQUE_REAL para int
            df_balanco['ESTOQUE_REAL'] = df_balanco['ESTOQUE_REAL'].astype(int)
            
            # Itera sobre o dataframe
            for index, row in df_balanco.iterrows():
                codid = row['CODID']
                estoque_real = row['ESTOQUE_REAL']
                
                comando = f'''
                UPDATE ESTOQUE_MATERIAIS
                SET ESTOQUE = '{estoque_real}'
                WHERE ARMAZEM = '1'
                AND MATERIAL_ID = '{codid}'
                '''
                
                cursor.execute(comando)
                conexao.commit()
                
                try:
                    registro = DataUltimoBalanco.objects.get(codid=codid)
                    registro.data_e_hora = timezone.now()
                    registro.save()
                except DataUltimoBalanco.DoesNotExist:
                    DataUltimoBalanco.objects.create(codid=codid)
            
            conexao.close()
            
            messages.add_message(request, constants.SUCCESS, 'Estoque atualizado com sucesso!')
            return redirect('index-ferramentas')
    
        else:
            messages.add_message(request, constants.ERROR, 'Erro no servidor!')
            return redirect('index-ferramentas')
        

def atualizar_info_fiscal_produtos(request):
    if request.method == 'POST':
        connection = get_connection()
        conexao = pyodbc.connect(connection)
        cursor = conexao.cursor()
        cod_interno = request.POST.get('cod_interno')

        # Valida se existe cod_interno
        try:
            comando = f'''
            SELECT COD_INTERNO
            FROM MATERIAIS
            WHERE COD_INTERNO = '{cod_interno}'
            '''

            df = pd.read_sql(comando, conexao)
            if len(df) <= 0:
                messages.add_message(request, constants.ERROR, 'COD_INTERNO não existe no Aton!')
                return redirect('index-ferramentas')
        except:
            messages.add_message(request, constants.ERROR, 'Erro no servidor!')
            return redirect('index-ferramentas')

        if 'btn_consultar_info_fiscal' in request.POST:
            print('oi')
            # Consulta NCM
            comando = f'''
            SELECT CLASS_FISCAL
            FROM MATERIAIS
            WHERE COD_INTERNO = '{cod_interno}'
            '''

            df_ncm = pd.read_sql(comando, conexao)
            if len(df_ncm) > 0:
                ncm = df_ncm['CLASS_FISCAL'][0]
            else:
                ncm = 'Vazio'

            # Consulta ORIGEM
            comando = f'''
            SELECT ORIGEM_TRIB
            FROM MATERIAIS
            WHERE COD_INTERNO = '{cod_interno}'
            '''

            df_origem = pd.read_sql(comando, conexao)
            if len(df_origem) > 0:
                origem = df_origem['ORIGEM_TRIB'][0]
            else:
                origem = 'Vazio'

            # Consulta CEST
            comando = f'''
            SELECT CEST
            FROM MATERIAIS
            WHERE COD_INTERNO = '{cod_interno}'
            '''

            df_cest = pd.read_sql(comando, conexao)
            if len(df_cest) > 0:
                cest = df_cest['CEST'][0]
            else:
                cest = 'Vazio'

            # Consulta TABELA_IMPOSTO
            comando = f'''
            SELECT TABELAIMPOSTO
            FROM MATERIAIS
            WHERE COD_INTERNO = '{cod_interno}'
            '''

            df_tabela_imposto = pd.read_sql(comando, conexao)
            if len(df_tabela_imposto) > 0:
                tabela_imposto = df_tabela_imposto['TABELAIMPOSTO'][0]

                if str(tabela_imposto) == '1':
                    tabela_imposto = 'Tabela Simples'
                elif str(tabela_imposto) == '2':
                    tabela_imposto = 'Tabela com ST'
            else:
                tabela_imposto = 'Vazio'

            # remove strip
            ncm = str(ncm).strip()
            origem = str(origem).strip()
            cest = str(cest).strip()
            tabela_imposto = str(tabela_imposto).strip()

            return render(request, 'index-ferramentas.html', {'cod_interno': cod_interno, 'ncm': ncm, 'origem': origem, 'cest': cest, 'tabela_imposto': tabela_imposto})


        if 'btn_alterar_info_fiscal' in request.POST:
            ncm = request.POST.get('ncm')
            origem = request.POST.get('origem')
            cest = request.POST.get('cest')
            tabela_imposto = request.POST.get('tabela_imposto')

            # removee strip
            ncm = str(ncm).strip()
            origem = str(origem).strip()
            cest = str(cest).strip()

            
            # NCM
            if str(ncm) == 'Apagar':
                comando = f'''
                    UPDATE MATERIAIS
                    SET CLASS_FISCAL = NULL
                    WHERE COD_INTERNO = '{cod_interno}'
                    '''

                cursor.execute(comando)
                conexao.commit()
            elif ncm != '':
                if len(ncm) != 8:
                    messages.add_message(request, constants.ERROR, 'NCM deve ter exatamente 8 digitos!')
                    return redirect('index-ferramentas')
                
                try:
                    # Atualiza NCM
                    comando = f'''
                    UPDATE MATERIAIS
                    SET CLASS_FISCAL = '{ncm}'
                    WHERE COD_INTERNO = '{cod_interno}'
                    '''

                    cursor.execute(comando)
                    conexao.commit()
                except:
                    messages.add_message(request, constants.ERROR, 'Erro ao atualizar NCM!')
                    return redirect('index-ferramentas')
            
            # ORIGEM
            if str(origem) == 'Apagar':
                comando = f'''
                    UPDATE MATERIAIS
                    SET ORIGEM_TRIB = NULL
                    WHERE COD_INTERNO = '{cod_interno}'
                    '''

                cursor.execute(comando)
                conexao.commit()
            elif origem != '':
                if len(origem) != 1:
                    messages.add_message(request, constants.ERROR, 'Origem deve ter 1 digito!')
                    return redirect('index-ferramentas')
                
                # Atualiza ORIGEM
                try:
                    comando = f'''
                    UPDATE MATERIAIS
                    SET ORIGEM_TRIB = '{origem}'
                    WHERE COD_INTERNO = '{cod_interno}'
                    '''

                    cursor.execute(comando)
                    conexao.commit()
                except:
                    messages.add_message(request, constants.ERROR, 'Erro ao atualizar ORIGEM!')
                    return redirect('index-ferramentas')
            
            # CEST
            if str(cest) == 'Apagar':
                comando = f'''
                    UPDATE MATERIAIS
                    SET CEST = NULL
                    WHERE COD_INTERNO = '{cod_interno}'
                    '''

                cursor.execute(comando)
                conexao.commit()
            elif cest != '':
                if len(cest) != 7:
                    messages.add_message(request, constants.ERROR, 'CEST deve ter 7 digitos!')
                    return redirect('index-ferramentas')
                
                # Atualiza CEST
                try:
                    comando = f'''
                    UPDATE MATERIAIS
                    SET CEST = '{cest}'
                    WHERE COD_INTERNO = '{cod_interno}'
                    '''

                    cursor.execute(comando)
                    conexao.commit()
                except:
                    messages.add_message(request, constants.ERROR, 'Erro ao atualizar CEST!')
                    return redirect('index-ferramentas')
            
            # Atualiza TABELA_IMPOSTO
            if tabela_imposto != None:
                try:
                    comando = f'''
                    UPDATE MATERIAIS
                    SET TABELAIMPOSTO = '{tabela_imposto}'
                    WHERE COD_INTERNO = '{cod_interno}'
                    '''

                    cursor.execute(comando)
                    conexao.commit()
                except:
                    messages.add_message(request, constants.ERROR, 'Erro ao atualizar TABELA_IMPOSTO!')
                    return redirect('index-ferramentas')

            messages.add_message(request, constants.SUCCESS, 'Informações fiscais atualizadas com sucesso!')
            return redirect('index-ferramentas')

