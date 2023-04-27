from django.utils import timezone
from django.db import models

class PosicaoNetshoes(models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=255)
    termo_busca = models.CharField(max_length=255)
    sku_netshoes = models.CharField(max_length=255)
    posicao = models.IntegerField(blank=True, null=True)
    pagina = models.IntegerField(blank=True, null=True)
    crescimento = models.CharField(max_length=20, null=True, blank=True)
    anuncio_concorrente = models.BooleanField(default=False)
    ultima_atualizacao = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if self.ultima_atualizacao is not None:
            tz = timezone.get_current_timezone()
            self.ultima_atualizacao = timezone.make_aware(self.ultima_atualizacao, tz)
            print(self.ultima_atualizacao)
        super(PosicaoNetshoes, self).save(*args, **kwargs)