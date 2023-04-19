from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('posicao-netshoes/', views.posicao_netshoes),
    path('posicao-netshoes/cadastrar/', views.cadastrar_posicao_netshoes, name='cadastrar-posicao-netshoes'),
    path('posicao-netshoes/remover/', views.remover_posicao_netshoes, name='remover-posicao-netshoes'),
    path('posicao-netshoes/lista/', views.lista_posicao_netshoes, name='lista-posicao-netshoes')
]