from django.urls import path
from . import views

urlpatterns = [
     path('', views.index, name='index-ferramentas'),
     path('baixar_fotos/', views.baixar_fotos),
     path('remover_fotos/', views.remover_fotos),
     path('remover_catalogo_requerido/', views.remover_catalogo_requerido, name='remover-catalogo-requerido'),
     path('alterar_ean/', views.alterar_ean, name='alterar-ean'),
     path('remover_mlb/', views.remover_mlb, name='remover-mlb'),
     path('remover_sku_netshoes/', views.remover_sku_netshoes, name='remover-sku-netshoes'),
     path('alterar_custo/', views.alterar_custo, name='alterar-custo'),
     path('baixar_planilha_via_sql/', views.baixar_planilha_via_sql, name='baixar-planilha-via-sql'),
     path('gerar_ean_aleatorio/', views.gerar_ean_aleatorio, name='gerar-ean-aleatorio'),
     path('inativar_produtos_aton/', views.inativar_produtos_aton, name='inativar-produtos-aton'),
     path('cadastrar_kit/', views.cadastrar_kit, name='cadastrar-kit'),
     path('copiar_atributos/', views.copiar_atributos, name='copiar-atributos'),
     path('atualizar_aton/', views.atualizar_aton, name='atualizar-aton'),
     path('consulta_vinculacao_mlb/', views.consulta_mlb_vinculado, name='consulta-vinculacao-mlb'),
     path('obter_data_hora_clique/', views.obter_data_hora_clique, name='obter_data_hora_clique'),
     path('criar_pedido_transferencia/', views.criar_pedido_transferencia, name='criar-pedido-transferencia'),
     path('balanco_estoque/', views.balanco_estoque, name='balanco-estoque'),
]
