# Etapa 2 - Camada TRUSTED

> É a **segunda camada do Data Lake.** Nesta etapa os dados brutos da camada RAW são **limpos, integrados e padronizados** usando **Apache Spark** rodando no **AWS Glue**. 
O resultado são arquivos **PARQUET** otimizados, **particionados por data de ingestão (ano/mês/dia)**, armazenados em **Amazon S3**, **catalogados no Glue Data Catalog** e **consultáveis via AWS Athena**.
> 

## 🔹 **Objetivo**

- Unificar e padronizar esquemas vindos de diferentes fontes (CSV, JSON TMDB).
- Tratar e normalizar tipos de dados (datas, numéricos, booleanos, textos).
- Explodir arrays (como listas de gêneros ou IDs) em linhas normalizadas.
- Remover inconsistências e dados corrompidos.
- Persistir os dados em **formato Parquet** (colunar e otimizado).
- Particionar os dados por `ano_raw`, `mes_raw`, `dia_raw` para facilitar consultas.
- Registrar as tabelas no **Glue Data Catalog** para uso no **Athena**.

![image.png](../assets/image%203.png)

## 🔹 Etapa 2A – Processamento dos CSVs

### 🧩 Passos do Processo

1. Leitura dos arquivos `.csv` diretamente do S3 (camada RAW).
2. Conversão e padronização de datas e valores numéricos.
3. Explosão de colunas com múltiplos valores.
4. Escrita dos resultados no bucket `TRUSTED` em formato **Parquet**.

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

## 🔹 Etapa 2B – Processamento dos JSONs (TMDB)

### 🧩 Passos do Processo

1. Leitura dos arquivos `.json` do bucket `RAW/TMDB/JSON/...`.
2. Explosão de arrays (`results`, `genre_ids`, `genres`) em linhas individuais.
3. Padronização de colunas (`release_date` como `DATE`, `popularity` como `DOUBLE`, etc).
4. Extração automática de `ano_raw`, `mes_raw`, `dia_raw` a partir do caminho do arquivo S3.
5. Escrita do resultado em formato **Parquet**, **particionado por data**.

### 📝 **Observação Importante**

> ⚠️ Os arquivos .json originais não estão versionados neste repositório para evitar o armazenamento de grandes volumes de dados.
> 
> 
> Eles são obtidos automaticamente via API TMDB.
> 
> Caso deseje testar localmente, há amostras reduzidas dos dados em:
> 
> ```bash
> data/sample/json/
> 
> ```
> 

---

## 🧩 **Criação do Glue Catalog**

Para que as tabelas sejam consultáveis via **AWS Athena**, é necessário criar e popular o catálogo de metadados no **AWS Glue**.

### 🧩 Passos do Processo

1. Criar um DataBase no Glue
2. Criar um Crawler
3. Consultar no Athena

---

## 🧾 **Execução do Job no Glue**

### Parâmetros esperados

O script recebe os seguintes parâmetros no Glue Job:

| Parâmetro | Descrição |
| --- | --- |
| `S3_INPUT_PATH_MOVIES_CARTAZ` | Caminho S3 dos JSONs de filmes em cartaz |
| `S3_INPUT_PATH_MOVIES_POPULARES` | Caminho S3 dos JSONs de filmes populares |
| `S3_INPUT_PATH_MOVIES_GENEROS` | Caminho S3 dos JSONs de gêneros |
| `S3_TARGET_PATH_MOVIES_CARTAZ` | Caminho de saída (Parquet) dos filmes em cartaz |
| `S3_TARGET_PATH_MOVIES_POPULARES` | Caminho de saída (Parquet) dos filmes populares |
| `S3_TARGET_PATH_MOVIES_GENEROS` | Caminho de saída (Parquet) dos gêneros |
| `S3_INPUT_PATH_MOVIES` | Caminho S3 do csv de movies |
| `S3_INPUT_PATH_SERIES` | Caminho S3 do csv de series |
| `S3_TARGET_PATH_MOVIES` | Caminho de saída (Parquet) dos movies |
| `S3_TARGET_PATH_SERIES` | Caminho de saída (Parquet) das series |

---

## 🧹 **Resultado Final**

✅ Dados limpos e normalizados em **Parquet**

✅ Particionados por data (`ano_raw`, `mes_raw`, `dia_raw`)

✅ Catalogados no **Glue Data Catalog**

✅ Consultáveis via **Athena**

✅ Prontos para consumo na **camada REFINED**