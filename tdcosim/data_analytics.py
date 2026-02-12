from __future__ import division
import json
import logging
import pdb
import os
import sys
import inspect

#import psspy
#import dyntools
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import six
import win32api


class DataAnalytics(object):
	
	voltage_mag_ph_a_property = 'Vmag_a'
	voltage_mag_ph_b_property = 'Vmag_b'
	voltage_mag_ph_c_property = 'Vmag_c'

	def __init__(self):
		self.__legend=[]
		self.__propertyInfo={
			'ANGL':'rotor angle of machine',
			'PLOD':'real power demand',
			'PMEC':'mechanical power input to machine',
			'POWR':'real power output of machine',
			'QLOD':'reactive power demand',
			'SPD':'omega of machine',
			'VARS':'reactive power output of machine',
			'VOLT':'voltage magnitude of transmission bus',
			'Vang_a':'phase a voltage magnitude of distribution node',
			'Vang_b':'phase b voltage magnitude of distribution node',
			'Vang_c':'phase c voltage magnitude of distribution node',
			'Vang_a':'phase a voltage angle of distribution node',
			'Vang_b':'phase b voltage angle of distribution node',
			'Vang_c':'phase c voltage angle of distribution node',
			'der_P':'real power output of der at a given distribution node',
			'der_Q':'reactive power output of der at a given distribution node',
			'der_p_total':'total real power output of der at a given transmission node',
			'der_q_total':'total reactive power output of der at a given transmission node'
		}

		return None

#===================================================================================================
	def get_simulation_result(self,folderPath):
		"""Will load T&D co-simulation results.
		folderPath -- path to folder where the generated output results are stored."""
		try:
			folderPath=win32api.GetLongPathName(os.path.abspath(folderPath))
			assert os.path.exists(folderPath),"{} does not exist".format(folderPath)
			df=pd.read_pickle(os.path.join(folderPath,'df_pickle.pkl'))

			return df
		except:
			raise

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
		except:
			raise

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
		except:
			raise

#===================================================================================================
	def _excel2df_tdcosim(self,data,scenarioid='1',tag='test'):
		try:
			df=pd.DataFrame(columns=['scenario','tag','t','tnodeid','dfeederid','dnodeid','property','phase','value'])
			t_all= list(data.keys())
			t_all.remove('TNet_results')
			
			t_all.sort()
			print('List of DER feeders:{}'.format(t_all))
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
			
			df.loc[:,'time']=t; df.loc[:,'tnodeid']=tnodeid; df.loc[:,'dnodeid']=dnodeid
			df.loc[:,'property']=prop; df.loc[:,'value']=val;df.loc[:,'phase']=phase
			df.loc[:,'scenarioid']=scenarioid
			df.loc[:,'tag']=['test']*len(df.time)
			df.time=df.time.map(lambda x:float(x))
			
			return df
		except:
			raise
			
#===================================================================================================
	def _dict2df_outfile(self,data,scenarioid='1',simType='tonly'):
		try:
			outfile = data # path to file
			outfile=outfile.encode('ascii')
			assert os.path.exists(outfile),"{} does not exist".format(outfile)

			if simType=='tonly':
				stride=1
			elif simType=='cosim':
				stride=2

			# psseVersion=psspy.psseversion()[1]
			# if psseVersion==33:
			# 	chnfobj = dyntools.CHNF(outfile,0)
			# 	_, ch_id, ch_data = chnfobj.get_data()
			# elif psseVersion==35:
			# 	chnfobj = dyntools.CHNF(outfile,outvrsn=0)
			# 	_, ch_id, ch_data = chnfobj.get_data()

			symbols=[ch_id[entry] for entry in ch_id]
			properties=list(set([ch_id[entry].split(' ')[0] for entry in ch_id]))
			nodes=list(set([ch_id[entry].split(' ')[1][0:ch_id[entry].split(' ')[1].find(
			'[')].replace(' ','') for entry in ch_id if 'Time' not in ch_id[entry]]))

			tnodeid=[]; tnodesubid=[]; props=[]; value=[]; t=[]; count=0
			for entry in ch_id:
				if 'Time' not in ch_id[entry]:
					prop_node=ch_id[entry].split()
					prop,node=prop_node[0],prop_node[1]
					if prop!='VOLT':
						tnodesubid.append(node[node.find(']')+1::].strip())
						node=node[0:node.find('[')].replace(' ','')
					else:
						tnodesubid.append('')
					value.extend(ch_data[entry][0::stride])
					props.extend([prop]*len(ch_data[entry][0::stride]))
					tnodeid.extend([node]*len(ch_data[entry][0::stride]))
					count+=1
			t.extend(ch_data['time'][0::stride]*count)

			df=pd.DataFrame(columns=['scenario','t','tnodeid','tnodesubid','dfeederid','dnodeid','property',
			'value'])
			df['t'],df['tnodeid'],df['tnodesubid'],df['property'],df['value']=t,tnodeid,tnodesubid,props,value
			df['scenario']=[scenarioid]*len(t)

			return df
		except:
			raise

