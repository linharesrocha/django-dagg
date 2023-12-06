from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.messages import constants
from django.contrib import messages
import os
import sys


def index(request):
    return render(request, 'index-home.html')


def atualizar_site(request):
    # Muda para o diretório do seu projeto
    os.chdir('/home/dagg/django-dagg')

    # Faz git pull
    os.system('git pull')
    
    messages.add_message(request, messages.SUCCESS, 'Site atualizado com sucesso!')
    return redirect('index-home')