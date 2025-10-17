import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, split, explode
from dotenv import load_dotenv

#PATHS
load_dotenv()
path_movies = os.getenv("path_movies")
path_series = os.getenv("path_series")
teste = os.getenv("teste")

spark = SparkSession \
    .builder \
    .master("local[*]") \
    .appName("job2_etl") \
    .getOrCreate()

# ===========
# CSV movies
# ===========

df_movies = spark.read.csv(path_movies, header=True, inferSchema=True, sep="|")

df_movies = (df_movies
            .withColumn("anoLancamento", col("anoLancamento").cast("int"))
            .withColumn("tempoMinutos", col("tempoMinutos").cast("int"))
            .withColumn("anoNascimento", col("anoNascimento").cast("int"))
            .withColumn("anoFalecimento", col("anoFalecimento").cast("int"))
            .withColumnRenamed("tituloPincipal", "tituloPrincipal")
)

df_movies = (df_movies
            .withColumn("genero", explode(split(col("genero"), r",\s*")))
            .withColumn("generoArtista", explode(split(col("generoArtista"), r",\s*")))
            .withColumn("profissao", explode(split(col("profissao"), r",\s*")))
            .withColumn("titulosMaisConhecidos", explode(split(col("titulosMaisConhecidos"), r",\s*")))
)

# ===========
# CSV series
# ===========

df_series = spark.read.csv(path_series, header=True, inferSchema=True, sep="|")

df_series = (df_series
            .withColumn("anoLancamento", col("anoLancamento").cast("int"))
            .withColumn("anoTermino", col("anoTermino").cast("int"))
            .withColumn("tempoMinutos", col("tempoMinutos").cast("int"))
            .withColumn("anoNascimento", col("anoNascimento").cast("int"))
            .withColumn("anoFalecimento", col("anoFalecimento").cast("int"))
            .withColumnRenamed("tituloPincipal", "tituloPrincipal")
)

df_series = (df_series
    .withColumn("genero", explode(split(col("genero"), r",\s*")))
    .withColumn("profissao", explode(split(col("profissao"), r",\s*")))
    .withColumn("titulosMaisConhecidos", explode(split(col("titulosMaisConhecidos"), r",\s*")))
)