from django.db import models

# Create your models here.
class TokenMercadoLivreAPI(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=255)
    access_token = models.CharField(max_length=255)
    client_id = models.CharField(max_length=255)
    client_secret = models.CharField(max_length=255)