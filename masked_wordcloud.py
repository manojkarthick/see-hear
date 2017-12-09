import matplotlib.pyplot as plt

from wordcloud import WordCloud, STOPWORDS
from pymongo import MongoClient

client = MongoClient()
db = client.SEEHEAR_DB

cursor = db.hot100.find()

for document in cursor:
    lyrics = document['Lyrics']
    if lyrics != "NA":
        wordcloud = WordCloud().generate(lyrics)

        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")

        wordcloud = WordCloud(background_color="white",width=500,
                                  height=500).generate(lyrics)
        plt.figure()
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        plt.savefig(document['ID']+".png",bbox_inches='tight')

