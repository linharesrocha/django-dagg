import requests
import os
from time import sleep
import webbrowser
from database_config import *

# # Url para obter Refresh Token Inicial
# url = f"https://auth.mercadolivre.com.br/authorization?response_type=code&client_id=1420082865478440"
# # print(url)
# # # Enviando requisição e abrendo a página
# webbrowser.open(url)

# Armazena o Refresh Token
CODE = input('Refresh Token: ').replace('https://fitgear.com.br/?code=', '').replace('fitgear.com.br/?code=', '')
print(CODE)

# Headers do Access Token
headers = {"accept": "application/json", "content-type": "application/x-www-form-urlencoded"}
data = {
    "grant_type": "authorization_code",
    "client_id": client_id,
    "client_secret": client_secret,
    "code": CODE,
    "redirect_uri": 'https://fitgear.com.br'
}

# Enviando Requisição para obter o Refresh Token Permanente
response = requests.post("https://api.mercadolibre.com/oauth/token", headers=headers, data=data).json()
print(response)
refresh_token = response['refresh_token']
print(refresh_token)

# Salva no banco de dados os Refresh Token
TokenMercadoLivreFitGearAPI.objects.filter(id=1).update(refresh_token_inicial=refresh_token)  

print('Sucesso!')