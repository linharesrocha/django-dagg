from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('atualiza_relatorio/', views.atualiza_dados),
    path('atualiza_relatorio/excel_planilha_categorias_duplicadas/', views.gerar_categorias_duplicadas),
    path('atualiza_relatorio/excel_planilha_vinculacoes_desconectadas/', views.gerar_vinculacoes_desconectadas)
]