#===================================================================================================
	def get_min_max_voltage_der(self,df):
		"""Returns dictionary containing information of minimum and maximum dnode voltage magnitudes."""
		try:
			voltage_dict_der ={'min':{},'max':{}}
			tnodeids = self.get_tnodeids(df)

			for tnodeid in tnodeids:
				dnodeids = df[df.tnodeid==tnodeid]['dnodeid'].dropna().unique() #Get dnodeids corresponding to tnodeid if they exist
				
				if  len(dnodeids)>=1: #Check if  of dnodes are available
					print('Distribution system with {} D nodes detected for T node:{}'.format(len(dnodeids),tnodeid))
					voltage_dict_der['min'].update({tnodeid:{}})
					voltage_dict_der['max'].update({tnodeid:{}})
					min_index = df[(df.property==self.voltage_mag_ph_a_property)&(df.tnodeid==tnodeid)]['value'].idxmin() #Get index of minimum dnode voltage value
					print('Minimum voltage {:.2f} V pu found at dnode {} at time {} s'.format(df.loc[min_index].value,df.loc[min_index].dnodeid,df.loc[min_index].t))
					
					max_index = df[(df.property==self.voltage_mag_ph_a_property)&(df.tnodeid==tnodeid)]['value'].idxmax() #Get index of maximum dnode voltage value
					print('Maximum voltage {:.2f} V pu found at dnode {} at time {} s'.format(df.loc[max_index].value,df.loc[max_index].dnodeid,df.loc[max_index].t))
					
					voltage_dict_der['min'][tnodeid].update({'voltage':df.loc[min_index].value})
					voltage_dict_der['min'][tnodeid].update({'property':df.loc[min_index].property})
					voltage_dict_der['min'][tnodeid].update({'time':df.loc[min_index].t})
					voltage_dict_der['min'][tnodeid].update({'tnodeid':df.loc[min_index].tnodeid})
					voltage_dict_der['min'][tnodeid].update({'dnodeid':df.loc[min_index].dnodeid})
					
					voltage_dict_der['max'][tnodeid].update({'voltage':df.loc[max_index].value})
					voltage_dict_der['max'][tnodeid].update({'time':df.loc[max_index].t})
					voltage_dict_der['max'][tnodeid].update({'tnodeid':df.loc[max_index].tnodeid})
					voltage_dict_der['max'][tnodeid].update({'dnodeid':df.loc[max_index].dnodeid})
					
					voltage_dict_der['min'][tnodeid].update({'df':df[(df.tnodeid==tnodeid) & (df.dnodeid ==df.loc[min_index].dnodeid)]})
					voltage_dict_der['max'][tnodeid].update({'df':df[(df.tnodeid==tnodeid) & (df.dnodeid ==df.loc[max_index].dnodeid)]})
					
			return voltage_dict_der
		except:
			raise

#===================================================================================================
	def get_tnodeids(self,df):
		"""Returns dictionary with bus names and distribution nodes"""
		try:
			tnodeids = list(df.groupby('tnodeid').nunique().index)
			print('Number of buses detected in dataframe:{}'.format(len(tnodeids)))
			return tnodeids
		except:
			raise

