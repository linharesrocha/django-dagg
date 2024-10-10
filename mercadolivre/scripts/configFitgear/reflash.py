import requests
import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
from database_config import *


def refreshToken():
    headers = {"accept": "application/json", "content-type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "refresh_token",
        "client_id": client_id, 
        "client_secret": client_secret,
        "refresh_token": refresh_token_inicial,
        "redirect_uri": 'https://fitgear.com.br'
    }

    # Enviando Requisição para obter o Refresh Token Temporario
    response = requests.post("https://api.mercadolibre.com/oauth/token", headers=headers, data=data).json()
    access_token = response['access_token']
    
    return access_token

refreshToken()