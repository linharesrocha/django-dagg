from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('atualiza_relatorio/', views.atualiza_dados)
]