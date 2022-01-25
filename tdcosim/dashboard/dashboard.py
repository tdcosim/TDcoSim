import pdb

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import numpy as np
import math
import plotly.express as px
import pandas as pd


class Dashboard(object):
	def __init__(self):
		self.df={}
		self.currentDF=None
		self._obj={}
		self.colortheme = 0
		self.colorobj = ['rgba(0,0,0,.8)', 'white', 'black']
#=======================================================================================================================
	def set_color(self, flag):
		self.colortheme = flag
		if self.colortheme == 0:
			self.colorobj = ['rgba(0,0,0,.8)', 'white', 'black']
		elif self.colortheme == 1:
			self.colorobj = ['white', 'black', 'white']

#=======================================================================================================================
	def add_df(self,id,df):
		try:
			self.df[id]=df
			self.currentDF=self.df[id]
		except:
			LogUtil.exception_handler()

#=======================================================================================================================
	def graph_template(self,id,track=False,**kwargs):
		try:
			figure={'data': [{'x': [], 'y': [], 'type': 'chart'}],
			'layout':{'height':'10vh','plot_bgcolor': self.colorobj[2],'paper_bgcolor': self.colorobj[2]}}

			if 'figure' in kwargs:
				figure.update(kwargs['figure'])
				newData={}
			else:
				newData=kwargs

			res={}
			res[id]=dcc.Graph(id=id,figure=figure,style={},**newData)
			if track:
				if 'graph' not in self._obj:
					self._obj['graph']={}
				if id not in self._obj['graph']:
					self._obj['graph'][id]=res

			return res
		except:
			LogUtil.exception_handler()

#=======================================================================================================================
	def tab_template(self,id,children):
		try:
			res={}
			childrenData=[dcc.Tab(label=thisID) for thisID in children]
			res[id]=dcc.Tabs(id=id,children=childrenData)
			return res
		except:
			LogUtil.exception_handler()

#=======================================================================================================================
	def update_children(self,parentObj,children):
		try:
			for thisChildID in children:
				for thisChildEntry in parentObj.children:
					if thisChildEntry.label==thisChildID:
						for item in children[thisChildID]:
							thisChildEntry.__dict__[item].children=children[thisChildID]
						break
		except:
			LogUtil.exception_handler()

#=======================================================================================================================
	def filter_dropdown(self,columnFilter=['tnodeid','property','scenario'],id=None,multi=['tnodeid']):
		try:
			if not id:
				id=columnFilter
			dropdown={}
			width='{}vw'.format(int((90/len(columnFilter))-1))
			if isinstance(self.currentDF,pd.DataFrame):
				options={thisID:[{'label':entry,'value':entry} for entry in set(self.currentDF[thisFilter]\
				[-self.currentDF[thisFilter].isna()])] for thisFilter,thisID in zip(columnFilter,id)}

				dropdown={thisID:dcc.Dropdown(id=thisID,options=options[thisID],value='',\
				placeholder=thisFilter,multi=False,style={'display':'inline-block','width':width}) \
				for thisFilter,thisID in zip(columnFilter,id)}

				for entry in multi:
					dropdown[entry].multi=True # allow multiselect of nodes

				if 'selectCase' in dropdown:
					dropdown['selectCase']=dcc.Dropdown(id='selectCase',\
						options=[{'label':entry,'value':entry} for entry in self.df],value='')

			return dropdown
		except:
			raise

#=======================================================================================================================
	def generate_lat_lon(self,nPts,latMin=33,latMax=44,lonMin=-115,lonMax=-80):
		try:
			res={}
			res['lat']=np.array([np.random.random()*(latMax-latMin)+latMin for entry in range(nPts)])
			res['lon']=np.array([np.random.random()*(lonMax-lonMin)+lonMin for entry in range(nPts)])

			return res
		except:
			raise

#=======================================================================================================================
	def add_lat_lon_to_df(self,df,uniqueColumnID):
		try:
			if 'lat' not in df.columns:
				df=df.assign(lat=[0]*df.shape[0])
			if 'lon' not in df.columns:
				df=df.assign(lon=[0]*df.shape[0])

			for entry in set(df[uniqueColumnID]):
			 	res=self.generate_lat_lon(nPts=1)
			 	tempd = df[df[uniqueColumnID]==entry].copy()
			 	df.loc[df[uniqueColumnID]==entry, 'lat'] = [res['lat'][0] for i in range(tempd.shape[0])]
			 	df.loc[df[uniqueColumnID]==entry, 'lon'] = [res['lon'][0] for i in range(tempd.shape[0])]

			return df
		except:
			raise

