from django.shortcuts import render, redirect
from django.http import HttpResponse
from scripts import planilha_campanha, produtos_sem_venda, comparativo_vendas_netshoes, todas_vinculacoes_aton_marketplace, todas_as_vendas_aton, relatorio_envio_full_v2, pedidos_do_dia
from datetime import datetime, date
from django.contrib.messages import constants
from django.contrib import messages
from io import BytesIO
from openpyxl.utils import get_column_letter
from openpyxl.styles import PatternFill
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl import Workbook
from relatorios.scripts import produtos_mlb_stats_pedro
from scripts.connect_to_database import get_connection
import pyodbc
import pandas as pd
import warnings

def index(request):
    return render(request, 'index-relatorios.html')

def gerar_planilha_campanha(request):
    
    # Obtem valor marketplace
    marketplace = request.POST['marketplace']
    
    if marketplace == 'Tudo':
        marketplace = None
    
    # Criando o nome da planilha com data e hroa
    today = date.today()
    dia_atual = str(today.strftime("%Y-%m-%d"))
    agora_hora = datetime.now()
    hora_atual = str(agora_hora.strftime("%H:%M:%S")).replace(':','-')
    nome_planilha = f'planilha-de-campanha-{dia_atual}-{hora_atual}.xlsx'
    
    # Chame a função que gera o arquvio Excel
    arquivo_excel = planilha_campanha.main(marketplace=marketplace)
    
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
            return redirect('index-relatorios')
        
        # Valida se a data é até hoje
        if data_final_principal > hoje_formatado:
            messages.add_message(request, constants.ERROR, 'Data principal final maior que hoje!')
            return redirect('index-relatorios')
        
        # Valida data principal 
        if data_inicial_principal > data_final_principal:
            messages.add_message(request, constants.ERROR, 'Data principal inicial maior que a data principal final!')
            return redirect('index-relatorios')
        
        # Valida data comparativa
        if data_inicial_comparativo > data_final_comparativo:
            messages.add_message(request, constants.ERROR, 'Data comparativa inicial maior que a data comparativa final!')
            return redirect('index-relatorios')
        
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
    marketplace = request.POST['marketplace']

    if marketplace == 'Tudo':
        marketplace = None
    
    arquivo_excel = todas_vinculacoes_aton_marketplace.main(marketplace=marketplace)
    
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
    
    output = relatorio_envio_full_v2.main(file)
    
    # Retorne a resposta HTTP com o arquivo Excel como anexo
    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=analise_envio_full.xlsx'
    return response