#===================================================================================================
	def get_dnodeids_der(self,df):
		"""Returns dictionary with bus names and distribution nodes"""
		try:
			tnodeids = self.get_tnodeids(df)
			dnodeid_dict ={}
			for tnodeid in tnodeids:
				dnodeid_dict.update({tnodeid:list(df[df.tnodeid==tnodeid].groupby('dnodeid').nunique().index)})
			return dnodeid_dict
		except:
			raise

#===================================================================================================
	def get_time_values(self,df):
		"""Returns list of time"""
		try:
			dnodeid_dict = self.get_dnodeids_der(df)
			if six.PY2:
				time_values = df[df.dnodeid==dnodeid_dict[dnodeid_dict.keys()[0]][0]].time
			elif six.PY3:
				time_values = df[df.dnodeid==dnodeid_dict[list(dnodeid_dict.keys())[0]][0]].time
			return time_values
		except:
			raise

#===================================================================================================
	def filter_time(self,df,fromTime,toTime=None):
		try:
			filteredDF=df[(df.t>=fromTime)&(df.t<=toTime)]

			return filteredDF
		except:
			raise

#===================================================================================================
	def filter_node(self,df,tnodeid,dfeederid=None,dnodeid=None):
		"""Filter the data frame based on node.
		P.S. The query is run in the following manner,
		for any tnode in tnodeid and any feeder in dfeederid and any dnode in dnodeid. In other words,
		each element of input argument list has an or condition and each input argument is an and
		condition."""
		try:
			if not isinstance(tnodeid,list):
				tnodeid=[tnodeid]

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
		except:
			raise

#===================================================================================================
	def filter_property(self,df,propertyid):
		try:
			assert isinstance(propertyid,list)

			for thisproperty in propertyid:
				filteredDF=df[df.property==thisproperty]

			return filteredDF
		except:
			raise

#===================================================================================================
	def filter_value(self,df,fromValue,toValue):
		"""Filter the given data frame based on >= and <= condition. For == condition use the same
		value for fromValue and toValue."""
		try:
			filteredDF=df[(df.value>=fromValue)&(df.value<=toValue)]

			return filteredDF
		except:
			raise

#===================================================================================================
	def filter_scenario(self,df,scenarioid):
		try:
			filteredDF=df[df.scenario==scenarioid]

			return filteredDF
		except:
			raise

#===================================================================================================
	def add_plot(self,df,propertyid,labelType='tnodeid'):
		try:
			thisDF=df[df.property==propertyid]
			thisDF=thisDF.sort_values(by='t',ascending=True)
			plt.plot(thisDF.t,thisDF.value)
			self.__legend.extend(list(set(thisDF[labelType])))
		except:
			raise

#===================================================================================================
	def clear_plot(self):
		try:
			plt.clf()
		except:
			raise

#===================================================================================================
	def show_plot(self,ylabel,title):
		try:
			plt.xlabel('Time (s)')
			plt.ylabel(ylabel)
			plt.title(title)
			plt.legend(self.__legend)
			plt.show()
			self.__legend=[]
		except:
			raise

#===================================================================================================
	def get_net_load(self,df,tnodeid,simType='tonly',tfr=True,nodeOffset=None):
		try:
			df_=df[(df.tnodeid==tnodeid)&(df.t>=0.0)]
			res={'p':[],'q':[],'t':[]}

			for subID in set(df_.tnodesubid):
				if isinstance(res['p'],list):
					if not df_[(df_.property=='PLOD')&(df_.tnodesubid==subID)].value.empty:
						res['p']=df_[(df_.property=='PLOD')&(df_.tnodesubid==subID)].value.values
						res['q']=df_[(df_.property=='QLOD')&(df_.tnodesubid==subID)].value.values
						res['t']=df_[(df_.property=='PLOD')&(df_.tnodesubid==subID)].t.values
				else:
					if not df_[(df_.property=='PLOD')&(df_.tnodesubid==subID)].value.empty:
						res['p']+=df_[(df_.property=='PLOD')&(df_.tnodesubid==subID)].value.values
						res['q']+=df_[(df_.property=='QLOD')&(df_.tnodesubid==subID)].value.values

			if simType=='tonly':
				if tfr:
					tnodeid='{}'.format(int(tnodeid)+nodeOffset)
				df=df[(df.tnodeid==tnodeid)&(df.t>=0.0)]
				df=df[(df.property=='POWR')|(df.property=='VARS')]
				for subID in set(df.tnodesubid):
					res['p']-=df[(df.property=='POWR')&(df.tnodesubid==subID)].value.values
					res['q']-=df[(df.property=='VARS')&(df.tnodesubid==subID)].value.values

			return res
		except:
			raise

