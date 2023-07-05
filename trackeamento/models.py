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
    posicao_full = models.IntegerField(blank=True, null=True)
    pagina_full = models.IntegerField(blank=True, null=True)
    visita_diaria = models.FloatField(blank=True, null=True)
    visita_total = models.IntegerField(blank=True, null=True)
    vendas_diaria = models.FloatField(blank=True, null=True)
    vendas_total = models.IntegerField(blank=True, null=True)
    vende_a_cada_visita = models.FloatField(blank=True, null=True)
    taxa_conversao_diaria = models.FloatField(blank=True, null=True)
    taxa_conversao_total = models.FloatField(blank=True, null=True)
    pontuacao_anuncio = models.FloatField(blank=True, null=True)
    criacao_anuncio = models.DateTimeField(null=True, blank=True)
    ultima_atualizacao = models.DateTimeField(default=timezone.now)

    def local_ultima_atualizacao(self):
        return timezone.localtime(self.ultima_atualizacao)
    
    
class MetricasAds(models.Model):
    id = models.AutoField(primary_key=True)
    desde = models.DateField()
    ate = models.DateField()
    nome_campanha = models.CharField(max_length=255)
    acos_campanha = models.FloatField(blank=True, null=True)
    mlb_anuncio = models.CharField(max_length=255)
    titulo_anuncio = models.CharField(max_length=255)
    preco_anuncio = models.FloatField(blank=True, null=True)
    link_anuncio = models.CharField(max_length=255)
    clicks_anuncio = models.IntegerField(blank=True, null=True)
    impressions_anuncio = models.IntegerField(blank=True, null=True)
    cost_anuncio = models.FloatField(blank=True, null=True)
    cpc_anuncio = models.FloatField(blank=True, null=True)
    ctr_anuncio = models.FloatField(blank=True, null=True)
    cvr_anuncio = models.FloatField(blank=True, null=True)
    sold_quantity_total_anuncio = models.IntegerField(blank=True, null=True)
    amount_total_anuncio = models.FloatField(blank=True, null=True)
    advertising_fee_anuncio = models.FloatField(blank=True, null=True)
    organic_orders_quantity_anuncio = models.IntegerField(blank=True, null=True)
    share_anuncio = models.FloatField(blank=True, null=True)
    
class PedidosCompra(models.Model):
    id = models.AutoField(primary_key=True)
    descricao = models.CharField(max_length=255)
    cod_interno = models.CharField(max_length=255)
    vlr_custo_antigo = models.FloatField(blank=True, null=True)