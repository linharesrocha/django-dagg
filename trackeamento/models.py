from django.db import models
from django.utils import timezone

class PosicaoNetshoes(models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=255)
    termo_busca = models.CharField(max_length=255)
    sku_netshoes = models.CharField(max_length=255)
    posicao = models.IntegerField(blank=True, null=True)
    pagina = models.IntegerField(blank=True, null=True)
    variacao = models.CharField(max_length=20, null=True, blank=True)
    anuncio_concorrente = models.BooleanField(default=False)
    ultima_atualizacao = models.DateTimeField(default=timezone.now)

    def local_ultima_atualizacao(self):
        return timezone.localtime(self.ultima_atualizacao)
    
class MetricasMercadoLivre(models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.CharField(blank=True, null=True, max_length=255)
    termo_busca = models.CharField(max_length=255)
    mlb_anuncio = models.CharField(max_length=255)
    posicao = models.IntegerField(blank=True, null=True)
    pagina = models.IntegerField(blank=True, null=True)
    visita_diaria = models.FloatField(blank=True, null=True)
    visita_total = models.IntegerField(blank=True, null=True)
    vendas_diaria = models.FloatField(blank=True, null=True)
    vendas_total = models.IntegerField(blank=True, null=True)
    taxa_conversao_diaria = models.FloatField(blank=True, null=True)
    taxa_conversao_total = models.FloatField(blank=True, null=True)
    pontuacao_anuncio = models.FloatField(blank=True, null=True)
    criacao_anuncio = models.DateTimeField(null=True, blank=True)