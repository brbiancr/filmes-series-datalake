import pandas as pd
import boto3
import datetime
from dotenv import load_dotenv
import os

# Configurações de variaveis
load_dotenv()
NOME_DO_BUCKET_S3 = os.getenv('NOME_DO_BUCKET_S3')
REGIAO_DO_BUCKET = os.getenv('REGIAO_DO_BUCKET')
CAMINHO_DO_ARQUIVO_LOCAL_MOVIES = os.getenv('CAMINHO_DO_ARQUIVO_LOCAL_MOVIES')
CAMINHO_DO_ARQUIVO_LOCAL_SERIES = os.getenv('CAMINHO_DO_ARQUIVO_LOCAL_SERIES')


#Cria o cliente S3 sem especificar perfil SSO
sessao_s3 = boto3.Session()
s3 = sessao_s3.client('s3', region_name=REGIAO_DO_BUCKET)

# Cria o bucket
try:
    s3.create_bucket(Bucket=NOME_DO_BUCKET_S3)
except s3.exceptions.BucketAlreadyOwnedByYou:
    print(f"Bucket {NOME_DO_BUCKET_S3} já existe")

#Upload dos arquivos
DATA_ATUAL = datetime.date.today()


arquivos = [
    (CAMINHO_DO_ARQUIVO_LOCAL_MOVIES, f"RAW/Local/CSV/Movies/{DATA_ATUAL.year}/{DATA_ATUAL.month}/{DATA_ATUAL.day}/movies.csv"),
    (CAMINHO_DO_ARQUIVO_LOCAL_SERIES, f"RAW/Local/CSV/Series/{DATA_ATUAL.year}/{DATA_ATUAL.month}/{DATA_ATUAL.day}/series.csv")
]

for arquivo_local, chave_s3 in arquivos:
    try:
        s3.upload_file(arquivo_local, NOME_DO_BUCKET_S3, chave_s3)
        print(f"Upload concluído: {arquivo_local} → s3://{NOME_DO_BUCKET_S3}/{chave_s3}")
    except Exception as e:
        print(f"Erro ao enviar {arquivo_local}: {e}")