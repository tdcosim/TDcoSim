import os
import pickle
import pdb

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.express as px
import pandas as pd
import networkx as nx

from tdcosim.dashboard import Dashboard


app = dash.Dash(__name__)
helper=Dashboard()

objects={'graph':{},'tab':{},'tabs':{},'upload':{},'textarea':{},'dropdown':{},'selection':{},'df':{}}
def create_graphs(objects,objID,title,fontColor,xlabel,ylabel):
	for thisObjID,thisTitle,thisFontColor,thisXlabel,thisYlabel in zip(objID,title,fontColor,xlabel,ylabel):
		objects['graph'].update(helper.graph_template(thisObjID))
		objects['graph'][thisObjID].figure['layout']['title']=thisTitle
		objects['graph'][thisObjID].figure['layout']['font']={'color':thisFontColor}
		objects['graph'][thisObjID].figure['layout']['xaxis']={'title':thisXlabel}
		objects['graph'][thisObjID].figure['layout']['yaxis']={'title':thisYlabel}


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
if __name__ == '__main__':
	create_graphs(objects,['vmag','freq'],['vmag','freq'],['white','white'],['Time (s)', 'Time (s)'],\
	['Vmag (PU)','f (hz)'])
	create_tab(objects,['gis','table','analytics'],['GIS','Table','Analytics'])
	create_tabs(objects,'main_tab',[objects['tab']['gis'],objects['tab']['table'],objects['tab']['analytics']])
	objects['tab']['analytics'].children=[
	html.Div(objects['graph']['freq'],style={'display':'inline-block','width':'49.9%','height':'98vh'}),
	html.Div(objects['graph']['vmag'],style={'display':'inline-block','width':'49.9%','padding':'1% 0% 0% .2%',\
	'height':'98vh'})]

	app.layout=html.Div(objects['tabs']['main_tab'],
	style={'width':'99vw','height':'98vh','background-color':'rgba(0,0,0,.8)'})
	# http://localhost:8050/
	app.run_server(debug=True,use_reloader=True)