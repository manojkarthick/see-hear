import os
import pandas as pd
import subprocess
import time

# Initially start Zookeeper and Kafka
# Delete topic and create new topic
delete_topic = "/Users/manojkarthick/Code/CMPT-732/Spark/Utils/kafka_2.12-0.11.0.0/bin/kafka-topics.sh \
				--zookeeper localhost:2181 --delete --topic twitterStream"
recreate_topic = "/Users/manojkarthick/Code/CMPT-732/Spark/Utils/kafka_2.12-0.11.0.0/bin/kafka-topics.sh --create --zookeeper localhost:2181 \
    --replication-factor 1 --partitions 1 --topic twitterStream"

streamer = "python3 producer-twitter-kafka.py"

data = pd.read_csv("spotify-data-100.csv")
for index,row in data.iterrows():
	ID = row["ID"].rstrip("\n")
	title = row["Title"].rstrip("\n")
	artist = row["Artist"]
	print("Working on ID:{} and title:{}".format(ID, title))

	spark_job = "/Users/manojkarthick/Code/CMPT-732/Spark/spark-2.2.0-bin-hadoop2.7/bin/spark-submit \
	--packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.2.0 \
	sentiment_analysis_rdd.py {} {} {} 2>/dev/null".format(ID, title, artist)

	# Delete and create topic
	os.system(command=delete_topic)
	print("Deleted topic")

	os.system(command=recreate_topic)
	print("Recreated topic")

	# Start the streaming
	track_term = "{} {}".format(title, artist)
	print("Starting Kafka streamer")
	sp = subprocess.Popen(['python3', 'producer-twitter-kafka.py', track_term])
	print('PID is ' + str(sp.pid))

	print("Started Spark Job")
	status_code = os.system(command=spark_job)
	# time.sleep(160)
	sp.terminate()
	print("Terminated job")







