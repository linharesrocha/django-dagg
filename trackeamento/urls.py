from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('posicao-netshoes/', views.posicao_netshoes),
]