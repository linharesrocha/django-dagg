import requests
import os
from time import sleep
import webbrowser
from database_config import *

# Url para obter Refresh Token Inicial
url = f"https://auth.mercadolivre.com.br/authorization?response_type=code&client_id={client_id}"
print(url)
# Enviando requisição e abrendo a página
webbrowser.open(url)

# Armazena o Refresh Token
CODE = input('Refresh Token: ').replace('http://localhost:8000/?code=', '').replace('localhost:8000/?code=', '')
print(CODE)

# Headers do Access Token
headers = {"accept": "application/json", "content-type": "application/x-www-form-urlencoded"}
data = {
    "grant_type": "authorization_code",
    "client_id": client_id,
    "client_secret": client_secret,
    "code": CODE,
    "redirect_uri": 'http://localhost:8000'
}

# Enviando Requisição para obter o Refresh Token Permanente
response = requests.post("https://api.mercadolibre.com/oauth/token", headers=headers, data=data).json()
refresh_token = response['refresh_token']

# Salva no banco de dados os Refresh Token
TokenMercadoLivreFitGearAPI.objects.filter(id=1).update(refresh_token_inicial=refresh_token)  

print('Sucesso!')