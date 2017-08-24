from flaskapp import app
from flask import render_template, request, url_for, redirect
from datetime import datetime
import sys
import os

# sys.path.insert(1,'C:\\Users\\chiau.lee\\Dropbox\\JP\\Scrapy\\iproperty\\House-Property\\')
# from multihouse import *

@app.route('/result')
def result():
	maps = os.listdir(os.getcwd()+'/flaskapp/templates/map')
	maps = [i.split('_')[-1].strip('.html') for i in maps]
	maps_dict = {i: datetime.strptime(i, '%Y%m%d').date().isoformat() for i in maps}
	return render_template('viewresult.html', maps=maps_dict)

@app.route('/map')
@app.route('/map/<dt>/')
def map_plot(dt=0):
	return render_template("map/house_prop_{}.html".format(dt))

@app.route('/', methods=['GET','POST'])
def set_up_crawl():
	if request.method == "POST":
		if request.form['submit'] == 'View Result':
			return redirect(url_for('result'))
		else:
			result = request.form
			return render_template("filledform.html",result = result)

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

	tenure =['Freehold','Leasehold','Any']

	return render_template('form.html', states=states, tenure=tenure)




