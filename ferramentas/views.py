from django.shortcuts import render, redirect
from django.http import HttpResponse
from scripts import baixar_fotos_codid, remover_fotos_codid
import tempfile
import requests
import zipfile
from ferramentas.scripts import catalogo_requerido
from django.contrib.messages import constants
from django.contrib import messages
from scripts.connect_to_database import get_connection
import pyodbc
import pandas as pd
import os
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
    mlb_vinculacao = str(request.POST.get('mlb-vinculacao'))
    
    if not mlb_vinculacao.startswith('MLB'):
        messages.add_message(request, constants.ERROR, 'MLB Inválido!')
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
            messages.add_message(request, constants.ERROR, 'MLB não encontrado!')
            return redirect('index-ferramentas')

        
        comando = f'''
        DELETE FROM ECOM_SKU
        WHERE ORIGEM_ID IN('8','9','10')
        AND SKU = '{mlb_vinculacao}'
        '''
        
        cursor.execute(comando)
        conexao.commit()
        
        messages.add_message(request, constants.SUCCESS, 'MLB Removido!')
        return redirect('index-ferramentas')
    except:
        messages.add_message(request, constants.INFO, 'Erro no servidor!')
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