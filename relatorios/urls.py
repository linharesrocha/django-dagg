from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index-relatorios'),
    path('excel_planilha_campanha/', views.gerar_planilha_campanha, name='excel_planilha_campanha'),
    path('excel_planilha_produtos_sem_vendas/', views.gerar_planilha_produtos_sem_venda, name='excel_planilha_produtos_sem_vendas'),
    path('excel_planilha_comparativo_vendas_netshoes/', views.gerar_planilha_comparativo_vendas_netshoes, name='excel_planilha_comparativo_vendas_netshoes'),
    path('excel_planilha_todas_vinculacoes_marketplace_aton/', views.gerar_planilha_todas_vinculacoes_aton_marketplace, name='excel_planilha_todas_vinculacoes_marketplace_aton'),
    path('excel_planilha_todas_as_vendas_aton/', views.gerar_planilha_todas_as_vendas_aton, name='excel_planilha_todas_as_vendas_aton'),
    path('excel_planilha_envio_full/', views.gerar_planilha_envio_full, name='excel_planilha_envio_full'),
    path('excel_planilha_pedidos_do_dia/', views.gerar_planilha_pedidos_dia, name='excel_planilha_pedidos_do_dia'),
    path('excel_planilha_gerar_mlbs_stats/', views.gerar_mlbs_stats, name='excel_planilha_gerar_mlbs_stats'),
    path('excel_gerar_planilha_peso_quant', views.gerar_planilha_peso_quant, name='excel_gerar_planilha_peso_quant'),
    path('margem_netshoes_personalizada/', views.margem_netshoes_personalizada, name='margem-netshoes-personalizada'),
    path('margem_decathlon_personalizada/', views.margem_decathlon_personalizada, name='margem-decathlon-personalizada'),
    path('margem_centauro_personalizada/', views.margem_centauro_personalizada, name='margem-centauro-personalizada'),
    path('margem_mercadolivre_madz_personalizada/', views.margem_mercadolivre_madz_personalizada, name='margem-mercadolivre-madz-personalizada'),
    path('margem_mercadolivre_redplace_personalizada/', views.margem_mercadolivre_redplace_personalizada, name='margem-mercadolivre-redplace-personalizada'),
    path('armazens_estoque_valor_custo_total/', views.armazens_estoque_valor_custo_total, name='armazens-estoque-valor-custo-total'),
]
