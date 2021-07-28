import pdb

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import numpy as np
import math
import plotly.express as px


class Dashboard(object):
	def __init__(self):
		self.df={}
		self.currentDF=None
		self._obj={}

	def add_df(self,id,df):
		try:
			self.df[id]=df
			self.currentDF=self.df[id]
		except:
			LogUtil.exception_handler()

	def graph_template(self,id,track=False,**kwargs):
		try:
			figure={'data': [{'x': [], 'y': [], 'type': 'chart'}],
			'layout':{'height':'100vh','plot_bgcolor': "black",'paper_bgcolor': "black"}}

			if 'figure' in kwargs:
				figure.update(kwargs['figure'])
				newData={}
			else:
				newData=kwargs

			res={}
			res[id]=dcc.Graph(id=id,figure=figure,**newData)
			if track:
				if 'graph' not in self._obj:
					self._obj['graph']={}
				if id not in self._obj['graph']:
					self._obj['graph'][id]=res

			return res
		except:
			LogUtil.exception_handler()

	def tab_template(self,id,children):
		try:
			res={}
			childrenData=[dcc.Tab(label=thisID) for thisID in children]
			res[id]=dcc.Tabs(id=id,children=childrenData)
			return res
		except:
			LogUtil.exception_handler()

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

	def filter_dropdown(self,columnFilter=['nodeid','property','scenario'],multi=['nodeid']):
		try:
			dropdown={}
			if isinstance(self.currentDF,pd.DataFrame):
				options={thisFilter:[{'label':entry,'value':entry} for entry in set(self.currentDF[thisFilter][-self.currentDF[thisFilter].isna()])] for thisFilter in columnFilter}
				dropdown={thisFilter:dcc.Dropdown(id=thisFilter,options=options[thisFilter],value='',\
				placeholder=thisFilter,multi=False,style={'display':'inline-block','width':'25%'}) \
				for thisFilter in columnFilter}

				for entry in multi:
					dropdown[entry].multi=True # allow multiselect of nodes

				if 'selectCase' in dropdown:
					dropdown['selectCase']=dcc.Dropdown(id='selectCase',\
						options=[{'label':entry,'value':entry} for entry in self.df],value='')

			return dropdown
		except:
			LogUtil.exception_handler()
	def generate_lat_lon(self,nPts,latMin=33,latMax=44,lonMin=-115,lonMax=-80):
		try:
			res={}
			res['lat']=np.array([np.random.random()*(latMax-latMin)+latMin for entry in range(nPts)])
			res['lon']=np.array([np.random.random()*(lonMax-lonMin)+lonMin for entry in range(nPts)])

			return res
		except:
			raise

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
	def map_template(self, df):
		myMap = px.scatter_mapbox(		
			data_frame=df, 
			lat="lat", 
			lon="lon", 
			hover_name=None, 
			hover_data=["tnodeid"],
			color_discrete_sequence=["fuchsia"], 
			zoom=3,
			width=900,
			height=300	
			)

		myMap.update_layout(mapbox_style='stamen-toner')
		myMap.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
		mapObj=dcc.Graph(id="mapObj",figure=myMap,clear_on_unhover=True, style={"width": "48vw", "height":"30vh",'display':'inline-block', 'vertical-align':'top', 'padding':'20px 0vw .5vh .5vw'})
		return mapObj

	def table_template(self, df):
		myTable = dash_table.DataTable(
			id='myTable',
			columns=[{"name": i, "id": i} for i in df.columns],
			data=df.to_dict('records'),
			editable=False,
			filter_action="native",
			sort_action="native",
			sort_mode="multi",		
			selected_columns=[],
			selected_rows=[],
			page_action="native",
			page_current= 0,
			page_size= 14,
			style_data_conditional=[
			{'if': {'row_index': 'odd'},'backgroundColor': 'rgb(248, 248, 248)'},
			{'if': {'row_index': 'even'},'backgroundColor': 'rgba(0, 0, 0,.9)','color':"white"}],
			style_header={'backgroundColor': 'rgb(200, 200, 200)','fontWeight': 'bold','fontSize':20})
		return myTable
	
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
	def filter_template(self, df, uniqueColumnID, selectednode):
		unselectedchildren, selectedchildren, columnoptions = self.update_filter(df, uniqueColumnID, selectednode)

		unselectednode = html.Select(multiple=True, id="unselectednodesel", children=unselectedchildren)
		nodeaddbtn = html.Button("==>", id='addbtn')
		noderemovebtn = html.Button("<==", id='removebtn')
		selectednode = html.Select(multiple=True, id="selectednodesel", children=selectedchildren)
		columndrop = dcc.Dropdown(id="columndrop",options=columnoptions)
		div = html.Div([
			unselectednode,
			nodeaddbtn,
			noderemovebtn,
			selectednode,
			columndrop
			])
		return div

