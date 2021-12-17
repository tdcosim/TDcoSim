import os
import sys
import pickle
import pdb
import time
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import dash_table
import plotly.express as px
import pandas as pd
import networkx as nx
import numpy as np
import dask.dataframe as dd #< 1s overhead
import glob
import six
import tdcosim.data_analytics as da
FONT_AWESOME = "https://use.fontawesome.com/releases/v5.10.2/css/all.css"

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, FONT_AWESOME])

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
def create_table(df, thisObjID):		
	objects['table'] = {
	 thisObjID : helper.table_template(df)	
	}

#=======================================================================================================================
def create_filter(df, thisObjID):
	objects['filter'] = {
	 thisObjID : helper.filter_template(df, 'tnodeid', [])	
	}

#=======================================================================================================================
def create_analytics(objects, df):
	objects['analytics']={}
	analyticstab = helper.analytics_template(objects, df)
	layout = html.Div(id="analyticsdiv", children=[analyticstab])
	return layout

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
	create_tab(objects,['gis','table','plots', 'analytics'],['GIS','Table','Plots','Analytics'])
	create_tabs(objects,'main_tab',[objects['tab']['gis'],objects['tab']['table'],objects['tab']['plots'],objects['tab']['analytics']])

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

	# Analytics
	analyticsdiv = create_analytics(objects, df)
	objects['tab']['analytics'].children=[analyticsdiv]

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
		
		tic = time.time() 
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
		toc = time.time() 
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

#=======================================================================================================================
@app.callback([Output('css1property', 'options')],[Input('css1tnodeid', 'value')])
def update_compare_signal1_plot_filter(tnodeid):
	try:		
		if tnodeid:			
			res=[]			
			res=set(df[df.tnodeid==tnodeid].property)
			property_options=[]
			for entry in res:
				property_options.append({'label':entry,'value':entry})
		else:
			property_options=objects['analytics']['cs']['css1property'].options

		return [property_options]
	except:
		raise

#=======================================================================================================================
@app.callback([Output('css2property', 'options')],
[Input('css2tnodeid', 'value')])
def update_compare_signal2_plot_filter(tnodeid):
	try:
		if tnodeid:			
			res=[]
			res=set(df[df.tnodeid==tnodeid].property)
			property_options=[]
			for entry in res:
				property_options.append({'label':entry,'value':entry})
		else:
			property_options=objects['analytics']['cs']['css2property'].options

		return [property_options]
	except:
		raise

#=======================================================================================================================
@app.callback([Output('csgraph', 'figure'),Output('csgraph', 'style'),
	Output('cslagresult', 'children'),Output('csmseresult', 'children'),Output('sb1seresult', 'children'),Output('sb2seresult', 'children')],
[Input('css1scenario', 'value'),Input('css1tnodeid', 'value'),Input('css1property', 'value'),
Input('css2scenario', 'value'),Input('css2tnodeid', 'value'),Input('css2property', 'value'),
Input('cs_error', 'value')])
def update_compare_signal_result(css1scenario,css1tnodeid,css1prop,css2scenario,css2tnodeid,css2prop, errorthreshhold):
	try:		
		figure=objects['analytics']['cs']['graph'].figure
		style=objects['analytics']['cs']['graph'].style
		lagresult = objects['analytics']['cs']['lagresult'].children
		mseresult = objects['analytics']['cs']['mseresult'].children
		sb1result = objects['analytics']['cs']['sb1result'].children
		sb2result = objects['analytics']['cs']['sb2result'].children

		if 'height' in figure['layout']:
			figure['layout'].pop('height')
		thisData=[]

		df1=objects['df']
		df1=df1[df1.t>=0]

		if css1scenario:
			df1=df1[df1.scenario==css1scenario]

		if css1prop:
			df1=df1[df1.property==css1prop]			
			filterDF=df1[df1.tnodeid==css1tnodeid]
			thisData.append({'x':filterDF.t, 'y':filterDF.value, 'type': 'chart','name':('Signal 1 ' + css1tnodeid)})
			figure['data']=thisData
			figure['layout']['title']='{}'.format(css1prop.capitalize())
			figure['layout']['xaxis']={'title':'Time (s)'}
			figure['layout']['yaxis']={'title':'{} (PU)'.format(css1prop.capitalize())}

		df2=objects['df']
		df2=df2[df2.t>=0]		
		
		if css2scenario:
			df2=df2[df2.scenario==css2scenario]

		if css2prop:
			df2=df2[df2.property==css2prop]			
			filterDF=df2[df2.tnodeid==css2tnodeid]
			thisData.append({'x':filterDF.t, 'y':filterDF.value, 'type': 'chart','name':('Signal 2 ' + css2tnodeid)})
			figure['data']=thisData
			figure['layout']['title']='{}'.format(css2prop.capitalize())
			figure['layout']['xaxis']={'title':'Time (s)'}
			figure['layout']['yaxis']={'title':'{} (PU)'.format(css2prop.capitalize())}

		try:
			if errorthreshhold != None:
				print("Call Compare Signals")				
				result = da.compare_signals(css1tnodeid[0],css2tnodeid[0],df1[df1.tnodeid==css1tnodeid[0]],df2[df2.tnodeid==css2tnodeid[0]],errorthreshhold*0.01,0)				
				print(result)
				lagresult = "{:.4f}".format(result[0]) + " ms"
				mseresult = "{:.4f}".format(result[1])
				if result[2][0] <= 0:
					sb1result = result[2][1]
				else:
					sb1result = "{:.4f}".format(result[2][0]) + " s"
				if result[3][0] <= 0:
					sb2result = result[3][1]
				else:
					sb2result = "{:.4f}".format(result[3][0]) + " s"								
				
		except:
			raise

		return [figure,style, lagresult, mseresult, sb1result, sb2result]
	except:
		raise