#=======================================================================================================================
	def build_map_df(self,df,prop='VOLT'):
		res={'tnodeid':[],'lat':[],'lon':[],'min_value':[],'max_value':[],'deviation_value':[]}
		df=df[df.property==prop]
		for thisTnode in set(df.tnodeid):
			res['tnodeid'].append(thisTnode)
			res['lat'].append(df[df.tnodeid==thisTnode].lat.values[0])
			res['lon'].append(df[df.tnodeid==thisTnode].lon.values[0])
			thisMin=df[df.tnodeid==thisTnode].value.min()
			res['min_value'].append(thisMin)
			thisMax=df[df.tnodeid==thisTnode].value.max()
			res['max_value'].append(thisMax)
			res['deviation_value'].append(thisMax-thisMin)
		newDF=pd.DataFrame(res)
		return newDF

#=======================================================================================================================
	def map_template(self, df,radarOverlay=True,color='min_value',size='deviation_value'):
		myMap = px.scatter_mapbox(		
			data_frame=df, 
			lat="lat", 
			lon="lon", 
			hover_name="tnodeid", 
			hover_data=["tnodeid","min_value"],
			color=color,
			color_continuous_scale="twilight",#icefire, mint, twilight
			size=size,
			zoom=3
#			width=2400,
#			height=600
			)
			#color_discrete_sequence=["fuchsia"], 

		myMap.update_layout(mapbox_style='stamen-toner')
		myMap.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

		if radarOverlay:
			myMap.update_layout(mapbox_layers=[
				{
				"sourcetype": "raster",
				"sourceattribution": "Government of Canada",
				"source": ["https://geo.weather.gc.ca/geomet/?"
						"SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&BBOX={bbox-epsg-3857}&CRS=EPSG:3857"
						"&WIDTH=1000&HEIGHT=1000&LAYERS=RADAR_1KM_RDBR&TILED=true&FORMAT=image/png"],
				}])

		mapObj=dcc.Graph(id="mapObj",figure=myMap,clear_on_unhover=True, style={"width": "97vw", "height":"65vh",\
		'display':'inline-block', 'vertical-align':'top', 'margin':'20px 1vw 20px 1vw'})
		return mapObj

#=======================================================================================================================
	def table_template(self, df):
		totalrow = len(df.index)
		pagesize = 20
		pagecount = int(totalrow / pagesize) + 1
		myTable = dash_table.DataTable(
			id='myTable',
			columns=[{"name": i, "id": i} for i in df.columns],
			# data=df.to_dict('records'),
			editable=False,
			filter_action='custom',
			filter_query='',
			sort_action='custom',
			sort_mode='multi',
			sort_by=[],
			selected_columns=[],
			selected_rows=[],
			page_action="custom",
			page_current= 0,
			page_size= pagesize,
			page_count= pagecount,
			style_data_conditional=[
			{'if': {'row_index': 'odd'},'backgroundColor': 'rgb(248, 248, 248)'},
			{'if': {'row_index': 'even'},'backgroundColor': 'grey','color':"white"}],
			style_header={'backgroundColor': 'rgb(200, 200, 200)','fontWeight': 'bold','fontSize':20})		
		return myTable

#=======================================================================================================================
	def update_filter(self, df, uniqueColumnID, selectednode):
		tnodeids = set(df[uniqueColumnID])
		unselectedchildren = []
		selectedchildren = []
		columnoptions = []
		for node in tnodeids:
			node = str(node)
			if node in selectednode:
				selectedchildren.append(
					html.Option(value=str(node), children=[node])
					)
			else:
				unselectedchildren.append(
					html.Option(value=str(node), children=[node])
					)

		return unselectedchildren, selectedchildren, columnoptions

#=======================================================================================================================
	def filter_template(self, objects, tabkey, df, objid):

		columnFilter=['scenario','tnodeid','property']				
		childrenform = []

		objids = []
		for x in columnFilter:			
			objids.append(str(tabkey+objid+x))
		
		width='{}vw'.format(int((70/len(columnFilter))-1))

		for thisFilter,thisID in zip(columnFilter,objids):
			option = [{'label':entry,'value':entry} for entry in set(df[thisFilter][-self.currentDF[thisFilter].isna()])]

			objects['analytics'][tabkey][thisID]=dcc.Dropdown(id=thisID,options=option,value='',
					placeholder=thisFilter,multi=False,style={'display':'inline-block','width':width}) 			
			childrenform.append(objects['analytics'][tabkey][thisID])

		return childrenform

