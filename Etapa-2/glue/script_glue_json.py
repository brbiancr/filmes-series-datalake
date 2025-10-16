import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql.functions import explode, col, input_file_name, regexp_extract
from pyspark.sql.types import StructType, StructField, ArrayType, IntegerType, StringType, DoubleType, BooleanType

# ======================
# PARÂMETROS
# ======================
args = getResolvedOptions(
    sys.argv,
    [
        'JOB_NAME',
        'S3_INPUT_PATH_MOVIES_CARTAZ',
        'S3_INPUT_PATH_MOVIES_POPULARES',
        'S3_INPUT_PATH_MOVIES_GENEROS',
        'S3_TARGET_PATH_MOVIES_CARTAZ',
        'S3_TARGET_PATH_MOVIES_POPULARES',
        'S3_TARGET_PATH_MOVIES_GENEROS'
    ]
)

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# ======================
# PATHS
# ======================
path_movies_populares = args['S3_INPUT_PATH_MOVIES_POPULARES']
path_movies_cartaz = args['S3_INPUT_PATH_MOVIES_CARTAZ']
path_movies_generos = args['S3_INPUT_PATH_MOVIES_GENEROS']
target_path_movies_populares = args['S3_TARGET_PATH_MOVIES_POPULARES']
target_path_movies_cartaz = args['S3_TARGET_PATH_MOVIES_CARTAZ']
target_path_movies_generos = args['S3_TARGET_PATH_MOVIES_GENEROS']

# ============================================================
# FUNÇÃO AUXILIAR → extrai ano/mês/dia e retorna novo DataFrame
# ============================================================
def extrair_data_raw(df):
    df = df.withColumn("source_file", input_file_name())
    df = (
        df.withColumn("ano_raw", regexp_extract(col("source_file"), r'RAW/TMDB/JSON/(\d{4})/', 1))
          .withColumn("mes_raw", regexp_extract(col("source_file"), r'RAW/TMDB/JSON/\d{4}/(\d{1,2})/', 1))
          .withColumn("dia_raw", regexp_extract(col("source_file"), r'RAW/TMDB/JSON/\d{4}/\d{1,2}/(\d{1,2})/', 1))
    )
    linha = df.select("ano_raw", "mes_raw", "dia_raw").first()
    return df, linha["ano_raw"], linha["mes_raw"], linha["dia_raw"]

# ======================
# JSON FILMES POPULARES
# ======================
schema_movies_populares = StructType([
    StructField("page", IntegerType(), True),
    StructField("results", ArrayType(
        StructType([
            StructField("adult", BooleanType(), True),
            StructField("backdrop_path", StringType(), True),
            StructField("genre_ids", ArrayType(IntegerType()), True),
            StructField("id", IntegerType(), True),
            StructField("original_language", StringType(), True),
            StructField("original_title", StringType(), True),
            StructField("overview", StringType(), True),
            StructField("popularity", DoubleType(), True),
            StructField("poster_path", StringType(), True),
            StructField("release_date", StringType(), True),
            StructField("title", StringType(), True),
            StructField("video", BooleanType(), True),
            StructField("vote_average", DoubleType(), True),
            StructField("vote_count", IntegerType(), True)
        ])
    ), True),
    StructField("total_pages", IntegerType(), True),
    StructField("total_results", IntegerType(), True)
])

df_movies_populares_spark = ( 
    spark.read .option("multiline", "true") 
    .schema(schema_movies_populares) 
    .json(f"{path_movies_populares}*.json") 
)

df_movies_populares_spark = (
    df_movies_populares_spark
        .withColumn("results", explode("results"))
        .select(
            "results.adult",
            "results.backdrop_path",
            "results.genre_ids",
            "results.id",
            "results.original_language",
            "results.original_title",
            "results.overview",
            "results.popularity",
            "results.poster_path",
            "results.release_date",
            "results.title",
            "results.video",
            "results.vote_average",
            "results.vote_count"
        )
        .withColumn("genre_id", explode(col("genre_ids")))
        .drop("genre_ids")
        .withColumn("release_date", col("release_date").cast("date"))
)

df_movies_populares_spark, ano_raw, mes_raw, dia_raw = extrair_data_raw(df_movies_populares_spark)

target_path_populares = f"{target_path_movies_populares}{ano_raw}/{mes_raw}/{dia_raw}/movies_populares"

