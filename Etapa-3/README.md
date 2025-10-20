# Etapa 3 - Camada REFINED

> A **camada Refined** representa o **nível analítico** do Data Lake — onde os dados já passaram por todas as etapas de limpeza, padronização e integração (camada Trusted) e agora são **modelados para análise**.
> 
> 
> Nesta camada, os dados estão **organizados segundo princípios de modelagem multidimensional** (fatos e dimensões), preparados para consumo direto por ferramentas de **Business Intelligence (BI)** como o **Amazon QuickSight**.
> 

## 🔹 **Objetivo**

- Transformar os dados padronizados da camada **Trusted** em estruturas analíticas otimizadas.
- Implementar um **modelo dimensional (Star Schema)**, com tabelas fato e dimensões.
- Facilitar consultas sobre diferentes perspectivas (por data, gênero, idioma, popularidade etc.).
- Armazenar os dados em formato **Parquet** e, quando necessário, particionar para performance.
- Registrar as novas tabelas e *views* no **AWS Glue Data Catalog** para consulta via **Athena** e integração com o **QuickSight**.

![image.png](../assets/image%203.png)

## 🧠 **Conceito de Modelagem**

Nesta etapa, aplicamos os **princípios de modelagem multidimensional**, organizando os dados em:

- **Tabelas Dimensão (Dim):**
    - Descrevem os atributos de contexto (ex: gênero, idioma, data, filme).
    - Contêm colunas descritivas, muitas vezes não numéricas.
- **Tabelas Fato (Fact):**
    - Contêm os eventos medidos ou métricas (ex: popularidade, votos, quantidade de filmes).
    - Referenciam dimensões por meio de *chaves estrangeiras*.

## 🧱 Modelagem Dimensional

**Dimensões:**

- `dim_tempo`: atributos temporais (ano, mês)
- `dim_filme`: informações descritivas dos filmes (título, gênero, popularidade)

**Tabela Fato:**

- `fato_filme_popular`: contém métricas como `numero_votos`, `media_votos` e `tempo_minutos`.

![image.png](image%201.png)

## ⚙️ Processamento

- Origem: camada `Trusted` (`movies_populares`, `movies_cartaz`, `movies_generos,` `movies`)
- Transformação: Apache Spark no AWS Glue
- Destino: camada `Refined`
- Formato: Parquet

## 🧭 Glue Catalog

- Criar novo **database**: `filmes_series_refined`
- Criar **crawlers**
- Consultar no Athena
- Disponibilizar para **QuickSight**