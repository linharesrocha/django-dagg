from django.urls import path
from . import views

urlpatterns = [
     path('', views.index, name='index-ferramentas'),
     path('baixar_fotos/', views.baixar_fotos),
     path('remover_fotos/', views.remover_fotos),
     path('remover_catalogo_requerido/', views.remover_catalogo_requerido, name='remover-catalogo-requerido')     
]