#=======================================================================================================================
	def analytics_template(self, objects, df):

		cstab = self.compare_signals_template(objects, df)
		sttab = self.stability_time_template(objects, df)
		vctab = self.violation_count_template(objects, df)

		title = html.H1(children="Data Analytics", style={'color':self.colorobj[1],'fontWeight':'bold'})
		tabs = dcc.Tabs(id="inner_analytics_tabs",children=[cstab, sttab, vctab])
		layoutdiv = html.Div(id="analyticsTemplate", children=[title, tabs])
		return layoutdiv

#=======================================================================================================================
	def compare_signals_template(self, objects, df):
		objects['analytics']['cs']={}

		s1filters=self.filter_template(objects, 'cs', df, 's1')			

		s1tooltip = self.tooltip_template("Select Signal 1 that you want to compare", 
			{'display':'inline-block', 'color':self.colorobj[1], 'marginRight':'5px'},
			'css1tooltip'
			)
		s1title = html.H2(children="Signal 1:", style={'display':'inline-block', 'color':self.colorobj[1],'fontWeight':'bold','marginRight':'20px'})		
		s1children = [s1tooltip, s1title]
		for x in s1filters:
			s1children.append(x)

		s1div = html.Div(children=s1children, style={'display':'block', 'marginTop': '10px', 'marginLeft': '10px', 'verticalAlign': 'middle'})

		s2filters=self.filter_template(objects, 'cs', df, 's2')			

		s2tooltip = self.tooltip_template("Select Signal 2 that you want to compare", 
			{'display':'inline-block', 'color':self.colorobj[1], 'marginRight':'5px'},
			'css2tooltip'
			)
		s2title = html.H2(children="Signal 2:", style={'display':'inline-block', 'color':self.colorobj[1],'fontWeight':'bold','marginRight':'20px'})		
		s2children = [s2tooltip, s2title]
		for x in s2filters:
			s2children.append(x)

		s2div = html.Div(children=s2children, style={'display':'block', 'marginTop': '10px', 'marginLeft': '10px', 'verticalAlign': 'middle'})


		err=dcc.Input(
				id="cs_error",
				type="number",
				placeholder="Error threshold (%)",
				style={'display':'inline-block', 'width': '20vw',}
			)
		objects['analytics']['cs']['err'] = err
		errtooltip = self.tooltip_template("Error threshold for stability time calculations. Maximum allowed signal deviation after stability time", 
				{'display':'inline-block', 'color':self.colorobj[1], 'marginRight':'5px'},
				'cserrtooltip'
			)
		errtitle = html.H2(children="Error threshold (%):", style={'display':'inline-block', 'color':self.colorobj[1],'fontWeight':'bold','marginRight':'20px'})		
		errdiv = html.Div(children=[errtooltip,errtitle,err], style={'display':'block', 'marginTop': '10px', 'marginLeft': '10px', 'verticalAlign': 'middle'})

		hr = html.Hr(style={'color':self.colorobj[1]})

		lagtooltip = self.tooltip_template("Delay between signals 1 and 2", 
				{'display':'inline-block', 'color':self.colorobj[1], 'marginRight':'5px'},
				'cslagtooltip'
			)
		lagtitle = html.H2(children="Lag", style={'display':'inline-block', 'color':self.colorobj[1],'fontWeight':'bold','marginRight':'20px'})		
		lagresult = html.H2(id='cslagresult', children="0.00 ms", style={'display':'block', 'color':self.colorobj[1],'fontWeight':'bold'})
		objects['analytics']['cs']['lagresult'] = lagresult
		lagdiv = html.Div(children=[lagtooltip,lagtitle,lagresult], style={'display':'block', 'marginTop': '10px', 'marginLeft': '10px', 'verticalAlign': 'middle'})

		msetooltip = self.tooltip_template("Mean Square Error between signals 1 and 2", 
				{'display':'inline-block', 'color':self.colorobj[1], 'marginRight':'5px'},
				'csmsetooltip'
			)
		msetitle = html.H2(children="Mean square error", style={'display':'inline-block', 'color':self.colorobj[1],'fontWeight':'bold','marginRight':'20px'})		
		mseresult = html.H2(id='csmseresult', children="0.00", style={'display':'block', 'color':self.colorobj[1],'fontWeight':'bold'})
		objects['analytics']['cs']['mseresult'] = mseresult
		msediv = html.Div(children=[msetooltip,msetitle,mseresult], style={'display':'block', 'marginTop': '10px', 'marginLeft': '10px', 'verticalAlign': 'middle'})

		sb1tooltip = self.tooltip_template("Time it takes for the signal 1 to stabilize after disturbance", 
				{'display':'inline-block', 'color':self.colorobj[1], 'marginRight':'5px'},
				'cssb1tooltip'
			)
		sb1title = html.H2(children="Stability time for signal 1", style={'display':'inline-block', 'color':self.colorobj[1],'fontWeight':'bold','marginRight':'20px'})		
		sb1result = html.H2(id='sb1seresult', children="0.00 s", style={'display':'block', 'color':self.colorobj[1],'fontWeight':'bold'})
		objects['analytics']['cs']['sb1result'] = sb1result
		sb1div = html.Div(children=[sb1tooltip,sb1title,sb1result], style={'display':'block', 'marginTop': '10px', 'marginLeft': '10px', 'verticalAlign': 'middle'})

		sb2tooltip = self.tooltip_template("Time it takes for the signal 2 to stabilize after disturbance", 
				{'display':'inline-block', 'color':self.colorobj[1], 'marginRight':'5px'},
				'cssb2tooltip'
			)
		sb2title = html.H2(children="Stability time for signal 2", style={'display':'inline-block', 'color':self.colorobj[1],'fontWeight':'bold','marginRight':'20px'})		
		sb2result = html.H2(id='sb2seresult', children="0.00 ms", style={'display':'block', 'color':self.colorobj[1],'fontWeight':'bold'})
		objects['analytics']['cs']['sb2result'] = sb2result
		sb2div = html.Div(children=[sb2tooltip,sb2title,sb2result], style={'display':'block', 'marginTop': '10px', 'marginLeft': '10px', 'verticalAlign': 'middle'})

		graphobj = self.graph_template('csgraph')
		graph = graphobj['csgraph']
		graph.figure['layout']['title']='Compare Signals'
		graph.figure['layout']['font']={'color':self.colorobj[1]}
		graph.figure['layout']['xaxis']={'title':'Time (s)'}
		graph.figure['layout']['yaxis']={'title':'TBD'}
		objects['analytics']['cs']['graph'] = graph
		
		resultdiv = html.Div(children=[lagdiv, msediv, sb1div, sb2div,], style={'display':'inline-block', 'marginTop': '10px', 'marginLeft': '10px'})
		graphdiv = html.Div(children=[graph], style={'display':'inline-block', 'marginTop': '10px','marginLeft': '10px', 'width':'60vw','height':'auto'})


		tabcontents = html.Div(id="compare_signals_div", children=[s1div, s2div, errdiv, hr, resultdiv, graphdiv])
		style={'backgroundColor':self.colorobj[2],'color':self.colorobj[1],'fontWeight':'bold','fontSize':'1em'}
		selected_style={'backgroundColor':'grey','color':self.colorobj[1],'fontWeight':'bold','fontSize':'1em'}
		tab = dcc.Tab(id="compare_signals_tab",label="Compare Signals",style=style,selected_style=selected_style, children=[tabcontents])
		return tab

