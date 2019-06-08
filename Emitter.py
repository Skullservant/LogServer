import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from DatabaseManagers import MainDatabaseManager
import numpy as np

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

'''helper functions:'''

def start_to_end_durations(logs):

	"""
		bief: computes the time between the start and the end of each event
		param logs: list of logs (format of entry = [timestamp (int), state (0 or 1)])
		return: list of all durations in chronological order
	"""

	shifted_logs=np.append(logs[1:], np.zeros((1,2)), axis=0)
	logs=(shifted_logs-logs)[:len(logs)-1]
	return logs[logs[:,1]==-1][:,0]

def start_to_start_durations(logs):

	"""
		bief: computes the time between the start of each event and the start of the one that follows
		param logs: list of logs (format of entry = [timestamp (int), state (0 or 1)])
		return: list of all durations in chronological order
	"""

	on_logs=logs[logs[:,1]==1]
	shifted_on_logs=np.append(on_logs[1:], np.zeros((1,2)), axis=0)
	return (shifted_on_logs-on_logs)[:len(on_logs)-1][:,0]

'''initialization of the layout: front-end implementation'''

db=MainDatabaseManager()
games=db.read('Game', [], [])
users=db.read('User', [], [])
robots_pos=np.unique(db.read('Position', [], ['robot_id']))
robots_events=np.unique(np.append(db.read('DiscreteEvent', [], ['robot_id']), db.read('ContinuousEvent', [], ['robot_id'])))
iters_pos=np.unique(db.read('Position', [], ['iter']))
iters_events=np.unique(np.append(db.read('DiscreteEvent', [], ['iter']), db.read('ContinuousEvent', [], ['iter'])))

app.layout =  html.Div([
	dcc.Markdown('''POSITION ANALYSIS:'''),
	dcc.Markdown('''Position Analysis Global Optional Arguments: Restrictions (Default=All Are Authorized):'''),
	dcc.Markdown('''Authorized Robot Ids:'''),
	dcc.Dropdown(
        	id='auth_bot',
		options= [{'label':i, 'value':i} for i in robots_pos],
		multi=True,
		value=[]
        ),
	dcc.Markdown('''Authorized Games:'''),
	dcc.Dropdown(
        	id='auth_game',
		options= [{'label':i[1], 'value':i[0]} for i in games],
		multi=True,
		value=[]
        ),
	dcc.Markdown('''Authorized Users:'''),
	dcc.Dropdown(
        	id='auth_user',
		options= [{'label':i[1], 'value':i[0]} for i in users],
		multi=True,
		value=[]
        ),
	dcc.Markdown('''Authorized Iterations:'''),
	dcc.Dropdown(
        	id='auth_iter',
		options= [{'label':i, 'value':str(i)} for i in iters_pos],
		multi=True,
		value=[]
        ),
	dcc.Markdown('''Trajectory Analysis:'''),
	dcc.Markdown('''Optional Arguments:'''),
	dcc.Markdown('''Source Of The Background Image:'''),
	dcc.Textarea(
    		placeholder='https://...',
    		style={'width': '100%'},
		id='image'
	),
	dcc.Input(
		id='image_x',
    		placeholder='X-Axis Length',
    		type='number',
		min=0
	),
	dcc.Input(
		id='image_y',
    		placeholder='Y-Axis Length',
    		type='number',
		min=0
	),
	html.Button('Draw The Trajectory', id='draw_button',n_clicks=0),
	dcc.Graph(id='pos_graph'),
	dcc.Markdown('''Position Analysis:'''),
	dcc.Markdown('''Compulsory Arguments:'''),
	dcc.Input(
		id='heat_x_div',
    		placeholder='X-Axis Boxes',
		type='number',
		min=1
	),
	dcc.Input(
		id='heat_y_div',
    		placeholder='Y-axis boxes',
    		type='number',
		min=1
	),
	dcc.Markdown('''Optional Arguments:'''),
	dcc.Input(
		id='heat_x_min',
    		placeholder='X-axis min value',
    		type='number'
	),
	dcc.Input(
		id='heat_x_max',
    		placeholder='X-axis max value',
    		type='number'
	),
	dcc.Input(
		id='heat_y_min',
    		placeholder='Y-axis min value',
    		type='number'
	),
	dcc.Input(
		id='heat_y_max',
    		placeholder='Y-axis max value',
    		type='number'
	),
	html.Button('Display Heat Map', id='cut_button',n_clicks=0),
	dcc.Markdown(id='heat_text'),
	dcc.Graph(
    		style={'height': 600},
    		id='heat_map'
	),
	dcc.Markdown('''EVENTS ANALYSIS:'''),
	dcc.Markdown('''Events Analysis Compulsory Arguments:'''),
	dcc.Markdown('''Robot Id:'''),
	dcc.Dropdown(
        	id='selected_bot',
		options= [{'label':i, 'value':i} for i in robots_events]
        ),
	dcc.Markdown('''Game:'''),
	dcc.Dropdown(
        	id='selected_game',
		options= [{'label':i[1], 'value':i[0]} for i in games]
        ),
	dcc.Markdown('''User:'''),
	dcc.Dropdown(
        	id='selected_user',
		options= [{'label':i[1], 'value':i[0]} for i in users]
        ),
	dcc.Markdown('''Iteration:'''),
	dcc.Dropdown(
        	id='selected_iter',
		options= [{'label':i, 'value':i} for i in iters_events]
        ),
	dcc.Markdown('''Events Analysis Optional Arguments:'''),
	dcc.Markdown('''Zone:'''),
	dcc.Dropdown(
        	id='auth_zone',
		disabled=True
        ),
	html.Button('Visualize Event Data', id='analyse_button',n_clicks=0),
	dcc.Markdown(children='',id='event_num_analysis'),
	dcc.Graph(
    		id='kidnap_graph'
	),
	dcc.Graph(
    		id='border_graph'
	),
	dcc.Graph(
    		id='inner_graph'
	),
	dcc.Graph(
    		id='distance_graph'
	)		
])

