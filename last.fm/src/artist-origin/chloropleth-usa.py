import plotly
import pandas as pd

df = pd.read_csv('chloropleth-usa-data.csv', sep=';')

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
        title = 'Number of artists part of Hot 100 by State',
        geo = dict(
            scope='usa',
            projection=dict( type='albers usa' ),
            showlakes = True,
            lakecolor = 'rgb(255, 255, 255)'),
             )
    
fig = dict( data=data, layout=layout )
plotly.offline.plot( fig)