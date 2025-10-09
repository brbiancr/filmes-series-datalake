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

1. Criar uma **imagem Docker** baseada no **Amazon Linux 2023** e instalar `pip` e `zip`.
2. Instalar as bibliotecas `requests` e `python-dotenv`, compactá-las em `minha-camada.zip` e subir como **layer no AWS Lambda**.
3. Criar a função Lambda para **consumir a API do TMDB** usando as credenciais configuradas no `.env`.
4. **Gerar arquivos JSON** com os dados de filmes e séries.
5. Fazer **upload automático** dos arquivos para o **bucket S3**, na **camada RAW** do Data Lake.

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

### 1️⃣ Criação da Layer (Camada)

Para criar a layer do Lambda, será utilizada uma imagem mínima do **Amazon Linux 2023**, garantindo compatibilidade com o ambiente do AWS Lambda.

```docker
FROM amazonlinux:2023

RUN yum update -y
RUN yum install -y \
    python3-pip \
    zip

RUN yum -y clean all

```

### 2️⃣ Construção da Imagem Docker

```bash
docker build -t amazonlinuxpython39 .
```

### 3️⃣  Acessando o Container

Inicie o container em modo interativo:

```bash
docker run -it amazonlinuxpython39 bash
```

### 4️⃣ Estrutura de Pastas no Container

Crie as pastas que irão armazenar as dependências de layer:

```bash
cd ~
mkdir layer_dir
cd layer_dir/
mkdir python
cd python/
pwd
```

### 5️⃣ Instalação das Dependências

Dentro da pasta python, instale as bibliotecas necessárias:

```bash
pip3 install requests -t .
pip3 install python-dotenv -t .
```

### 6️⃣ Compactação da Layer

Após instalar as dependências, compacte o conteúdo:

```bash
zip -r minha-camada.zip .
```

### 7️⃣ Copiando a Layer para a Máquina Local

Abra outro terminal e copie o .zip gerado do container para sua máquina local.

Substitua CONTAINER_ID pelo ID do seu container:

```bash
docker cp CONTAINER_ID:/root/layer_dir/minha-camada.zip ./
```

### 8️⃣ Incluindo o Script de Upload no Container

Em outro terminal:

```bash
docker exec -it CONTAINER_ID mkdir -p /root/layer_dir
docker cp upload_s3.py CONTAINER_ID:/root/layer_dir/
```

Depois, dentro do container, compacte novamente:

```bash
cd /root/layer_dir
zip -r minha-camada.zip .
```

E copie novamente para a máquina local: 

```bash
docker cp CONTAINER_ID:/root/layer_dir/minha-camada.zip ./
```

### 9️⃣ Upload da Layer no AWS Lambda

- Acesse o **AWS Management Console**
- Vá até **Lambda → Layers → Create layer**
- Faça upload do arquivo `minha-camada.zip`
- Selecione a versão do Python compatível (ex: **Python 3.9**)
- Clique em **Create**

### 1️⃣0️⃣ Criação da Função Lambd

1. No console do **AWS Lambda**, crie uma nova função 
2. Anexe a layer criada anteriormente
3. Faça o upload do seu script `upload_s3.py`
4. Configure as **variáveis de ambiente** listadas no `.env`:

| Variável | Descrição |
| --- | --- |
| `NOME_DO_BUCKET_S3` | Nome do bucket S3 de destino |
| `REGIAO_DO_BUCKET` | Região do bucket |
| `NOME_DO_PERFIL_SSO` | Nome do perfil de autenticação |
| `aws_access_key_id` | Chave de acesso AWS |
| `aws_secret_access_key` | Chave secreta AWS |
| `aws_session_token` | Token de sessão temporário |

### ✅ Resultado Esperado

Ao executar a função Lambda, os dados da API do TMDB serão baixados e armazenados automaticamente no bucket S3, compondo a **camada RAW** do Data Lake.