'''callbacks: back-end implementation'''

@app.callback(
	dash.dependencies.Output('pos_graph','figure'),
	[dash.dependencies.Input('draw_button', 'n_clicks')],
	[dash.dependencies.State('auth_bot', 'value'),
	 dash.dependencies.State('auth_game', 'value'),
	 dash.dependencies.State('auth_user', 'value'),
	 dash.dependencies.State('auth_iter', 'value'),
	 dash.dependencies.State('image', 'value'), 
	 dash.dependencies.State('image_x', 'value'),
	 dash.dependencies.State('image_y', 'value')])

def draw_trajectory(clicks, bot, game, user, ite, image, x, y):

	"""
		bief: updates the display of the position scatter plot when the "Draw The Trajectory" button gets pressed
		param clicks: amount of times the button has been pressed
		param bot: list of all selected robot ids
		param game: list of all selected game ids
		param user: list of all selected user ids
		param ite: list of all selected iterations
		param image: URL of the image to display as background
		param x: width of the image (in mm)
		param y: height of the image (in mm)
		return: the updated figure of the scatter plot
	"""

	if clicks==0:
		x_axis=[]
		y_axis=[]
	else:
		x_axis=db.read('Position', [bot, game, user, ite], ['x']).flatten()
		y_axis=db.read('Position', [bot, game, user, ite], ['y']).flatten()
	min_x=0 if len(x_axis)==0 else np.min(x_axis)
	max_x=0 if len(x_axis)==0 else np.max(x_axis)
	min_y=0 if len(y_axis)==0 else np.min(y_axis)
	max_y=0 if len(y_axis)==0 else np.max(y_axis)
	x_image=0 if x==None else x
	y_image=0 if y==None else y
	return go.Figure(
        		data=[
            			go.Scatter(
                			x=x_axis,
					y=y_axis,
                			marker = dict(
                    				color='rgb(55, 83, 109)'
                			)
            			)
        		],
        		layout=go.Layout(
            			title='Trajectory Scatter Plot',
            			margin = dict(l=50, r=50, t=50, b=50),
            			images = [dict(
   					source=image,
   					xref= "x",
   					yref= "y",
   					x= 0,
   					y= y,
   					sizex= x_image,
   					sizey= y_image,
   					sizing= "stretch",
   					opacity= 0.7,
   					visible = True,
   					layer= "below")
				],
				xaxis=go.layout.XAxis(
        				title=go.layout.xaxis.Title(
            					text='X (in mm)',
            					font=dict(
                					family='Courier New, monospace',
                					size=18,
                					color='#7f7f7f'
            					)
        				),
					range=(min(min_x, 0), max(max_x, x_image))
    				),
    				yaxis=go.layout.YAxis(
        				title=go.layout.yaxis.Title(
            					text='Y (in mm)',
            					font=dict(
                					family='Courier New, monospace',
                					size=18,
                					color='#7f7f7f'
            					)
        				),
					range=(min(min_y, 0), max(max_y, y_image))	
    				)

        		)
    		)

