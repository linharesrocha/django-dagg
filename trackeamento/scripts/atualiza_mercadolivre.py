import requests
import os
from dotenv import load_dotenv
import json
import pandas as pd
from datetime import datetime, date
from openpyxl.workbook import Workbook


def visitas_anuncio(header, item_id):
    url_visitas = f"https://api.mercadolibre.com/visits/items?ids={item_id}"
    response = requests.get(url_visitas, headers=header).json()
    visitas = response[item_id]
    return visitas


def saude_anuncio(header):
    url_saude_anuncio = f'https://api.mercadolibre.com/items/{ITEM_ID}/health/actions'
    response = requests.get(url_saude_anuncio, headers=header).json()
    saude = response['health']
    acoes = response['actions']
    return saude, acoes


def retorna_posicao(header):
    #product = input('Produto: ').replace(' ', '%')
    product = 'Galão Halter'
    mlb_procurado = 'MLB-1933109839'.replace('-','').replace('/', '')
    
    url_pesquisa_ml = f'https://api.mercadolibre.com/sites/MLB/search?q={product}'
    response = requests.get(url_pesquisa_ml, headers=header).json()
    with open('result.txt', 'w') as arquivo:
        arquivo.write(json.dumps(response, indent=4))
    
    mlbs = []
    for dicionario in response['results']:
        mlb_anuncio = dicionario['id']
        mlbs.append(mlb_anuncio)

    if mlb_procurado in mlbs:
        index_mlb = mlbs.index(mlb_procurado)
        posicao_anuncio = index_mlb + 1
        print(f'Posição: {posicao_anuncio}')
    else:
        print(f'O valor {mlb_procurado} não está nos resultados.')



