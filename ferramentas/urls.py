from django.urls import path
from . import views

urlpatterns = [
     path('', views.index),
     path('baixar_fotos/', views.baixar_fotos),
     path('remover_fotos/', views.remover_fotos)
]
