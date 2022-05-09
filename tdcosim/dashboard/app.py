import sys
import os
import json

import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table
import plotly.express as px
import pandas as pd

from tdcosim.dashboard import Dashboard

helper=Dashboard()
app = dash.Dash(__name__,assets_folder='assets',include_assets_files=True)


#=======================================================================================================================
def create_query_bar(fpath):
	ddData=helper.get_scenario_info(fpath)
	ddScenarios=[{'label':thisScenario,'value':thisScenario} for thisScenario in ddData['scenario']]
	ddTnodeid=[{'label':entry,'value':entry} for entry in ddData['tnodeid']]
	ddProperty=[{'label':entry,'value':entry} for entry in ddData['property']]

	ddData['index']={}
	for entry in ddData['scenario']:
		ddData['index'][entry]=json.load(open(ddData['scenario'][entry]['indexPath']))
		if not isinstance(ddData['index'][entry]['pointer'],np.ndarray):
			ddData['index'][entry]['pointer']=np.cumsum(ddData['index'][entry]['pointer'])

	# ddOptions=[{'label':'apple','value':'apple'},{'label':'google','value':'google'}]
	dd1=dcc.Dropdown(id='dd1',options=ddScenarios,value='',placeholder='scenarios',multi=True,
	style={'minWidth':'200px','backgroundColor':'#ada9a9','border':'1px solid black','borderRadius':'2px'})
	dd2=dcc.Dropdown(id='dd2',options=ddTnodeid,value='',placeholder='tnodeid',multi=True,
	style={'minWidth':'200px','backgroundColor':'#ada9a9','border':'1px solid black','borderRadius':'2px'})
	dd3=dcc.Dropdown(id='dd3',options=ddProperty,value='',placeholder='property',multi=False,
	style={'minWidth':'200px','backgroundColor':'#ada9a9','border':'1px solid black','borderRadius':'2px'})
	b1=html.Button(id='b1',n_clicks=0,style={'minWidth':'50px','minHeight':'20px'})

	# query bar
	queryBar=html.Div(children=[dd1,dd2,dd3,b1],id='query',className='flexDiv',style={'height':'50vh','width':'300px',\
	'backgroundColor':'rgb(180, 180, 180)','borderRadius':'20px','flexDirection':'column','justifyContent':'space-around'})

	return queryBar,ddData

#=======================================================================================================================
def create_mapObj():
	df=pd.DataFrame({'lat':[35,36,37],'lon':[-110,-100,-90],'size':[12,22,45]})
	myMap=px.scatter_mapbox(df,'lat','lon',size='size')
	myMap.update_layout(mapbox_style='stamen-toner')
	myMap.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
	mapObj=dcc.Graph(id='mapObj',figure=myMap,style={'width':'90vw','height':'70vh'})
	return mapObj

#=======================================================================================================================
@app.callback(Output('f1', 'figure'),[Input('b1','n_clicks'),Input('dd1','value'),Input('dd2','value'),\
Input('dd3','value')])
def update_plot(n_clicks,scenario,tnodeid,prop):
	if n_clicks>lastUpdateClickVal[0]:
		figure['data']=[]

		if not isinstance(scenario,list):
			scenario=[scenario]
		if not isinstance(tnodeid,list):
			tnodeid=[tnodeid]
		
		for thisScenario in scenario:
			for thisTnodeid in tnodeid:
				thisDf=helper.indexer.query(ddData['scenario'][thisScenario]['csvPath'],\
				ddData['index'][thisScenario],thisTnodeid,prop)
				figure['data'].append({'x':thisDf.t,'y':thisDf.value.tolist(),'type':'chart',\
				'name':"{}_{}".format(thisTnodeid,thisScenario)})
		lastUpdateClickVal[0]+=1

	return figure


#=======================================================================================================================
if __name__ == '__main__':
	rootDir=sys.argv[1]

	# state
	lastUpdateClickVal=[0]

	# graphs
	figure={'data': [],'layout':{'plot_bgcolor':'black','title':'Sample Plot',
	'paper_bgcolor': 'rgba(45,45,45,1)','xaxis':{'color':'white','title':'Time (s)'},
	'yaxis':{'color':'white','title':'Value'},'font':{'color':'white'}}}

	# graph
	f1=dcc.Graph(id='f1',figure=figure)

	# options bar
	options=html.Div(children=[],id='options',className='flexDiv',style={'height':'40vh','width':'40px',\
	'backgroundColor':'rgb(180, 180, 180)',
	'borderRadius':'20px'})
	optionsParent=html.Div(children=[options],id='optionsParent',className='flexDiv',style={\
	'height':'calc(100vh - 8px)','width':'40px','backgroundColor':'inherit','display':'flex','flexDirection':'column','justifyContent':'center'})

	# query bar
	queryBar,ddData=create_query_bar(rootDir)

	# map
	mapObj=create_mapObj()

	# layout
	ddContainer=html.Div(children=[],id='ddContainer',className='ddContainer')
	plotContainer=html.Div(children=[ddContainer,f1],id='plotContainer',style={'flex':'1 1 40%'})
	mapContainer=html.Div(children=[mapObj],id='mapContainer',style={'display':'flex',
	'justifyContent':'center','alignItems':'center','width':'calc(98vw - 40px)','height':'80vh'})

	app.layout = html.Div(children=[optionsParent,plotContainer,mapContainer,queryBar],id='rootDiv',className="flexDiv")

	# run
	app.run_server(debug=True,use_reloader=True)