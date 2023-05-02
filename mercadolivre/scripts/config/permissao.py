import requests
import os
from time import sleep
import webbrowser
from database_config import *

URL = 'http://localhost:8000'

# Url para obter Refresh Token
url = f"https://auth.mercadolivre.com.br/authorization?response_type=code&client_id={client_id}&redirect_uri={URL}"

# Enviando requisição e abrendo a página
webbrowser.open(url)

# Armazena o Refresh Token
CODE = input('Refresh Token: ').replace('http://localhost:8000/?code=', '').replace('localhost:8000/?code=', '')

# Atualiza no BD
first_row = TokenMercadoLivreAPI.objects.get(id=1)
first_row.code = CODE
first_row.save()

print('Refresh Token salvo no banco de dados!')