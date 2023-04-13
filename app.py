from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.coingecko.com/en/coins/ethereum/historical_data/usd?start_date=2020-01-01&end_date=2021-06-30#panel')
soup = BeautifulSoup(url_get.content,"html.parser")

#find your right key here
table = soup.find('tbody', attrs={'data-target':'historical.tableBody'})
table
table.find_all('th', attrs={'scope':'row'})[0].text
table.find_all('td', attrs={'class':'text-center'})[5]

row = table.find_all('th', attrs={'scope':'row'})
row_length = len(row)

rows = table.find_all('tr')
rows

temp = [] #initiating a tuple

for i in range(0, row_length):
    
    #get date 
    Date_Ethereum = table.find_all('th', attrs={'class':'font-semibold text-center'})[i].text

    #get volume 
    Volume = table.find_all('td', attrs={'class':'text-center'})[i * 4 + 1].text
    Volume = Volume.strip() #to remove excess white space
    
    temp.append((Date_Ethereum,Volume)) 
temp[:20] 

temp = temp[::-1]

#change into dataframe
df = pd.DataFrame(temp, columns = ('Date_Ethereum','Volume'))
df.head()

#insert data wrangling here
df['Date_Ethereum'] = df['Date_Ethereum'].astype('datetime64')
df['Volume'] = df['Volume'].map(lambda x: x.lstrip('$'))
df['Volume'] = df['Volume'].str.replace(",","")
df['Volume'] = df['Volume'].astype('float64')
df['Month'] = df["Date_Ethereum"].dt.month_name()
df['Month'] = df['Month'].astype('category')
df.isna().sum()
df = df.set_index('date')

#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'{df["Volume"].mean().round(2)}'#be careful with the " and ' 

	# generate plot
	ax = df.plot(figsize = (20,9))
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)