@app.callback(
	dash.dependencies.Output('heat_text','children'),
	[dash.dependencies.Input('cut_button', 'n_clicks')],
	[dash.dependencies.State('heat_x_div', 'value'),
	 dash.dependencies.State('heat_y_div', 'value')])

def update_heat_text(clicks, x_div, y_div):

	"""
		bief: updates the warning text below the "Display Heat Map" button when it gets pressed
		param clicks: amount of times the button has been pressed
		param x_div: amount of blocks in the x-dimension
		param y_div: amount of blocks in the y-dimension
		return: the updated warning text of the button
	"""

	if clicks==0:
		return ""
	elif x_div==None or y_div==None:
		return "Some Of The Compulsory Arguments Haven't Been filled!"
	else:
		return "All Clear!"

@app.callback(
	dash.dependencies.Output('heat_map','figure'),
	[dash.dependencies.Input('cut_button', 'n_clicks')],
	[dash.dependencies.State('auth_bot', 'value'),
	 dash.dependencies.State('auth_game', 'value'),
	 dash.dependencies.State('auth_user', 'value'),
	 dash.dependencies.State('auth_iter', 'value'),
	 dash.dependencies.State('heat_x_div', 'value'),
	 dash.dependencies.State('heat_y_div', 'value'),
	 dash.dependencies.State('heat_x_min', 'value'),
	 dash.dependencies.State('heat_x_max', 'value'),
	 dash.dependencies.State('heat_y_min', 'value'),
	 dash.dependencies.State('heat_y_max', 'value')])

def draw_positions(clicks, bot, game, user, ite, x_div, y_div, x_min, x_max, y_min, y_max):
	
	"""
		bief: updates the display of the position heat map when the "Display Heat Map" button gets pressed
		param clicks: amount of times the button has been pressed
		param bot: list of all selected robot ids
		param game: list of all selected game ids
		param user: list of all selected user ids
		param ite: list of all selected iterations
		param x_div: amount of blocks in the x-dimension
		param y_div: amount of blocks in the y-dimension
		param x_min: lower bound for the x axis
		param x_max: upper bound for the x axis
		param y_min: lower bound for the y axis
		param y_max: upper bound for the y axis
		return: the updated figure of the heat map
	"""

	z=np.array([])
	fract_x=np.array([])
	fract_y=np.array([])
	if clicks!=0 and x_div!=None and y_div!=None:
		coord=db.read('Position', [bot, game, user, ite], ['x', 'y'])
		z=np.zeros((y_div, x_div))
		if len(coord)!=0:
			min_x=np.min(coord[:, 0]) if x_min==None else x_min
			min_y=np.min(coord[:, 1]) if y_min==None else y_min
			max_x=np.max(coord[:, 0])+1 if x_max==None else x_max
			max_y=np.max(coord[:, 1])+1 if y_max==None else y_max
			fract_x=[min_x+i/x_div*(max_x-min_x) for i in range(x_div+1)]
			fract_y=[min_y+i/y_div*(max_y-min_y) for i in range(y_div+1)]
			for i in range(x_div):
				for j in range(y_div):
					z[j,i]=np.sum((coord[:, 0]>=fract_x[i])*(coord[:, 0]<fract_x[i+1])*(coord[:, 1]>=fract_y[j])*(coord[:, 1]<fract_y[j+1]))
	return go.Figure(
		data=[
            		go.Heatmap(
                		x = fract_x,
				y = fract_y,
				z = 100*z/np.sum(z),
				xgap = 1,
				ygap = 1
            		)
        	],
        	layout=go.Layout(
            		title='Location Heat Map (Z = Percentage Of Points)',
            		margin = dict(l=50, r=50, t=50, b=50),
			xaxis=go.layout.XAxis(
        			title=go.layout.xaxis.Title(
            				text='X (in mm)',
            				font=dict(
                				family='Courier New, monospace',
                				size=18,
                				color='#7f7f7f'
            				)
        			)
    			),
    			yaxis=go.layout.YAxis(
        			title=go.layout.yaxis.Title(
            				text='Y (in mm)',
            				font=dict(
                				family='Courier New, monospace',
                				size=18,
                				color='#7f7f7f'
            				)
        			)	
    			)
			
        	)
    	)

