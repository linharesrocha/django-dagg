from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('atualiza_relatorio/', views.atualiza_dados),
    path('atualiza_relatorio/excel_planilha_categorias_duplicadas/', views.gerar_categorias_duplicadas),
    path('atualiza_relatorio/excel_planilha_vinculacoes_desconectadas/', views.gerar_vinculacoes_desconectadas),
    path('atualiza_relatorio/excel_planilha_vinculacoes_full_erradas/', views.gerar_vinculacoes_full_erradas),
    path('atualiza_relatorio/excel_planilha_inativos_com_estoque_marketplace/', views.gerar_inativos_com_estoque_marketplace),
    path('atualiza_relatorio/excel_planilha_produtos_kit_sem_desmembra/', views.gerar_produtos_kit_sem_desmembra)
]