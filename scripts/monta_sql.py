import colorama
from colorama import Fore
import os

os.system('cls')
list_cod = [
]

print(Fore.RED, '\nLISTA DE CÓDIGOS:')
while True:
    user_input  = input()
    if user_input  == '':
        break
    else:
        list_cod.append(user_input)

print(Fore.RED, '\nCOLUNA:')
coluna = input('').upper()
last_element = list_cod[-1]
string_inicial = f"WHERE {coluna} IN("

print(Fore.RED + '\nCÓDIGO PARA O BANCO DE DADOS:')
print(Fore.BLUE + string_inicial, end="")
for cod in list_cod:
    if cod == last_element:
        print("'" + cod + "')")
    else:
        print("'" + cod + "', ", end="")

print(Fore.RED + '\nQUANTIDADE TOTAL DOS DADOS:')
print(Fore.BLUE + str(len(list_cod)))
print(' ')