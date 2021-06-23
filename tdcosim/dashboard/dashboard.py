import pdb

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table


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

