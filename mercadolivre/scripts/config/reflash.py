from database_config import *
import requests

def refreshToken():
    headers = {"accept": "application/json", "content-type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "refresh_token",
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token_inicial,
        "redirect_uri": 'http://localhost:8000'
    }
    
    # Enviando Requisição para obter o Refresh Token Temporario
    response = requests.post("https://api.mercadolibre.com/oauth/token", headers=headers, data=data).json()
    access_token = response['access_token']
    
    return access_token