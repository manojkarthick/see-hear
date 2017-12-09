from flask import Flask, render_template, request
import pandas as pd

import plotly
from plotly.graph_objs import Scatter, Layout, Bar
from flask import abort
from pymongo import MongoClient
from collections import defaultdict

app = Flask(__name__)

client = MongoClient('192.168.0.7', 27017)
db = client.SEEHEAR

@app.route("/")
def home_page():
	return render_template("see-hear.html")

@app.route("/hot100/overview")
def overview():
	hot100_songs = db.hot100.find()
	return render_template("hot100-overview.html", hot100_songs=hot100_songs)

@app.route("/classic/overview/")
def classic_overview():
	collection = request.args.get('genre')
	if collection == 'Pop':
		songs = db.Pop.find()
	elif collection == 'Country':
		songs = db.Country.find()
	elif collection == 'Rock':
		songs = db.Rock.find()
	else:
		abort(404)
	return render_template("classic-overview.html", songs=songs, genre=collection)

@app.route('/hot100/stats/')
def hot100_stats():
	dance_top_songs = db.hot100.aggregate([{'$sort':{'Danceability':-1}},{'$limit':10}])
	energy_top_songs = db.hot100.aggregate([{'$sort':{'Energy':-1}},{'$limit':10}])
	inst_top_songs = db.hot100.aggregate([{'$sort':{'Instrumentalness':-1}},{'$limit':10}])
	accou_top_songs = db.hot100.aggregate([{'$sort':{'Acousticness':-1}},{'$limit':10}])

	dance_x = list()
	dance_y = list()
	for song in dance_top_songs:
		dance_y.append(song['Title'])
		dance_x.append(song['Danceability'])

	energy_x = list()
	energy_y = list()
	for song in energy_top_songs:
		energy_y.append(song['Title'])
		energy_x.append(song['Energy'])

	inst_x = list()
	inst_y = list()
	for song in inst_top_songs:
		inst_y.append(song['Title'])
		inst_x.append(song['Instrumentalness'])

	accou_x = list()
	accou_y = list()
	for song in accou_top_songs:
		accou_y.append(song['Title'])
		accou_x.append(song['Acousticness'])

	dance_div = plotly.offline.plot({
    "data": [Bar(x=dance_y, y=dance_x)], 
    'layout': Layout(title='<b>Most Danceable Songs</b>')
	}, output_type="div", include_plotlyjs=False,link_text="",show_link="False")

	energy_div = plotly.offline.plot({
    "data": [Bar(x=energy_y, y=energy_x)], 'layout': Layout(title='<b>Highly Energetic Songs</b>')
	}, output_type="div", include_plotlyjs=False,link_text="",show_link="False")

	inst_div = plotly.offline.plot({
    "data": [Bar(x=inst_y, y=inst_x)], 'layout': Layout(title='<b>Songs with High Instrumentality</b>')
	}, output_type="div", include_plotlyjs=False,link_text="",show_link="False")

	accou_div = plotly.offline.plot({
    "data": [Bar(x=accou_y, y=accou_x)], 'layout': Layout(title='<b>Top Acoustic Songs</b>')
	}, output_type="div", include_plotlyjs=False,link_text="",show_link="False")

	genre_list = list()
	genre_values = list()
	genre_count = 1
	count_sum = 0
	top_genres = db.hot100.aggregate([{'$group' :{'_id':{'Genre':"$Genre"}, 'count':{'$sum':1}}},{'$sort':{'count':-1}}])
	
	genre_dict = dict()


	for genre_obj in top_genres:
		if genre_count > 8:
			break
		genre_name = ''
		if genre_obj['_id']['Genre'] == '':
			genre_name = 'unspecified'
		else:
			genre_name = genre_obj['_id']['Genre']
		genre_list.append(genre_name)
		genre_values.append(genre_obj['count'])
		count_sum += genre_obj['count']
		genre_count += 1
	genre_list.append('others')
	genre_values.append(100 - count_sum)

	genre_pie_props ={
  	"data": [{
      		"values": genre_values,
      		"labels": genre_list,
      		"domain": {"x": [0, .85]},
      		"hoverinfo":"label+percent+name",
      		"hole": .4,
      		"type": "pie"
    		}],
  	"layout":{
        	"title":"<b>Genres in Hot 100</b>",
        	"annotations":[
            {
                "font":{
                    "size": 14
                	},
                "showarrow": False,
                "text": "Genre",
                "x": 0.42,
                "y": 0.50
            }
    		]}}
	genre_div = plotly.offline.plot(genre_pie_props, output_type="div", include_plotlyjs=False,link_text="",show_link="False")

	tone_count_dict = defaultdict(lambda: 0)
	hot_100_songs = db.hot100.find()
	for song in hot_100_songs:
		if 'Tone' in song:
			document_tones = song['Tone']['document_tone']['tones']
			max_tone = -1
			max_tone_name = 'Mix'
			for tone in document_tones:
				if tone['score'] > max_tone:
					max_tone = tone['score']
					max_tone_name = tone['tone_name']
			tone_count_dict[max_tone_name] += 1
		else:
			tone_count_dict['Unspecified'] += 1

	tone_names_list = list()
	tones_count_list = list()

	for tone_name in tone_count_dict.keys():
		tone_names_list.append(tone_name)
		tones_count_list.append(tone_count_dict[tone_name])

	tone_pie_props ={
  	"data": [{
      		"values": tones_count_list,
      		"labels": tone_names_list,
      		"domain": {"x": [0, .85]},
      		"hoverinfo":"label+percent+name",
      		"hole": .4,
      		"type": "pie"
    		}],
  	"layout":{
        	"title":"<b>Tones in Hot 100</b>",
        	"annotations":[
            {
                "font":{
                    "size": 14
                	},
                "showarrow": False,
                "text": "Tone",
                "x": 0.42,
                "y": 0.50
            }
    		]}}
	tone_div = plotly.offline.plot(tone_pie_props, output_type="div", include_plotlyjs=False,link_text="",show_link="False")

	df = pd.read_csv('static/chloropleth-usa-data.csv', sep=';')
	for col in df.columns:
		df[col] = df[col].astype(str)

	data = [ dict(
    	   	type='choropleth',
        	autocolorscale = True,
        	locations = df['Code'],
        	z = df['Count'].astype(float),
        	text = df['Artists'],
        	locationmode = 'USA-states',
        	marker = dict(
            	line = dict (
                	color = 'rgb(255,255,255)',
                	width = 2
            	) ),
        	colorbar = dict(
            	title = "Number of artists")
        	) ]

	layout = dict(
    	    title = '<b>Number of artists by States in Hot 100<b>',
        	geo = dict(
            	scope='usa',
            	projection=dict( type='albers usa' ),
            	showlakes = True,
            	lakecolor = 'rgb(255, 255, 255)'),
             	)

	fig = dict( data=data, layout=layout )
	map_div = plotly.offline.plot(fig, output_type="div", include_plotlyjs=False,link_text="",show_link="False")

	for g_obj in db.hot100.aggregate([{'$group' :{'_id':{'Genre':"$Genre"}, 'count':{'$sum':1}}},{'$sort':{'count':-1}}]):
		genre_name = ''
		if g_obj['_id']['Genre'] == '':
			genre_name = 'unspecified'
		else:
			genre_name = g_obj['_id']['Genre']
		print(g_obj)
		genre_dict[genre_name] = g_obj['count']

	boring_genres_names = list()
	boring_genres_count = list()
	boring_genres_values = list()
	# boring_genres = db.hot100.aggregate([{'$group' :{'_id':{'Genre':"$Genre"}, 'mean':{'$avg':'$boring'}}}])

	reqd_genres = ['pop','hip hop','country','rap','american']

	for rgenre in reqd_genres:
		for boring_genre in db.hot100.aggregate([{'$group' :{'_id':{'Genre':"$Genre"}, 'mean':{'$avg':'$boring'}}}]):
			if boring_genre['_id']['Genre'] == rgenre:
				boring_genres_names.append(boring_genre['_id']['Genre'])
				boring_genres_values.append(boring_genre['mean']/10)
				boring_genres_count.append(genre_dict[boring_genre['_id']['Genre']])

	print(boring_genres_names, boring_genres_count, boring_genres_values)

	trace1 = Scatter(
    x=boring_genres_names,
    y=boring_genres_count,
    name='No. of songs in genre'
	)
	trace2 = Bar(
    x=boring_genres_names,
    y=boring_genres_values,
    name='Boringness quotient'
	)	

	mix_layout = Layout(title='<b>Boringness Quotient by Genre</b>')

	mix_data = [trace1, trace2]
	mig_fig = {'data': mix_data, 'layout':mix_layout}
	mix_div = plotly.offline.plot(mig_fig, output_type="div", include_plotlyjs=False,link_text="",show_link="False")

	return render_template("hot100-stats.html", dance_div=dance_div, energy_div=energy_div, accou_div=accou_div,
		inst_div=inst_div, genre_div=genre_div, tone_div=tone_div, map_div=map_div, mix_div=mix_div)

