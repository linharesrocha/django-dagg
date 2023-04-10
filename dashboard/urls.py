from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('excel_planilha_campanha/', views.gerar_planilha_campanha)
]
