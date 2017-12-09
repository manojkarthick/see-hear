from pyspark import SparkConf, SparkContext
from nltk.corpus import stopwords
import sys
import operator
import re
import string
import unicodedata
from os import path
from wordcloud import WordCloud
from scipy.misc import imread
import matplotlib.pyplot as plt

conf = SparkConf().setAppName('word cloud')
sc = SparkContext(conf=conf)

assert sys.version_info >= (3, 5)  # make sure we have Python 3.5+
assert sc.version >= '2.2'  # make sure we have Spark 2.2+

def get_tweets(line):
	contents = line.split(',')
	return contents[0]

stopwords = stopwords.words('english')
twitter_words = ['https','co','com','twitter','rt', 'brokerages']

def words_normalized(line):
    wordsep = re.compile(r'[%s\s]+' % re.escape(string.punctuation))
    for w in wordsep.split(line):
        return unicodedata.normalize('NFD', w.lower())

def get_key(kv):
    return kv[0]

def get_value(kv):
    return kv[1]

def output_format(kv):
    k, v = kv
    return '%s %i' % (k, v)

from os import listdir
from os.path import isfile, join
mypath = 'hot100-tweets'
files = [f for f in listdir(mypath) if isfile(join(mypath, f))]
# files.remove('.DS_Store') # Mac specific

for file in files:
    print("Processing file: {}".format(file))
    inputs = 'hot100-tweets/{}'.format(file)

    text = sc.textFile(inputs)  # Read the contents of the text file
    lines = text.map(lambda line: line.replace('(','').replace(')','').lstrip("'").rstrip("'"))
    tweets = lines.map(get_tweets)
    wo_stopwords = tweets.map(words_normalized).filter(lambda word: word.startswith('@') == False)
    words = wo_stopwords.filter(lambda word: len(word) > 0)
    true_words = words.filter(lambda word: word not in twitter_words).filter(lambda word: word not in stopwords)
    # wordcount = true_words.reduceByKey(operator.add)
    # outdata1 = wordcount.sortBy(get_key).sortBy(get_value,ascending=False).take(10)
    if true_words.count() > 0: 
        concatenated_words = true_words.reduce(lambda x,y: x + " " + y)

        twitter_mask = imread('./twitter_mask.png', flatten=True)

        wordcloud = WordCloud(background_color='white',
                              width=500,
                              height=500,
                              mask=twitter_mask
                    ).generate(concatenated_words)
        plt.figure()
        plt.imshow(wordcloud)
        plt.axis("off")
        plt.savefig('hot100-wordclouds/{}.png'.format(file.replace('.txt','')), dpi=300)
        # plt.show()


