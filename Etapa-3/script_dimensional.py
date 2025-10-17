import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import year, col, month
from pyspark.sql.functions import max as spark_max
from awsglue.dynamicframe import DynamicFrame

## @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'S3_INPUT_PATH_MOVIES', 'S3_INPUT_PATH_MOVIES_POPULARES', 'S3_INPUT_PATH_MOVIES_GENEROS', 'S3_TARGET_PATH_DATA', 'S3_TARGET_PATH_AVALIACAO', 'S3_TARGET_PATH_FILME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

path_movies = args['S3_INPUT_PATH_MOVIES']
path_movies_populares = args['S3_INPUT_PATH_MOVIES_POPULARES']
path_movies_generos = args['S3_INPUT_PATH_MOVIES_GENEROS']
target_path_data = args['S3_TARGET_PATH_DATA']
target_path_avaliacao = args['S3_TARGET_PATH_AVALIACAO']
target_path_filme = args['S3_TARGET_PATH_FILME']

#=================
# Lendo os Parquet
#=================
dyf_movies = glueContext.create_dynamic_frame.from_options(
    connection_type="s3",
    format="parquet",
    connection_options={"path": path_movies}
)
df_movies = dyf_movies.toDF()

dyf_movies_populares = glueContext.create_dynamic_frame.from_options(
    connection_type="s3",
    format="parquet",
    connection_options={"path": path_movies_populares}
)
df_movies_populares = dyf_movies_populares.toDF()

dyf_movies_generos = glueContext.create_dynamic_frame.from_options(
    connection_type="s3",
    format="parquet",
    connection_options={"path": path_movies_generos}
)
df_movies_generos = dyf_movies_generos.toDF()

#================
# Dimensão tempo 
#================
dim_tempo = df_movies_populares.select(
    col("id").alias("id_data"),
    year(col("release_date")).alias("ano_lancamento"),
    month(col("release_date")).alias("mes_lancamento"),
).distinct()

dim_tempo.show(5)

#================
# Dimensão filme
#================
dim_filme = df_movies_populares.join(
    df_movies_generos.select("genre_id", "genre_name"),
    df_movies_populares["genre_id"] == df_movies_generos["genre_id"],
    "left"
).select(
    col("title").alias("titulo_filme"),
    col("genre_name").alias("genero"),
    col("popularity").alias("popularidade"),
    col("id").alias("id_filme")
).distinct()

dim_filme.show(5)

#====================
# Fato filme popular
#====================

fato_filme_popular = df_movies_populares.join(
    df_movies.select("tituloPrincipal", "tempoMinutos"),
    df_movies_populares["title"] == df_movies["tituloPrincipal"],
    "left"
).select(
    col("id").alias("id_filme"),
    col("id").alias("id_data"),
    col("vote_average").alias("media_votos"),
    col("vote_count").alias("contagem_votos"),
    col("tempoMinutos").alias("duracao_minutos")
).filter(
    col("duracao_minutos").isNotNull()
).groupBy(
    "id_data", "id_filme", "media_votos", "contagem_votos", "duracao_minutos"
).agg(
    spark_max("duracao_minutos").alias("duracao_minutos")
).distinct()

fato_filme_popular.show(5)

#====================
# Salvando as tabelas
#====================
# Dimensão Data
dyf_dim_tempo = DynamicFrame.fromDF(dim_tempo, glueContext, "dyf_dim_tempo")
glueContext.write_dynamic_frame.from_options(
    frame=dyf_dim_tempo,
    connection_type="s3",
    connection_options={"path": target_path_data},
    format="parquet"
)

# Dimensão Avaliação
dyf_dim_filme = DynamicFrame.fromDF(dim_filme, glueContext, "dyf_dim_filme")
glueContext.write_dynamic_frame.from_options(
    frame=dyf_dim_filme,
    connection_type="s3",
    connection_options={"path": target_path_avaliacao},
    format="parquet"
)

# Fato Filme Popular
dyf_fato_filme_popular = DynamicFrame.fromDF(fato_filme_popular, glueContext, "dyf_fato_filme_popular")
glueContext.write_dynamic_frame.from_options(
    frame=dyf_fato_filme_popular,
    connection_type="s3",
    connection_options={"path": target_path_filme},
    format="parquet"
)

job.commit()