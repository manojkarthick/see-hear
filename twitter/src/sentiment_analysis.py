from pyspark.sql import SparkSession
from pyspark.sql import types
from pyspark.sql.functions import from_json, udf
from pyspark.streaming import StreamingContext

import os
import time
import sys

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

ID = sys.argv[1]
print("Saving to: {}".format(ID))

spark = SparkSession.builder.appName('Spark Kafka Consumer').getOrCreate()
sc = spark.sparkContext
ssc = StreamingContext(sc, 5)

topic = 'twitterStream'

messages = spark.readStream.format('kafka') \
        .option('kafka.bootstrap.servers', 'localhost:9092') \
        .option('zookeeper.connect', 'localhost:2181') \
        .option('subscribe', topic).load()

schema = types.StructType([ 
 types.StructField("created_at", types.StringType()), 
 types.StructField("id", types.StringType()), 
 types.StructField("id_str", types.StringType()), 
 types.StructField("text", types.StringType()),
 types.StructField("source", types.StringType()),
 types.StructField("coordinates", types.StringType()),
 types.StructField("place", types.StringType()),
 types.StructField("retweet_count", types.StringType()), 
 types.StructField("favorite_count", types.StringType()), 
 types.StructField("favorited", types.StringType()), 
 types.StructField("retweeted", types.StringType()), 
 types.StructField("lang", types.StringType()), 
 types.StructField("possibly_sensitive", types.StringType()),
])

json_df = messages.selectExpr("CAST(value as STRING) as json_string") \
			.select(from_json("json_string", schema=schema).alias('tweet')) \
			.selectExpr("tweet.text",
						"CAST(tweet.id as long)",
						"tweet.lang")

def calculate_score(text):
	analyzer = SentimentIntensityAnalyzer()
	if text == None:
		return None
	else:
		return str(analyzer.polarity_scores(text)['compound'])

udf_analyzer = udf(calculate_score, types.StringType())

json_df = json_df.withColumn('score', udf_analyzer(json_df['text']))

#.option('path',path) .option("checkpointLocation",'/tmp')

path = ID
stream = json_df.writeStream.format('console') \
        .outputMode('append').start()
stream.awaitTermination(600)