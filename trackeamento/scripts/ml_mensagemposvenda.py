from pathlib import Path
import sys
import requests
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))
from mercadolivre.scripts.config import reflash
 
# Obtem access token ML
ACCESS_TOKEN = reflash.refreshToken()

# Header
header = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

# Obtendo dia de ontem
ontem = datetime.now() - timedelta(days=5)
data_anterior = ontem.strftime('%Y-%m-%d')

message_seller = '''Olá, agradecemos por escolher nosso produto!
Caso tenha um momento, ficaríamos muito felizes se pudesse compartilhar seu comentário sobre nosso produto no Mercado Livre. ^-^'''

all_orders = requests.get(f"https://api.mercadolibre.com/orders/search?seller=195279505&order.status=paid&order.date_created.from={data_anterior}T00:00:00.000-00:00", headers=header).json()
total_orders = all_orders['paging']['total']

offset = 0

while offset < total_orders:
    # Envia mensagem
    for orders in all_orders['results']:
        order_tags = orders['tags']
        if 'delivered' in order_tags:
            order_id = orders['id']
            
            # Messages
            messages = str(requests.get(f"https://api.mercadolibre.com/messages/packs/{order_id}/sellers/195279505?tag=post_sale", headers=header).json())
            
            if "'status_code': 400" in messages:
                continue
            
            if "'substatus': 'blocked_by_time'" in messages:
                continue
            
            
            if "Olá, agradecemos por escolher nosso produto!" in messages:
                continue

            # Envia mensagem
            url = f'https://api.mercadolibre.com/messages/action_guide/packs/{order_id}/option'
            data = {
                "option_id": "OTHER",
                "text": f"{message_seller}",
            }

            response = requests.post(url, json=data, headers=header)
            
            print(order_id, response.status_code)
            
    offset += 50
    all_orders = requests.get(f"https://api.mercadolibre.com/orders/search?seller=195279505&order.status=paid&order.date_created.from={data_anterior}T00:00:00.000-00:00&offset={offset}", headers=header).json()
    print(offset, total_orders)