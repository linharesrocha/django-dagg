from pathlib import Path
import sys
import os
import requests
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))
from mercadolivre.scripts.config import reflash

def main():    
    # Obtem access token ML
    ACCESS_TOKEN = reflash.refreshToken()
    
    # Header
    header = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    
    data_packs = requests.get(f"https://api.mercadolibre.com/messages/unread?role=seller&tag=post_sale", headers=header).json()
    
    if len(data_packs['results']) == 0:
        print('Nenhuma mensagem de pós venda não lida')
        return
    
    # Slack
    load_dotenv()
    client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])
    SLACK_CHANNEL_ID='C030X3UMR3M'
    
    # Obtem dados do pack
    pack_id = None
    text_message = None
    last_message = None
    
    message_slack_default = f"ML MENSAGENS!\n{len(data_packs['results'])} mensagens de pós venda não lidas.\n"
    
    try:
        client.chat_postMessage(channel=SLACK_CHANNEL_ID, text=message_slack_default)
    except SlackApiError as e:
        print("Error sending message: {}".format(e))
        
    
    for i in data_packs['results']:
        pack_id = i['resource'].replace('/packs/', '').replace('/sellers/195279505', '')
        text_message = requests.get(f"https://api.mercadolibre.com/messages/packs/{pack_id}/sellers/195279505?tag=post_sale", headers=header).json()
        last_message = text_message['messages'][0]['text']
        
        message_slack = f"ID: {pack_id}\nMensagem: {last_message}\n"
        
        try:
            client.chat_postMessage(channel=SLACK_CHANNEL_ID, text=message_slack)
        except SlackApiError as e:
            print("Error sending message: {}".format(e))