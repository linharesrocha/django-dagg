from bs4 import BeautifulSoup
import requests



def main(pesquisa, quantidade, opcao_pesquisa):
    url_mais_populares = f'https://www.netshoes.com.br/busca?nsCat=Natural&q={pesquisa}'
    url_mais_vendidos = f'https://www.netshoes.com.br/busca?nsCat=Natural&q={pesquisa}&sort=best-sellers'
    url_lancamentos = f'https://www.netshoes.com.br/busca?nsCat=Natural&q={pesquisa}&sort=new-releases'
    url_ofertas = f'https://www.netshoes.com.br/busca?nsCat=Natural&q={pesquisa}&sort=offers'
    url_mais_avaliados = f'https://www.netshoes.com.br/busca?nsCat=Natural&q={pesquisa}&sort=review-stars'
    url_maior_preco = f'https://www.netshoes.com.br/busca?nsCat=Natural&q={pesquisa}&sort=highest-first'
    url_menor_preco = f'https://www.netshoes.com.br/busca?nsCat=Natural&q={pesquisa}&sort=lowest-first'

    if opcao_pesquisa >= 1 and opcao_pesquisa <= 7:
        if opcao_pesquisa == 1:
            url = url_mais_populares
        elif opcao_pesquisa == 2:
            url = url_mais_vendidos
        elif opcao_pesquisa == 3:
            url = url_lancamentos
        elif opcao_pesquisa == 4:
            url = url_ofertas
        elif opcao_pesquisa == 5:
            url = url_mais_avaliados
        elif opcao_pesquisa == 6:
            url = url_maior_preco
        elif opcao_pesquisa == 7:
            url = url_menor_preco


    user_agent = {'User-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)' 'Chrome/106.0.0.0 Safari/537.36'}

    titulo_list = []
    preco_de_list = []
    preco_por_list = []
    avaliacoes_list = []
    notas_list = []
    link_anuncios_list = []
    posicao_list = []
    link_photos_list = []

    page = requests.get(url, headers=user_agent)
    site = BeautifulSoup(page.content, "html.parser")

    # Obtendo links
    container = site.find(class_="item-list")

    # Coletando todos links href do atributo a
    all_links = [link['href'] for link in container.find_all('a')]
        
    # Filtrando apenas os links que começam com //www.netshoes.com
    netshoes_links = [link.replace('//','https://') for link in all_links if link.startswith('//www.netshoes.com')]

    # Removendo links que não são de anúncios
    for i in range(len(netshoes_links)-1, -1, -1):
        if "//www.netshoes.com.br/busca?" in netshoes_links[i]:
            del netshoes_links[i]

    # Entrando em cada link (produto)
    for index, link in enumerate(netshoes_links):
        if index == quantidade:
            break
        
        page = requests.get(link, headers=user_agent)
        site = BeautifulSoup(page.content, "html.parser")
        
        container = site.find(id='content')
        
        # Posição do anúncio
        posicao_list.append(index+1)
        
        # Titulo do Anúncio
        title = container.find(class_="short-description").find('h1').getText()
        
        # Nem sempre terá Preço DE
        try:
            preco_de = container.find(class_="reduce").getText().replace('R$ ', '')
        except:
            preco_de = '0'
            
        # Preço Por do Anúncio
        preco_por = container.find('div', class_="default-price").find('strong').getText().replace('R$ ', '')
        
        # Avaliações do Produto
        try:
            container_review = container.find(class_="rating-box")
            avaliacoes = container_review.find('span', class_='rating-box__numberOfReviews').getText().replace(' avaliações', '').replace(' avaliação', '')
            nota = container_review.find(class_='rating-box__value').getText()
        except:
            avaliacoes = '0'
            nota = '0'
            
        # Foto
        link_photo = container.find('img', class_='zoom').get('src')
        
        # Trata valores
        preco_de = float(preco_de.replace(',', '.'))
        preco_por = float(preco_por.replace(',', '.'))
        nota = float(nota.replace(',', '.'))
        avaliacoes = float(avaliacoes.replace(',', '.'))
        
        # Append lista
        titulo_list.append(title)
        preco_de_list.append(preco_de)
        preco_por_list.append(preco_por)
        avaliacoes_list.append(avaliacoes)
        notas_list.append(nota)
        link_anuncios_list.append(link)
        link_photos_list.append(link_photo)


    # Criar o dicionário
    dicionario = {
        "posicao": posicao_list,
        "titulo": titulo_list,
        "preco_de": preco_de_list,
        "preco_por": preco_por_list,
        "avaliacoes": avaliacoes_list,
        "notas": notas_list,
        "link_fotos": link_photos_list,
        "link_anuncios": link_anuncios_list
    }
    
        # Combine as listas usando a função zip
    dados_combinados = zip(
        dicionario["posicao"],
        dicionario["titulo"],
        dicionario["preco_de"],
        dicionario["preco_por"],
        dicionario["avaliacoes"],
        dicionario["notas"],
        dicionario["link_fotos"],
        dicionario["link_anuncios"]
    )
    
    return dados_combinados