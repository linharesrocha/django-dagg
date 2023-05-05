from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import PosicaoNetshoes, MetricasMercadoLivre
from django.db.models import OuterRef, Subquery, Max
import pandas as pd
from datetime import datetime
from io import BytesIO
from trackeamento.scripts import atualiza_netshoes
from openpyxl.styles import Alignment, PatternFill

def index(request):
    return render(request, 'trackeamento/index.html')


def posicao_netshoes(request):
    return render(request, 'trackeamento/netshoes/posicao-netshoes.html')


def painel_posicao_netshoes(request):

    ultimos_valores = PosicaoNetshoes.objects.filter(
        id__in=Subquery(
            PosicaoNetshoes.objects.filter(
                sku_netshoes=OuterRef('sku_netshoes')
            ).values('sku_netshoes').annotate(
                ultima_id=Max('id')
            ).values('ultima_id')
        )
    )
    
    for valor in ultimos_valores:
        valor.ultima_atualizacao = valor.ultima_atualizacao.strftime('%d/%m/%Y %H:%M')
    
    posicoes_netshoes = {
        'posicoes_netshoes': ultimos_valores
    }

    return render(request, 'trackeamento/netshoes/painel-posicao-netshoes.html', posicoes_netshoes)


def cadastrar_posicao_netshoes(request):
    termo = request.POST['termo-cadastro']
    sku_netshoes = request.POST['sku-netshoes-cadastro']
    nome = request.POST['nome-cadastro']
    tipo_anuncio = request.POST['tipo_anuncio']
    
    # Verifica campo vazio
    if termo == '' or sku_netshoes == '' or nome == '':
        return HttpResponse('<script>alert("Preencha os campos vazios!"); window.history.back();</script>')
    
    # Transforma em lower
    termo = termo.lower()
    sku_netshoes = sku_netshoes.upper()
    sku_netshoes = sku_netshoes.strip()
    nome = nome.strip()
    
    # Verifica se existe no banco
    my_obj = PosicaoNetshoes.objects.filter(sku_netshoes=sku_netshoes).first()
    if my_obj is not None:
        return HttpResponse('<script>alert("SKU já existe no banco de dados!"); window.history.back();</script>')
    
    # Cadastra
    nova_posicao = PosicaoNetshoes()
    nova_posicao.nome = nome
    nova_posicao.termo_busca = termo
    nova_posicao.sku_netshoes = sku_netshoes
    nova_posicao.anuncio_concorrente = True if tipo_anuncio == 'concorrente' else False    
    nova_posicao.save()
    
    return HttpResponse('<script>alert("Cadastro feito com sucesso!"); window.history.back();</script>')


def remover_posicao_netshoes(request):
    sku_netshoes = request.POST['sku-netshoes-delete']
    
    # Verifica campo vazio
    if sku_netshoes == '':
        return HttpResponse('<script>alert("Preencha o campo vazio!"); window.history.back();</script>')
    
    # Verifica se existe no banco
    my_obj = PosicaoNetshoes.objects.filter(sku_netshoes=sku_netshoes).first()
    if my_obj is None:
        return HttpResponse('<script>alert("SKU não encontrado no banco de dados!"); window.history.back();</script>')
    
    # Deleta
    PosicaoNetshoes.objects.filter(sku_netshoes=sku_netshoes).delete()

    return HttpResponse('<script>alert("SKU Deletado do Banco de Dados!"); window.history.back(); </script>')


