import json
from datetime import datetime
import requests
import boto3
import os
import requests

TMDB_TOKEN = os.getenv("TMDB_TOKEN")

#Configurações S3
NOME_DO_BUCKET_S3 = os.getenv("BUCKET_S3")
REGIAO_BUCKET = os.getenv("REGIAO_BUCKET")
s3 = boto3.client('s3', region_name=REGIAO_BUCKET)


DATA_ATUAL = datetime.today()

def lambda_handler(event, context):
    import_jsons(TMDB_TOKEN)

def import_jsons(TMDB_TOKEN):
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {TMDB_TOKEN}"
    }

    #FILMES EM CARTAZ

    #Descobrindo total de paginas
    pagina = 1

    url = f"https://api.themoviedb.org/3/movie/now_playing?language=en-US&page={pagina}"
    nome_arquivo = "filmes_em_cartaz"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    dados = response.json()
    total_paginas = dados.get('total_pages')

    fetch_and_upload(url, nome_arquivo)

    for pagina in range(2, total_paginas + 1):
        url = f"https://api.themoviedb.org/3/movie/now_playing?language=en-US&page={pagina}"
        fetch_and_upload(url, nome_arquivo, pagina)

    #LISTA DE GENEROS
    url = "https://api.themoviedb.org/3/genre/movie/list?language=en"
    nome_arquivo = "lista_de_generos"
    fetch_and_upload(url, nome_arquivo)

    #FILMES POPULARES
    url = "https://api.themoviedb.org/3/movie/popular?language=en-US&page=1"
    nome_arquivo = "filmes_populares"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    dados = response.json()
    total_paginas = dados.get('total_pages')
    fetch_and_upload(url, nome_arquivo)

    for pagina in range(2, total_paginas + 1):
        url = f"https://api.themoviedb.org/3/movie/popular?language=en-US&page={pagina}"
        fetch_and_upload(url, nome_arquivo, pagina)

def fetch_and_upload(url, nome_arquivo, pagina=1):
    response = requests.get(url, headers={"accept": "application/json", "Authorization": f"Bearer {TMDB_TOKEN}"})
    response.raise_for_status()
    data = response.json()
    upload_to_s3(data, nome_arquivo, pagina)


def upload_to_s3(data, nome_arquivo, pagina):
    chave_s3 = (
        f"RAW/TMDB/JSON/{DATA_ATUAL.year}/{DATA_ATUAL.month}/{DATA_ATUAL.day}/{nome_arquivo}_{pagina}.json"
    )
    s3.put_object(Bucket=NOME_DO_BUCKET_S3, Key=chave_s3, Body=json.dumps(data, ensure_ascii=False, indent=4),
        ContentType="application/json"
    )
