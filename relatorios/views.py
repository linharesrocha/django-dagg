from django.shortcuts import render, redirect
from django.http import HttpResponse
from scripts import planilha_campanha, produtos_sem_venda, comparativo_vendas_netshoes, todas_vinculacoes_aton_marketplace, todas_as_vendas_aton, relatorio_envio_full, pedidos_do_dia
from datetime import datetime, date
from django.contrib.messages import constants
from django.contrib import messages


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
            messages.add_message(request, constants.ERROR, 'Preencha todas as datas!')
            return redirect('index')
        
        # Valida se a data é até hoje
        if data_final_principal > hoje_formatado:
            messages.add_message(request, constants.ERROR, 'Data principal final maior que hoje!')
            return redirect('index')
        
        # Valida data principal 
        if data_inicial_principal > data_final_principal:
            messages.add_message(request, constants.ERROR, 'Data principal inicial maior que a data principal final!')
            return redirect('index')
        
        # Valida data comparativa
        if data_inicial_comparativo > data_final_comparativo:
            messages.add_message(request, constants.ERROR, 'Data comparativa inicial maior que a data comparativa final!')
            return redirect('index')
        
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
    
    output = relatorio_envio_full.main(file)
    
    # Retorne a resposta HTTP com o arquivo Excel como anexo
    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=analise_envio_full.xlsx'
    return response

def gerar_planilha_pedidos_dia(request):
    output = pedidos_do_dia.main()
    
    today = date.today()
    dia_atual = str(today.strftime("%d-%m-%Y"))
    nome_planilha = f'pedidos_do_dia_{dia_atual}'
    
    # Retorne a resposta HTTP com o arquivo Excel como anexo
    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename={nome_planilha}.xlsx'
    return response