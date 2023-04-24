from django.shortcuts import render
from django.http import HttpResponse
from .models import PosicaoNetshoes
from django.db.models import OuterRef, Subquery, Max
import pandas as pd
from datetime import datetime
from io import BytesIO
from trackeamento.scripts import atualiza_netshoes

def index(request):
    return render(request, 'trackeamento/index.html')


def posicao_netshoes(request):
    return render(request, 'trackeamento/posicao-netshoes.html')


def lista_posicao_netshoes(request):

    ultimos_valores = PosicaoNetshoes.objects.filter(
        id__in=Subquery(
            PosicaoNetshoes.objects.filter(
                sku_netshoes=OuterRef('sku_netshoes')
            ).values('sku_netshoes').annotate(
                ultima_id=Max('id')
            ).values('ultima_id')
        )
    )
    
    posicoes_netshoes = {
        'posicoes_netshoes': ultimos_valores
    }

    return render(request, 'trackeamento/lista-posicao-netshoes.html', posicoes_netshoes)


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
         'anuncio_concorrente': [posicao_netshoes.anuncio_concorrente for posicao_netshoes in posicoes_netshoes],
         'ultima_atualizacao': [posicao_netshoes.ultima_atualizacao for posicao_netshoes in posicoes_netshoes]
     }
     
    df = pd.DataFrame(dados)
    
    df['ultima_atualizacao'] = df['ultima_atualizacao'].dt.tz_localize(None)
    df['pagina'].fillna('None', inplace=True)
    df['posicao'].fillna('None', inplace=True)
    
    excel_bytes = BytesIO()
    df.to_excel(excel_bytes, index=False)
    excel_bytes.seek(0)
    bytes_data = excel_bytes.getvalue()
    
    response = HttpResponse(bytes_data, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = f'attachment; filename=historico_netshoes_{datetime.now().strftime("%d-%m-%Y_%H-%M-%S")}.xlsx'
    return response


def atualizar_historico(request):
    atualiza_netshoes.main()
    
    return HttpResponse('<script>alert("Histórico atualizado!"); window.history.back();</script>')