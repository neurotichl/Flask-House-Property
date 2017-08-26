from flaskapp import app
from flask import render_template, request, url_for, redirect
from datetime import datetime
import sys
import os

sys.path.insert(1,'C:\\Users\\user-pc\\Documents\\Python Scripts\\House-Property')
# sys.path.insert(1,'C:\\Users\\chiau.lee\\Dropbox\\JP\\Scrapy\\iproperty\\House-Property')
from datetime import datetime
import pandas as pd
import requests
import folium
import json
import re
import os

@app.route('/result')
def result(result=None):
	maps = os.listdir(os.getcwd()+'/flaskapp/templates/map')
	maps = [i.split('_')[-1].strip('.html') for i in maps]
	maps_dict = {i: datetime.strptime(i, '%Y%m%d').date().isoformat() for i in maps}
	return render_template('viewresult.html', maps=maps_dict)

@app.route('/table')
def table(result=None):
	with open('data/item.js') as data_file:    
		data = json.load(data_file)
	cols = ['name', 'tenure', 'price', 'size','amenities', 'address', 'link']
	return render_template('table.html', resp_json=data, columns=cols)

@app.route('/map')
@app.route('/map/<dt>/')
def map_plot(dt=0):
	return render_template("map/house_prop_{}.html".format(dt))

@app.route('/', methods=['GET','POST'])
def set_up_crawl():
	if request.method == "POST":
		if request.form['submit'] == 'View History':
			return redirect(url_for('result'))
		else:
			result = request.form.copy()
			process = CrawlerProcess({
				'FEED_URI':'house_{}_{}.csv'.format(result['user'],datetime.today().date().isoformat()),
				'FEED_FORMAT':'csv'
				})
			result['state'] = 'selangor,kuala-lumpur'
			result = {k:v for k,v in result.items() if k in ['state','min_price','max_price']}
			process.crawl(HouseSpiderExp,**result)
			process.start(stop_after_crawl=False)
			return redirect(url_for('result'))
			# return render_template("filledform.html",result = result)

	states=['Johor',
			'Kedah',
			'Kelantan',
			'Labuan',
			'Kuala Lumpur',
			'Melaka',
			'Negeri Sembilan',
			'Pahang',
			'Perak',
			'Pulau Pinang',
			'Putrajaya',
			'Sabah',
			'Sarawak',
			'Selangor',
			'Terengganu']
	state_dict = {i.lower().replace(' ','-'):i for i in states}
	tenure =['Freehold','Leasehold','Any']

	return render_template('form.html', states=state_dict, tenure=tenure)