def baixar_historico(request):
    posicoes_netshoes = PosicaoNetshoes.objects.all()
    
    if len(posicoes_netshoes) == 0:
        return HttpResponse('<script>alert("Não há dados para baixar!"); window.history.back();</script>')
     
    dados = {
         'id': [posicao_netshoes.id for posicao_netshoes in posicoes_netshoes],
         'pagina': [posicao_netshoes.pagina for posicao_netshoes in posicoes_netshoes],
         'posicao': [posicao_netshoes.posicao for posicao_netshoes in posicoes_netshoes],
         'nome': [posicao_netshoes.nome for posicao_netshoes in posicoes_netshoes],
         'sku_netshoes': [posicao_netshoes.sku_netshoes for posicao_netshoes in posicoes_netshoes],
         'termo_busca': [posicao_netshoes.termo_busca for posicao_netshoes in posicoes_netshoes],
         'variacao': [posicao_netshoes.variacao for posicao_netshoes in posicoes_netshoes],
         'anuncio_concorrente': [posicao_netshoes.anuncio_concorrente for posicao_netshoes in posicoes_netshoes],
         'ultima_atualizacao': [posicao_netshoes.ultima_atualizacao for posicao_netshoes in posicoes_netshoes]
     }
     
    df = pd.DataFrame(dados)
    
    df['ultima_atualizacao'] = df['ultima_atualizacao'].dt.tz_localize(None)
    df['pagina'].fillna('None', inplace=True)
    df['variacao'].fillna('None', inplace=True)
    df['posicao'].fillna('None', inplace=True)
    df['ultima_atualizacao'] = pd.to_datetime(df['ultima_atualizacao'])
    df['ultima_atualizacao'] = df['ultima_atualizacao'].dt.strftime('%d-%m-%Y %H:%M:%S')
    
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    df.to_excel(writer, sheet_name='HISTORICO',index=False)
    worksheet = writer.sheets['HISTORICO']
    
    # Adicionando filtros
    worksheet.auto_filter.ref = "A1:I1"
    
    # Alterando tamanho das colunas
    worksheet.column_dimensions['A'].width = '3.30'
    worksheet.column_dimensions['B'].width = '10.71'
    worksheet.column_dimensions['C'].width = '11.57'
    worksheet.column_dimensions['D'].width = '51'
    worksheet.column_dimensions['E'].width = '15.57'
    worksheet.column_dimensions['F'].width = '16.29'
    worksheet.column_dimensions['G'].width = '11.14'
    worksheet.column_dimensions['H'].width = '19.29'
    worksheet.column_dimensions['I'].width = '21.71'
        
    # Escondendo coluna ID
    worksheet.column_dimensions['A'].hidden = True
    
    # Congelando painel
    worksheet.freeze_panes = 'A2'
    
    # Define a formatação de centralização
    alignment = Alignment(horizontal='center', vertical='center')
    for row in worksheet.iter_rows():
        for cell in row:
            cell.alignment = alignment

    # Atualiza cores do cabeçalho
    cor_header = 'F79646'
    for i, row in enumerate(worksheet.iter_rows(min_row=1, max_row=1)):
        if i == 0:
            fill = PatternFill(start_color=cor_header, end_color=cor_header, fill_type='solid')
        for cell in row:
            cell.fill = fill
    
    writer._save()
    output.seek(0)
    
    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=historico_netshoes_{datetime.now().strftime("%d-%m-%Y_%H-%M-%S")}.xlsx'
    return response


def atualizar_historico(request):
    slack = False
    atualiza_netshoes.main(slack)
    
    return HttpResponse('<script>alert("Certo! Atualize a página."); window.history.back();</script>')


def item_posicao_netshoes(request, sku_netshoes):
    item = PosicaoNetshoes.objects.filter(sku_netshoes=sku_netshoes).first()
    return render(request, 'trackeamento/netshoes/item-posicao-netshoes.html', {'item': item})


def item_alterar_nome(request):
    novo_nome = request.POST['novo-nome']
    sku_netshoes = request.POST.get('sku_netshoes')
    PosicaoNetshoes.objects.filter(sku_netshoes=sku_netshoes).update(nome=novo_nome)

    return redirect('painel-posicao-netshoes')


def metricas_mercadolivre(request):
    # Caso o usuário entre
    if request.method == 'GET':
        return render(request, 'trackeamento/mercadolivre/metricas-mercadolivre.html')
    
    # Caso o usário faça alguma ação
    elif request.method == 'POST':
        action = request.POST.get('action')
       
       # Caso a ação seja cadastrar um MLB
        if action == 'cadastrar':
            
            # Tratando os dados
            termo = request.POST['termo-cadastro'].lower()
            mlb = request.POST['mlb-mercadolivre-cadastro'].upper().replace('-','')
            
            # Verifica se existe no banco
            my_obj = MetricasMercadoLivre.objects.filter(mlb_anuncio=mlb).first()
            if my_obj is not None:
                return HttpResponse('<script>alert("MLB já existe no banco de dados!"); window.history.back();</script>')
            
            # Cadastra
            MetricasMercadoLivre(termo_busca=termo, mlb_anuncio=mlb).save()
            
            return HttpResponse('<script>alert("Cadastrado com sucesso!"); window.history.back();</script>')
        
        # Caso a ação seja remover um MLB
        elif action == 'remover':
            mlb_anuncio = request.POST['mlb-mercadolivre-delete']
            
            # Verifica se existe no banco de dados
            my_obj = MetricasMercadoLivre.objects.filter(mlb_anuncio=mlb_anuncio).first()
            if my_obj is None:
                return HttpResponse('<script>alert("MLB não existe no banco de dados!"); window.history.back();</script>')
            # Caso exista, deleta
            else:
                MetricasMercadoLivre.objects.filter(mlb_anuncio=mlb_anuncio).delete()
                return HttpResponse('<script>alert("Removido com sucesso!"); window.history.back();</script>')
        
        return render(request, 'trackeamento/mercadolivre/metricas-mercadolivre.html')
    

