from django.shortcuts import render
from scripts import verifica_categorias_duplicadas_aton

def index(request):
    return render(request, 'dashboard/index.html')

def atualiza_dados(request):
    download = False
    num_linhas_duplicadas = verifica_categorias_duplicadas_aton.main(download)
    contexto = {'num_linhas_duplicadas' : num_linhas_duplicadas}
    return render(request, 'dashboard/index.html', contexto)