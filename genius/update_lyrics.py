from pyspark.sql import SparkSession, types
from bs4 import BeautifulSoup
import requests


#cachedStopWords = stopwords.words("english")

base_url = "http://api.genius.com"
headers = {'Authorization': 'Bearer LKil58D1p5rCPpT3IyPniPs_0hYTYmVS0nxk3dRJRs8xk-WWQD2sq1UsnM1tjTH5'}
punctuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
lyrics = ""


spark = SparkSession \
    .builder \
    .appName("myApp") \
    .config("spark.mongodb.input.uri", "mongodb://localhost/SEEHEAR_DB") \
    .config("spark.mongodb.output.uri", "mongodb://localhost/SEEHEAR") \
    .getOrCreate()

hot100_df = spark.read.format("com.mongodb.spark.sql.DefaultSource").option("uri",
"mongodb://localhost/SEEHEAR_DB.hot100").load()
pop_df = spark.read.format("com.mongodb.spark.sql.DefaultSource").option("uri",
"mongodb://localhost/SEEHEAR_DB.Pop").load()
country_df = spark.read.format("com.mongodb.spark.sql.DefaultSource").option("uri",
"mongodb://localhost/SEEHEAR_DB.Country").load()
rock_df = spark.read.format("com.mongodb.spark.sql.DefaultSource").option("uri",
"mongodb://localhost/SEEHEAR_DB.Rock").load()


def lyrics_from_song_api_path(song_api_path):
  song_url = base_url + song_api_path
  response = requests.get(song_url, headers=headers)
  json = response.json()
  path = json["response"]["song"]["path"]
  page_url = "http://genius.com" + path
  page = requests.get(page_url)
  html = BeautifulSoup(page.text, "html.parser")
  [h.extract() for h in html('script')]
  lyrics = html.find("div", class_="lyrics").get_text()
  return lyrics

def get_song_lyrics(song_title,artist_name):
  search_url = base_url + "/search"
  data = {'q': song_title}
  response = requests.get(search_url, params=data, headers=headers)
  json = response.json()
  song_info = None
  for hit in json["response"]["hits"]:
    if artist_name in hit["result"]["primary_artist"]["name"]:
      song_info = hit
      break
  if song_info:
    song_api_path = song_info["result"]["api_path"]
    lyrics =lyrics_from_song_api_path(song_api_path)
  else:
    lyrics = "NA"
  return lyrics


def append_lyrics(row):
    lyrics = get_song_lyrics(row.Title, row.Artist)
    return (row.ID, lyrics)



schema = types.StructType([types.StructField('ID', types.StringType(), False),
                           types.StructField('Lyrics', types.StringType(), False)])
# The below process has to be performed for pop_df,rock_df, and country_df as it is done for hot_df
# inorder to load the data
hot_100 = hot100_df.rdd.map(append_lyrics)
hot100_lyrics = spark.createDataFrame(hot_100,schema)
hot100_df.createOrReplaceTempView('hot100')
hot100_lyrics.createOrReplaceTempView('hot100_lyrics')

hot_final = spark.sql("""
          SELECT *
          FROM hot100 INNER JOIN hot100_lyrics ON hot100.ID = hot100_lyrics.ID """)

hot_final.write.format("com.mongodb.spark.sql.DefaultSource").mode("append")\
    .option("database","SEEHEAR").option("collection", "hot100").save()

rock = rock_df.rdd.map(append_lyrics)
rock_lyrics = spark.createDataFrame(rock,schema)
rock_df.createOrReplaceTempView('rock')
rock_lyrics.createOrReplaceTempView('rock_lyrics')

rock_final = spark.sql("""
          SELECT *
          FROM rock INNER JOIN rock_lyrics ON rock.ID = rock_lyrics.ID """)

rock_final.write.format("com.mongodb.spark.sql.DefaultSource").mode("append")\
    .option("database","SEEHEAR").option("collection", "Rock").save()

pop = pop_df.rdd.map(append_lyrics)
pop_lyrics = spark.createDataFrame(pop,schema)
pop_df.createOrReplaceTempView('pop')
pop_lyrics.createOrReplaceTempView('pop_lyrics')

pop_final = spark.sql("""
          SELECT *
          FROM pop INNER JOIN pop_lyrics ON pop.ID = pop_lyrics.ID """)

pop_final.write.format("com.mongodb.spark.sql.DefaultSource").mode("append")\
    .option("database","SEEHEAR").option("collection", "Pop").save()

country = country_df.rdd.map(append_lyrics)
country_lyrics = spark.createDataFrame(country,schema)
country_df.createOrReplaceTempView('country')
country_lyrics.createOrReplaceTempView('country_lyrics')

country_final = spark.sql("""
          SELECT *
          FROM country INNER JOIN country_lyrics ON country.ID = country_lyrics.ID """)

country_final.write.format("com.mongodb.spark.sql.DefaultSource").mode("append")\
    .option("database","SEEHEAR").option("collection", "Country").save()