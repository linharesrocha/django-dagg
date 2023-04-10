from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from scripts.planilha_campanha import main_gerar_excel
from datetime import datetime, date

def index(request):
    return render(request, 'dashboard/index.html')

def gerar_planilha_campanha(request):
    
    # Criando o nome da planilha com data e hroa
    today = date.today()
    dia_atual = str(today.strftime("%Y-%m-%d"))
    agora_hora = datetime.now()
    hora_atual = str(agora_hora.strftime("%H:%M:%S")).replace(':','-')
    nome_planilha = f'planilha-de-campanha-{dia_atual}-{hora_atual}.xlsx'
    
    # Chame a função que gera o arquvio Excel
    arquivo_excel = main_gerar_excel()
    
    # Crie uma resposta HTTP para retornar o arquivo ao usuário
    response = HttpResponse(arquivo_excel, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = f'attachment; filename="{nome_planilha}"'
    return response