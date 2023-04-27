from django.db import models
import pytz

class PosicaoNetshoes(models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=255)
    termo_busca = models.CharField(max_length=255)
    sku_netshoes = models.CharField(max_length=255)
    posicao = models.IntegerField(blank=True, null=True)
    pagina = models.IntegerField(blank=True, null=True)
    crescimento = models.CharField(max_length=20, null=True, blank=True)
    anuncio_concorrente = models.BooleanField(default=False)
    ultima_atualizacao = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        tz = pytz.timezone('America/Sao_Paulo')
        self.created_at = tz.localize(self.created_at)
        super(PosicaoNetshoes, self).save(*args, **kwargs)