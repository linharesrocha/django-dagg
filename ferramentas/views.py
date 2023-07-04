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
    
def alterar_custo(request):
    if request.method == 'POST':
        # Coleta id
        codid = request.POST.get('codid-custo')
        
        # Verifica se o produto existe no banco de dados
        connection = get_connection()
        conexao = pyodbc.connect(connection)
        cursor = conexao.cursor()
        
        comando = f'''
        SELECT CODID FROM MATERIAIS
        WHERE CODID = {codid}
        '''
        check_codid_exists = pd.read_sql(comando, conexao)
        if len(check_codid_exists) <= 0:
            messages.add_message(request, constants.ERROR, 'CODID não existe no Aton!')
            return redirect('index-ferramentas')
        
        # Retorna imagem
        if 'btn-visualizar' in request.POST:
            connection = get_connection()
            
        
            comando = f'''
            SELECT TOP 1 URL FROM MATERIAIS_IMAGENS
            WHERE CODID = {codid}
            '''
            
            df_url_imagem = pd.read_sql(comando, conexao)
            
            # Verifica se tem imagem
            if len(df_url_imagem) <= 0:
                messages.add_message(request, constants.ERROR, 'CODID não tem imagem!')
                return redirect('index-ferramentas')
            
            url_imagem = df_url_imagem['URL'][0]
            
            if not url_imagem.startswith('http://') and not url_imagem.startswith('https://'):
                url_imagem = 'https://' + url_imagem
            
            return render(request, 'index-ferramentas.html', {'url_imagem': url_imagem, 'codid_custo': codid})