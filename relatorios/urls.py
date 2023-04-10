from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('excel_planilha_campanha/', views.gerar_planilha_campanha),
    path('excel_planilha_produtos_sem_vendas/', views.gerar_planilha_produtos_sem_venda),
    path('excel_planilha_comparativo_vendas_netshoes/', views.gerar_planilha_comparativo_vendas_netshoes)
]
