import pymongo as pmg
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from DatabaseManagers import *
import numpy as np

csvdb=CSVDatabaseManager()
db=MainDatabaseManager()
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

'''initialization of the layout: front-end implementation'''

def layout():

	"""
		bief: updates the layout of the website when it gets refreshed
		return: the new layout
	"""

	return html.Div([
		dcc.Markdown('''Files:'''),
		dcc.Dropdown(
                	id='file_name',
                	options=[{'label': name, 'value': name} for name in csvdb.names()]
		),
		dcc.Markdown('''Tables:'''),
		dcc.Dropdown(
                	id='tables',
                	options=[{'label': name, 'value': name} for name in db.names()]
		),
		dcc.Markdown('''Warning: you must fill all the previous arguments to start matching!'''),
		html.Button('Start matching', id='match_button',n_clicks=0),
		dcc.Markdown(id='match_text'),
		dcc.Dropdown(id='match_drop', multi=True),
		dcc.Checklist(id='overwrite_box',
			options=[
        			{'label': 'Overwrite', 'value': ''}
    			],
			values=[]
		),
		dcc.Markdown(id='add_text'), 
		html.Button('Add', id='add_button',n_clicks=0)
	])

app.layout = layout

'''callbacks: back-end implementation'''

@app.callback(
	dash.dependencies.Output('match_drop','options'),
	[dash.dependencies.Input('match_button', 'n_clicks')],
	[dash.dependencies.State('file_name', 'value'), 
	 dash.dependencies.State('tables', 'value')])

def update_drop_ops(clicks, file_name, table_name):

	"""
		bief: updates the options of the file-to-table key matching dropdown when the "Start Matching" button gets pressed
		param clicks: amount of times the "Start Matching" button has been pressed
		param file_name: selected CSV file name
		param table_name: selected table name
		return: the new options of the file-to-table key matching dropdown
	"""

	keys=[]
	if file_name!=None and table_name!=None:
		for key in csvdb.read(file_name).keys():
			keys.append({'label': key, 'value': key})
	return keys

@app.callback(
	dash.dependencies.Output('match_drop','value'),
	[dash.dependencies.Input('match_button', 'n_clicks')])

def reset_drop_val(clicks):

	"""
		bief: resets the list of selected values of the file-to-table key matching dropdown when the "Start Matching" button gets pressed
		param clicks: amount of times the "Start Matching" button has been pressed
		return: the reseted version of the list of values of the file-to-table key matching dropdown (empty list)
	"""

	return []

@app.callback(
	dash.dependencies.Output('match_text','children'),
	[dash.dependencies.Input('match_button', 'n_clicks')],
	[dash.dependencies.State('file_name', 'value'), 
	 dash.dependencies.State('tables', 'value')])

def update_match_text(clicks, file_name, table_name):

	"""
		bief: updates the description text of the file-to-table key matching dropdown when the "Start Matching" button gets pressed
		param clicks: amount of times the "Start Matching" button has been pressed
		param file_name: selected CSV file name
		param table_name: selected table name
		return: the new description text of the file-to-table key matching dropdown
	"""

	if file_name!=None and table_name!=None:
		return file_name+'->'+table_name+', Parameters To Match: '+('|').join(db.keys(table_name))
	else:
		return ''

@app.callback(
	dash.dependencies.Output('match_drop', 'disabled'),
	[dash.dependencies.Input('match_button', 'n_clicks')],
	[dash.dependencies.State('file_name', 'value'), 
	 dash.dependencies.State('tables', 'value')])

def update_drop_dis(clicks, file_name, table_name):

	"""
		bief: updates the access status of the file-to-table key matching dropdown when the "Start Matching" button gets pressed
		param clicks: amount of times the "Start Matching" button has been pressed
		param file_name: selected CSV file name
		param table_name: selected table name
		return: the new access status of the file-to-table key matching dropdown (true <=> disabled)
	"""

	return file_name==None or table_name==None

@app.callback(
	dash.dependencies.Output('add_text','children'),
	[dash.dependencies.Input('add_button', 'n_clicks')],
	[dash.dependencies.State('match_drop', 'value'),
	 dash.dependencies.State('match_drop', 'disabled'),
	 dash.dependencies.State('match_text', 'children'),
	 dash.dependencies.State('file_name', 'value'),
	 dash.dependencies.State('tables', 'value'),
	 dash.dependencies.State('overwrite_box', 'values')])

def update_add_text(clicks, vals, dis, text, file_name, table_name, overwrite):

	"""
		bief: performs the data transfer from one database to the other and displays the results of the operation when the "Add" button gets pressed
		param clicks: amount of times the "Add" button has been pressed
		param vals: list of all the values of the file-to-table key matching dropdown that were selected
		param dis: current access status of the file-to-table key matching dropdown (true <=> disabled)
		param text: descriptive text of the file-to-table key matching dropdown
		param file_name: selected CSV file name
		param table_name: selected table name
		param overwrite: list containing the value of each checked box of the "Overwrite" checklist (empty if the only box is unchecked, len=1 otherwise) 
		return: the new description text of the final procedure
	"""

	if clicks==0:
		return '''Warning: do not press the folowing button if the matching process isn't complete.'''
	if dis:
		return '''Take care of the file-table matching first!'''
	if len(vals)!=len(text.split('|')):
		return '''The match dropdown hasn't been filled properly!'''
	csv=csvdb.read(file_name)
	csv_reorg=[]
	for val in vals:
		csv_reorg.append(csv[val])
	db.write(table_name, np.array(csv_reorg).T, len(overwrite)==1)
	return '''Added!!!'''

if __name__ == '__main__':
    app.run_server(debug=False, port=8051, host= '0.0.0.0') #launches the server (host='0.0.0.0' makes it accessible online)
