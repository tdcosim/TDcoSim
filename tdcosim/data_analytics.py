from __future__ import division
import json
import logging
import pdb
import os
import sys
import inspect

pssePath="C:\Program Files (x86)\PTI\PSSE33\PSSBIN"
sys.path.append(pssePath)
import dyntools
import pandas as pd
import matplotlib.pyplot as plt


class DataAnalytics(object):

	def __init__(self):
		self.__legend=[]
		return None

#===================================================================================================
	def dict2df(self,data,scenarioid='1',inputType='outfile'):
		try:
			if inputType.lower()=='tdcosim':
				df=self._dict2df_tdcosim(data=data,scenarioid=scenarioid)
			elif inputType.lower()=='outfile':
				df=self._dict2df_outfile(data=data,scenarioid=scenarioid)
			elif inputType.lower()=='tdcosim-excel':
				df=self._excel2df_tdcosim(data=data,scenarioid=scenarioid)

			return df
		except Exception as e:
			logging.error(e)

#===================================================================================================
	def _dict2df_tdcosim(self,data,scenarioid='1'):
		try:
			df=pd.DataFrame(columns=['scenario','t','tnodeid','dfeederid','dnodeid','property',
			'value'])

			t_all=list(data['TNet']['Dynamic'].keys())
			t_all.sort()
			t=[]; tnodeid=[]; dfeederid=[]; dnodeid=[]; prop=[]; val=[]

			for thisT in t_all:
				for node in data['TNet']['Dynamic'][thisT]['S']:
					t.append(thisT)
					val.append(data['TNet']['Dynamic'][thisT]['S'][node]['P'])
					prop.append('P')
					tnodeid.append(node)
					t.append(thisT)
					val.append(data['TNet']['Dynamic'][thisT]['S'][node]['Q'])
					prop.append('Q')
					tnodeid.append(node)
					t.append(thisT)
					val.append(data['TNet']['Dynamic'][thisT]['V'][node])
					prop.append('Vmag')
					tnodeid.append(node)

			df.loc[:,'t']=t; df.loc[:,'tnodeid']=tnodeid
			df.loc[:,'property']=prop; df.loc[:,'value']=val
			df.loc[:,'scenario']=scenarioid
			df.t=df.t.map(lambda x:float(x))

			return df
		except Exception as e:
			logging.error(e)

#===================================================================================================
	def _excel2df_tdcosim(self,data,scenarioid='1',tag='test'):
		try:
			df=pd.DataFrame(columns=['scenarioid','tag','time','busid','dnodeid','property','phase','value'])
			t_all= list(data.keys())
			t_all.remove('TNet_results')
            
			t_all.sort()
			print(t_all)
			t=[]; tnodeid=[]; dfeederid=[]; dnodeid=[]; prop=[]; val=[]; phase =[]
            
			for tnode in t_all:                
				vmag = data[tnode].filter(regex='tfr',axis=1).filter(regex='vmag',axis=1) 
				vang = data[tnode].filter(regex='tfr',axis=1).filter(regex='vang',axis=1)
				vmag_list = list(vmag.columns)
				vang_list = list(vang.columns)
                
				v_dict = {node:{'node':node.strip('vmagang_tfr_bc'),'phase':node[-1],'property':node[0:4]} for node in vmag_list+vang_list}

				for node_id in list(vmag.columns):
					i = 0
					for thisT in data[tnode]['time']:
						t.append(thisT)
						val.append(vmag[node_id][i])
						prop.append(v_dict[node_id]['property'])
						phase.append(v_dict[node_id]['phase'])
						dnodeid.append(v_dict[node_id]['node'])
						tnodeid.append(tnode)
						i = i+1
            
			df.loc[:,'time']=t; df.loc[:,'busid']=tnodeid; df.loc[:,'dnodeid']=dnodeid
			df.loc[:,'property']=prop; df.loc[:,'value']=val;df.loc[:,'phase']=phase
			df.loc[:,'scenarioid']=scenarioid
			df.loc[:,'tag']=['test']*len(df.time)
			df.time=df.time.map(lambda x:float(x))
            
			return df
		except Exception as e:
			logging.error(e)
            
