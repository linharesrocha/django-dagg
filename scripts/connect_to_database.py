from dotenv import load_dotenv
import os

def get_connection():
    load_dotenv()
    DATABASE = os.getenv('DATABASE')
    UID = os.getenv('UID')
    PWD = os.getenv('PWD')
    connection = ("Driver={SQL Server};"
                    "Server=erp.ambarxcall.com.br;"
                    "Database=" + DATABASE + ";"
                    "UID=" + UID + ";"
                    "PWD=" + PWD + ";"
                    "TrustServerCertificate=yes;")
    return connection

#