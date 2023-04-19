from django.shortcuts import render

def index(request):
    return render(request, 'trackeamento/index.html')

def posicao_netshoes(request):
    return render(request, 'trackeamento/posicao-netshoes.html')