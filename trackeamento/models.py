from django.db import models

class PosicaoNetshoes(models.Model):
    id = models.AutoField(primary_key=True)
    termo_busca = models.CharField(max_length=255)
    sku_netshoes = models.CharField(max_length=255)