def metricas_mercadolivre_painel(request):
    ultimos_valores = MetricasMercadoLivre.objects.filter(
        id__in=Subquery(
            MetricasMercadoLivre.objects.filter(
                mlb_anuncio=OuterRef('mlb_anuncio')
            ).values('mlb_anuncio').annotate(
                ultima_id=Max('id')
            ).values('ultima_id')
        )
    )
    
    for valor in ultimos_valores:
        valor.ultima_atualizacao = valor.ultima_atualizacao.strftime('%d/%m/%Y %H:%M')
        

    return render(request, 'trackeamento/mercadolivre/painel-metricas-mercadolivre.html', {'lista_mercadolivre': ultimos_valores})


def baixar_historico_mercadolivre(request):
    lista_mercadolivre = MetricasMercadoLivre.objects.all()
    
    if len(lista_mercadolivre) == 0:
        return HttpResponse('<script>alert("Não há dados para baixar!"); window.history.back();</script>')
     
    dados = {
        'id': [anuncio.id for anuncio in lista_mercadolivre],
        'nome': [anuncio.nome for anuncio in lista_mercadolivre],
        'termo_busca': [anuncio.termo_busca for anuncio in lista_mercadolivre],
        'mlb_anuncio': [anuncio.mlb_anuncio for anuncio in lista_mercadolivre],
        'posicao': [anuncio.posicao for anuncio in lista_mercadolivre],
        'pagina': [anuncio.pagina for anuncio in lista_mercadolivre],
        'visita_diaria': [anuncio.visita_diaria for anuncio in lista_mercadolivre],
        'visita_total': [anuncio.visita_total for anuncio in lista_mercadolivre],
        'vendas_diaria': [anuncio.vendas_diaria for anuncio in lista_mercadolivre],
        'vendas_total': [anuncio.vendas_total for anuncio in lista_mercadolivre],
        'vende_a_cada_visita': [anuncio.vende_a_cada_visita for anuncio in lista_mercadolivre],
        'taxa_conversao_diaria': [anuncio.taxa_conversao_diaria for anuncio in lista_mercadolivre],
        'taxa_conversao_total': [anuncio.taxa_conversao_total for anuncio in lista_mercadolivre],
        'pontuacao_anuncio': [anuncio.pontuacao_anuncio for anuncio in lista_mercadolivre],
        'criacao_anuncio': [anuncio.criacao_anuncio for anuncio in lista_mercadolivre],
        'ultima_atualizacao': [anuncio.ultima_atualizacao for anuncio in lista_mercadolivre]
    }
     
    df = pd.DataFrame(dados)
    
    df['ultima_atualizacao'] = df['ultima_atualizacao'].dt.tz_localize(None)
    df['nome'].fillna('None', inplace=True)
    df['posicao'].fillna('None', inplace=True)
    df['pagina'].fillna('None', inplace=True)
    df['visita_diaria'].fillna('None', inplace=True)
    df['visita_total'].fillna('None', inplace=True)
    df['vendas_diaria'].fillna('None', inplace=True)
    df['vendas_total'].fillna('None', inplace=True)
    df['vende_a_cada_visita'].fillna('None', inplace=True)
    df['taxa_conversao_diaria'].fillna('None', inplace=True)
    df['taxa_conversao_total'].fillna('None', inplace=True)
    df['pontuacao_anuncio'].fillna('None', inplace=True)
    df['criacao_anuncio'].fillna('None', inplace=True)
    df['ultima_atualizacao'] = pd.to_datetime(df['ultima_atualizacao'])
    df['ultima_atualizacao'] = df['ultima_atualizacao'].dt.strftime('%d-%m-%Y %H:%M:%S')
    
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    df.to_excel(writer, sheet_name='HISTORICO',index=False)
    worksheet = writer.sheets['HISTORICO']
    
    writer._save()
    output.seek(0)
    
    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=historico_netshoes_{datetime.now().strftime("%d-%m-%Y_%H-%M-%S")}.xlsx'
    return response