df_movies_populares_dynamic = DynamicFrame.fromDF(df_movies_populares_spark, glueContext, "df_movies_populares_dynamic")

glueContext.write_dynamic_frame.from_options(
    frame=df_movies_populares_dynamic,
    connection_type="s3",
    connection_options={"path": target_path_populares},
    format="parquet"
)

print(f"✅ Filmes populares salvos em: {target_path_populares}")
print(f"📦 Total de registros: {df_movies_populares_spark.count()}")

# ======================
# JSON FILMES EM CARTAZ
# ======================
schema_movies_cartaz = StructType([
    StructField("page", IntegerType(), True),
    StructField("results", ArrayType(
        StructType([
            StructField("adult", BooleanType(), True),
            StructField("backdrop_path", StringType(), True),
            StructField("genre_ids", ArrayType(IntegerType()), True),
            StructField("id", IntegerType(), True),
            StructField("original_language", StringType(), True),
            StructField("original_title", StringType(), True),
            StructField("overview", StringType(), True),
            StructField("popularity", DoubleType(), True),
            StructField("poster_path", StringType(), True),
            StructField("release_date", StringType(), True),
            StructField("title", StringType(), True),
            StructField("video", BooleanType(), True),
            StructField("vote_average", DoubleType(), True),
            StructField("vote_count", IntegerType(), True)
        ])
    ), True)
])

df_movies_cartaz = (
    spark.read
        .option("multiline", "true")
        .schema(schema_movies_cartaz)
        .json(f"{path_movies_cartaz}*.json")
)

df_movies_cartaz = (
    df_movies_cartaz
        .withColumn("results", explode("results"))
        .select(
            "results.adult",
            "results.backdrop_path",
            "results.genre_ids",
            "results.id",
            "results.original_language",
            "results.original_title",
            "results.overview",
            "results.popularity",
            "results.poster_path",
            "results.release_date",
            "results.title",
            "results.video",
            "results.vote_average",
            "results.vote_count"
        )
        .withColumn("genre_id", explode(col("genre_ids")))
        .drop("genre_ids")
        .withColumn("release_date", col("release_date").cast("date"))
)

df_movies_cartaz, ano_raw, mes_raw, dia_raw = extrair_data_raw(df_movies_cartaz)

target_path_cartaz = f"{target_path_movies_cartaz}{ano_raw}/{mes_raw}/{dia_raw}/movies_cartaz"

df_movies_cartaz_dynamic = DynamicFrame.fromDF(df_movies_cartaz, glueContext, "df_movies_cartaz_dynamic")

glueContext.write_dynamic_frame.from_options(
    frame=df_movies_cartaz_dynamic,
    connection_type="s3",
    connection_options={"path": target_path_cartaz},
    format="parquet"
)

print(f"✅ Filmes em cartaz salvos em: {target_path_cartaz}")
print(f"📦 Total de registros: {df_movies_cartaz.count()}")

# ======================
# JSON LISTA DE GÊNEROS
# ======================
schema_movies_generos = StructType([
    StructField("genres", ArrayType(
        StructType([
            StructField("id", IntegerType(), True),
            StructField("name", StringType(), True)
        ])
    ), True)
])

df_movies_generos = (
    spark.read
        .option("multiline", "true")
        .schema(schema_movies_generos)
        .json(path_movies_generos)
)

df_movies_generos = (
    df_movies_generos
        .withColumn("genre", explode(col("genres")))
        .select(
            col("genre.id").alias("genre_id"),
            col("genre.name").alias("genre_name")
        )
)

df_movies_generos, ano_raw, mes_raw, dia_raw = extrair_data_raw(df_movies_generos)

target_path_generos = f"{target_path_movies_generos}{ano_raw}/{mes_raw}/{dia_raw}/movies_generos"

df_movies_generos_dynamic = DynamicFrame.fromDF(df_movies_generos, glueContext, "df_movies_generos_dynamic")

glueContext.write_dynamic_frame.from_options(
    frame=df_movies_generos_dynamic,
    connection_type="s3",
    connection_options={"path": target_path_generos},
    format="parquet"
)

print(f"✅ Gêneros salvos em: {target_path_generos}")
print(f"📦 Total de registros: {df_movies_generos.count()}")

job.commit()
