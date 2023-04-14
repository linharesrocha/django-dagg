from django.shortcuts import render
from django.http import HttpResponse
from scripts import planilha_campanha, produtos_sem_venda, comparativo_vendas_netshoes, todas_vinculacoes_aton_marketplace, todas_as_vendas_aton, relatorio_envio_full
from datetime import datetime, date
import pandas as pd
from openpyxl import Workbook
from io import BytesIO


def index(request):
    return render(request, 'relatorios/index.html')

def gerar_planilha_campanha(request):
    
    # Criando o nome da planilha com data e hroa
    today = date.today()
    dia_atual = str(today.strftime("%Y-%m-%d"))
    agora_hora = datetime.now()
    hora_atual = str(agora_hora.strftime("%H:%M:%S")).replace(':','-')
    nome_planilha = f'planilha-de-campanha-{dia_atual}-{hora_atual}.xlsx'
    
    # Chame a função que gera o arquvio Excel
    arquivo_excel = planilha_campanha.main()
    
    # Crie uma resposta HTTP para retornar o arquivo ao usuário
    response = HttpResponse(arquivo_excel, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = f'attachment; filename="{nome_planilha}"'
    return response

def gerar_planilha_produtos_sem_venda(request):
    
    # Criando o nome da planilha
    today = date.today()
    last_month = date(today.year, today.month-1, 1)
    month_name = last_month.strftime('%B')
    nome_planilha = f'produtos-sem-venda-{month_name}.xlsx'
    
    # Chame a função que gera o arquvio Excel
    arquivo_excel = produtos_sem_venda.main()
    
    response = HttpResponse(arquivo_excel, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = f'attachment; filename={nome_planilha}'
    return response

def gerar_planilha_comparativo_vendas_netshoes(request):
    
    hoje = date.today()
    hoje_formatado = hoje.strftime("%Y-%m-%d")
    
    if request.method == 'POST':
        data_inicial_principal = request.POST['data_inicial_principal']
        data_final_principal = request.POST['data_final_principal']
        data_inicial_comparativo = request.POST['data_inicial_comparativo']
        data_final_comparativo = request.POST['data_final_comparativo']
        
        # Verifica se todas estão com data
        if data_inicial_principal == '' or data_final_principal == '' or data_inicial_comparativo == '' or data_inicial_comparativo == '':
            return HttpResponse('<script>alert("Preencha todas as datas!"); window.history.back();</script>')
        
        # Valida se a data é até hoje
        if data_final_principal > hoje_formatado:
            return HttpResponse('<script>alert("Data final principal maior do que hoje!"); window.history.back();</script>')
        
        # Valida data principal 
        if data_inicial_principal > data_final_principal:
            return HttpResponse('<script>alert("Data principal inicial maior que a data principal final!"); window.history.back();</script>')
        
        # Valida data comparativa
        if data_inicial_comparativo > data_final_comparativo:
            return HttpResponse('<script>alert("Data comparativa inicial maior que a data comparativa final!"); window.history.back();</script>')
        
        # Nome planilha
        nome_planilha = f'relatorio_comparativo_netshoes.xlsx'
        
        # Chama função de relatório
        arquivo_excel = comparativo_vendas_netshoes.main(data_inicial_principal=data_inicial_principal,
                                         data_final_principal=data_final_principal,
                                         data_inicial_comparativo=data_inicial_comparativo,
                                         data_final_comparativo=data_final_comparativo)
        
        response = HttpResponse(arquivo_excel, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = f'attachment; filename={nome_planilha}'
        return response
    
def gerar_planilha_todas_vinculacoes_aton_marketplace(request):
    nome_planilha = f'todas_vinculacoes_aton_marketplace.xlsx'
    
    arquivo_excel = todas_vinculacoes_aton_marketplace.main()
    
    # Crie uma resposta HTTP para retornar o arquivo ao usuário
    response = HttpResponse(arquivo_excel, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = f'attachment; filename="{nome_planilha}"'
    return response

def gerar_planilha_todas_as_vendas_aton(request):
    arquivo_excel = todas_as_vendas_aton.main()
    
     # Crie uma resposta HTTP para retornar o arquivo ao usuário
    response = HttpResponse(arquivo_excel, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = f'attachment; filename="todas_as_vendas_aton.xlsx"'
    return response

def gerar_planilha_envio_full(request):
    file = request.FILES['file']
    
    df_ml_full = pd.read_excel(file, skiprows=3, skipfooter=1)
        
    


    pass