#===================================================================================================
	def get_der_data(self,df):
		try:
			df_der_slice=df[(df.property.str.startswith('der'))|(df.property.str.endswith('der'))]
			return df_der_slice
		except:
			raise

#===================================================================================================
	def get_transmission_data(self,df):
		try:
			df_transmission_slice=df[-df.dfeederid.notna()]
			return df_transmission_slice
		except:
			raise

#===================================================================================================
	def get_distribution_data(self,df):
		try:
			df_distribution_slice=df[df.dfeederid.notna()]
			return df_distribution_slice
		except:
			raise

#===================================================================================================
	def get_distribution_der_data(self,df,tnodeid=None):
		try:
			df=self.get_distribution_data(df)
			if tnodeid:
				df=df[df.tnodeid==tnodeid]
			df=df[(df.property=='der_P')|(df.property=='der_q')|\
			(df.property=='der_p_total')|(df.property=='der_q_total')]
			return df
		except:
			raise

#===================================================================================================
	def plot_distribution_der_data(self,df,tnodeid=None,plotDerTotal=True):
		try:
			df=self.get_distribution_der_data(df,tnodeid)
			if plotDerTotal:
				props=['der_p_total','der_q_total']
			else:
				props=['der_P','der_Q']

			for n in range(len(props)):
				legend=[]
				for thisTnodeid in set(df.tnodeid):
					df_temp=df[(df.property==props[n])&(df.tnodeid=='{}'.format(thisTnodeid))]
					plt.plot(df_temp.t,df_temp.value)
					plt.xlabel('Time (s)')
					if props[n]=='der_P' or props[n]=='der_p_total':
						plt.ylabel('Mw')
					elif props[n]=='der_Q' or props[n]=='der_q_total':
						plt.ylabel('Mvar')
					legend.append('bus_{}'.format(thisTnodeid))
				plt.legend(legend)
				plt.show()
		except:
			raise

#===================================================================================================
	def get_property_info(self,qry):
		"""Get the property info for elements of df.property.
		Sample call: da.get_property_info('der_p_total')"""
		try:
			res={}
			if qry in self.__propertyInfo:
				res={qry:self.__propertyInfo[qry]}
			else:
				res={'error':'property not found, available properties: {}'.format(\
				self.__propertyInfo.keys())}
			return res
		except:
			raise

#===================================================================================================
	def query(self,df,columnName,condition,value):
		"""Sample call: da.query(df,[['tnodeid','tnodeid']],[['eq','eq']],[['41','42']])
		da.query(df,['tnodeid','property','value'],['eq','eq','ge'],['41','VOLT',.95])"""
		try:
			for thisColumnName,thisCondition,thisValue in zip(columnName,condition,value):
				if not isinstance(thisColumnName,list):
					thisColumnName=[thisColumnName]
					thisCondition=[thisCondition]
					thisValue=[thisValue]
				assert type(thisColumnName)==type(thisCondition)==type(thisValue)
				assert len(thisColumnName)==len(thisCondition)==len(thisValue)

				flag=[False]*df.shape[0]
				for thisSubColumnName,thisSubCondition,thisSubValue in \
				zip(thisColumnName,thisCondition,thisValue):
					if thisSubCondition=='eq':
						flag=flag|df[thisSubColumnName].eq(thisSubValue)
					elif thisSubCondition=='ne':
						flag=flag|df[thisSubColumnName].ne(thisSubValue)
					elif thisSubCondition=='ge':
						flag=flag|df[thisSubColumnName].ge(thisSubValue)
					elif thisSubCondition=='le':
						flag=flag|df[thisSubColumnName].le(thisSubValue)
				df=df[flag]

			return df
		except:
			raise

