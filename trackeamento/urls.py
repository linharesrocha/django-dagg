from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('match-netshoes/', views.match_netshoes, name='match-netshoes'),
    path('ajuste-tarifas/', views.ajuste_tarifas, name='ajuste-tarifas'),
    path('ajuste-tarifas/visualizar/', views.ajuste_tarifas_visualizar, name='ajuste-tarifas-visualizar'),
    path('ajuste-tarifas/atualizar-netshoes/', views.atualizar_tarifa_netshoes, name='atualizar-tarifa-netshoes'),
    path('ajuste-tarifas/atualizar-decathlon/', views.atualizar_tarifa_decathlon, name='atualizar-tarifa-decathlon'),
    path('ajuste-tarifas/atualizar-centauro/', views.atualizar_tarifa_centauro, name='atualizar-tarifa-centauro'),
    path('painel-match-netshoes/', views.painel_match_netshoes, name='painel-match-netshoes'),
    path('posicao-netshoes/', views.posicao_netshoes, name='posicao-netshoes'),
    path('posicao-netshoes/cadastrar/', views.cadastrar_posicao_netshoes, name='cadastrar-posicao-netshoes'),
    path('match-netshoes/cadastrar/', views.cadastrar_match_netshoes, name='cadastrar-match-netshoes'),
    path('posicao-netshoes/remover/', views.remover_posicao_netshoes, name='remover-posicao-netshoes'),
    path('match-netshoes/remover', views.remover_match_netshoes, name='remover-match-netshoes'),
    path('posicao-netshoes/painel/', views.painel_posicao_netshoes, name='painel-posicao-netshoes'),
    path('match-netshoes/painel/', views.painel_match_netshoes, name='painel-match-netshoes'),
    path('posicao-netshoes/baixar-historico/', views.baixar_historico, name='baixar-historico'),
    path('posicao-netshoes/atualizar-historico/', views.atualizar_historico, name='atualizar-historico'),
    path('posicao-netshoes/painel/item/<str:sku_netshoes>', views.item_posicao_netshoes, name='item-posicao-netshoes'),
    path('posicao-netshoes/painel/alterar_nome', views.item_alterar_nome, name='item-alterar-nome'),
    path('metricas-mercadolivre/', views.metricas_mercadolivre, name='metricas-mercadolivre'),
    path('metricas-mercadolivre/baixar-historico-mercadolivre/', views.baixar_historico_mercadolivre, name='baixar-historico-mercadolivre'),
    path('metricas-mercadolivre/atualizar-historico-mercadolivre/', views.atualizar_metricas_mercadolivre, name='atualizar-historico-mercadolivre'),
]