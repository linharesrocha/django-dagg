from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index-home'),
    path('atualizar_site/', views.atualizar_site, name='atualizar-site'),
]
