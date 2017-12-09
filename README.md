## SEE-HEAR

# Steps:

1. Get Spotify Credentials
2. Set up MongoDB on the machine
3. Run spotify source code to populate MongoDB with spotify data
4. Run Genius/update_lyrics.py to update the MongoDB collection with lyric data
5. Run Genius/masked_wordcloud.py to generate lyric word clouds
6. Set up Apache Zookeeper ( required for Kafka)
7. Write a kafka producer using twitter streaming with tweepy.
8. Write Kafka consumer using spark streaming API
9. Run zookeeper, Kafka
10. Run kafka producer and Run spark-kafka consumer, we can will see the data being consumed.
11. Set up Twitter Developer account ( for API Key, Secret)
12. Run last.fm/src/lastfm_api.py to get genre and album art
13. Run twitter/job.py to get tweets of the Hot 100 songs which uses producer-twitter-kafka.py and sentiment_analysis.py
14. Run wordclouds.py to generate wordclouds of tweets
15. Set up flask and install required libraries
16. Run flask-app/app.py to start the flask webserver and visit the web page to see the UI.