from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('gerar_excel/', views.gerar_planilha_campanha)
]
