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
	with open('data/item2.js') as data_file:    
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
			state = result.get('state') or 'kuala-lumpur'
			min_price = result.get('min_price') or '280'
			max_price = result.get('max_price') or '350'
			scrapyrt_url = 'http://localhost:9080/crawl.json?spider_name=house_exp&url='
			req_url = 'https://www.iproperty.com.my/buy/{0}/?mp={1},000&xp={2},000&ht=F'.format(state,min_price,max_price)
			resp = requests.get(scrapyrt_url+req_url)
			json.dump(json.loads(resp.text)['items'],open('data/item2.js','w'))
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




