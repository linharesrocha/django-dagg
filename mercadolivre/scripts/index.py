from config import database_config
from config import token

if database_config.code == 'NULL' or database_config.code == '' or database_config.code == None:
    from config import permissao
else:
    print('Tudo certo!')