from kafka import SimpleProducer, KafkaClient
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import sys

kafka = KafkaClient('localhost:9092')
producer = SimpleProducer(kafka)

class Listener(StreamListener):
    def on_data(self, data):
        producer.send_messages(topic, data.encode('utf-8'))
        return True

    def on_error(self, status):
        print(status)

topic = 'twitterStream'
track_terms = sys.argv[1]
terms = track_terms.split(' ')

title = terms[0]
artist = terms[1]


print("Tracking {}".format(track_terms))

print('Start twitter to Kafka producer')
listener = Listener()
consumer_key = 'aMi2tyW2jE3zG2EUkf0GOg8uQ'
consumer_secret = 'uRpLY2In02z50zL18W736iDWkgRmo18quSSbpfecPxBVSHZ0pW'
access_token = '30427118-DEcNQWA4QUlKfTjAfR635Oa4qWoTWrd5jSERn37Sd'
access_token_secret = 'Q5ynHitpqZfY3QCZVcGAzv8qG1pIucrwMLs46ygBoC4FJ'
authentication = OAuthHandler(consumer_key, consumer_secret)
authentication.set_access_token(access_token, access_token_secret)
stream = Stream(authentication, listener)
while True:
    try:
        stream.filter(languages=["en"], track=[title, artist])
    except:
        pass

