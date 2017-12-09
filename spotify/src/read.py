from pyspark import SparkConf
from pyspark.sql import SparkSession

my_spark = SparkSession \
    .builder \
    .appName("myApp") \
    .config("spark.mongodb.input.uri", "mongodb://127.0.0.1/SEEHEAR.hot100") \
    .config("spark.mongodb.output.uri", "mongodb://127.0.0.1/SEEHEAR.hot100") \
    .getOrCreate()

df = my_spark.read.format("com.mongodb.spark.sql.DefaultSource").load()

print(df.printSchema())

df = df.drop('_id')
df.write.csv('Songs.csv')

