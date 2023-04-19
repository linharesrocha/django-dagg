from django.shortcuts import render
from django.http import HttpResponse
from .models import PosicaoNetshoes

def index(request):
    return render(request, 'trackeamento/index.html')


def posicao_netshoes(request):
    return render(request, 'trackeamento/posicao-netshoes.html')


def lista_posicao_netshoes(request):
    
    posicoes_netshoes = {
        'posicoes_netshoes': PosicaoNetshoes.objects.all()
    }
    
    return render(request, 'trackeamento/lista-posicao-netshoes.html', posicoes_netshoes)


def cadastrar_posicao_netshoes(request):
    termo = request.POST['termo-cadastro']
    sku_netshoes = request.POST['sku-netshoes-cadastro']
    
    # Verifica campo vazio
    if termo == '' or sku_netshoes == '':
        return HttpResponse('<script>alert("Preencha os campos vazios!"); window.history.back();</script>')
    
    # Transforma em lower
    termo = termo.lower()
    sku_netshoes = sku_netshoes.upper()
    sku_netshoes = sku_netshoes.strip()
    
    # Verifica se existe no banco
    my_obj = PosicaoNetshoes.objects.filter(sku_netshoes=sku_netshoes).first()
    if my_obj is not None:
        return HttpResponse('<script>alert("SKU já existe no banco de dados!"); window.history.back();</script>')
    
    # Cadastra
    nova_posicao = PosicaoNetshoes()
    nova_posicao.termo_busca = termo
    nova_posicao.sku_netshoes = sku_netshoes    
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