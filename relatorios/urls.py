from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('excel_planilha_campanha/', views.gerar_planilha_campanha, name='excel_planilha_campanha'),
    path('excel_planilha_produtos_sem_vendas/', views.gerar_planilha_produtos_sem_venda, name='excel_planilha_produtos_sem_vendas'),
    path('excel_planilha_comparativo_vendas_netshoes/', views.gerar_planilha_comparativo_vendas_netshoes, name='excel_planilha_comparativo_vendas_netshoes'),
    path('excel_planilha_todas_vinculacoes_marketplace_aton/', views.gerar_planilha_todas_vinculacoes_aton_marketplace, name='excel_planilha_todas_vinculacoes_marketplace_aton'),
    path('excel_planilha_todas_as_vendas_aton/', views.gerar_planilha_todas_as_vendas_aton, name='excel_planilha_todas_as_vendas_aton'),
    path('excel_planilha_envio_full/', views.gerar_planilha_envio_full, name='excel_planilha_envio_full'),
    path('excel_planilha_pedidos_do_dia/', views.gerar_planilha_pedidos_dia, name='excel_planilha_pedidos_do_dia'),
    path('excel_planilha_gerar_mlbs_stats/', views.gerar_mlbs_stats, name='excel_planilha_gerar_mlbs_stats'),
]
