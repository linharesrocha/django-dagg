from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('netshoes/', views.painel_mercado_netshoes, name='painel-mercado-netshoes'),
    path('netshoes/pesquisa/', views.pesquisa_mercado_netshoes, name='pesquisa-mercado-netshoes'),
    path('decathlon/', views.painel_mercado_decathlon, name='painel-mercado-decathlon'),
    path('decathlon/pesquisa/', views.pesquisa_mercado_decathlon, name='pesquisa-mercado-decathlon'),
]