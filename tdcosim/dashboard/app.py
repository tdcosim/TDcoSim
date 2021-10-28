import os
import sys
import pickle
import pdb
import time
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table
import plotly.express as px
import pandas as pd
import networkx as nx
import numpy as np
import dask.dataframe as dd
import glob
app = dash.Dash(__name__)


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
	multi=['tnodeid','tnodesubid','dnodeid','scenario'])

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
	df = objects['df']
	
	if isinstance(df,dd.core.DataFrame):
		df = objects['df_scenario'] #Only show one scenario in table when using Dask
	
	create_table(df, 'table')
	create_graphs(objects,['vmag','freq'],['vmag','freq'],['white','white'],['Time (s)', 'Time (s)'],\
	['Vmag (PU)','f (hz)'])
	create_tab(objects,['gis','table','plots'],['GIS','Table','Plots'])
	create_tabs(objects,'main_tab',[objects['tab']['gis'],objects['tab']['table'],objects['tab']['plots']])

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
					if isinstance(df,dd.core.DataFrame):
						res=set(list(objects['df_temp'][objects['df_temp'].tnodeid==thisTnodeid].property.unique()))
					else:
						res=set(df[df.tnodeid==thisTnodeid].property)
				else:
					if isinstance(df,dd.core.DataFrame):
						res=res.intersection(set(list(objects['df_temp'][objects['df_temp'].tnodeid==thisTnodeid].property.unique())))
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
		if not isinstance(scenario,list):
			scenario=[scenario]
		
		if tnodesubid:
			df=df[df.tnodesubid==tnodesubid[0]]####
		tic = time.clock()
		thisData=[]
		if prop:
			if isinstance(df,dd.core.DataFrame):
				df_temp=df[(df.property==prop) & (df.tnodeid.isin(tnodeid)) & (df.scenario.isin(scenario))].compute()
			else:
				df=df[df.property==prop]
			for thisTnodeid in tnodeid:
				for thisScenario in scenario:
					if isinstance(df,dd.core.DataFrame):
						filterDF=df_temp[(df_temp.tnodeid==thisTnodeid) & (df_temp.scenario==thisScenario)]
					else:
						filterDF=df[(df.tnodeid==thisTnodeid) & (df.scenario==thisScenario)]
					thisData.append({'x':filterDF.t, 'y':filterDF.value, 'type': 'chart','name':"{}_{}".format(thisTnodeid,thisScenario)})
					
			figure['data']=thisData
			figure['layout']['title']='{}'.format(prop.capitalize())
			figure['layout']['xaxis']={'title':'Time (s)'}
			figure['layout']['yaxis']={'title':'{} (PU)'.format(prop.capitalize())}
		toc = time.clock()
		print("Time taken to process dataframe:{:.2f} s".format(toc - tic))

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
	nFiles = int(sys.argv[4])
	useDask = sys.argv[5]
	
	tic = time.clock()
	if os.path.isfile(sys.argv[1]):
		print("{} is a file.".format(sys.argv[1]))
		if '.pkl' in sys.argv[1]:
			df=pd.read_pickle(sys.argv[1])
		elif '.csv' in sys.argv[1]:
			df=pd.read_csv(sys.argv[1])
		else:
			df=pd.read_pickle(sys.argv[1]) #Assume that df is saved as a pickle file by default.
	
	elif os.path.isdir(sys.argv[1]):
		csvFileNames = []
		pickleFileNames = []
		simulationFolders = os.listdir(sys.argv[1])
		print('Directory:{} contains {} simulation folders'.format(sys.argv[1],len(simulationFolders)))
		
		_ = [csvFileNames.extend(glob.glob(os.path.join(sys.argv[1],simulationFolder,"df_pickle.csv"))) for simulationFolder in simulationFolders]
		print("Directory:{} contains {} CSV files!".format(sys.argv[1],len(csvFileNames),sys.argv[4]))
		_ = [pickleFileNames.extend(glob.glob(os.path.join(sys.argv[1],simulationFolder,"df_pickle.pkl"))) for simulationFolder in simulationFolders if "df_pickle.csv" not in os.listdir(os.path.join(sys.argv[1],simulationFolder))]
		print("Directory:{} contains {} Pickle files with no corresponding CSV files!".format(sys.argv[1],len(pickleFileNames),sys.argv[4]))
		
		if csvFileNames + pickleFileNames:
			if len(csvFileNames) < nFiles:
				pickleFileNames = pickleFileNames[0:nFiles-len(csvFileNames)] #Priority is for CSV files
			else:
				pickleFileNames = []
			csvFileNames = csvFileNames[0:nFiles] #First n CSV files
			print("First {} CSV files and {} Pickle files will be read.".format(len(csvFileNames),len(pickleFileNames)))
			dfs = []
			if useDask.lower()=="false" or not useDask: #Check if user wants to use Dask
				if csvFileNames:
					print("Concatenating {} CSV files into a single data frame using Pandas...".format(len(csvFileNames)))
					#dfs.extend(pd.concat(map(pd.read_csv, csvFileNames), ignore_index=True))
					dfs.append(pd.concat([pd.read_csv(csvFileName,dtype={'tnodesubid': 'object','tnodeid':'object','dfeederid':'object','dnodeid':'object','t':'float32','value':'float32'}) for csvFileName in csvFileNames],ignore_index=True))
				if pickleFileNames:
					print("Concatenating {} Pickle files into a single data frame using Pandas...".format(len(pickleFileNames)))
					dfs.append(pd.concat([pd.read_pickle(pickleFileName,dtype={'tnodesubid': 'object','tnodeid':'object','dfeederid':'object','dnodeid':'object','t':'float32','value':'float32'}) for pickleFileName in pickleFileNames],ignore_index=True))
				
				df= pd.concat(dfs, ignore_index=True)
				
				print("Dataframe shape:{}".format(df.shape))
			else:
				if csvFileNames:
					print("Concatenating {} CSV files into a single data frame using Dask...".format(len(csvFileNames)))
					df = dd.read_csv(csvFileNames,dtype={'tnodesubid': 'object','tnodeid':'object','dfeederid':'object','dnodeid':'object','t':'float32','value':'float32'})
					#dfs = [dd.read_csv(csvFileName,dtype={'tnodesubid': 'object','tnodeid':'object','dfeederid':'object','dnodeid':'object','t':'float32','value':'float32'}) for csvFileName in csvFileNames]
					#df = dd.concat(dfs) #Another option
				if pickleFileNames:
					print("Pickle files will not be read using dask")
				
		else:
			raise NotImplementedError("No CSV or Pickle files were found!")
	else:
		raise ValueError("Only folder names or file names are accepted")
	toc = time.clock()
	print("Time taken to load CSV/Pickle files into dataframe:{:.2f} s".format(toc - tic))
	
	tic = time.clock()
	if sys.argv[3].lower()=="true":# reduced memory
		df=df[df.dfeederid.isna()]
	da=DataAnalytics()
	helper=Dashboard()
	# setup objects
	objects={'graph':{},'tab':{},'tabs':{},'upload':{},'textarea':{},'dropdown':{},'selection':{},'df':{}}
	
	if isinstance(df,dd.core.DataFrame):
		objects['df_temp'] = df[(df.t>0.0) & (df.t<=0.01)].compute()
		objects['scenariosFound'] = list(objects['df_temp'].scenario.unique())
		helper.add_df('df',objects['df_temp'])
	else:
		objects['scenariosFound'] = list(df.scenario.unique())
		helper.add_df('df',df)
	print("Following scenarios were found from the CSV and Pickle files:{}".format(objects['scenariosFound']))
	
	objects['df']=df
	
	if isinstance(df,dd.core.DataFrame):
		objects['df_scenario'] = df[df.scenario==objects['scenariosFound'][0]].compute()
		objects['dfMap'] = helper.add_lat_lon_to_df(objects['df_scenario'][objects['df_scenario'].property=='VOLT'], 'tnodeid')
	else:
		objects['dfMap'] = helper.add_lat_lon_to_df(df[(df.property=='VOLT') & (df.scenario==objects['scenariosFound'][0])], 'tnodeid')
	# define layout
	gather_objects()
	app.layout=html.Div(objects['tabs']['main_tab'],
	style={'width':'99vw','height':'98vh','background-color':'rgba(0,0,0,.8)'})
	toc = time.clock()
	print("Time taken to process dataframe:{:.2f} s".format(toc - tic))
	# run
	app.run_server(debug=False,use_reloader=False)
