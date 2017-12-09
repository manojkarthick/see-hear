import pandas as pd

df = pd.read_csv("by-states.csv")

usa = pd.read_csv('usa-artists.csv')

f = open('chloropleth-usa-data.csv', 'w')

for index,row in df.iterrows():
	Code = row['Code']
	Count = row['Count']
	artists = usa.loc[usa['Code'] == Code]
	current_artists = artists['Artist'].values.flatten().tolist()
	to_write = "{};{};{}".format(Code, Count, ','.join(current_artists))
	f.write(to_write)
	f.write('\n')

