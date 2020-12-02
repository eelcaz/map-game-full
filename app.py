from flask import Flask, render_template, request
import plotly.express as px
import os
from datetime import datetime
import random
from states import STATES

app = Flask(__name__)
app.jinja_env.cache = {}


states = dict.fromkeys(STATES[0], STATES[0][0])
for i in range(49):
	states.update(dict.fromkeys(STATES[i+1], STATES[i+1][0]))

guessed = ['']
now = datetime.now()
str = now.strftime("%Y%m%d%H%M%s")

@app.route('/')
def index():
	fig = px.choropleth(locations=guessed, locationmode="USA-states", color=[0], scope="usa")
	fig.update_layout(coloraxis_showscale=False)
	update_now(datetime.now())
	update_str(now.strftime("%Y%m%d%H%M%s"))
	fig.write_image('static/images/map' + str + '.png')
	return render_template('index.html', map_image = '../static/images/map' + str + '.png')

@app.route('/', methods=['POST'])
def index_post():
	text = request.form['text']
	processed_text = text.upper()
	if processed_text not in states:
		return render_template('index.html', map_image = '../static/images/map' + str + '.png', error_message = 'Not a valid state')
	processed_text = states[processed_text]
	new_guessed = guessed + [processed_text]
	update_guessed(new_guessed)
	fig = px.choropleth(locations=guessed, locationmode="USA-states", color=[0]*len(guessed), scope="usa")
	fig.update_layout(coloraxis_showscale=False)
	update_now(datetime.now())
	update_str(now.strftime("%Y%m%d%H%M%s"))
	fig.write_image('static/images/map' + str + '.png')
	return render_template('index.html', map_image = '../static/images/map' + str + '.png')

def update_guessed(new_guessed):
	global guessed
	guessed = new_guessed
	return guessed
	
def update_now(new_now):
	global now
	now = new_now
	return now

def update_str(new_str):
	global str
	str = new_str
	return now