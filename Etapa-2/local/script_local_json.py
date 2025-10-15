import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, split, explode
from dotenv import load_dotenv

#PATHS
load_dotenv()
path_movies_cartaz = os.getenv("path_movies_cartaz")
path_generos = os.getenv("path_generos")
path_movies_populares = os.getenv("path_movies_populares")

spark = SparkSession \
    .builder \
    .master("local[*]") \
    .appName("job2_etl") \
    .getOrCreate()

#====================
# JSON movies_cartaz
#====================

df_movies_cartaz = spark.read.option("multiLine", True).json(path_movies_cartaz)

df_movies_cartaz = df_movies_cartaz.withColumn("results", explode("results")) \
                    .select("results.adult", "results.backdrop_path", "results.genre_ids", \
                    "results.id", "results.original_language", "results.original_title", \
                    "results.overview", "results.popularity", "results.poster_path", \
                    "results.release_date", "results.title", "results.video", \
                    "results.vote_average", "results.vote_count")

df_movies_cartaz = (df_movies_cartaz
    .withColumn("genre_ids", explode("genre_ids"))
    .drop("genre_ids)")
)

#==============
# JSON generos
#==============

df_generos = spark.read.option("multiLine", True).json(path_generos)

df_generos = (df_generos
            .select(explode("genres").alias("genres"))
            .select(col("genres.id").alias("id"), col("genres.name").alias("name"))
)

#=======================
# JSON movies_populares
#=======================

df_movies_populares = spark.read.option("multiLine", True).json(path_movies_populares)

df_movies_populares = df_movies_populares.withColumn("results", explode("results")) \
                    .select("results.adult", "results.backdrop_path", "results.genre_ids", \
                    "results.id", "results.original_language", "results.original_title", \
                    "results.overview", "results.popularity", "results.poster_path", \
                    "results.release_date", "results.title", "results.video", \
                    "results.vote_average", "results.vote_count")

df_movies_populares = (df_movies_populares
    .withColumn("genre_ids", explode("genre_ids"))
    .drop("genre_ids)")
)

df_movies_populares = (df_movies_populares
            .withColumn("release_date", col("release_date").cast("date"))
)
