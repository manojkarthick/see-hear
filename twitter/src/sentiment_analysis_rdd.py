from pyspark import SparkContext  
from pyspark.streaming import StreamingContext  
from pyspark.streaming.kafka import KafkaUtils
import json
import sys
import os

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

sc = SparkContext(appName="PythonStreamingKafka")
ssc = StreamingContext(sc, 30)

ID = sys.argv[1]
title = sys.argv[2]
artist = sys.argv[3]

print("Starting for ID:{}".format(ID))

kvs = KafkaUtils.createStream(ssc, 'localhost:2181', "spark-streaming-consumer", {'twitterStream': 1})

analyzer = SentimentIntensityAnalyzer()

def extract_fields(line):
	if 'coordinates' in line:
		coordinates = line['coordinates']
	else:
		coordinates = None
	
	if 'place' in line:
		place = line['place']
	else:
		place = None

	if 'text' in line:
		text = line['text'].replace('\n','')
		pos = analyzer.polarity_scores(text)['pos']
		neg = analyzer.polarity_scores(text)['neg']
		neutral = analyzer.polarity_scores(text)['neu']
		comp = analyzer.polarity_scores(text)['compound']
		return (text, coordinates, place, pos, neg, neutral, comp)
	else:
		text = None
		return None

lines = kvs.map(lambda x: json.loads(x[1]))
fields = lines.map(extract_fields).filter(lambda x: x is not None).filter(lambda x: (title in x[0]) or (artist in x[0]))

# lines.pprint()
fields.saveAsTextFiles('datasets-3/{}/{}'.format(ID,ID))

ssc.start()
ssc.awaitTermination(180)