@app.callback(
	dash.dependencies.Output('auth_zone','options'),
	[dash.dependencies.Input('selected_bot', 'value'),
	 dash.dependencies.Input('selected_game', 'value'),
	 dash.dependencies.Input('selected_user', 'value'),
	 dash.dependencies.Input('selected_iter', 'value')])

def update_auth_zones(bot, game, user, ite):

	"""
		bief: updates the options of the zone selection dropdown whenever a user-set restriction changes
		param bot: selected robot id
		param game: selected game id
		param user: selected user id
		param ite: selected iteration
		return: the updated list of zone options
	"""

	if bot==None or game==None or user==None or ite==None:
		return []
	else:
		dis_zone_ids=db.read('DiscreteEvent', [[bot], [game], [user], [], [ite], []], ['zone_id'])
		con_zone_ids=db.read('ContinuousEvent', [[bot], [game], [user], [], [ite], []], ['zone_id'])
		zone_ids=np.unique(np.append(dis_zone_ids, con_zone_ids))
		zones=db.read('Zone', [zone_ids], []) if len(zone_ids)!=0 else []
		return [{'label':j, 'value':i} for i,j in zones]

@app.callback(
	dash.dependencies.Output('auth_zone','value'),
	[dash.dependencies.Input('selected_bot', 'value'),
	 dash.dependencies.Input('selected_game', 'value'),
	 dash.dependencies.Input('selected_user', 'value'),
	 dash.dependencies.Input('selected_iter', 'value')])

def reset_zones_val(bot, game, user, ite):

	"""
		bief: resets the value of the zone selection dropdown whenever a user-set restriction changes
		param bot: selected robot id
		param game: selected game id
		param user: selected user id
		param ite: selected iteration
		return: the reseted version of the value (None)
	"""
	return None

@app.callback(
	dash.dependencies.Output('auth_zone','disabled'),
	[dash.dependencies.Input('selected_bot', 'value'),
	 dash.dependencies.Input('selected_game', 'value'),
	 dash.dependencies.Input('selected_user', 'value'),
	 dash.dependencies.Input('selected_iter', 'value')])

def update_zone_dis(bot, game, user, ite):

	"""
		bief: updates the access status of the zone selection dropdown whenever a user-set restriction changes
		param bot: selected robot id
		param game: selected game id
		param user: selected user id
		param ite: selected iteration
		return: the updated access status (true <=> disabled) 
	"""

	return bot==None or game==None or user==None or ite==None

@app.callback(
	dash.dependencies.Output('event_num_analysis','children'),
	[dash.dependencies.Input('analyse_button', 'n_clicks')],
	[dash.dependencies.State('selected_bot', 'value'),
	 dash.dependencies.State('selected_game', 'value'),
	 dash.dependencies.State('selected_user', 'value'),
	 dash.dependencies.State('auth_zone', 'value'),
	 dash.dependencies.State('selected_iter', 'value')])

def analyse_events(clicks, bot, game, user, zone, ite):

	"""
		bief: updates the text representing the results of the numerical event analysis when the "Visualize Event Data" button gets pressed
		param clicks: amount of times the button has been pressed
		param bot: selected robot id
		param game: selected game id
		param user: selected user id
		param zone: selected zone id
		param ite: selected iteration
		return: text exposing the updated results of the numerical event analysis
	"""

	if clicks==0:
		return ''
	elif bot==None or game==None or user==None or ite==None or zone==None:
		return '''Some Of The Compulsory Arguments Haven't Been filled!'''
	else:
		kid=start_to_end_durations(db.read('DiscreteEvent', [[bot], [game], [user], [zone], [ite], [], ['kidnap']], ['timestamp', 'state']))
		border=start_to_start_durations(db.read('DiscreteEvent', [[bot], [game], [user], [zone], [ite], [], ['border']], ['timestamp', 'state']))
		inner=db.read('DiscreteEvent', [[bot], [game], [user], [zone], [ite], [], ['inner']], ['timestamp', 'state'])
		inner=start_to_end_durations(inner)
		distance=db.read('ContinuousEvent', [[bot], [game], [user], [zone], [ite], [], ['distance']], ['value'])
		return '''
		Kidnapping Time: MEAN: {}|STD: {}
		Border-To-Border Time: MEAN: {}|STD: {}
		Inner Time: MEAN: {}|STD: {}
		Distance To The Zone: MEAN: {}|STD: {}|MIN: {}|MAX: {}'''.format(np.mean(kid), np.std(kid), np.mean(border), np.std(border), np.mean(inner), np.std(inner), np.mean(distance), np.std(distance), np.min(distance), np.max(distance))

