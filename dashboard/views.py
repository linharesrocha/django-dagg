from django.shortcuts import render
from scripts import verifica_categorias_duplicadas_aton, vinculacoes_desativadas_aton_marketplace, vinculacoes_erradas_full_ecom_sku, inativos_com_estoque_marktetplace, produtos_kit_sem_desmembra, inativos_com_estoque_aton
from django.http import HttpResponse

def index(request):
    return render(request, 'dashboard/index.html')


def atualiza_dados(request):
    download = False
    num_linhas_duplicadas = verifica_categorias_duplicadas_aton.main(download)
    num_vinculacoes_desconectadas = vinculacoes_desativadas_aton_marketplace.main(download)
    num_vinculacoes_erradas_full = vinculacoes_erradas_full_ecom_sku.main(download)
    num_inativos_com_estoque_mktp = inativos_com_estoque_marktetplace.main(download)
    num_produtos_kit_sem_desmembra = produtos_kit_sem_desmembra.main(download)
    num_inativos_com_estoque_aton = inativos_com_estoque_aton.main(download)
    
    contexto = {'num_linhas_duplicadas' : num_linhas_duplicadas, 'num_vinculacoes_desconectadas': num_vinculacoes_desconectadas, 
                'num_vinculacoes_erradas_full': num_vinculacoes_erradas_full, 'num_inativos_com_estoque_mktp': num_inativos_com_estoque_mktp,
                'num_produtos_kit_sem_desmembra': num_produtos_kit_sem_desmembra, 'num_inativos_com_estoque_aton': num_inativos_com_estoque_aton}
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
    
    arquivo_excel = vinculacoes_desativadas_aton_marketplace.main(download)
    
    # Crie uma resposta HTTP para retornar o arquivo ao usuário
    response = HttpResponse(arquivo_excel, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = f'attachment; filename="{nome_planilha}"'
    return response


def gerar_vinculacoes_full_erradas(request):
    download = True
    
    nome_planilha = 'vinculacoes_erradas_full.xlsx'
    
    arquivo_excel = vinculacoes_erradas_full_ecom_sku.main(download)
    
    # Crie uma resposta HTTP para retornar o arquivo ao usuário
    response = HttpResponse(arquivo_excel, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = f'attachment; filename="{nome_planilha}"'
    return response

def gerar_inativos_com_estoque_marketplace(request):
    download = True
    
    nome_planilha = 'produtos_inativos_com_estoque_mktp.xlsx'
    
    arquivo_excel = inativos_com_estoque_marktetplace.main(download)
    
    # Crie uma resposta HTTP para retornar o arquivo ao usuário
    response = HttpResponse(arquivo_excel, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = f'attachment; filename="{nome_planilha}"'
    return response

def gerar_produtos_kit_sem_desmembra(request):
    download = True
    
    nome_planilha = 'produtos_kit_sem_desmembra.xlsx'
    
    arquivo_excel = produtos_kit_sem_desmembra.main(download)
    
    # Crie uma resposta HTTP para retornar o arquivo ao usuário
    response = HttpResponse(arquivo_excel, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = f'attachment; filename="{nome_planilha}"'
    return response

def gerar_inativos_com_estoque_aton(request):
    download = True
    
    arquivo_excel = inativos_com_estoque_aton.main(download)
    
    # Crie uma resposta HTTP para retornar o arquivo ao usuário
    response = HttpResponse(arquivo_excel, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = f'attachment; filename="inativos_com_estoque_aton.xlsx"'
    return response