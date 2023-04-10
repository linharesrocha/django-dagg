from dotenv import load_dotenv
import os
from pathlib import Path
import pyodbc

def get_connection():
    env_path = Path('.') / 'C:\workspace\cadastro-aton\mordomo\programas\.env-sql'
    load_dotenv(dotenv_path=env_path)
    DATABASE = os.environ['DATABASE']
    UID = os.environ['UID']
    PWD = os.environ['PWD']
    connection = ("Driver={SQL Server};"
                    "Server=erp.ambarxcall.com.br;"
                    "Database=" + DATABASE + ";"
                                            "UID=" + UID + ";"
                                                            "PWD=" + PWD + ";")
    return connection