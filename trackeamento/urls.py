from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('posicao-netshoes/', views.posicao_netshoes),
    path('posicao-netshoes/cadastrar/', views.cadastrar_posicao_netshoes, name='cadastrar-posicao-netshoes'),
    path('posicao-netshoes/remover/', views.remover_posicao_netshoes, name='remover-posicao-netshoes'),
    path('posicao-netshoes/painel/', views.painel_posicao_netshoes, name='painel-posicao-netshoes'),
    path('posicao-netshoes/baixar-historico/', views.baixar_historico, name='baixar-historico'),
    path('posicao-netshoes/atualizar-historico/', views.atualizar_historico, name='atualizar-historico'),
    path('posicao-netshoes/painel/item/<str:sku_netshoes>', views.item_posicao_netshoes, name='item-posicao-netshoes'),
    path('posicao-netshoes/painel/alterar_nome', views.item_alterar_nome, name='item-alterar-nome'),
]