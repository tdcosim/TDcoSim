import os
import sys
import pickle
import pdb

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table
import plotly.express as px
import pandas as pd
import networkx as nx
import numpy as np


app = dash.Dash(__name__)
#### helper=Dashboard()
#### objects={'graph':{},'tab':{},'tabs':{},'upload':{},'textarea':{},'dropdown':{},'selection':{},'df':{}}


#=======================================================================================================================
def create_graphs(objects,objID,title,fontColor,xlabel,ylabel):
	for thisObjID,thisTitle,thisFontColor,thisXlabel,thisYlabel in zip(objID,title,fontColor,xlabel,ylabel):
		objects['graph'].update(helper.graph_template(thisObjID))
		objects['graph'][thisObjID].figure['layout']['title']=thisTitle
		objects['graph'][thisObjID].figure['layout']['font']={'color':thisFontColor}
		objects['graph'][thisObjID].figure['layout']['xaxis']={'title':thisXlabel}
		objects['graph'][thisObjID].figure['layout']['yaxis']={'title':thisYlabel}

#=======================================================================================================================
def create_map(df, thisObjID):
	objects['map']={}
	objects['map']['df_{}'.format(thisObjID)]=helper.build_map_df(df)
	objects['map'][thisObjID]=helper.map_template(objects['map']['df_{}'.format(thisObjID)],radarOverlay=False)

#=======================================================================================================================
def create_table(df, thisObjID,reducedMemory=True):
	if reducedMemory:
		df=df[(df.t==0)&((df.property=='VOLT')|(df.property=='SPD'))]	
	objects['table'] = {
	 thisObjID : helper.table_template(df)	
	}

#=======================================================================================================================
def create_filter(df, thisObjID):
	objects['filter'] = {
	 thisObjID : helper.filter_template(df, 'tnodeid', [])	
	}

#=======================================================================================================================
def create_tab(objects,objID,label,style=None,selected_style=None):
	if not style:
		style={'backgroundColor':'rgba(0,0,0,.7)','color':'white','fontWeight':'bold','fontSize':'1em'}
	if not selected_style:
		selected_style={'backgroundColor':'grey','color':'white','fontWeight':'bold','fontSize':'1em'}

	for thisObjID,thisLabel in zip(objID,label):
		objects['tab'][thisObjID]=dcc.Tab(id=thisObjID,label=thisLabel,style=style,selected_style=selected_style)

#=======================================================================================================================
def create_tabs(objects,objID,children):
	objects['tabs'][objID]=dcc.Tabs(id=objID,children=children)

#=======================================================================================================================
def gather_objects():
	# dropdown objects
	objects['dropdown']=helper.filter_dropdown(columnFilter=['tnodeid','tnodesubid','dnodeid','property','scenario'],
	multi=['tnodeid','tnodesubid','dnodeid'])

	objects['dropdown']['bubble_property']=dcc.Dropdown(id='bubble_property',\
		options=[{'label':entry,'value':entry} for entry in ['VOLT']],value='',\
		placeholder='bubble_property',multi=False,style={'display':'inline-block','width':'200px','margin':'20px'})

	objects['dropdown']['bubble_color_property']=dcc.Dropdown(id='bubble_color_property',\
		options=[{'label':entry,'value':entry} for entry in ['min_value','max_value','deviation_value']],value='',\
		placeholder='bubble_color_property',multi=False,style={'display':'inline-block','width':'200px','margin':'20px'})

	objects['dropdown']['bubble_size_property']=dcc.Dropdown(id='bubble_size_property',\
		options=[{'label':entry,'value':entry} for entry in ['min_value','max_value','deviation_value']],value='',\
		placeholder='bubble_size_property',multi=False,style={'display':'inline-block','width':'200px','margin':'20px'})

	# create required objects
	create_map(objects['dfMap'], 'gis')
	create_table(df, 'table')
	create_graphs(objects,['vmag','freq'],['vmag','freq'],['white','white'],['Time (s)', 'Time (s)'],\
	['Vmag (PU)','f (hz)'])
	create_tab(objects,['gis','table','plots','analytics'],['GIS','Table','Plots','Analytics'])
	create_tabs(objects,'main_tab',[objects['tab']['gis'],objects['tab']['table'],objects['tab']['plots'],\
	objects['tab']['analytics']])

	# define tab objects
	# gis
	objects['tab']['gis'].children=[
		objects['map']['gis'],\
		html.Div(children=[objects['dropdown']['bubble_property'],objects['dropdown']['bubble_color_property'],\
		objects['dropdown']['bubble_size_property']],\
		style={'display':'flex','justifyContent':'end','marginRight':'20px','marginLeft':'20px'})
	]

	# table
	parentDiv=html.Div(children=[objects['table']['table']],style={'width':'100%'})
	objects['tab']['table'].children=[html.Div(children=[parentDiv],\
	style={'display':'flex','flexDirection':'row','alignItems':'space-around','justifyContent':'space-around',\
	'height':'auto','width':'90vw','marginTop':'10vh','marginLeft':'4vw','marginRight':'4vw'})]

	# plots
	objects['graph']['vmag'].style['height']='70vh'
	objects['tab']['plots'].children=[
		html.Div(style={'display':'flex','flexDirection':'column','justifyContent':'space-around'},children=[
			html.Div(children=[objects['dropdown']['scenario'],objects['dropdown']['tnodeid'],\
			objects['dropdown']['dnodeid'],objects['dropdown']['tnodesubid'],objects['dropdown']['property']],
			style={'display':'flex','width':'auto','height':'40px','margin':'20px','justifyContent':'space-between'}),
			html.Div(objects['graph']['vmag'],style={'display':'flex','flexDirection':'column',
			'justifyContent':'end','width':'99%','height':'auto','marginTop':'60px','marginLeft':'10px','marginRight':'5px'})
		])
	]