#=======================================================================================================================
	def stability_time_template(self, objects, df):
		objects['analytics']['st']={}

		s1filters=self.filter_template(objects, 'st', df, 's1')			

		s1tooltip = self.tooltip_template("Select Signal 1 that you want to compare", 
			{'display':'inline-block', 'color':self.colorobj[1], 'marginRight':'5px'},
			'sts1tooltip'
			)
		s1title = html.H2(children="Signal 1:", style={'display':'inline-block', 'color':self.colorobj[1],'fontWeight':'bold','marginRight':'20px'})		
		s1children = [s1tooltip, s1title]
		for x in s1filters:
			s1children.append(x)

		s1div = html.Div(children=s1children, style={'display':'block', 'marginTop': '10px', 'marginLeft': '10px', 'verticalAlign': 'middle'})		

		err=dcc.Input(
				id="st_error",
				type="number",
				placeholder="Error threshold (%)",
				style={'display':'inline-block', 'width': '20vw',}
			)
		objects['analytics']['st']['err'] = err
		errtooltip = self.tooltip_template("Error threshold for stability time calculations. Maximum allowed signal deviation after stability time", 
				{'display':'inline-block', 'color':self.colorobj[1], 'marginRight':'5px'},
				'sterrtooltip'
			)
		errtitle = html.H2(children="Error threshold (%):", style={'display':'inline-block', 'color':self.colorobj[1],'fontWeight':'bold','marginRight':'20px'})		
		errdiv = html.Div(children=[errtooltip,errtitle,err], style={'display':'block', 'marginTop': '10px', 'marginLeft': '10px', 'verticalAlign': 'middle'})

		hr = html.Hr(style={'color':self.colorobj[1]})
		
		sb1tooltip = self.tooltip_template("Time it takes for the signal 1 to stabilize after disturbance", 
				{'display':'inline-block', 'color':self.colorobj[1], 'marginRight':'5px'},
				'stsb1tooltip'
			)
		sb1title = html.H2(children="Stability time for signal 1", style={'display':'inline-block', 'color':self.colorobj[1],'fontWeight':'bold','marginRight':'20px'})		
		sb1result = html.H2(id='stsb1seresult', children="0.00 s", style={'display':'block', 'color':self.colorobj[1],'fontWeight':'bold'})
		objects['analytics']['st']['sb1result'] = sb1result
		sb1div = html.Div(children=[sb1tooltip,sb1title,sb1result], style={'display':'block', 'marginTop': '10px', 'marginLeft': '10px', 'verticalAlign': 'middle'})

		sb2tooltip = self.tooltip_template("Difference between maximum and minimum signal value after stability", 
				{'display':'inline-block', 'color':self.colorobj[1], 'marginRight':'5px'},
				'stsb2tooltip'
			)
		sb2title = html.H2(children="Maximum deviation after stability", style={'display':'inline-block', 'color':self.colorobj[1],'fontWeight':'bold','marginRight':'20px'})		
		sb2result = html.H2(id='stsb2seresult', children="0.00 s", style={'display':'block', 'color':self.colorobj[1],'fontWeight':'bold'})
		objects['analytics']['st']['sb2result'] = sb2result
		sb2div = html.Div(children=[sb2tooltip,sb2title,sb2result], style={'display':'block', 'marginTop': '10px', 'marginLeft': '10px', 'verticalAlign': 'middle'})

		graphobj = self.graph_template('stgraph')
		graph = graphobj['stgraph']
		graph.figure['layout']['title']='Signal 1'
		graph.figure['layout']['font']={'color':self.colorobj[1]}
		graph.figure['layout']['xaxis']={'title':'Time (s)'}
		graph.figure['layout']['yaxis']={'title':'TBD'}
		objects['analytics']['st']['graph'] = graph
		
		resultdiv = html.Div(children=[sb1div, sb2div], style={'display':'inline-block', 'marginTop': '10px', 'marginLeft': '10px'})
		graphdiv = html.Div(children=[graph], style={'display':'inline-block', 'marginTop': '10px','marginLeft': '10px', 'width':'60vw','height':'auto'})



		tabcontents = html.Div(id="stability_time_div", children=[s1div, errdiv, hr, resultdiv, graphdiv])
		style={'backgroundColor':self.colorobj[2],'color':self.colorobj[1],'fontWeight':'bold','fontSize':'1em'}
		selected_style={'backgroundColor':'grey','color':self.colorobj[1],'fontWeight':'bold','fontSize':'1em'}
		tab = dcc.Tab(id="stability_time_tab",label="Stability Time",style=style,selected_style=selected_style, children=[tabcontents])
		return tab

