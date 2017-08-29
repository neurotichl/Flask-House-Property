from flaskapp import app
from flask import render_template, request, url_for, redirect
from datetime import datetime
import subprocess
import sys
import os

import pandas as pd
import requests
import folium
import json
import re

@app.before_first_request
def set_work_dir():
	global crawldir
	global flaskdir
	flaskdir = os.getcwd()
	crawldir = flaskdir+'\\iproperty'

def change_work_space(t):
	global crawldir
	global flaskdir
	if t == 'flask':
		os.chdir(flaskdir)
	elif t == 'crawl':
		os.chdir(crawldir)

@app.route('/result', methods=['GET','POST'])
def result():
	if request.method == 'POST':
		if request.form['displayType']=='Map':
			return redirect(url_for('map_plot'))
		else:
			return redirect(url_for('table'))
	return render_template('displayType.html')

@app.route('/table')
def table():
	change_work_space('crawl')
	with open('data/item2.json','r') as data_file:    
		data = json.load(data_file)
	cols = ['name', 'tenure', 'price', 'size','amenities', 'address', 'link']
	return render_template('table.html', resp_json=data, columns=cols)

@app.route('/map')
@app.route('/map/<dt>/')
def map_plot(dt=0):
	def facilities(x):
		try:
			return x.replace('Bedroom(s)','Room').replace('Bathroom(s)','Bath').replace('Parking Bay(s)','Park')
		except:
			pass

	change_work_space('crawl')
	with open('data/item2.json','r') as data_file:    
		data = json.load(data_file)
	df = pd.DataFrame.from_records(data)
	df['facilities'] = df['amenities'].map(facilities)
	df = df[df['lat'].notnull()]
	df['prize_range'] = 'Low'
	df = df.reset_index(drop=True).reset_index()	

	change_work_space('flask')
	plot_map(df)

	return render_template("map/house_prop.html")

@app.route('/', methods=['GET','POST'])
def set_up_crawl():
	print(os.getcwd())
	if request.method == "POST":
		if request.form['submit'] == 'View History':
			return redirect(url_for('result'))
		else:
			result = request.form
			state = result.get('state') or 'kuala-lumpur'
			min_price = result.get('min_price') or '280'
			max_price = result.get('max_price') or '350'
			user = result.get('user') or 'Unknown'
			# scrapyrt_url = 'http://localhost:9080/crawl.json?spider_name=house_exp&url='
			# req_url = 'https://www.iproperty.com.my/buy/{0}/?mp={1},000&xp={2},000&ht=F'.format(state,min_price,max_price)
			# resp = requests.get(scrapyrt_url+req_url)
			# json.dump(json.loads(resp.text)['items'],open('data/item2.js','w'))	
			change_work_space('crawl')
			subprocess.call(['scrapy','crawl','houseprop','-a','state={}'.format(state),\
								'-a','min_price={}'.format(min_price),\
								'-a','max_price={}'.format(max_price),\
								'-o','data/item2.json'])
			return redirect(url_for('result'))

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


def plot_map(df,house_conf=None):
	def add_frame(index,name,price,size,facilities,link,**kwargs):
		html="""
<pre>
{0}
Name      : {1}
Price     : {2}
Amenities : {3}
sq. ft    : {4}
link      : <a href="{5}">link</a>
</pre>
		    """
		return folium.IFrame(html= html.format(index+1,name,price,facilities,size,link), width=400, height=100)

	# def getHTML(house_conf=None):
	# 	global timestamp
	# 	html_name = '{0}/{1}_{2}'.format(house_conf['Map']['folder'],\
	# 									  house_conf['Map']['filename'],\
	# 									  timestamp)
	# 	lat_lon = house_conf['MyHouse'] if 'MyHouse' in house_conf.keys() else None
	# 	return html_name, lat_lon

	# html_name, lat_lon = getHTML(house_conf)
	html_name = 'house_prop'
	lat_lon = None

	color_group = {'High':'red','Low':'blue'}

	m = folium.Map(location=[3.139, 101.6869], zoom_start = 10)

	for row in df.to_dict(orient='records'):
		iframe = add_frame(**row)
		popup = folium.Popup(iframe, max_width=2650)
		folium.Marker([row['lat'], row['lon']], popup=popup, icon=folium.Icon(color=color_group[row['prize_range']])).add_to(m)

	if lat_lon: folium.Marker([float(lat_lon['lat']),float(lat_lon['lng'])],\
								popup='MyHome', icon=folium.Icon(color='green')).add_to(m)

	m.save('flaskapp/templates/map/{}.html'.format(html_name))