def informacoes_anuncio(header):
    # Lista
    (mlb_id_list, titulo_list, preco_list, vendas_list, vendas_por_mes_list, vendas_por_dia_list, visitas_list,
    vende_a_cada_visita_list, conversao_list, criacao_anuncio_list, tempo_de_anuncio_dias_list, ultima_atualizacao_list, tempo_ultima_atualizacao_list,
    pontuacao_anuncio_list, categoria_id_list, atributo_list, quantidade_desponivel_list, status_list, link_list) = [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []
    
    # MLBs
    df_mlbs = pd.read_excel('C:/workspace/api-mercado-livre/ml-anuncios.xlsx')

    for index, item_id in enumerate(df_mlbs['mlb-coluna']):
        item_id = 'MLB1089999807'
        
        print(f'{str(index+1)}/{str(len(df_mlbs))} - {item_id}')
        
        # Request
        url = f"https://api.mercadolibre.com/items/{item_id}?include_attributes=all"
        response = requests.get(url, headers=header).json()

        # Data atual
        data_atual = date.today()
        
        # Visitas
        visitas = visitas_anuncio(header, item_id)

        # Escrevendo em um arquivo txt
        with open(f'{item_id}.txt', 'w') as arquivo:
            arquivo.write(json.dumps(response, indent=4))
        
        # Informações base
        titulo = response['title']
        categoria_id = response['category_id']
        status = response['status']
        criacao_anuncio = response['date_created']
        ultima_atualizacao = response['last_updated']
        pontuacao_anuncio = response['health']
        link = response['permalink']
        vendas_anuncio = response['sold_quantity']
        
        if vendas_anuncio > 0:
            # Calcula conversão de vendas
            conversao = round((vendas_anuncio / visitas) * 100,2)
            # Calcula vende a cada visita
            vende_a_cada_visita = round(visitas / vendas_anuncio , 1)
        else:
            conversao = 0
            vende_a_cada_visita = 0
            
        # Converte as datas
        criacao_anuncio = criacao_anuncio.replace('Z', '')
        criacao_anuncio = datetime.strptime(criacao_anuncio, "%Y-%m-%dT%H:%M:%S.%f")
        criacao_anuncio = criacao_anuncio.strftime("%d/%m/%y")
        data_sub = datetime.strptime(criacao_anuncio, '%d/%m/%y').date()
        
        tempo_de_anuncio_dias = data_atual - data_sub
        tempo_de_anuncio_dias = tempo_de_anuncio_dias.days
        
        ultima_atualizacao = ultima_atualizacao.replace('Z', '')
        ultima_atualizacao = datetime.strptime(ultima_atualizacao, "%Y-%m-%dT%H:%M:%S.%f")
        ultima_atualizacao = ultima_atualizacao.strftime("%d/%m/%y")
        
        data_sub_at = datetime.strptime(ultima_atualizacao, '%d/%m/%y').date()
        tempo_ultima_atualizacao = data_atual - data_sub_at
        tempo_ultima_atualizacao = tempo_ultima_atualizacao.days
        
        # Coletando quantidade de variacoes
        quantidade_variacoes = len(response['variations'])
        if quantidade_variacoes > 0:
            for variation in response['variations']:
                
                # Escrevendo em um arquivo txt
                # with open(f'{item_id}-variation.txt', 'w') as arquivo:
                #     arquivo.write(json.dumps(variation, indent=4))

                mlb_id = variation['id']
                preco = variation['price']
                atributo = variation['attribute_combinations'][0]['value_name']
                quantidade_desponivel = variation['available_quantity']
                vendas = variation['sold_quantity']
                
                if vendas > 0:
                    # Calcula vendas por dia
                    vendas_por_dia = round(vendas / tempo_de_anuncio_dias,1)
                    # Calcula vendas por mês
                    vendas_por_mes = round(vendas_por_dia * 30, 1)

                else:
                    vendas_por_mes = 0
                    vendas_por_dia = 0

                mlb_id_list.append(mlb_id)
                preco_list.append(preco)
                atributo_list.append(atributo)
                quantidade_desponivel_list.append(quantidade_desponivel)
                vendas_list.append(vendas)
                status_list.append(status)
                pontuacao_anuncio_list.append(pontuacao_anuncio)
                ultima_atualizacao_list.append(ultima_atualizacao)
                tempo_de_anuncio_dias_list.append(tempo_de_anuncio_dias)
                criacao_anuncio_list.append(criacao_anuncio)
                titulo_list.append(titulo)
                categoria_id_list.append(categoria_id)
                vendas_por_dia_list.append(vendas_por_dia)
                vendas_por_mes_list.append(vendas_por_mes)
                visitas_list.append(visitas)
                tempo_ultima_atualizacao_list.append(tempo_ultima_atualizacao)
                vende_a_cada_visita_list.append(vende_a_cada_visita)
                conversao_list.append(conversao)
                link_list.append(link)
        else:
            mlb_id = response['id']
            preco = response['price']
            vendas = response['sold_quantity']
            atributo = 'N/A'
            quantidade_desponivel = 'N/A'
        
            if vendas > 0:
                # Calcula vendas por dia
                vendas_por_dia = round(vendas / tempo_de_anuncio_dias, 1)
                
                # Calcula vendas por mês
                vendas_por_mes = round(vendas_por_dia * 30, 1)
            else:
                vendas_por_mes = 0
                vendas_por_dia = 0
            
            mlb_id_list.append(mlb_id)
            preco_list.append(preco)
            atributo_list.append(atributo)
            quantidade_desponivel_list.append(quantidade_desponivel)
            vendas_list.append(vendas)
            status_list.append(status)
            pontuacao_anuncio_list.append(pontuacao_anuncio)
            ultima_atualizacao_list.append(ultima_atualizacao)
            tempo_de_anuncio_dias_list.append(tempo_de_anuncio_dias)
            criacao_anuncio_list.append(criacao_anuncio)
            titulo_list.append(titulo)
            categoria_id_list.append(categoria_id)
            vendas_por_dia_list.append(vendas_por_dia)
            vendas_por_mes_list.append(vendas_por_mes)
            visitas_list.append(visitas)
            tempo_ultima_atualizacao_list.append(tempo_ultima_atualizacao)
            vende_a_cada_visita_list.append(vende_a_cada_visita)
            conversao_list.append(conversao) 
            link_list.append(link)
        
        if index == 0:
            break

    # Criando dataframe
    dicionario = {'mlb_id': mlb_id_list,
              'titulo': titulo_list,
              'atributo': atributo_list,
              'preco': preco_list,
              'vendas': vendas_list,
              'vendas_por_mes': vendas_por_mes_list,
              'vendas_por_dia': vendas_por_dia_list,
              'visitas': visitas_list,
              'anuncio_vende_a_cada_visita': vende_a_cada_visita_list,
              'anuncio_conversao': conversao_list,
              'criacao_anuncio': criacao_anuncio_list,
              'tempo_de_anuncio_dias': tempo_de_anuncio_dias_list,
              'ultima_atualizacao': ultima_atualizacao_list,
              'tempo_ultima_atualizacao': tempo_ultima_atualizacao_list,
              'pontuacao_anuncio': pontuacao_anuncio_list,
              'categoria_id': categoria_id_list,
              'quantidade_disponivel': quantidade_desponivel_list,
              'status': status_list,
              'link': link_list}
    
    # Criando dataframe a partir do dicionario
    df = pd.DataFrame(dicionario)
    
    df.to_excel('relatorio-api-mercado-livre.xlsx', index=False)


if __name__ == '__main__':
    os.system('cls')
    
    # Carrega as variáveis de ambiente existentes, se houver
    load_dotenv()
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
    
    ITEM_ID = '/MLB-1933109839'.replace('-','').replace('/', '')
    USER_ID_DAGG = '195279505'
    NICKNAME_SELLER = 'DAGG SPORT'
    
    # Cabeçalho
    header = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    
    custo_frete_pra_vender2(header=header)
    