#===================================================================================================
	def _dict2df_outfile(self,data,scenarioid='1',simType='tonly'):
		try:
			outfile = data # path to file
			if simType=='tonly':
				stride=1
			elif simType=='cosim':
				stride=2

			PSSE_VERSION=self.psse_version()
			if not PSSE_VERSION:
				PSSE_VERSION='33'
			if PSSE_VERSION=='33':
				chnfobj = dyntools.CHNF(outfile,0)
				_, ch_id, ch_data = chnfobj.get_data()
			elif PSSE_VERSION=='35':
				chnfobj = dyntools.CHNF(outfile,outvrsn=0)
				_, ch_id, ch_data = chnfobj.get_data()

			symbols=[ch_id[entry] for entry in ch_id]
			properties=list(set([ch_id[entry].split(' ')[0] for entry in ch_id]))
			nodes=list(set([ch_id[entry].split(' ')[1][0:ch_id[entry].split(' ')[1].find(
			'[')].replace(' ','') for entry in ch_id if 'Time' not in ch_id[entry]]))

			tnodeid=[]; props=[]; value=[]; t=[]; count=0
			for entry in ch_id:
				if 'Time' not in ch_id[entry]:
					prop_node=ch_id[entry].split()
					prop,node=prop_node[0],prop_node[1]
					if prop!='VOLT':
						node=node[0:node.find('[')].replace(' ','')
					value.extend(ch_data[entry][0::stride])
					props.extend([prop]*len(ch_data[entry][0::stride]))
					tnodeid.extend([node]*len(ch_data[entry][0::stride]))
					count+=1
			t.extend(ch_data['time'][0::stride]*count)

			df=pd.DataFrame(columns=['scenario','t','tnodeid','dfeederid','dnodeid','property',
			'value'])
			df['t'],df['tnodeid'],df['property'],df['value']=t,tnodeid,props,value
			df['scenario']=[scenarioid]*len(t)

			return df
		except Exception as e:
			logging.error(e)

#===================================================================================================
	def filter_time(self,df,fromTime,toTime=None):
		try:
			filteredDF=df[(df.t>=fromTime)&(df.t<=toTime)]

			return filteredDF
		except Exception as e:
			logging.error(e)

#===================================================================================================
	def filter_node(self,df,tnodeid,dfeederid=None,dnodeid=None):
		"""Filter the data frame based on node.
		P.S. The query is run in the following manner,
		for any tnode in tnodeid and any feeder in dfeederid and any dnode in dnodeid. In other words,
		each element of input argument list has an or condition and each input argument is an and
		condition."""
		try:
			if not isinstance(tnodeid,list):
				tnodeid=list(tnodeid)

			filteredDF=df[df.tnodeid==tnodeid[0]]

			for thisNode in tnodeid[1::]:
				filteredDF.append(df[df.tnodeid==tnodeid[0]],ignore_index=True)

			if dfeederid:
				for thisdfeeder in dfeederid:
					filteredDF=filteredDF[filteredDF.dfeederid==thisdfeeder]

			if dnodeid:
				for thisdnode in dnodeid:
					filteredDF=filteredDF[filteredDF.dnodeid==thisdnode]

			filteredDF.index=range(len(filteredDF))

			return filteredDF
		except Exception as e:
			logging.error(e)

#===================================================================================================
	def filter_property(self,df,propertyid):
		try:
			assert isinstance(propertyid,list)

			for thisproperty in propertyid:
				filteredDF=df[df.property==thisproperty]

			return filteredDF
		except Exception as e:
			logging.error(e)

#===================================================================================================
	def filter_value(self,df,fromValue,toValue):
		"""Filter the given data frame based on >= and <= condition. For == condition use the same
		value for fromValue and toValue."""
		try:
			filteredDF=df[(df.value>=fromValue)&(df.value<=toValue)]

			return filteredDF
		except Exception as e:
			logging.error(e)

#===================================================================================================
	def filter_scenario(self,df,scenarioid):
		try:
			filteredDF=df[df.scenario==scenarioid]

			return filteredDF
		except Exception as e:
			logging.error(e)

#===================================================================================================
	def add_plot(self,df,propertyid,labelType='tnodeid'):
		try:
			thisDF=df[df.property==propertyid]
			thisDF=thisDF.sort_values(by='t',ascending=True)
			plt.plot(thisDF.t,thisDF.value)
			self.__legend.extend(list(set(thisDF[labelType])))
		except Exception as e:
			logging.error(e)

#===================================================================================================
	def clear_plot(self):
		try:
			plt.clf()
		except Exception as e:
			logging.error(e)

#===================================================================================================
	def show_plot(self,ylabel,title):
		try:
			plt.xlabel('Time (s)')
			plt.ylabel(ylabel)
			plt.title(title)
			plt.legend(self.__legend)
			plt.show()
			self.__legend=[]
		except Exception as e:
			logging.error(e)

#==================================================================================
	def psse_version(self):
		try:
			psseDir=os.path.dirname(inspect.getfile(dyntools))
			psseVersion=''
			for version in ['33','34','35']:
				if os.path.exists(psseDir+os.path.sep+'psse{}.py'.format(version)):
					psseVersion=version
					break
			return psseVersion
		except Exception as e:
			logging.error(e)