@app.route('/classic/stats/')
def classic_stats():
	return render_template("classic-stats.html")

@app.route('/classic/song/')
def classic_song():
	song_id = request.args.get('song_id')
	collection = request.args.get('genre')

	if collection == 'Pop':
		song_document = db.Pop.find_one({'ID': song_id})
	elif collection == 'Country':
		song_document = db.Country.find_one({'ID': song_id})
	else:
		song_document = db.Rock.find_one({'ID': song_id})

	table_lines = list()

	tone = song_document['Tone']
	doc_tones = tone['document_tone']['tones']
	if len(doc_tones) == 0:
		doc_tones = ''
		tone_div = None
	else:
		tone_dict = dict()
		for t in doc_tones:
			if t['tone_name'] == 'Anger':
				Anger = t['score']
				tone_dict['Anger'] = Anger
			elif t['tone_name'] == 'Fear':
				Fear = t['score']
				tone_dict['Fear'] = Fear
			elif t['tone_name'] == 'Joy':
				Joy = t['score']
				tone_dict['Joy'] = Joy
			elif t['tone_name'] == 'Sadness':
				Sadness = t['score']
				tone_dict['Sadness'] = Sadness
			elif t['tone_name'] == 'Analytical':
				Analytical = t['score']
				tone_dict['Analytical'] = Analytical
			elif t['tone_name'] == 'Confident':
				Confident = t['score']
				tone_dict['Confident'] = Confident
			elif t['tone_name'] == 'Tentative':
				Tentative = t['score']
				tone_dict['Tentative'] = Tentative
			else:
				pass
		
		tone_names = tone_dict.keys()
		tone_values = tone_dict.values()

		size = list()
		color = list()
		for value in list(tone_values):
			size.append(value*100)
		
		for name in list(tone_names):
			if name == 'Anger':
				color.append('rgb(255,0,0)')
			elif name == 'Fear':
				color.append('rgb(165,42,42)')
			elif name == 'Joy':
				color.append('rgb(0,128,0)')
			elif name == 'Sadness':
				color.append('rgb(255,165,0)')
			elif name == 'Analytical':
				color.append('rgb(0,0,255)')
			elif name == 'Confident':
				color.append('rgb(128,0,128)')
			else:
				color.append('rgb(70,130,180)')

		tone_div = plotly.offline.plot({"data": [Scatter(
			x=list(tone_names),
			y=list(tone_values),
			mode='markers',
			marker=dict(color=color, size=size)
		)], 'layout': Layout(title='<b>Prominent tones in the lyrics</b>')}, output_type="div", include_plotlyjs=False,link_text="",show_link="False")

	if 'sentences_tone' in tone:
		sentences_tones = tone['sentences_tone']
		if len(sentences_tones) == 0:
			sentences_tones = ''
		else:
			for sentence_tone in sentences_tones:
				Anger = ''
				Fear = ''
				Joy = ''
				Sadness = ''
				Analytical = ''
				Confident = ''
				Tentative = ''
				text = sentence_tone['text']
				if text != '':
					all_tones = sentence_tone['tones']
					if len(all_tones) > 0:
						for t in all_tones:
							if t['tone_name'] == 'Anger':
								Anger = t['score']
							elif t['tone_name'] == 'Fear':
								Fear = t['score']
							elif t['tone_name'] == 'Joy':
								Joy = t['score']
							elif t['tone_name'] == 'Sadness':
								Sadness = t['score']
							elif t['tone_name'] == 'Analytical':
								Analytical = t['score']
							elif t['tone_name'] == 'Confident':
								Confident = t['score']
							elif t['tone_name'] == 'Tentative':
								Tentative = t['score']
							else:
								pass
					table_lines.append((text, Anger, Fear, Joy, Sadness, Analytical, Confident, Tentative))
	else:
		sentences_tones = None

	normalized_dict = { 
		'Acousticness': song_document['Acousticness'], 
		'Instrumentalness': song_document['Instrumentalness'],
		'Mode': song_document['Mode'],
		'Valence': song_document['Valence'],
		'Danceability': song_document['Danceability'],
		'Energy': song_document['Energy'],
		'Liveness': song_document['Liveness'],
		'Speechiness': song_document['Speechiness']
		}

	other_dict = {
		'Key': song_document['Key'],
		'Loudness': -1*song_document['Loudness'],
		'Tempo': song_document['Tempo']
	}

	hist1_x = list(normalized_dict.keys())
	hist1_y = list(normalized_dict.values())

	norm_div = plotly.offline.plot({
    "data": [Bar(x=hist1_y, y=hist1_x, orientation='h')],
	}, output_type="div", include_plotlyjs=False,link_text="",show_link="False")

	hist2_x = list(other_dict.keys())
	hist2_y = list(other_dict.values())

	other_div = plotly.offline.plot({
    "data": [Bar(x=hist2_x, y=hist2_y)],
	}, output_type="div", include_plotlyjs=False,link_text="",show_link="False")

	return render_template("classic-song.html", song_document=song_document, norm_div=norm_div, other_div=other_div,
		doc_tones=doc_tones, sentences_tones=sentences_tones, table_lines=table_lines, tone_div=tone_div)