#=======================================================================================================================
@app.callback([Output('sts1property', 'options')],[Input('sts1tnodeid', 'value')])
def update_stability_time_plot_filter(tnodeid):
	try:		
		if tnodeid:			
			res=[]			
			res=set(df[df.tnodeid==tnodeid].property)
			property_options=[]
			for entry in res:
				property_options.append({'label':entry,'value':entry})
		else:
			property_options=objects['analytics']['st']['sts1property'].options

		return [property_options]
	except:
		raise

#=======================================================================================================================
@app.callback([Output('stgraph', 'figure'),Output('stgraph', 'style'),
	Output('stsb1seresult', 'children'),Output('stsb2seresult', 'children')],
[Input('sts1scenario', 'value'),Input('sts1tnodeid', 'value'),Input('sts1property', 'value'),
Input('st_error', 'value')])
def update_stability_time_result(css1scenario,css1tnodeid,css1prop,errorthreshhold):
	try:		
		figure=objects['analytics']['st']['graph'].figure
		style=objects['analytics']['st']['graph'].style		
		sb1result = objects['analytics']['st']['sb1result'].children
		sb2result = objects['analytics']['st']['sb2result'].children

		if 'height' in figure['layout']:
			figure['layout'].pop('height')
		thisData=[]

		df1=objects['df']
		df1=df1[df1.t>=0]

		if css1scenario:
			df1=df1[df1.scenario==css1scenario]

		if css1prop:
			df1=df1[df1.property==css1prop]			
			filterDF=df1[df1.tnodeid==css1tnodeid]
			thisData.append({'x':filterDF.t, 'y':filterDF.value, 'type': 'chart','name':('Signal 1 ' + css1tnodeid)})
			figure['data']=thisData
			figure['layout']['title']='{}'.format(css1prop.capitalize())
			figure['layout']['xaxis']={'title':'Time (s)'}
			figure['layout']['yaxis']={'title':'{} (PU)'.format(css1prop.capitalize())}

		try:
			if errorthreshhold != None:
				print("Call Stability Time")				
				result = da.compute_stability_time(df1[df1.tnodeid==css1tnodeid[0]],errorthreshhold*0.01)								
				print(result)
				if result[0] <= 0:
					sb1result = result[1]
				else:
					sb1result = "{:.4f}".format(result[0]) + " s"
				sb2result = "{:.4f}".format(result[2]) + " s"
				
		except:
			raise

		return [figure,style, sb1result, sb2result]
	except:
		raise

#=======================================================================================================================
@app.callback([Output('vcgraph', 'figure'),Output('vcgraph', 'style'),
	Output('vcsb1seresult', 'children')],
[Input('vcs1scenario', 'value'),Input('vcs1tnodeid', 'value'),Input('vcs1property', 'value'),
Input('vc_uplimit', 'value'), Input('vc_lowlimit', 'value')])
def update_stability_time_result(css1scenario,css1tnodeid,css1prop, upperlimit, lowerlimit):
	try:		
		figure=objects['analytics']['vc']['graph'].figure
		style=objects['analytics']['vc']['graph'].style		
		sb1result = objects['analytics']['vc']['sb1result'].children		

		if 'height' in figure['layout']:
			figure['layout'].pop('height')
		thisData=[]

		df1=objects['df']
		df1=df1[df1.t>=0]

		if css1scenario:
			df1=df1[df1.scenario==css1scenario]

		if css1prop:
			df1=df1[df1.property==css1prop]			
			filterDF=df1[df1.tnodeid==css1tnodeid]
			thisData.append({'x':filterDF.t, 'y':filterDF.value, 'type': 'chart','name':('Signal 1 ' + css1tnodeid)})
			figure['data']=thisData
			figure['layout']['title']='{}'.format(css1prop.capitalize())
			figure['layout']['xaxis']={'title':'Time (s)'}
			figure['layout']['yaxis']={'title':'{} (PU)'.format(css1prop.capitalize())}

		try:
			if upperlimit != None and lowerlimit != None:
				print("Call Violation Count")				
				result = da.instances_of_violation(df1[df1.tnodeid==css1tnodeid[0]],upperlimit, lowerlimit)								
				print(result)
				sb1result = "{:.4f}".format(result)
				
				
		except:
			raise

		return [figure,style, sb1result]
	except:
		raise

