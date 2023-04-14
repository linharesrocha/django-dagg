from dotenv import load_dotenv
import os

def get_connection():
    load_dotenv()
    DATABASE = os.environ['DATABASE']
    UID = os.environ['UID']
    PWD = os.environ['PWD']
    connection = ("Driver={SQL Server};"
                    "Server=erp.ambarxcall.com.br;"
                    "Database=" + DATABASE + ";"
                                            "UID=" + UID + ";"
                                                            "PWD=" + PWD + ";")
    return connection

#