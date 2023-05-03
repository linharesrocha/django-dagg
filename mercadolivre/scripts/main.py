import requests
from config.database_config import *


def visitas_anuncio(header, item_id):
    url_visitas = f"https://api.mercadolibre.com/visits/items?ids={item_id}"
    response = requests.get(url_visitas, headers=header).json()
    visitas = response[item_id]
    return visitas

if __name__ == '__main__':

    ITEM_ID = '/MLB-1933109839'.replace('-','').replace('/', '')
    USER_ID_DAGG = '195279505'
    NICKNAME_SELLER = 'DAGG SPORT'
    
    # Cabeçalho
    header = {"Authorization": f"Bearer {access_token}"}
    
    visitas = visitas_anuncio(header=header, item_id=ITEM_ID)
    
    print(visitas)