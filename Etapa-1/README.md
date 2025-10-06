# Etapa 1 -  Camada RAW

> É a **primeira camada do Data Lake**, responsável por **armazenar os dados brutos**, do jeito que foram recebidos das fontes. Ela funciona como um **repositório histórico e de rastreabilidade** — se algo der errado em etapas posteriores, você pode sempre voltar aqui e reprocessar.
> 

## 🔹 **Objetivo**

- **Preservar a integridade original** dos dados.
- Garantir que nada seja perdido — nem erros, nem duplicações, nem inconsistências.
- **Desacoplar a ingestão da transformação**, ou seja, deixar a coleta independente da limpeza.
- Servir como **base para reproduzir pipelines** (ex: se precisar reconstruir a camada tratada no futuro).

## 🔹 Etapa 1A – Ingestão  Batch

Nesta estapa deve ser contruído um código Python que será executado dentro de um container Docker para carregar os dados locais dos arquivos disponibilizados para nuvem. Nesse caso utilizaremos, principalmente, a lib boto 3 como parte do processo de ingestão via batch para geração de arquivo (CSV).

![image 1.png](../assets/image%202.png)

### 🧩 Passos do Processo

1. Ler os arquivos **de filmes e séries** no formato `.csv`, sem aplicar filtros ou transformações.
2. Fazer o upload desses arquivos diretamente para o bucket **`raw/`** no S3.

### 📝 **Observação Importante**

> ⚠️ Os arquivos .csv originais não estão versionados neste repositório para evitar o armazenamento de grandes volumes de dados.
> 
> 
> Eles podem ser acessados diretamente no **bucket S3** configurado para este projeto.
> 
> Caso deseje testar localmente, há amostras reduzidas dos dados disponíveis na pasta:
> 
> ```
> data/sample/
> ```
> 
> com apenas algumas linhas, para fins de demonstração.
> 

### 🚀 Executando o Pipeline via Docker

### Pré-requisitos

- Docker instalado
- CSVs de filmes e séries disponíveis na pasta `sample_data/` ou caminho correto
- Arquivo `.env` com as seguintes variáveis definidas:

```
# Caminhos dos arquivos CSV locais
CAMINHO_DO_ARQUIVO_LOCAL_MOVIES=../Filmes+e+series/movies.csv
CAMINHO_DO_ARQUIVO_LOCAL_SERIES=../Filmes+e+series/series.csv

# Bucket S3
NOME_DO_BUCKET_S3=meu-bucket
REGIAO_DO_BUCKET=us-east-1

# Perfil SSO (opcional)
NOME_DO_PERFIL_SSO=default

# Credenciais AWS
aws_access_key_id=SEU_ACCESS_KEY
aws_secret_access_key=SUA_SECRET_KEY
aws_session_token=SEU_SESSION_TOKEN  # opcional, se estiver usando STS ou SSO

```

### 1️⃣ Build da imagem

```bash
docker build -t csv_ingestion .
```

### 2️⃣ Executar o container

```bash
docker run --rm --env-file .env csv_ingestion
```

> O script fará upload dos CSVs para o bucket S3 configurado.
> 
> 
> Logs de execução serão exibidos no terminal.
> 

### 3️⃣ Rodando localmente (sem Docker)

```bash
python script.py
```

> O script irá ler os arquivos CSV definidos em CAMINHO_DO_ARQUIVO_LOCAL_MOVIES e CAMINHO_DO_ARQUIVO_LOCAL_SERIES e fazer o upload para o bucket S3 configurado.
> 
> 
> Logs de execução serão exibidos no terminal.
> 

---

## 🔹 Etapa 1B – Ingestão de API

Nesta etapa iremos capturar dados do TMDB via `AWS Lambda` realizando requisições para a API. Os dados coletados devem ser persistidos em Amazon S3, camada RAW Zone, mantendo o formatto da origem (JSON). 

O objetivo desta etapa é complementar os dados dos Filmes e Séries, carregados na Etapa 1B, com dados oriundos do TMDB.

![image.png](../assets/image%201.png)

### 🧩 Passos do Processo

1. Configurar as credenciais da API TMDB (chave de acesso) no `.env`.
2. Fazer requests para os endpoints de filmes e séries.
3. Salvar a resposta da API em arquivos JSON locais.
4. Fazer o upload desses arquivos para o bucket S3, na pasta correspondente à camada RAW.

### 📝 **Observação Importante**

> ⚠️ Os arquivos .json originais não estão versionados neste repositório para evitar o armazenamento de grandes volumes de dados.
> 
> 
> Eles podem ser acessados diretamente no **bucket S3** configurado para este projeto.
> 
> Caso deseje testar localmente, há amostras reduzidas dos dados disponíveis na pasta:
> 
> ```
> data/sample/
> ```
> 
> com apenas algumas linhas, para fins de demonstração.
>