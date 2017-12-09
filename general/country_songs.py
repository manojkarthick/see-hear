import json
import re
import requests
from bs4 import BeautifulSoup

with open('country-songs-list.txt', 'w') as f:
	for i in range(1, 51):
		url = "http://www.countryliving.com/life/g4292/classic-country-songs/?slide={}".format(i)
		r = requests.get(url)
		soup = BeautifulSoup(r.text)
		title_div = soup.findAll("div", { "class" : "gallery-slide--title" })[-1].find('h3').text
		title = re.findall(r'\"(.+?)\"', title_div)[0].rstrip(',')
		f.write(title)
		f.write('\n')