#===================================================================================================
	def plot_omega(self,df,excludeNodes=None):
		try:
			df=df[df.property=='SPD']
			legend=[]
			for thisNode in set(df.tnodeid):
				if not thisNode == excludeNodes:
					thisDF=df[df.tnodeid==thisNode]
					plt.plot(thisDF.t,thisDF.value)
					legend.append(thisNode)
			plt.legend(legend)
			plt.xlabel('Time (s)')
			plt.ylabel('Freq (hz)')
			plt.show()
		except:
			raise

#===================================================================================================
	def plot_t_vmag(self,df,tnodeid=None,excludeNodes=None):
		try:
			df=df[df.property=='VOLT']
			legend=[]
			if not tnodeid:
				tnodeid=set(df.tnodeid)
			if not isinstance(tnodeid,list):
				tnodeid=[tnodeid]
			for thisNode in tnodeid:
				if not thisNode == excludeNodes:
					thisDF=df[df.tnodeid==thisNode]
					plt.plot(thisDF.t,thisDF.value)
					legend.append(thisNode)
			plt.legend(legend)
			plt.xlabel('Time (s)')
			plt.ylabel('Vmag (PU)')
			plt.show()
		except:
			raise

#===================================================================================================
	def plot_t_delayed_voltage_recovery(self,df,distClearTime,tThreshold,vThreshold,excludeNodes=None):
		try:
			df=df[df.property=='VOLT']
			df_=df[df.t>=distClearTime]
			df_=df_[(df_.t>=tThreshold+distClearTime)&(df_.value<=vThreshold)]

			legend=[]
			for thisNode in set(df_.tnodeid):
				if not thisNode == excludeNodes:
					thisDF=df[df.tnodeid==thisNode]
					plt.plot(thisDF.t,thisDF.value)
					legend.append(thisNode)
			plt.legend(legend)
			plt.xlabel('Time (s)')
			plt.ylabel('Vmag (PU)')
			plt.show()
		except:
			raise

#===================================================================================================
	def plot_vt_filt_fast_der(self,df,tnodeid,legendDistNode=False,showPlot=False):
		try:
			df=df[df.t>=0]
			df=df[df.tnodeid==tnodeid]
			vmag=df[df.property=='VOLT']
			plt.plot(vmag.t,vmag.value,'-.')
			legend=['Transmission node {}'.format(tnodeid)]
			
			df=df[df.property=='vt_filt_fast_der']
			for thisNode in set(df.dnodeid):
				thisDF=df[df.dnodeid==thisNode]
				plt.plot(thisDF.t,thisDF.value)
				if legendDistNode:
					legend.append(thisNode)
			if not legendDistNode:
				legend.append('vt_filt seen by DERs in feeder')
			plt.legend(legend)
			plt.title('vt_filt seen by DERs')
			plt.xlabel('Time (s)')
			plt.ylabel('Vmag (PU)')
			if showPlot:
				plt.show()
		except:
			raise


#===================================================================================================
	def exclude_value(self,df,fromValue,toValue):
		"""Filter the given data frame based on >= and <= condition. For == condition use the same
		value for fromValue and toValue."""
		try:
			excludedDF=df[(df.value<=fromValue)|(df.value>=toValue)]
			return excludedDF
		except:
			raise