#=======================================================================================================================
	def violation_count_template(self, objects, df):
		objects['analytics']['vc']={}

		s1filters=self.filter_template(objects, 'vc', df, 's1')			

		s1tooltip = self.tooltip_template("Select Signal 1 that you want to compare", 
			{'display':'inline-block', 'color':self.colorobj[1], 'marginRight':'5px'},
			'vcs1tooltip'
			)
		s1title = html.H2(children="Signal 1:", style={'display':'inline-block', 'color':self.colorobj[1],'fontWeight':'bold','marginRight':'20px'})		
		s1children = [s1tooltip, s1title]
		for x in s1filters:
			s1children.append(x)

		s1div = html.Div(children=s1children, style={'display':'block', 'marginTop': '10px', 'marginLeft': '10px', 'verticalAlign': 'middle'})		

		vcuplimit=dcc.Input(
				id="vc_uplimit",
				type="number",
				placeholder="Upper limit",
				style={'display':'inline-block', 'width': '20vw',}
			)
		objects['analytics']['vc']['uplimit'] = vcuplimit
		vcuplimittooltip = self.tooltip_template("Maximum allowed signal value", 
				{'display':'inline-block', 'color':self.colorobj[1], 'marginRight':'5px'},
				'vcuplimittooltip'
			)
		vcuplimittitle = html.H2(children="Upper limit:", style={'display':'inline-block', 'color':self.colorobj[1],'fontWeight':'bold','marginRight':'20px'})		
		vcuplimitdiv = html.Div(children=[vcuplimittooltip,vcuplimittitle,vcuplimit], style={'display':'block', 'marginTop': '10px', 'marginLeft': '10px', 'verticalAlign': 'middle'})

		vclowlimit=dcc.Input(
				id="vc_lowlimit",
				type="number",
				placeholder="Upper limit",
				style={'display':'inline-block', 'width': '20vw',}
			)
		objects['analytics']['vc']['lowlimit'] = vclowlimit
		vclowlimittooltip = self.tooltip_template("Minimum allowed signal value", 
				{'display':'inline-block', 'color':self.colorobj[1], 'marginRight':'5px'},
				'vclowlimittooltip'
			)
		vclowlimittitle = html.H2(children="Lower limit:", style={'display':'inline-block', 'color':self.colorobj[1],'fontWeight':'bold','marginRight':'20px'})		
		vclowlimitdiv = html.Div(children=[vclowlimittooltip,vclowlimittitle,vclowlimit], style={'display':'block', 'marginTop': '10px', 'marginLeft': '10px', 'verticalAlign': 'middle'})

		hr = html.Hr(style={'color':self.colorobj[1]})
		
		sb1tooltip = self.tooltip_template("Number of times signal value increased more than upper limit and decreased lower than lower limit", 
				{'display':'inline-block', 'color':self.colorobj[1], 'marginRight':'5px'},
				'vcsb1tooltip'
			)
		sb1title = html.H2(children="Number of violations", style={'display':'inline-block', 'color':self.colorobj[1],'fontWeight':'bold','marginRight':'20px'})		
		sb1result = html.H2(id='vcsb1seresult', children="0", style={'display':'block', 'color':self.colorobj[1],'fontWeight':'bold'})
		objects['analytics']['vc']['sb1result'] = sb1result
		sb1div = html.Div(children=[sb1tooltip,sb1title,sb1result], style={'display':'block', 'marginTop': '10px', 'marginLeft': '10px', 'verticalAlign': 'middle'})

		graphobj = self.graph_template('vcgraph')
		graph = graphobj['vcgraph']
		graph.figure['layout']['title']='Signal 1'
		graph.figure['layout']['font']={'color':self.colorobj[1]}
		graph.figure['layout']['xaxis']={'title':'Time (s)'}
		graph.figure['layout']['yaxis']={'title':'TBD'}
		objects['analytics']['vc']['graph'] = graph
		
		resultdiv = html.Div(children=[sb1div], style={'display':'inline-block', 'marginTop': '10px', 'marginLeft': '10px'})
		graphdiv = html.Div(children=[graph], style={'display':'inline-block', 'marginTop': '10px','marginLeft': '10px', 'width':'60vw','height':'auto'})



		tabcontents = html.Div(id="violation_count_div", children=[s1div, vcuplimitdiv, vclowlimitdiv, hr, resultdiv, graphdiv])
		style={'backgroundColor':self.colorobj[2],'color':self.colorobj[1],'fontWeight':'bold','fontSize':'1em'}
		selected_style={'backgroundColor':'grey','color':self.colorobj[1],'fontWeight':'bold','fontSize':'1em'}
		tab = dcc.Tab(id="violation_count_tab",label="Violation Count",style=style,selected_style=selected_style, children=[tabcontents])
		return tab

#=======================================================================================================================
	def tooltip_template(self, text, styleobj, objid):
		tooltip = html.Div(
		    [
		        html.I(className="fas fa-question-circle fa-lg", id=objid, title=text),
		    ],
		    style=styleobj
		)
		return tooltip