#=======================================================================================================================
@app.callback([Output('property', 'options'),Output('dnodeid', 'style'),Output('dnodeid', 'options')],\
[Input('tnodeid', 'value')])
def update_plot_filter(tnodeid):
	try:
		currentStyle=objects['dropdown']['dnodeid'].style
		currentStyle['display']='inline-block'
		dnodeid_options=objects['dropdown']['dnodeid'].options
		if tnodeid:
			if len(tnodeid)>1:
				currentStyle.update({'display':'none'})
				dnodeid_options=[{'label':'','value':''}]
			res=[]
			for thisTnodeid in tnodeid:
				if not res:
					res=set(df[df.tnodeid==thisTnodeid].property)
				else:
					res=res.intersection(set(df[df.tnodeid==thisTnodeid].property))

			property_options=[]
			for entry in res:
				property_options.append({'label':entry,'value':entry})
		else:
			property_options=objects['dropdown']['property'].options

		return [property_options,currentStyle,dnodeid_options]
	except:
		raise

#=======================================================================================================================
@app.callback([Output('vmag', 'figure'),Output('vmag', 'style')],\
[Input('scenario', 'value'),Input('tnodeid', 'value'),Input('dnodeid', 'value'),
Input('tnodesubid', 'value'),Input('property', 'value')])
def update_plot(scenario,tnodeid,dnodeid,tnodesubid,prop):
	try:
		df=objects['df']
		df=df[df.t>=0]
		figure=objects['graph']['vmag'].figure
		style=objects['graph']['vmag'].style
		if 'height' in figure['layout']:
			figure['layout'].pop('height')

		if not isinstance(tnodeid,list):
			tnodeid=[tnodeid]

		if scenario:
			df=df[df.scenario==scenario]

		if tnodesubid:
			df=df[df.tnodesubid==tnodesubid[0]]####

		thisData=[]
		if prop:
			df=df[df.property==prop]
			for thisTnodeid in tnodeid:
				filterDF=df[df.tnodeid==thisTnodeid]
				thisData.append({'x':filterDF.t, 'y':filterDF.value, 'type': 'chart','name':thisTnodeid})
			figure['data']=thisData
			figure['layout']['title']='{}'.format(prop.capitalize())
			figure['layout']['xaxis']={'title':'Time (s)'}
			figure['layout']['yaxis']={'title':'{} (PU)'.format(prop.capitalize())}

		return [figure,style]
	except:
		raise

#=======================================================================================================================
@app.callback(Output('mapObj', 'figure'),\
[Input('bubble_property', 'value'),Input('bubble_color_property', 'value'),Input('bubble_size_property', 'value')])
def update_gis(bubble_property,bubble_color_property,bubble_size_property):
	try:
		df=objects['dfMap']
		figure=objects['map']['gis'].figure
		if not bubble_property:
			bubble_property='VOLT'
		if not bubble_color_property:
			bubble_color_property='min_value'
		if not bubble_size_property:
			bubble_size_property='deviation_value'

		mapDF=objects['map']['df_gis']=helper.build_map_df(df,prop=bubble_property)
		figure['data'][0]['customdata']=np.array([[x,y] for x,y in zip(mapDF.tnodeid,mapDF.min_value)])
		figure['data'][0]['hovertext']=figure['data'][0]['customdata'][:,0]
		figure['data'][0]['lat']=mapDF['lat']
		figure['data'][0]['lon']=mapDF['lon']
		figure['data'][0]['marker']['size']=mapDF[bubble_size_property]
		figure['data'][0]['marker']['color']=mapDF[bubble_color_property]

		return figure
	except:
		raise


#======================================================================================================================
if __name__ == '__main__':	
	# http://localhost:8050/

	import sys
	sys.path.insert(0,sys.argv[2])

	from tdcosim.dashboard import Dashboard
	from tdcosim.data_analytics import DataAnalytics

	# # init
	df=pd.read_pickle(sys.argv[1])
	da=DataAnalytics()
	helper=Dashboard()
	helper.add_df('df',df)

	# setup objects
	objects={'graph':{},'tab':{},'tabs':{},'upload':{},'textarea':{},'dropdown':{},'selection':{},'df':{}}
	objects['df']=df
	objects['dfMap'] = helper.add_lat_lon_to_df(df[(df.property=='VOLT')], 'tnodeid')

	# define layout
	gather_objects()
	app.layout=html.Div(objects['tabs']['main_tab'],
	style={'width':'99vw','height':'98vh','background-color':'rgba(0,0,0,.8)'})

	# run
	app.run_server(debug=False,use_reloader=False)