def gerar_planilha_peso_quant(request):
    file = request.FILES['file']
    
    df_peso_quant = pd.read_excel(file)
    
    try:
        df_peso_quant['COD_INTERNO'] = df_peso_quant['COD_INTERNO'].str.strip()
    except:
        messages.add_message(request, constants.ERROR, 'Erro ao ler planilha! Verifique se a primeira coluna se chama "COD_INTERNO" e a segunda coluna se chama "QUANT" ou "Quant."')
        return redirect('index-relatorios')
    
    # Verifica se a primeira coluna se chama COD_INTERNO
    if str(df_peso_quant.columns[0]).upper() != 'COD_INTERNO':
        messages.add_message(request, constants.ERROR, 'A primeira coluna deve se chamar "COD_INTERNO"')
        return redirect('index-relatorios')
    
    # Verifica se a segunda coluna se chama QUANT
    if df_peso_quant.columns[1].upper() != 'QUANT' and str(df_peso_quant.columns[1]) != 'Quant.':
        messages.add_message(request, constants.ERROR, 'A segunda coluna deve se chamar "QUANT" ou "Quant."')
        return redirect('index-relatorios')
    
    df_peso_quant.rename(columns={'COD_INTERNO': 'COD_INTERNO', 'quant': 'QUANT', 'Quant.': 'QUANT'}, inplace=True)
    
    try:
        # Puxa Peso
        lista_cod_interno = df_peso_quant['COD_INTERNO'].tolist()
        cod_interno_com_aspas = ["'" + str(cod) + "'" for cod in lista_cod_interno]
        cod_interno_str = ', '.join(cod_interno_com_aspas)
        warnings.filterwarnings('ignore')
        connection = get_connection()
        conexao = pyodbc.connect(connection)
        
        comando = f'''
        SELECT COD_INTERNO, PESO
        FROM MATERIAIS
        WHERE COD_INTERNO IN ({cod_interno_str})
        '''
        
        df_resultado_peso = pd.read_sql(comando, conexao)
        df_resultado_peso['COD_INTERNO'] = df_resultado_peso['COD_INTERNO'].str.strip()
        
        df_peso_quant = pd.merge(df_peso_quant, df_resultado_peso, on='COD_INTERNO', how='left')
        
        # Multiplica coluna QUANT por PESO
        df_peso_quant['PESO_MULT'] = df_peso_quant['QUANT'] * df_peso_quant['PESO']
        
        # Soma todos os pesos
        peso_total = df_peso_quant['PESO_MULT'].sum()
        
        # Cria coluna para colocar peso_total mas apenas na primeira celula
        df_peso_quant['PESO_TOTAL'] = peso_total
        
        excel_bytes = BytesIO()
        df_peso_quant.to_excel(excel_bytes, index=False)
        excel_bytes.seek(0)
        bytes_data = excel_bytes.getvalue()
        
        response = HttpResponse(bytes_data, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = f'attachment; filename="peso_quant.xlsx"'
        return response
    except:
        messages.add_message(request, constants.ERROR, 'Erro ao gerar planilha!')
        return redirect('index-relatorios')
        
    

def gerar_planilha_pedidos_dia(request):
    output = pedidos_do_dia.main()
    
    today = date.today()
    dia_atual = str(today.strftime("%d-%m-%Y"))
    nome_planilha = f'pedidos_do_dia_{dia_atual}'
    
    # Retorne a resposta HTTP com o arquivo Excel como anexo
    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename={nome_planilha}.xlsx'
    return response

def gerar_mlbs_stats(request):
    arquivo_excel = produtos_mlb_stats_pedro.main()
    
    # Crie uma resposta HTTP para retornar o arquivo ao usuário
    response = HttpResponse(arquivo_excel, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = f'attachment; filename="mlbs_stats.xlsx"'
    return response

def margem_netshoes_personalizada(request):
    empresa_personalizada = request.POST['empresa_personalizada']
    data_inicio = request.POST['data_inicial']
    data_fim = request.POST['data_final']
    personalizado = True

    print(data_inicio, data_fim)

    from scripts.confere_margem_netshoes import main

    main(data_inicio, data_fim, empresa_personalizada, personalizado)

    return redirect('index-relatorios')

def adjust_column_width(sheet):
    for column in sheet.columns:
        max_length = 0
        column_letter = get_column_letter(column[0].column)
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2) * 1.2
        sheet.column_dimensions[column_letter].width = adjusted_width

def armazens_estoque_valor_custo_total(request):
    connection = get_connection()
    conexao = pyodbc.connect(connection)
    
    # Dicionário para mapear números de armazéns para nomes de abas
    armazem_nomes = {
        1: "PRINCIPAL",
        2: "FULL ML MADZ",
        11: "FULL MAGALU MADZ",
        12: "FBA AMAZON",
        13: "FULL MAGALU LEAL"
    }
    
    # Criar um objeto BytesIO para armazenar o arquivo Excel
    output = BytesIO()
    
    # Criar um objeto Workbook
    workbook = Workbook()
    
    # Definir a cor laranja para os cabeçalhos
    cor_laranja = PatternFill(start_color='F1C93B', end_color='F1C93B', fill_type='solid')
    
    # Dicionário para armazenar os totais de cada armazém
    resumo_armazens = {}
    
    for armazem, nome_aba in armazem_nomes.items():
        comando = f'''
        SELECT 
            A.CODID, 
            A.COD_INTERNO, 
            A.DESCRICAO, 
            B.ESTOQUE AS ESTOQUE_REAL, 
            A.VLR_CUSTO,
            A.VLR_CUSTO * B.ESTOQUE AS TOTAL_CUSTO
        FROM MATERIAIS A
        LEFT JOIN ESTOQUE_MATERIAIS B ON A.CODID = B.MATERIAL_ID
        WHERE B.ARMAZEM = {armazem}
        AND A.INATIVO = 'N'
        AND A.COD_INTERNO NOT LIKE '%PAI'
        AND A.DESMEMBRA = 'N'
        ORDER BY CODID
        '''
        
        df = pd.read_sql(comando, conexao)
        
        # Criar uma nova aba com o nome especificado
        sheet = workbook.create_sheet(title=nome_aba)
        
        # Escrever os cabeçalhos e aplicar a cor laranja
        headers = df.columns.tolist()
        for col, header in enumerate(headers, start=1):
            cell = sheet.cell(row=1, column=col, value=header)
            cell.fill = cor_laranja
        
        # Escrever os dados
        for row, data in enumerate(df.values, start=2):
            for col, value in enumerate(data, start=1):
                sheet.cell(row=row, column=col, value=value)
        
        # Ajustar a largura das colunas
        adjust_column_width(sheet)
        
        # Adicionando filtros
        sheet.auto_filter.ref = sheet.dimensions
        
        # Congelando painel
        sheet.freeze_panes = 'A2'
        
        # Calcular totais para o resumo
        estoque_total = df['ESTOQUE_REAL'].sum()
        valor_total = df['TOTAL_CUSTO'].sum()
        resumo_armazens[nome_aba] = {'ESTOQUE': estoque_total, 'VALOR': valor_total}
    
    # Criar a aba de resumo
    resumo_sheet = workbook.create_sheet(title="RESUMO")
    
    # Adicionar cabeçalhos ao resumo
    headers_resumo = ["ARMAZEM", "ESTOQUE", "VALOR"]
    for col, header in enumerate(headers_resumo, start=1):
        cell = resumo_sheet.cell(row=1, column=col, value=header)
        cell.fill = cor_laranja
    
    # Preencher dados do resumo
    for row, (armazem, dados) in enumerate(resumo_armazens.items(), start=2):
        resumo_sheet.cell(row=row, column=1, value=armazem)
        resumo_sheet.cell(row=row, column=2, value=dados['ESTOQUE'])
        resumo_sheet.cell(row=row, column=3, value=dados['VALOR'])
    
    # Ajustar a largura das colunas na aba de resumo
    adjust_column_width(resumo_sheet)
    
    # Adicionar filtros à aba de resumo
    resumo_sheet.auto_filter.ref = resumo_sheet.dimensions
    
    # Congelar painel na aba de resumo
    resumo_sheet.freeze_panes = 'A2'
    
    # Remover a planilha padrão criada pelo openpyxl
    workbook.remove(workbook['Sheet'])
    
    # Salvar o workbook no objeto BytesIO
    workbook.save(output)
    output.seek(0)
    
    # Fechar a conexão
    conexao.close()
    
    # Criar uma resposta HTTP com o arquivo Excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=estoque_por_armazem.xlsx'
    response.write(output.getvalue())
    
    return response