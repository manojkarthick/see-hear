import json
from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
import requests
import csv
import plotly.plotly as py
import plotly.graph_objs as go
import matplotlib as mpl

client = MongoClient('192.168.0.7', 27017)
db = client.SEEHEAR
cursor = db.hot100.find()


# Expand the cursor and construct the DataFrame
hot_df = pd.DataFrame(list(cursor))
hot_df = hot_df[['Title','Playcount','Genre']]

hot_df[['Playcount']] = hot_df[['Playcount']].apply(pd.to_numeric)

hot_df = hot_df.sort_values(by = 'Playcount',ascending=False).head(20)
# genres = hot_df['Genre'].unique()

y_axis_range = range(1,len(hot_df.index)+1)


plt.hlines(y=y_axis_range, xmin=0, xmax=hot_df['Playcount'], color='skyblue')

plt.plot(hot_df['Playcount'], y_axis_range,'o')
plt.gca().invert_yaxis()
plt.legend()
plt.yticks(y_axis_range, hot_df['Title'])
plt.show()