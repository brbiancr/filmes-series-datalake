import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import col, explode, split
from awsglue.dynamicframe import DynamicFrame

## @params: [JOB_NAME, S3_INPUT_PATH_MOVIES, S3_INPUT_PATH_SERIES, S3_INPUT_PATH_MOVIES_POPULARES, S3_INPUT_PATH_MOVIES_GENEROS, S3_INPUT_PATH_MOVIES_CARTAZ]
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'S3_INPUT_PATH_MOVIES', 'S3_INPUT_PATH_SERIES', 'S3_TARGET_PATH_MOVIES', 'S3_TARGET_PATH_SERIES'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

#PATHS
path_movies =args['S3_INPUT_PATH_MOVIES']
path_series = args['S3_INPUT_PATH_SERIES']
target_path_movies = args['S3_TARGET_PATH_MOVIES']
target_path_series = args['S3_TARGET_PATH_SERIES']

# ===========
# CSV movies
# ===========

df_movies = glueContext.create_dynamic_frame.from_options(
    connection_type="s3",
    connection_options={
        "paths": [path_movies]
    },
    format="csv",
    format_options={
        "withHeader": True,
        "separator": "|"
    }
)

df_movies_spark = df_movies.toDF()

df_movies_spark = (df_movies_spark
            .withColumn("anoLancamento", col("anoLancamento").cast("int"))
            .withColumn("tempoMinutos", col("tempoMinutos").cast("int"))
            .withColumn("anoNascimento", col("anoNascimento").cast("int"))
            .withColumn("anoFalecimento", col("anoFalecimento").cast("int"))
            .withColumnRenamed("tituloPincipal", "tituloPrincipal")
)

df_movies_spark = (df_movies_spark
            .withColumn("genero", explode(split(col("genero"), r",\s*")))
            .withColumn("generoArtista", explode(split(col("generoArtista"), r",\s*")))
            .withColumn("profissao", explode(split(col("profissao"), r",\s*")))
            .withColumn("titulosMaisConhecidos", explode(split(col("titulosMaisConhecidos"), r",\s*")))
)

df_movies_dynamic = DynamicFrame.fromDF(df_movies_spark, glueContext, "df_movies_dynamic")

# Salvar no S3 em formato parquet
glueContext.write_dynamic_frame.from_options(
    frame=df_movies_dynamic,
    connection_type="s3",
    connection_options={"path": target_path_movies},
    format="parquet"
)

# ===========
# CSV series
# ===========

df_series = glueContext.create_dynamic_frame.from_options(
    connection_type="s3",
    connection_options={
        "paths": [path_series]
    },
    format="csv",
    format_options={
        "withHeader": True,
        "separator": "|"
    }
)

df_series_spark = df_series.toDF()

df_series_spark = (df_series_spark
            .withColumn("anoLancamento", col("anoLancamento").cast("int"))
            .withColumn("anoTermino", col("anoTermino").cast("int"))
            .withColumn("tempoMinutos", col("tempoMinutos").cast("int"))
            .withColumn("anoNascimento", col("anoNascimento").cast("int"))
            .withColumn("anoFalecimento", col("anoFalecimento").cast("int"))
            .withColumnRenamed("tituloPincipal", "tituloPrincipal")
)

df_series_spark = (df_series_spark
    .withColumn("genero", explode(split(col("genero"), r",\s*")))
    .withColumn("profissao", explode(split(col("profissao"), r",\s*")))
    .withColumn("titulosMaisConhecidos", explode(split(col("titulosMaisConhecidos"), r",\s*")))
)

# Converter para DynamicFrame para salvar no Glue
df_series_dynamic = DynamicFrame.fromDF(df_series_spark, glueContext, "df_series_dynamic")

# Salvar no S3 em formato parquet
glueContext.write_dynamic_frame.from_options(
    frame=df_series_dynamic,
    connection_type="s3",
    connection_options={"path": target_path_series},
    format="parquet"
)

job.commit()