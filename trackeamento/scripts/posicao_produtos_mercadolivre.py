import requests
from bs4 import BeautifulSoup

def main(termo_busca, mlb_anuncio):
    # Global
    user_agent = 'Mozilla/5.0 (Windows; 10) Gecko/20100101 Firefox/88.0'
    
    # Controle
    pagina_normal = 1
    contador_pagina = 49
    posicao_anuncio_normal = None
    mlbs = []
    mlb_found = False
    
    # Primeira página
    response = requests.get(f'https://lista.mercadolivre.com.br/{termo_busca}', headers={'User-agent': user_agent})
    
    # Página normal
    while True:        
        # Request
        soup = BeautifulSoup(response.content, 'html.parser')
        items = soup.find_all(class_='ui-search-layout__item')
        
        # Armazena mlb dos anúncios
        for item in items:
            form_class = item.find(class_='ui-search-bookmark')
            item_id = form_class.find('input', {'name': 'itemId'})['value']
            mlbs.append(item_id)
            
            if str(item_id) == str(mlb_anuncio):
                posicao_anuncio_normal = mlbs.index(mlb_anuncio) + 1
                mlb_found = True
                break
            
        # Stop
        if mlb_found or pagina_normal > 20:
            if posicao_anuncio_normal == None:
                pagina_normal = None
                break
        else:
            pagina_normal += 1
            response = requests.get(f'https://lista.mercadolivre.com.br/{termo_busca}_Desde_{contador_pagina}_NoIndex_True', headers={'User-agent': user_agent})
            contador_pagina += 48
                
    # Controle
    pagina_normal = 1
    contador_pagina = 49
    posicao_anuncio_normal = None
    mlbs = []
    mlb_found = False
    
    # Página Full
    while True:
        pass

posicao_anuncio_normal, pagina_normal = main('maquina de tosa', 'MLB3295486402')

print(posicao_anuncio_normal)
print(pagina_normal)