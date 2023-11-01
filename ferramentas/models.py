from django.db import models

class ArquivoAton(models.Model):
    arquivo = models.FileField(upload_to='ferramentas/atualizacao-aton/')  # Define o diretório onde os arquivos serão armazenados

    def __str__(self):
        return self.arquivo.name

class RegistroClique(models.Model):
    data_hora = models.DateTimeField(auto_now_add=True)
    
class DataUltimoBalanco(models.Model):
    codid = models.IntegerField()
    data_e_hora = models.DateTimeField(auto_now_add=True)