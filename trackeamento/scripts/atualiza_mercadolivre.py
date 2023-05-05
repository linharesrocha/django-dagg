import requests
from pathlib import Path
import sys
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))
from mercadolivre.scripts.config import reflash

def main():
    # Django Utils
    import os
    import django
    import sys
    from django.db.models import Min

    sys.path.append(str(BASE_DIR))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dagg.settings')
    django.setup()
    
    from trackeamento.models import MetricasMercadoLivre
    
    # Obtem access token
    ACCESS_TOKEN = reflash.refreshToken()
    
    # Header
    header = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    
    lista_mercadolivre = MetricasMercadoLivre.objects.values('termo_busca', 'mlb_anuncio').annotate(sku_min=Min('mlb_anuncio'))
    print(f'ATUALIZANDO TRACKEAMENTO DE {len(lista_mercadolivre)} PRODUTOS MERCADOLIVRE')
    
    for indice, anuncio in enumerate(lista_mercadolivre):
        print(f'{indice+1}/{len(lista_mercadolivre)} - {anuncio["mlb_anuncio"]}')
        termo_busca = anuncio['termo_busca']
        mlb_anuncio = anuncio['mlb_anuncio']

        # Visitas
        visitas_totais = requests.get(f"https://api.mercadolibre.com/visits/items?ids={mlb_anuncio}", headers=header).json().get(mlb_anuncio)

        # Nome / Pontuação Anúncio / Criação Anúncio
        response = requests.get(f"https://api.mercadolibre.com/items/{mlb_anuncio}?include_attributes=all", headers=header).json()
        titulo = response['title']
        pontuacao_anuncio = response['health']
        criacao_anuncio = response['date_created']
        dt = datetime.fromisoformat(criacao_anuncio[:-1])
        criacao_anuncio = dt.strftime("%Y-%m-%d %H:%M:%S")
        vendas_anuncio = response['sold_quantity']

        # Vende a cada visita / Conversao
        if vendas_anuncio > 0:
            taxa_conversao_total = round((vendas_anuncio / visitas_totais) * 100,2)
            vende_a_cada_visita = round(visitas_totais / vendas_anuncio , 1)
        else:
            taxa_conversao = 0
            vende_a_cada_visita = 0
            
        # Visita Diaria / Vendas Diaria / Taxa Conversao Diaria
        visitas_diaria = round(visitas_totais / 30,2)
        vendas_diaria = round(vendas_anuncio / 30, 2)
        taxa_conversao_diaria = round((vendas_diaria / visitas_diaria) * 100, 2)

        # Posição do Anúncio
        offset = 0
        mlbs = []
        mlb_found = False
        posicao_anuncio = None
        

        while True:
            # Limita a quantidade de requisições    
            if offset >= 500 or mlb_found:
                break

            response = requests.get(f'https://api.mercadolibre.com/sites/MLB/search?q={termo_busca}&offset={offset}', headers=header).json()

            # Proxima pagina
            offset = offset + 50
            
            # Adiciona todos os mlbs em uma lista
            for dicionario in response['results']:
                mlb_anuncio = dicionario['id']
                mlbs.append(mlb_anuncio)

                # Verifica se o mlb está na lista e retorna o index + 1 se não retorna None
                if mlb_anuncio in mlbs:
                    posicao_anuncio = mlbs.index(mlb_anuncio) + 1
                    mlb_found = True
                    break

        # Obtem a página
        if posicao_anuncio is None:
            pagina = None
        elif posicao_anuncio <= 56:
            pagina = 1
        else:
            pagina = (posicao_anuncio - 57) // 56 + 2
            pagina = min(pagina, 10)


        # Salvando no banco de dados
        novo_registro_meli = MetricasMercadoLivre()
        novo_registro_meli.nome = titulo
        novo_registro_meli.termo_busca = termo_busca
        novo_registro_meli.mlb_anuncio = mlb_anuncio
        novo_registro_meli.posicao = posicao_anuncio
        novo_registro_meli.pagina = pagina
        novo_registro_meli.visita_diaria = visitas_diaria
        novo_registro_meli.visita_total = visitas_totais
        novo_registro_meli.vendas_diaria = vendas_diaria
        novo_registro_meli.vendas_total = vendas_anuncio
        novo_registro_meli.vende_a_cada_visita = vende_a_cada_visita
        novo_registro_meli.taxa_conversao_diaria = taxa_conversao_diaria
        novo_registro_meli.taxa_conversao_total = taxa_conversao_total
        novo_registro_meli.pontuacao_anuncio = pontuacao_anuncio
        novo_registro_meli.criacao_anuncio = criacao_anuncio
        novo_registro_meli.save()
        
    
main()