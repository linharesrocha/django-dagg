from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse('<h1><a href="/relatorios">Relatórios</a></h1>') 