@app.route('/hot100/song/')
def hot100_song():
	song_id = request.args.get('song_id')
	song_document = db.hot100.find_one({'ID': song_id})

	positive = db.Tweets.aggregate([{"$match":{'ID':song_id}},{"$group": {'_id': 'null',"mean_positive":{'$avg': "$Positive" }}}]).next()['mean_positive']
	negative = db.Tweets.aggregate([{"$match":{'ID':song_id}},{"$group": {'_id': 'null',"mean_negative":{'$avg': "$Negative" }}}]).next()['mean_negative']
	neutral = db.Tweets.aggregate([{"$match":{'ID':song_id}},{"$group": {'_id': 'null',"mean_neutral":{'$avg': "$Neutral" }}}]).next()['mean_neutral']
	compound = db.Tweets.aggregate([{"$match":{'ID':song_id}},{"$group": {'_id': 'null',"mean_compound":{'$avg': "$Compound" }}}]).next()['mean_compound']

	tweet_sentiment_div = plotly.offline.plot({"data": [Scatter(
			x=list(['Positive', 'Negative', 'Neutral', 'Compound']),
			y=list([positive, negative, neutral, compound]),
			mode='markers',
			marker=dict(color=list(['rgb(0,128,0)', 'rgb(255,0,0)', 'rgb(255,165,0)', 'rgb(70,130,180)']), size=list([positive*100, negative*100, neutral*100, compound*100]))
		)], 'layout': Layout(title='<b>Twitter Sentiment</b>')}, output_type="div", include_plotlyjs=False,link_text="",show_link="False")

	table_lines = list()

	tone = song_document['Tone']
	doc_tones = tone['document_tone']['tones']
	if len(doc_tones) == 0:
		doc_tones = ''
		tone_div = None
	else:
		tone_dict = dict()
		for t in doc_tones:
			if t['tone_name'] == 'Anger':
				Anger = t['score']
				tone_dict['Anger'] = Anger
			elif t['tone_name'] == 'Fear':
				Fear = t['score']
				tone_dict['Fear'] = Fear
			elif t['tone_name'] == 'Joy':
				Joy = t['score']
				tone_dict['Joy'] = Joy
			elif t['tone_name'] == 'Sadness':
				Sadness = t['score']
				tone_dict['Sadness'] = Sadness
			elif t['tone_name'] == 'Analytical':
				Analytical = t['score']
				tone_dict['Analytical'] = Analytical
			elif t['tone_name'] == 'Confident':
				Confident = t['score']
				tone_dict['Confident'] = Confident
			elif t['tone_name'] == 'Tentative':
				Tentative = t['score']
				tone_dict['Tentative'] = Tentative
			else:
				pass
		
		tone_names = tone_dict.keys()
		tone_values = tone_dict.values()

		size = list()
		color = list()
		for value in list(tone_values):
			size.append(value*100)
		
		for name in list(tone_names):
			if name == 'Anger':
				color.append('rgb(255,0,0)')
			elif name == 'Fear':
				color.append('rgb(165,42,42)')
			elif name == 'Joy':
				color.append('rgb(0,128,0)')
			elif name == 'Sadness':
				color.append('rgb(255,165,0)')
			elif name == 'Analytical':
				color.append('rgb(0,0,255)')
			elif name == 'Confident':
				color.append('rgb(128,0,128)')
			else:
				color.append('rgb(70,130,180)')

		tone_div = plotly.offline.plot({"data": [Scatter(
			x=list(tone_names),
			y=list(tone_values),
			mode='markers',
			marker=dict(color=color, size=size)
		)], 'layout': Layout(title='<b>Prominent tones in the lyrics</b>')}, output_type="div", include_plotlyjs=False,link_text="",show_link="False")

	if 'sentences_tone' in tone:
		sentences_tones = tone['sentences_tone']
		if len(sentences_tones) == 0:
			sentences_tones = ''
		else:
			for sentence_tone in sentences_tones:
				Anger = ''
				Fear = ''
				Joy = ''
				Sadness = ''
				Analytical = ''
				Confident = ''
				Tentative = ''
				text = sentence_tone['text']
				if text != '':
					all_tones = sentence_tone['tones']
					if len(all_tones) > 0:
						for t in all_tones:
							if t['tone_name'] == 'Anger':
								Anger = t['score']
							elif t['tone_name'] == 'Fear':
								Fear = t['score']
							elif t['tone_name'] == 'Joy':
								Joy = t['score']
							elif t['tone_name'] == 'Sadness':
								Sadness = t['score']
							elif t['tone_name'] == 'Analytical':
								Analytical = t['score']
							elif t['tone_name'] == 'Confident':
								Confident = t['score']
							elif t['tone_name'] == 'Tentative':
								Tentative = t['score']
							else:
								pass
					table_lines.append((text, Anger, Fear, Joy, Sadness, Analytical, Confident, Tentative))
	else:
		sentences_tones = None

	normalized_dict = { 
		'Acousticness': song_document['Acousticness'], 
		'Instrumentalness': song_document['Instrumentalness'],
		'Mode': song_document['Mode'],
		'Valence': song_document['Valence'],
		'Danceability': song_document['Danceability'],
		'Energy': song_document['Energy'],
		'Liveness': song_document['Liveness'],
		'Speechiness': song_document['Speechiness']
		}

	other_dict = {
		'Key': song_document['Key'],
		'Loudness': -1*song_document['Loudness'],
		'Tempo': song_document['Tempo']
	}

	hist1_x = list(normalized_dict.keys())
	hist1_y = list(normalized_dict.values())

	norm_div = plotly.offline.plot({
    "data": [Bar(x=hist1_y, y=hist1_x, orientation='h')],
	}, output_type="div", include_plotlyjs=False,link_text="",show_link="False")

	hist2_x = list(other_dict.keys())
	hist2_y = list(other_dict.values())

	other_div = plotly.offline.plot({
    "data": [Bar(x=hist2_x, y=hist2_y)],
	}, output_type="div", include_plotlyjs=False,link_text="",show_link="False")

	return render_template("hot100-song.html", song_document=song_document, norm_div=norm_div, other_div=other_div,
		doc_tones=doc_tones, sentences_tones=sentences_tones, table_lines=table_lines, tone_div=tone_div, tweet_sentiment_div=tweet_sentiment_div)

if __name__ == '__main__':
	app.run(port=5000, debug=True)