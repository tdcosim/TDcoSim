import os
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

from tdcosim.dashboard import Dashboard


app = dash.Dash(__name__)
PIQIDIR=os.path.dirname(os.path.abspath(__file__))
PIQIDIR=PIQIDIR + "\\vizsample"
print(PIQIDIR)
df=pd.read_csv(open(os.path.join(PIQIDIR,'dataframe.csv')),compression=None)
helper=Dashboard()
df = helper.add_lat_lon_to_df(df, 'tnodeid')
print('mapdf')


objects={'graph':{},'tab':{},'tabs':{},'upload':{},'textarea':{},'dropdown':{},'selection':{},'df':{}}
def create_graphs(objects,objID,title,fontColor,xlabel,ylabel):
	for thisObjID,thisTitle,thisFontColor,thisXlabel,thisYlabel in zip(objID,title,fontColor,xlabel,ylabel):
		objects['graph'].update(helper.graph_template(thisObjID))
		objects['graph'][thisObjID].figure['layout']['title']=thisTitle
		objects['graph'][thisObjID].figure['layout']['font']={'color':thisFontColor}
		objects['graph'][thisObjID].figure['layout']['xaxis']={'title':thisXlabel}
		objects['graph'][thisObjID].figure['layout']['yaxis']={'title':thisYlabel}

def create_map(df, thisObjID):	
	objects['map'] = {
	 thisObjID : helper.map_template(df)	
	}
def create_table(df, thisObjID):	
	objects['table'] = {
	 thisObjID : helper.table_template(df)	
	}

def create_filter(df, thisObjID):
	objects['filter'] = {
	 thisObjID : helper.filter_template(df, 'tnodeid', [])	
	}

def create_tab(objects,objID,label,style=None,selected_style=None):
	if not style:
		style={'backgroundColor':'rgba(50,255,0,.6)','color':'white','fontWeight':'bold','fontSize':'1em'}
	if not selected_style:
		selected_style={'backgroundColor':'rgba(0,90,155,.6)','color':'white','fontWeight':'bold','fontSize':'1em'}
	
	for thisObjID,thisLabel in zip(objID,label):
		objects['tab'][thisObjID]=dcc.Tab(id=thisObjID,label=thisLabel,style=style,selected_style=selected_style)

def create_tabs(objects,objID,children):
	objects['tabs'][objID]=dcc.Tabs(id=objID,children=children)


#======================================================================================================================
create_map(df, 'gis')
create_table(df, 'table')
create_filter(df, 'filter')
create_graphs(objects,['vmag','freq'],['vmag','freq'],['white','white'],['Time (s)', 'Time (s)'],\
['Vmag (PU)','f (hz)'])

create_tab(objects,['gis','table','analytics'],['GIS','Table','Analytics'])

create_tabs(objects,'main_tab',[objects['tab']['gis'],objects['tab']['table'],objects['tab']['analytics']])
objects['tab']['gis'].children=[
	objects['map']['gis']
]
objects['tab']['table'].children=[
	objects['table']['table']
]
objects['tab']['analytics'].children=[
objects['filter']['filter'],
html.Div(objects['graph']['freq'],style={'display':'inline-block','width':'49.9%','height':'98vh'}),
html.Div(objects['graph']['vmag'],style={'display':'inline-block','width':'49.9%','padding':'1% 0% 0% .2%',\
'height':'98vh'})]

app.layout=html.Div(objects['tabs']['main_tab'],
style={'width':'99vw','height':'98vh','background-color':'rgba(0,0,0,.8)'})

#======================================================================================================================
@app.callback(	
		Output('unselectednodesel', 'children'),
		Output('selectednodesel', 'children'),
		Output('columndrop', 'options'),
		Input('addbtn', 'n_clicks'),
		Input('removebtn', 'n_clicks'),
		Input('unselectednodesel', 'children'),
		Input('selectednodesel', 'children'),
		prevent_initial_call=True 
	)
def click_addbtn(addn_clicks, remove_clicks, unselectoptions, selectedoptions):		
	changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
	selectednode = []
	if 'addbtn' in changed_id:	
		for x in selectedoptions:		
			selectednode.append(x['props']['value'])
		for x in unselectoptions:		
			if 'n_clicks' in x['props']:
				selectednode.append(x['props']['value'])
		addbtnclick = addn_clicks
	elif 'removebtn' in changed_id:
		for x in selectedoptions:
			if 'n_clicks' not in x['props']:	
				selectednode.append(x['props']['value'])
		removebtnclick = remove_clicks
			

	unselectedchildren, selectedchildren, columnoptions = helper.update_filter(df, 'tnodeid', selectednode)

	return unselectedchildren, selectedchildren, columnoptions



#======================================================================================================================
if __name__ == '__main__':	
	# http://localhost:8050/
	app.run_server(debug=True,use_reloader=True)
