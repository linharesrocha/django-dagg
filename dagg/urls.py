from django.urls import path, include

urlpatterns = [
    path('', include('home.urls')),
    path('relatorios/', include('relatorios.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('ferramentas/', include('ferramentas.urls')),
    path('trackeamento/', include('trackeamento.urls')),
    path('mercado/', include('mercado.urls')),
]