@app.callback(
	dash.dependencies.Output('kidnap_graph','figure'),
	[dash.dependencies.Input('analyse_button', 'n_clicks')],
	[dash.dependencies.State('selected_bot', 'value'),
	 dash.dependencies.State('selected_game', 'value'),
	 dash.dependencies.State('selected_user', 'value'),
	 dash.dependencies.State('auth_zone', 'value'),
	 dash.dependencies.State('selected_iter', 'value')])

def draw_kidnap_times(clicks, bot, game, user, zone, ite):

	"""
		bief: updates the display of the kidnap duration histogram when the "Visualize Event Data" button gets pressed
		param clicks: amount of times the button has been pressed
		param bot: selected robot id
		param game: selected game id
		param user: selected user id
		param zone: selected zone id
		param ite: selected iteration
		return: the updated figure of the histogram
	"""

	if clicks!=0 and bot!=None and game!=None and user!=None and ite!=None and zone!=None:
		kid=start_to_end_durations(db.read('DiscreteEvent', [[bot], [game], [user], [zone], [ite], [], ['kidnap']], ['timestamp', 'state']))
		return go.Figure(
        		data=[
            			go.Bar(
                			x=np.arange(len(kid))+1,
                			y=kid
            			)
        		],
        		layout=go.Layout(
            			title='Kidnapping Durations In The Chronological Order (Histogram)',
            			margin = dict(l=50, r=50, t=50, b=50),
				xaxis=go.layout.XAxis(
        				title=go.layout.xaxis.Title(
            					text='Iteration',
            					font=dict(
                					family='Courier New, monospace',
                					size=18,
                					color='#7f7f7f'
            					)
        				)
    				),
    				yaxis=go.layout.YAxis(
        				title=go.layout.yaxis.Title(
            					text='Time (in ms)',
            					font=dict(
                					family='Courier New, monospace',
                					size=18,
                					color='#7f7f7f'
            					)
        				)	
    				)
        		)
    		)

@app.callback(
	dash.dependencies.Output('border_graph','figure'),
	[dash.dependencies.Input('analyse_button', 'n_clicks')],
	[dash.dependencies.State('selected_bot', 'value'),
	 dash.dependencies.State('selected_game', 'value'),
	 dash.dependencies.State('selected_user', 'value'),
	 dash.dependencies.State('auth_zone', 'value'),
	 dash.dependencies.State('selected_iter', 'value')])

def draw_border_times(clicks, bot, game, user, zone, ite):

	"""
		bief: updates the display of the border-to-border duration histogram when the "Visualize Event Data" button gets pressed
		param clicks: amount of times the button has been pressed
		param bot: selected robot id
		param game: selected game id
		param user: selected user id
		param zone: selected zone id
		param ite: selected iteration
		return: the updated figure of the histogram
	"""

	if clicks!=0 and bot!=None and game!=None and user!=None and ite!=None and zone!=None:
		border=start_to_start_durations(db.read('DiscreteEvent', [[bot], [game], [user], [zone], [ite], [], ['border']], ['timestamp', 'state']))
		return go.Figure(
        		data=[
            			go.Bar(
                			x=np.arange(len(border))+1,
                			y=border
            			)
        		],
        		layout=go.Layout(
            			title='Border-To-Border Durations In The Chronological Order (Histogram)',
            			margin = dict(l=50, r=50, t=50, b=50),
				xaxis=go.layout.XAxis(
        				title=go.layout.xaxis.Title(
            					text='Iteration',
            					font=dict(
                					family='Courier New, monospace',
                					size=18,
                					color='#7f7f7f'
            					)
        				)
    				),
    				yaxis=go.layout.YAxis(
        				title=go.layout.yaxis.Title(
            					text='Time (in ms)',
            					font=dict(
                					family='Courier New, monospace',
                					size=18,
                					color='#7f7f7f'
            					)
        				)	
    				)
        		)
    		)
	
