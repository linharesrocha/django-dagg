from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .scripts.planilha_campanha import gerar_excel

def index(request):
    return render(request, 'dashboard/index.html')

def gerar_planilha_campanha(request):
    
    # Chame a função que gera o arquvio Excel
    arquivo_excel = gerar_excel()
    
    # Crie uma resposta HTTP para retornar o arquivo ao usuário
    response = HttpResponse(arquivo_excel, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="meu_arquivo_excel.xlsx"'
    return response