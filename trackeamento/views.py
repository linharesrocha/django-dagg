from django.shortcuts import render
from django.http import HttpResponse
from .models import PosicaoNetshoes

def index(request):
    return render(request, 'trackeamento/index.html')

def posicao_netshoes(request):
    return render(request, 'trackeamento/posicao-netshoes.html')

def cadastrar_posicao_netshoes(request):
    nova_posicao = PosicaoNetshoes()

    termo = request.POST['termo']
    sku_netshoes = request.POST['sku-netshoes']
    
    nova_posicao.termo_busca = termo
    nova_posicao.sku_netshoes = sku_netshoes
    
    if termo == '' or sku_netshoes == '':
        return HttpResponse('<script>alert("Preencha os campos vazios!"); window.history.back();</script>')
        
    
    nova_posicao.save()
    
    return HttpResponse('<script>alert("Cadastro feito com sucesso!"); window.history.back();</script>')