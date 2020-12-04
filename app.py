from flask import Flask, render_template, request
import plotly.express as px
import os
from datetime import datetime
import random
from states import STATES
import pandas as pd
from copy import deepcopy
import webbrowser

app = Flask(__name__)
app.jinja_env.cache = {}

trivia = pd.read_csv(r'data/statescsv.csv')

states = dict.fromkeys(STATES[0], STATES[0][0])
for i in range(49):
	states.update(dict.fromkeys(STATES[i+1], STATES[i+1][0]))

states_used = ['stateIncorrect', 'stateCorrect']
colors = [0,1]
color_scale = [(0,"red"), (1,"green")]
left_to_guess = deepcopy(states)

current_state = states[random.choice(list(left_to_guess.keys()))]
is_current_state = trivia['State']==current_state
trivia_current_state = trivia[is_current_state].index[0]
question_choices = trivia.iloc[trivia_current_state]

cols = ['Flower-Bird','Funfact1','Funfact2']
question_type = random.choice(cols)

current_question = 'State Flower: ' + question_choices['Flower'] +', State Bird: ' + question_choices['Bird'] if question_type == 'Flower-Bird' else question_choices[question_type]

now = datetime.now()
str = now.strftime("%Y%m%d%H%M%s")

@app.route('/')
def index():
	fig = px.choropleth(locations=states_used, locationmode="USA-states", scope="usa", color=colors, color_continuous_scale=color_scale)
	fig.update_layout(coloraxis_showscale=False)
	update_map_path()
	fig.write_image('static/images/map' + str + '.png')
	return render_template('index.html', map_image = '../static/images/map' + str + '.png', trivia_question = current_question)

@app.route('/', methods=['POST'])
def index_post():
	if 'AnswerRequest' in request.form:
		text = request.form['text']
		processed_text = text.upper()
		if processed_text not in states:
			return render_template('index.html', map_image = '../static/images/map' + str + '.png', trivia_question = current_question, feedback_message = 'Not a valid state!')
		if processed_text not in left_to_guess:
			return render_template('index.html', map_image = '../static/images/map' + str + '.png', trivia_question = current_question, feedback_message = 'State already used!')
		
		processed_text = states[processed_text]
		result = ''
		if processed_text == current_state:
			update_colors(colors+[1])
			result = 'Correct! This state will now be highlighted'
		else:
			update_colors(colors+[0])
			result = 'Incorrect :( The correct state is ' + current_state + '. This state will now be highlighted.'

		update_trivia_parameters()
		
		fig = px.choropleth(locations=states_used, locationmode="USA-states", scope="usa", color=colors, color_continuous_scale=color_scale)
		fig.update_layout(coloraxis_showscale=False)

		update_map_path()

		fig.write_image('static/images/map' + str + '.png')
		return render_template('index.html', map_image = '../static/images/map' + str + '.png', trivia_question = current_question, feedback_message = result)
	elif 'SkipRequest' in request.form:
		result = 'You skipped :( The correct state was ' + current_state + '. This state will now be highlighted.'
		update_colors(colors+[0])
		update_trivia_parameters()
		fig = px.choropleth(locations=states_used, locationmode="USA-states", scope="usa", color=colors, color_continuous_scale=color_scale)
		fig.update_layout(coloraxis_showscale=False)

		update_map_path()

		fig.write_image('static/images/map' + str + '.png')
		return render_template('index.html', map_image = '../static/images/map' + str + '.png', trivia_question = current_question, feedback_message = result)
	elif 'RestartGame' in request.form:
		result = reset_game()
		return result
	elif 'TakeSurvey' in request.form:
		webbrowser.open('https://www.surveymonkey.com/r/8GPRNPL')
		return render_template('index.html', map_image = '../static/images/map' + str + '.png', trivia_question = current_question, feedback_message = result)

def reset_game():
		global states_used
		states_used = ['stateIncorrect', 'stateCorrect']
		global colors
		colors = [0,1]
		global left_to_guess
		left_to_guess = deepcopy(states)

		global current_state
		current_state = states[random.choice(list(left_to_guess.keys()))]
		global is_current_state
		is_current_state = trivia['State']==current_state
		global trivia_current_state
		trivia_current_state = trivia[is_current_state].index[0]
		global question_choices
		question_choices = trivia.iloc[trivia_current_state]

		cols = ['Flower-Bird','Funfact1','Funfact2']
		question_type = random.choice(cols)
        
		global current_question
		current_question = 'State Flower: ' + question_choices['Flower'] +', State Bird: ' + question_choices['Bird'] if question_type == 'Flower-Bird' else question_choices[question_type]
		fig = px.choropleth(locations=states_used, locationmode="USA-states", scope="usa", color=colors, color_continuous_scale=color_scale)

		fig.update_layout(coloraxis_showscale=False)
		update_map_path()
		fig.write_image('static/images/map' + str + '.png')
		return render_template('index.html', map_image = '../static/images/map' + str + '.png', trivia_question = current_question, feedback_message='Restarted!')

def update_map_path():
	global now
	now = datetime.now()
	global str
	str = now.strftime("%Y%m%d%H%M%s")

def update_colors(new_colors):
	global colors
	colors = new_colors
	return colors

def update_states_used(new_used):
	global states_used
	states_used = new_used
	return states_used

def update_current_state(new_state):
	global current_state
	current_state = new_state
	return current_state

def generateNewQuestion():
	is_current_state = trivia['State']==current_state
	trivia_current_state = trivia[is_current_state].index[0]
	question_choices = trivia.iloc[trivia_current_state]

	cols = ['Flower-Bird','Funfact1','Funfact2']
	question_type = random.choice(cols)

	return 'State Flower: ' + question_choices['Flower'] +', State Bird: ' + question_choices['Bird'] if question_type == 'Flower-Bird' else question_choices[question_type]

def update_current_question(new_question):
	global current_question
	current_question = new_question
	return current_question

def update_trivia_parameters():
	update_states_used(states_used + [current_state])
	keys_to_remove = []
	if current_state in left_to_guess :
		for q,v in left_to_guess.items():
			if v==current_state:
				keys_to_remove += [q]
	for k in keys_to_remove:
		left_to_guess.pop(k)
	update_current_state(states[random.choice(list(left_to_guess.keys()))])
	update_current_question(generateNewQuestion())
