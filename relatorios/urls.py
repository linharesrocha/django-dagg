from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('excel_planilha_campanha/', views.gerar_planilha_campanha),
    path('excel_planilha_produtos_sem_vendas/', views.gerar_planilha_produtos_sem_venda),
    path('excel_planilha_comparativo_vendas_netshoes/', views.gerar_planilha_comparativo_vendas_netshoes),
    path('excel_planilha_todas_vinculacoes_marketplace_aton/', views.gerar_planilha_todas_vinculacoes_aton_marketplace),
    path('excel_planilha_todas_as_vendas_aton/', views.gerar_planilha_todas_as_vendas_aton),
    path('excel_planilha_envio_full/', views.gerar_planilha_envio_full)
]
