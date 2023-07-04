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
]
