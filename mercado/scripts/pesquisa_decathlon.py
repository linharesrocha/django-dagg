from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from time import sleep
import platform


def main(pesquisa, quantidade):
    pesquisa = pesquisa.replace(' ', '+').lower()
    url_pesquisa = f"https://www.decathlon.com.br/pesquisa?q={pesquisa}&sort=score_desc&page=0"
    
    if platform.system() == 'Linux':
        webdriver_path = 'chromedriver'
    elif platform.system() == 'Windows':
        webdriver_path = 'chromedriver.exe'

    service = Service(webdriver_path)
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=service, options=options)

    driver.get(url_pesquisa)
    sleep(10)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    driver.quit()

    posicao_list = []
    names_list = []
    price_list = []
    link_list = []
    photo_list = []

    anuncios = soup.find_all(class_='product-card-bluefriday')

    for index, anuncio in enumerate(anuncios):
        # Para caso a quantidade de anuncio alcançar o limite
        if index == quantidade:
            break
        
        # Posição
        posicao_list.append(index+1)
        
        # Nome
        name = anuncio.find(class_='product-card__content--product-name').text.strip()
        names_list.append(name)
        
        # Preço
        price = anuncio.find(class_='product-card__content--price')
        price_1 = price.find('p').text.replace('R$', '').replace(',', '.').replace(' ', '').strip()
        price_list.append(price_1)

        # Link
        link = anuncio.find('a', attrs={'data-testid': 'product-link', 'href': True}).get('href')
        link = f'https://www.decathlon.com.br{link}'
        link_list.append(link)
        
        # Foto
        foto = anuncio.find('img', attrs={'src': True, 'data-store-image':'true'}).get('src')
        photo_list.append(foto)


    dicionario = {
        'posicao': posicao_list,
        'nome': names_list,
        'preco': price_list,
        'link': link_list,
        'foto': photo_list
    }

    dados_combinados = zip(
        dicionario['posicao'],
        dicionario['nome'],
        dicionario['preco'],
        dicionario['link'],
        dicionario['foto']
    )

    return dados_combinados