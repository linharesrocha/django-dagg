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
            
            # Confere se o anúncio é o que está sendo buscado
            if str(item_id) == str(mlb_anuncio):
                posicao_anuncio_normal = mlbs.index(mlb_anuncio) + 1
                mlb_found = True
                break
            
        # Caso o anúncio seja encontrado ou a página ser maior que 20
        if mlb_found or pagina_normal > 20:
            if posicao_anuncio_normal == None:
                pagina_normal = None
            break
        else:
            pagina_normal += 1
            response = requests.get(f'https://lista.mercadolivre.com.br/{termo_busca}_Desde_{contador_pagina}_NoIndex_True', headers={'User-agent': user_agent})
            contador_pagina += 48
                
    # Controle
    pagina_full = 1
    contador_pagina = 49
    posicao_anuncio_full = None
    mlbs = []
    mlb_found = False
    
    # Primeira página
    response = requests.get(f'https://lista.mercadolivre.com.br/{termo_busca}_Frete_Full', headers={'User-agent': user_agent})
    
    # Página Full
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
                posicao_anuncio_full = mlbs.index(mlb_anuncio) + 1
                mlb_found = True
                break
        
        # Stop
        if mlb_found or pagina_full > 10:
            if posicao_anuncio_full == None:
                pagina_full = None
            return posicao_anuncio_normal, pagina_normal, posicao_anuncio_full, pagina_full
        else:
            pagina_full += 1
            response = requests.get(f'https://lista.mercadolivre.com.br/{termo_busca}_Frete_Full_Desde_{contador_pagina}_NoIndex_True', headers={'User-agent': user_agent})
            contador_pagina += 48