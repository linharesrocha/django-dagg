import sys
import os
import django

sys.path.append('C:\\workspace\\django-dagg\\')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dagg.settings')
django.setup()

from mercadolivre.models import TokenMercadoLivreAPI

first_row = TokenMercadoLivreAPI.objects.first()

refresh_token_inicial = first_row.refresh_token_inicial
access_token = first_row.access_token
client_id = first_row.client_id
client_secret = first_row.client_secret