#=======================================================================================================================
@app.callback([Output('vcs1property', 'options')],[Input('vcs1tnodeid', 'value')])
def update_violation_count_plot_filter(tnodeid):
	try:		
		if tnodeid:			
			res=[]			
			res=set(df[df.tnodeid==tnodeid].property)
			property_options=[]
			for entry in res:
				property_options.append({'label':entry,'value':entry})
		else:
			property_options=objects['analytics']['vc']['vcs1property'].options

		return [property_options]
	except:
		raise

#======================================================================================================================
operators = [['ge ', '>='],
             ['le ', '<='],
             ['lt ', '<'],
             ['gt ', '>'],
             ['ne ', '!='],
             ['eq ', '='],
             ['contains '],
             ['datestartswith ']]

def split_filter_part(filter_part):
	for operator_type in operators:
		for operator in operator_type:
			if operator in filter_part:
				name_part, value_part = filter_part.split(operator, 1)
				name = name_part[name_part.find('{') + 1: name_part.rfind('}')]

				value_part = value_part.strip()
				v0 = value_part[0]
				if (v0 == value_part[-1] and v0 in ("'", '"', '`')):
					value = value_part[1: -1].replace('\\' + v0, v0)
				else:
					try:
						value = float(value_part)
					except ValueError:
						value = value_part

				# word operators need spaces after them in the filter string,
				# but we don't want these later
				return name, operator_type[0].strip(), value

	return [None] * 3


@app.callback(
	Output('myTable', 'data'),
	Output('myTable', 'page_count'),
	Input('myTable', "page_current"),
	Input('myTable', "page_size"),
	Input('myTable', 'sort_by'),
	Input('myTable', 'filter_query'))
def update_table(page_current, page_size, sort_by, filter):
	filtering_expressions = filter.split(' && ')
	df = objects['df']
	dff = df
	for filter_part in filtering_expressions:
		col_name, operator, filter_value = split_filter_part(filter_part)

		if operator in ('eq', 'ne', 'lt', 'le', 'gt', 'ge'):
			# these operators match pandas series operator method names
			dff = dff.loc[getattr(dff[col_name], operator)(filter_value)]
		elif operator == 'contains':
			dff = dff.loc[dff[col_name].str.contains(filter_value)]
		elif operator == 'datestartswith':
			# this is a simplification of the front-end filtering logic,
			# only works with complete fields in standard format
			dff = dff.loc[dff[col_name].str.startswith(filter_value)]

	if len(sort_by):
		dff = dff.sort_values(
			[col['column_id'] for col in sort_by],
			ascending=[
				col['direction'] == 'asc'
				for col in sort_by
			],
			inplace=False
		)

	page = page_current
	size = page_size

	totalrow = len(dff.index)
	pagesize = page_size
	pagecount = int(totalrow / pagesize) + 1

	return dff.iloc[page * size: (page + 1) * size].to_dict('records'), pagecount

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
	
	tic = time.time()
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
		_ = [pickleFileNames.extend(glob.glob(os.path.join(sys.argv[1],simulationFolder,"df_pickle.pkl"))) for simulationFolder in simulationFolders if "df_pickle.csv" not in os.listdir(os.path.join(sys.argv[1],simulationFolder))]
		print("Directory:{} contains total {} files ({} CSV files + {} Pickle files with no corresponding CSV files)".format(sys.argv[1],len(csvFileNames)+len(pickleFileNames),len(csvFileNames),len(pickleFileNames)))
		
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
					dfs.append(pd.concat([pd.read_csv(csvFileName,dtype={'tnodesubid': 'object','tnodeid':'object','dfeederid':'object','dnodeid':'object','t':'float32','value':'float32'}) for csvFileName in csvFileNames],ignore_index=True))
				if pickleFileNames:
					print("Concatenating {} Pickle files into a single data frame using Pandas...".format(len(pickleFileNames)))
					dfs.append(pd.concat(map(pd.read_pickle, pickleFileNames), ignore_index=True))
				
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
	toc = time.time()
	print("Time taken to load and process dataframe:{:.2f} s".format(toc - tic))
	# run
	app.run_server(debug=False,use_reloader=False)
