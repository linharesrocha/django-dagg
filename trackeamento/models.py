from django.db import models

class PosicaoNetshoes(models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=255)
    termo_busca = models.CharField(max_length=255)
    sku_netshoes = models.CharField(max_length=255)
    posicao = models.IntegerField(blank=True, null=True)
    pagina = models.IntegerField(blank=True, null=True)
    anuncio_concorrente = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)