#-------------------------------------------------------------------------------------------			
	def compute_stability_time(self,df,error_threshold):
		try:
			comment = 'Stability is determined'
			df=df.sort_values(by='t')
			V =np.array(df.value)
			T = np.array(df.t)
			dV = []
			for t in range(len(V)-1):
				dV.append(V[t+1]-V[t]) 	 # Compute difference function of signal values
			t0 = 0 # Index of first sigificant deviation in signal value
			t2 = 0	 # time index of stability 
			exit_token = 0
			stability_time = 0
			T1 = -1
			for i in range(int(np.floor(len(dV)*0.95))):
				if abs(dV[i]) >= error_threshold*V[0] and t0 == 0 and exit_token == 0:
					t0 = i # index of first significant deviation
					T0 = T[i] # # time of first significant deviation
				if t0 != 0 and abs((max(V[i:len(V)]) - min(V[i:len(V)]))/min(V[i:len(V)]))<= error_threshold and exit_token == 0:
					exit_token = 1
					T1 = T[i] # time of stability
					t2 = i # time index of stability
					stability_time = T1 - T0
			if t0 == 0:
				comment = 'System is always stable'
				stability_time = -1
				max_deviation = max(V[0:len(V)]) - min(V[0:len(V)])

			elif t2 == 0:
				comment = 'System does not Stabilize'
				stability_time = -1
				max_deviation = -1
			elif t2 !=0:
				max_deviation = max(V[t2:len(V)]) - min(V[t2:len(V)])

			else:
				comment = 'Stability could not be determined'
				stability_time = -1
				max_deviation = -1
			
			return stability_time,comment,max_deviation
		except:
			raise

#-------------------------------------------------------------------------------------------			
	def instances_of_violation(self,df,maxValue,minValue):
		try:
			violated_df=df[(df.value<=minValue)|(df.value>=maxValue)]
			V =np.array(violated_df)
			violations = len(V)
			return violations
		except:
			raise

#--------------------------------------------------------------	
	def lag_finder(self,df1, df2):
		try:
			delay = -1
			if self.check_dataframes(df1, df2):
				y1=np.array(df1.value)
				y2=np.array(df2.value)
				n = len(y1)
				corr = []

				if n%2:
					delay_arr = range(int(-(n-1)/2), int((n-1)/2))
				else:
					delay_arr = range(int(-n/2),int(n/2))

				for i in delay_arr:
					y_temp = np.roll(y1,i)
					corr.append(sum(y_temp*y2))
				delay = delay_arr[np.argmax(corr)]

			return delay
		except:
			raise

	#-----------------------------------------------------------
	def compute_mean_square_error(self,df1,df2):
			try:
				MSE = -1
				if self.check_dataframes(df1, df2):
					V1 =np.array(df1.value)
					V2 =np.array(df2.value)
					MSE = (((V1-V2)/V1)**2).mean(axis=None)
				return MSE
			except:
				raise


