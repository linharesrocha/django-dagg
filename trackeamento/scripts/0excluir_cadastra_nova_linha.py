import requests
from pathlib import Path
import sys
from dotenv import load_dotenv
import os
import pandas as pd
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import pyodbc


BASE_DIR = Path(__file__).resolve().parent.parent.parent



def main():
    import django
    
    sys.path.append(str(BASE_DIR))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dagg.settings')
    django.setup()
    
    from trackeamento.models import UltimoProdutoCadastrado
    
    # cadastra nova linha
    UltimoProdutoCadastrado.objects.create(
        id=1,
        autoid=28531,
    )
    
main()