@app.callback(
	dash.dependencies.Output('inner_graph','figure'),
	[dash.dependencies.Input('analyse_button', 'n_clicks')],
	[dash.dependencies.State('selected_bot', 'value'),
	 dash.dependencies.State('selected_game', 'value'),
	 dash.dependencies.State('selected_user', 'value'),
	 dash.dependencies.State('auth_zone', 'value'),
	 dash.dependencies.State('selected_iter', 'value')])

def draw_inner_times(clicks, bot, game, user, zone, ite):

	"""
		bief: updates the display of the inner-to-inner duration histogram when the "Visualize Event Data" button gets pressed
		param clicks: amount of times the button has been pressed
		param bot: selected robot id
		param game: selected game id
		param user: selected user id
		param zone: selected zone id
		param ite: selected iteration
		return: the updated figure of the histogram
	"""

	if clicks!=0 and bot!=None and game!=None and user!=None and ite!=None and zone!=None:
		inner=start_to_end_durations(db.read('DiscreteEvent', [[bot], [game], [user], [zone], [ite], [], ['inner']], ['timestamp', 'state']))
		return go.Figure(
        		data=[
            			go.Bar(
                			x=np.arange(len(inner))+1,
                			y=inner
            			)
        		],
        		layout=go.Layout(
            			title='Inner Durations In The Chronological Order (Histogram)',
            			margin = dict(l=50, r=50, t=50, b=50),
				xaxis=go.layout.XAxis(
        				title=go.layout.xaxis.Title(
            					text='Iteration',
            					font=dict(
                					family='Courier New, monospace',
                					size=18,
                					color='#7f7f7f'
            					)
        				)
    				),
    				yaxis=go.layout.YAxis(
        				title=go.layout.yaxis.Title(
            					text='Time (in ms)',
            					font=dict(
                					family='Courier New, monospace',
                					size=18,
                					color='#7f7f7f'
            					)
        				)	
    				)
        		)
    		)

@app.callback(
	dash.dependencies.Output('distance_graph','figure'),
	[dash.dependencies.Input('analyse_button', 'n_clicks')],
	[dash.dependencies.State('selected_bot', 'value'),
	 dash.dependencies.State('selected_game', 'value'),
	 dash.dependencies.State('selected_user', 'value'),
	 dash.dependencies.State('auth_zone', 'value'),
	 dash.dependencies.State('selected_iter', 'value')])

def draw_distances(clicks, bot, game, user, zone, ite):

	"""
		bief: updates the display of the distance-vs-time scatter plot when the "Visualize Event Data" button gets pressed
		param clicks: amount of times the button has been pressed
		param bot: selected robot id
		param game: selected game id
		param user: selected user id
		param zone: selected zone id
		param ite: selected iteration
		return: the updated figure of the scatter plot
	"""

	if clicks!=0 and bot!=None and game!=None and user!=None and ite!=None and zone!=None:
		distance=db.read('ContinuousEvent', [[bot], [game], [user], [zone], [ite], [], ['distance']], ['timestamp', 'value'])
		return go.Figure(
        		data=[
            			go.Scatter(
                			x=distance[:,0],
					y=distance[:,1],
                			marker = dict(
                    				color='rgb(55, 83, 109)'
                			)
            			)
        		],
        		layout=go.Layout(
            			title='Distance To Zone Scatter Plot',
            			margin = dict(l=50, r=50, t=50, b=50),
				xaxis=go.layout.XAxis(
        				title=go.layout.xaxis.Title(
            					text='Time (in ms)',
            					font=dict(
                					family='Courier New, monospace',
                					size=18,
                					color='#7f7f7f'
            					)
        				)
    				),
    				yaxis=go.layout.YAxis(
        				title=go.layout.yaxis.Title(
            					text='Distance (in mm)',
            					font=dict(
                					family='Courier New, monospace',
                					size=18,
                					color='#7f7f7f'
            					)
        				)	
    				)
        		)
    		)
		
if __name__ == '__main__':
    app.run_server(debug=False, host= '0.0.0.0') #launches the server (host='0.0.0.0' makes it accessible online)