#------------------------------------------------------------
	def compare_signals(self,thisBusId1,thisBusId2,df1,df2,error_threshold,show_results):
		try:
			
			lag = -1
			MSE = -1
			Stability_time_1 = (-1,"Failed to analyze stability",-1)
			Stability_time_2 = (-1,"Failed to analyze stability",-1)
			if self.check_dataframes(df1, df2):
				V1 =np.array(df1.value)
				T1 = np.array(df1.t)
				V2 =np.array(df2.value)
				T2 = np.array(df2.t)
				
				# Check if signals are essentially the same
				MSE = (((V1-V2)/V1)**2).mean(axis=None)
				lag = self.lag_finder(df1, df2)
				status = 0
				if MSE <= error_threshold**2:
					status = 1
					MSG = 'Both Signals are essentially the same'
				else:
				# If signals are not same and if there is a time shift, detect it and correct it
					V2 = self.shift_array(V2, -lag)							# Leg correction
					MSE = (((V1-V2)/V1)**2).mean(axis=None)					# Compute Mean Square Error after lag correction
					if MSE <= error_threshold**2:
						status = 2
						MSG = 'Both Signals are essentially the same after correcting the lag of ' + str(lag) +'.'
					
					# If signals are not same after bias corrections. Correct for measurement bias...
					if status == 0:
						V2 =np.array(df2.value)
						M1 = np.mean(V1)
						M2 = np.mean(V2)
						V2 = V2 - (M2-M1)
						MSE = (((V1-V2)/V1)**2).mean(axis=None)	
				
						if MSE <= error_threshold**2 and status == 0:
							MSG = 'Both Signals are essentially the same after correcting the Bias of ' + str(M2-M1) + '.'
							status = 3
					
					# If signals are not same after bias and lag corrections. try both...
					if status == 0:
						V2 =np.array(df2.value)
						V2 = self.shift_array(V2, -lag)			# Leg correction
						M1 = np.mean(V1)
						M2 = np.mean(V2)
						V2 = V2 - (M2-M1)
						MSE = (((V1-V2)/V1)**2).mean(axis=None)	
						if MSE <= error_threshold**2:
							MSG = 'Both Signals are essentially the same after correcting the lag of ' + str(lag)+' and the Bias of ' + str(M2-M1) + '.'
							status = 4
						else:
						# Both signals are not same
							MSG = 'Both Signals are not same'
							status = 5
						
				V1 =np.array(df1.value)
				T1 = np.array(df1.t)
				V2 =np.array(df2.value)
				T2 = np.array(df2.t)
				
				P1_min = np.min(V1)
				P1_max = np.max(V1)
				P2_min = np.min(V2)
				P2_max = np.max(V2)
				Stability_time_1 = self.compute_stability_time(df1,error_threshold)
				Stability_time_2 = self.compute_stability_time(df2,error_threshold)
		#Plot signals
				if show_results ==1:
					fig, axs = plt.subplots()
					axs.plot(T1,V1, '-b', label = '%s' % thisBusId1)
					axs.plot(T2,V2, '--r', label = '%s' % thisBusId2)
					axs.set_title('Original Signals without Bias and Lag Corrections')
					axs.legend()
					plt.text(0.1, 0.05, 'Signal 1\nMin Value = %s\nMax Value = %s\nStability Time = %s' %(P1_min,P1_max,Stability_time_1) , transform=axs.transAxes)
					plt.text(0.9, 0.05, 'Signal 2\nMin Value = %s\nMax Value = %s\nStability Time = %s' %(P2_min,P2_max,Stability_time_2) , transform=axs.transAxes)
					plt.text(0.5, 0.05, 'Mean Square Error = %s\nLag between Signals = %s' %(MSE, lag) , transform=axs.transAxes)
					plt.text(0.5, 0.95, '%s' %(MSG) , transform=axs.transAxes)
					axs.grid(True)		
			return lag,MSE,Stability_time_1,Stability_time_2
		except:
			raise

#-------------------------------------------------------------------	
	def shift_array(self,y, n):
		try:
			Y = np.roll(y,n)
			if n<0:
				n = -n
				for i in range(n):
					Y[len(y) - i-1] = y[len(y)-1]
			elif n>0:
				for i in range(n):
					Y[i] = y[0]
			else:
				Y = y
			return Y
		except:
			raise

#===================================================================================================
	def compare_prop_across_scenarios(self,dfDict,prop,topN=3,showPlot=False):
		try:
			res={}; legend=[]
			for scenario in dfDict:
				thisDF=dfDict[scenario]
				thisDF=thisDF[thisDF.property==prop]
				res[scenario]={'tnodeid':[],'value':[]}

				for thisTnodeID in set(thisDF.tnodeid):
					res[scenario]['tnodeid'].append(thisTnodeID)
					res[scenario]['value'].append(thisDF[thisDF.tnodeid==thisTnodeID].value.std())
				res[scenario]['df']=pd.DataFrame(res[scenario])
				res[scenario]['df']=res[scenario]['df'].sort_values(by='value',ascending=False)
				res[scenario]['df']=res[scenario]['df'].head(topN)


				for thisTnodeID in set(res[scenario]['df'].tnodeid):
					tempDF=thisDF[thisDF.tnodeid==thisTnodeID]
					plt.plot(tempDF.t,tempDF.value)
					legend.append('{}_{}'.format(scenario,thisTnodeID))

			if showPlot:
				plt.legend(legend)
				plt.show()

			return res
		except:
			raise


#-------------------------------------------------------------------	
	def check_dataframes(self,df1, df2):
		try:
			flag = True
			if (len(df1) != len(df2)):
				flag = False
			return flag
		except:
			raise

