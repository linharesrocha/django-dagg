from database_config import *
import requests

# Site para autenticação
url_access_token = "https://api.mercadolibre.com/oauth/token"
URL = 'http://localhost:8000'

# Headers do Access Token 
headers = {"accept": "application/json", "content-type": "application/x-www-form-urlencoded"}
data = {
    "grant_type": "authorization_code",
    "client_id": client_id,
    "client_secret": client_secret,
    "code": code,
    "redirect_uri": URL
}

# Enviando Requisição para obter o Access Token
response = requests.post(url_access_token, headers=headers, data=data).json()

try:
    if response['status'] == 400:
        print('Erro ao obter o Access Token')
        print(response)
except:
    access_token = response['access_token']

    # Atualiza no BD
    first_row = TokenMercadoLivreAPI.objects.get(id=1)
    first_row.access_token = access_token
    first_row.save()
    
    print('Access Token atualizado!')