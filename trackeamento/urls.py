from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('posicao-netshoes/', views.posicao_netshoes),
    path('posicao-netshoes/cadastrar/', views.cadastrar_posicao_netshoes, name='cadastrar-posicao-netshoes'),
]