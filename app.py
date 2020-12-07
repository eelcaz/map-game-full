from flask import Flask, render_template, request
import plotly.express as px
import os
from datetime import datetime
import random
from states import STATES
import pandas as pd
from copy import deepcopy
import webbrowser
import platform
from playsound import playsound

app = Flask(__name__)
app.jinja_env.cache = {}

trivia = pd.read_csv(r'data/statescsv.csv')

states = dict.fromkeys(STATES[0], STATES[0][0])
for i in range(49):
	states.update(dict.fromkeys(STATES[i+1], STATES[i+1][0]))
state_names = dict.fromkeys(STATES[0], STATES[0][1])
for i in range(49):
	state_names.update(dict.fromkeys(STATES[i+1], STATES[i+1][1]))

states_used = ['stateIncorrect', 'stateCorrect']
colors = [0,1]
color_scale = [(0,"red"), (0.75, 'green'), (1,"lightgreen")]
left_to_guess = deepcopy(states)

table = [['AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA'],['HI', 'ID', 'IL', 'IN','IA','KS','KY','LA','ME','MD'],['MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ'],['NM','NY','NC','ND','OH','OK','OR','PA','RI','SC'],['SD','TN','TX','UT','VT','VA','WA','WV','WI','WY']]

current_state = states[random.choice(list(left_to_guess.keys()))]
is_current_state = trivia['State']==current_state
trivia_current_state = trivia[is_current_state].index[0]
question_choices = trivia.iloc[trivia_current_state]

cols = ['Flower-Bird','Funfact1','Funfact2']
question_type = random.choice(cols)

current_question = 'State Flower: ' + question_choices['Flower'] +', State Bird: ' + question_choices['Bird'] if question_type == 'Flower-Bird' else question_choices[question_type]

now = datetime.now()
date_string = now.strftime("%Y%m%d%H%M%s")
current_score = 0

@app.route('/')
def index():
	update_map()
	return render_template('index.html', map_image = '../static/images/map' + date_string + '.png', trivia_question = current_question, curr_score = get_score(), tbl = table)

@app.route('/', methods=['POST'])
def index_post():
	if 'AnswerRequest' in request.form:
		return handle_guess(request)
	elif 'SkipRequest' in request.form:
		return handle_skip()
	elif 'RestartGame' in request.form:
		return handle_reset()
	elif 'TakeSurvey' in request.form:
		webbrowser.open('https://www.surveymonkey.com/r/8GPRNPL')
		return render_template('index.html', map_image = '../static/images/map' + date_string + '.png', trivia_question = current_question, feedback_message = "Thanks for taking our survey!", curr_score = current_score, tbl = table)

def handle_guess(request):
	if len(left_to_guess) == 0:
		return render_template('index.html', map_image = '../static/images/map' + date_string + '.png', trivia_question = current_question, feedback_message = "Click restart to play again!", curr_score = get_score(), tbl = table)

	text = request.form['text']
	processed_text = text.upper()
	if processed_text not in states:
		sound('sounds/error.wav')
		return render_template('index.html', map_image = '../static/images/map' + date_string + '.png', trivia_question = current_question, feedback_message = 'Not a valid state!', curr_score = get_score(), tbl = table)
	if processed_text not in left_to_guess:
		sound('sounds/error.wav')
		return render_template('index.html', map_image = '../static/images/map' + date_string + '.png', trivia_question = current_question, feedback_message = 'State already used!', curr_score = get_score(), tbl = table)
	
	processed_text = states[processed_text]
	result = ''
	if processed_text == current_state:
		update_colors(colors+[1])
		update_score(current_score+1)
		sound('sounds/correct.wav')
		result = 'Correct! This state will now be highlighted'
	else:
		update_colors(colors+[0])
		update_score(current_score)
		sound('sounds/incorrect.wav')
		result = 'Incorrect :( The correct state is ' + get_state_name() + '. This state will now be highlighted.'
	update_trivia_parameters()
	update_map()

	return render_template('index.html', map_image = '../static/images/map' + date_string + '.png', trivia_question = current_question, feedback_message = result, curr_score = get_score(), tbl = table)

def get_state_name():
	return state_names[current_state].capitalize()

def handle_skip():
	if len(left_to_guess) == 0:
		return render_template('index.html', map_image = '../static/images/map' + date_string + '.png', trivia_question = current_question, feedback_message = "Click restart to play again!", curr_score = get_score(), tbl = table)
	sound('sounds/skip.wav')
	result = 'You skipped :( The correct state was ' + get_state_name() + '. This state will now be highlighted.'
	update_colors(colors+[0])
	update_trivia_parameters()
	update_map()
	update_score(current_score)
	
	return render_template('index.html', map_image = '../static/images/map' + date_string + '.png', trivia_question = current_question, feedback_message = result, curr_score = get_score(), tbl = table)

def update_map():
	fig = px.choropleth(locations=states_used, locationmode="USA-states", scope="usa", color=colors, color_continuous_scale=color_scale)
	fig.update_layout(coloraxis_showscale=False)
	update_map_path()
	fig.write_image('static/images/map' + date_string + '.png', engine='kaleido')

def handle_reset():
	update_states_used(['stateIncorrect', 'stateCorrect'])
	update_colors([0,1])
	update_score(0)
	global left_to_guess
	left_to_guess = deepcopy(states)
	global table
	table = [['AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA'],['HI', 		'ID', 'IL', 'IN','IA','KS','KY','LA','ME','MD'],		['MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ'],		['NM','NY','NC','ND','OH','OK','OR','PA','RI','SC'],									['SD','TN','TX','UT','VT','VA','WA','WV','WI','WY']]

	update_current_state(states[random.choice(list(left_to_guess.keys()))])    
	update_current_question(generateNewQuestion())

	update_map()
	return render_template('index.html', map_image = '../static/images/map' + date_string + '.png', trivia_question = current_question, feedback_message='Restarted!', curr_score = get_score(), tbl = table)

def get_score():
	if len(states_used) == 2:
		return 'NA'
	return str(current_score) + '/ ' + str(len(states_used)-2) # + ' = ' + str(round(current_score/(len(states_used)-2)*100, 2)) + '%'

def update_score(new_score):
	global current_score
	current_score = new_score

def update_map_path():
	global now
	now = datetime.now()
	global date_string
	date_string = now.strftime("%Y%m%d%H%M%s")

def update_colors(new_colors):
	last_color = new_colors[-2]
	if len(new_colors) >= 4:
		if last_color == 0:
			new_colors[-2]=0.25
		elif last_color == 1:
			new_colors[-2]=0.75
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
		for x in range(len(table)):
			for y in range(len(table[x])):
				if table[x][y]==k:
					table[x][y] = "  "

	if len(left_to_guess) > 0:
		update_current_state(states[random.choice(list(left_to_guess.keys()))])
		update_current_question(generateNewQuestion())  
	else:
		update_current_question("Congratulations, you've completed the game!")  

def sound(path):
	if platform.system() == 'Linux':
		os.system('aplay ' + path + '&')
	elif platform.system() == 'Mac':
		playsound(path)
