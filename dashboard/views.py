from django.shortcuts import render
from scripts import verifica_categorias_duplicadas_aton, vinculacoes_aton_marketplace
from django.http import HttpResponse

def index(request):
    return render(request, 'dashboard/index.html')


def atualiza_dados(request):
    download = False
    num_linhas_duplicadas = verifica_categorias_duplicadas_aton.main(download)
    num_vinculacoes_desconectadas = vinculacoes_aton_marketplace.main(download)
    
    contexto = {'num_linhas_duplicadas' : num_linhas_duplicadas, 'num_vinculacoes_desconectadas': num_vinculacoes_desconectadas}
    return render(request, 'dashboard/index.html', contexto)


def gerar_categorias_duplicadas(request):
    download = True
    
    nome_planilha = 'categorias_duplicadas.xlsx'
    
    # Chame a função que gera o arquvio Excel
    arquivo_excel = verifica_categorias_duplicadas_aton.main(download)
    
    # Crie uma resposta HTTP para retornar o arquivo ao usuário
    response = HttpResponse(arquivo_excel, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = f'attachment; filename="{nome_planilha}"'
    return response

def gerar_vinculacoes_desconectadas(request):
    download = True
    
    nome_planilha = 'vinculacoes_desconectadas.xlsx'
    
    arquivo_excel = vinculacoes_aton_marketplace.main(download)
    
    # Crie uma resposta HTTP para retornar o arquivo ao usuário
    response = HttpResponse(arquivo_excel, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = f'attachment; filename="{nome_planilha}"'
    return response