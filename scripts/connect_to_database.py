from dotenv import load_dotenv
import os

def get_connection():
    load_dotenv()
    DATABASE = os.getenv('DATABASE')
    UID_BD = os.getenv('UID_BD')
    PWD_BD = os.getenv('PWD_BD')
    connection = ("Driver={SQL Server};"
                    "Server=erp.ambarxcall.com.br;"
                    "Database=" + DATABASE + ";"
                    "UID=" + UID_BD + ";"
                    "PWD=" + PWD_BD + ";"
                    "TrustServerCertificate=yes;")
    return connection

#