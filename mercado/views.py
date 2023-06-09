from django.shortcuts import render, redirect
from django.contrib.messages import constants
from django.contrib import messages
from .scripts import pesquisa_netshoes, pesquisa_decathlon

def index(request):
    return render(request, 'index.html')


def painel_mercado_netshoes(request):    
    return render(request, 'netshoes/painel-mercado-netshoes.html')


def pesquisa_mercado_netshoes(request):
    if request.method == 'POST':
        pesquisa = request.POST.get('pesquisa').strip()
        quantidade = int(request.POST.get('quantidade'))
        opcao_pesquisa = int(request.POST.get('opcoes_pesquisa'))
        
        # Validação
        if pesquisa == None or pesquisa == '' or quantidade == None or opcao_pesquisa == None:
            messages.add_message(request, constants.ERROR, 'Preencha todos os campos!')
            return redirect('painel-mercado-netshoes')
        
        
        resultados = pesquisa_netshoes.main(pesquisa, quantidade, opcao_pesquisa)
        
        return render(request, 'netshoes/painel-mercado-netshoes.html', {'resultados': resultados})
    else:
        return redirect('painel-mercado-netshoes')


def painel_mercado_decathlon(request):
    return render(request, 'decathlon/painel-mercado-decathlon.html')


def pesquisa_mercado_decathlon(request):
    if request.method == 'POST':
        pesquisa = request.POST.get('pesquisa').strip()
        quantidade = int(request.POST.get('quantidade'))
        # Validação
        if pesquisa == None or pesquisa == '' or quantidade == None:
            messages.add_message(request, constants.ERROR, 'Preencha todos os campos!')
            return redirect('painel-mercado-decathlon')
        
        resultados = pesquisa_decathlon.main(pesquisa, quantidade)
        return render(request, 'decathlon/painel-mercado-decathlon.html', {'resultados': resultados})
    else:
        return redirect('painel-mercado-decathlon')