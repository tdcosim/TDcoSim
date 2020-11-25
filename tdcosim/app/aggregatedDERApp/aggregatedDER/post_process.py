import os
import copy
import json
import pdb
from itertools import product
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import psspy
import dyntools
from scipy import signal
from tdcosim.data_analytics import DataAnalytics
from utils import PrintException


class PostProcess(DataAnalytics):
	def __init__(self):
		super(DataAnalytics,self).__init__()
		self.baseDir=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
		self.outDir=self.baseDir+os.path.sep+'data'+os.path.sep+'out'
		self.metadata={'scenarioid':'','tag':'','config':{}}
		self.search_scope('','')
		return None

#=======================================================================================================================
	def add_metadata(self,scenarioid,tag,config):
		try:
			self.metadata['scenarioid']=scenarioid
			self.metadata['tag']=tag
			self.metadata['config']=config
		except:
			PrintException()

#=======================================================================================================================
	def load_outfile(self,fpath):
		try:
			# convert to df
			dfOld=self._dict2df_outfile(fpath)

			# reformat
			df=pd.DataFrame(columns=['time','scenarioid','tag','busid','property','value'])
			df.time=dfOld.t
			df.scenarioid=[self.metadata['scenarioid']]*len(dfOld.t)
			df.tag=[self.metadata['tag']]*len(dfOld.t)
			df.busid=dfOld.tnodeid
			df.property=dfOld.property
			df.value=dfOld.value

			# change property names
			df.property=df.property.map(self.__mapper)

			return df
		except:
			PrintException()

#=======================================================================================================================
	def __mapper(self,x,mapio={'POWR':'pinj','VARS':'qinj','PLOD':'pd','QLOD':'qd',
	'SPD':'omega','VOLT':'vmag','PMEC':'pmech','ANGL':'delta'}):
		try:
			if x in mapio:
				x=mapio[x]
			return x
		except:
			PrintException()

#=======================================================================================================================
	def show_plot(self,df,propertyid,ylabel='',title=''):
		try:
			df=df[df.property==propertyid]
			df=df.sort_values(by='time',ascending=True)
			legend=[]
			for thisBusid in set(df.busid):
				thisDF=df[df.busid==thisBusid]
				plt.plot(thisDF.time,thisDF.value)
				legend.append(thisBusid)

			plt.xlabel('Time (s)')
			plt.ylabel(ylabel)
			plt.title(title)
			plt.legend(legend)
			plt.show()
		except Exception as e:
			logging.error(e)

#=======================================================================================================================
	def save(self,df):
		try:
			for thisScenario,thisTag in product(*(set(df.scenarioid),set(df.tag))):
				thisDF=df[(df.scenarioid==thisScenario)&(df.tag==thisTag)]
				if not thisDF.empty:
					dirPath=self.outDir+os.path.sep+'{}_{}'.format(thisScenario,thisTag)
					if not os.path.exists(dirPath):
						os.mkdir(dirPath)
					thisDF.to_pickle(open(dirPath+os.path.sep+'{}_{}_df.pkl'.format(thisScenario,thisTag),'wb'),
					compression=None)
					json.dump(self.metadata['config'],open(dirPath+os.path.sep+'{}_{}_config.json'.format(\
					thisScenario,thisTag),'w'),indent=3)
		except:
			PrintException()

#=======================================================================================================================
	def search_scope(self,scenarioid,tag):
		try:
			if isinstance(scenarioid,str):
				scenarioid=[scenarioid]
			if isinstance(tag,str):
				tag=[tag]

			self.index={'info':{},'path':[]}
			for thisScenario,thisTag in zip(scenarioid,tag):
				if thisScenario not in self.index['info']:
					self.index['info'][thisScenario]={}
				self.index['info'][thisScenario][thisTag]={}
				dirPath=self.outDir+os.path.sep+'{}_{}'.format(thisScenario,thisTag)
				self.index['path'].append(dirPath+os.path.sep+'{}_{}_df.pkl'.format(thisScenario,thisTag))
		except:
			PrintException()

#=======================================================================================================================
	def filter_node(self,busid,df=None):
		try:
			if not isinstance(df,pd.DataFrame):
				df=self.get_df()

			if isinstance(busid,str) or isinstance(busid,int):
				busid=[busid]

			filteredDF=pd.DataFrame(columns=df.columns)
			for thisNode in busid:
				filteredDF=filteredDF.append(df[df.busid==thisNode],ignore_index=True)

			filteredDF.index=range(len(filteredDF))
			return filteredDF
		except:
			PrintException()

#===================================================================================================
	def filter_time(self,fromTime,toTime,df=None):
		try:
			if not isinstance(df,pd.DataFrame):
				df=self.get_df()
			df=df[(df.value>=fromTime)&(df.value<=toTime)]
			return df
		except:
			PrintException()

#===================================================================================================
	def filter_property(self,propertyid,df=None):
		try:
			if not isinstance(df,pd.DataFrame):
				df=self.get_df()

			if isinstance(propertyid,str) or isinstance(propertyid,int):
				propertyid=[propertyid]

			filteredDF=pd.DataFrame(columns=df.columns)
			for thisproperty in propertyid:
				filteredDF=filteredDF.append(df[df.property==thisproperty],ignore_index=True)

			filteredDF.index=range(len(filteredDF))
			return filteredDF
		except:
			PrintException()

#===================================================================================================
	def filter_value(self,fromValue,toValue,df=None):
		try:
			if not isinstance(df,pd.DataFrame):
				df=self.get_df()
			df=df[(df.value>=fromValue)&(df.value<=toValue)]
			return df
		except:
			PrintException()

#===================================================================================================
	def filter_violations(self,lowerLimit,upperLimit,df=None):
		try:
			if not isinstance(df,pd.DataFrame):
				df=self.get_df()
			df=df[(df.value<=lowerLimit)|(df.value>=upperLimit)]
			return df
		except:
			PrintException()
            
#===================================================================================================
	def get_df(self):
		try:
			df=pd.DataFrame(columns=['time','scenarioid','tag','busid','property','value'])
			for thisDFPath in self.index['path']:
				df=df.append(pd.read_pickle(open(thisDFPath,'rb'),compression=None))
			return df
		except:
			PrintException()



#===================================================================================================
	def show_voltage_violations_der(self,vmin,vmax,df=None):
		try:
			if not isinstance(df,pd.DataFrame):
				df=self.get_df()
			time_values = self.get_time_values(df)
			print('Minimum voltage:{:.2f},Maximum voltage:{:.2f}'.format(df[df.property=='vmag'].value.min(),df[df.property=='vmag'].value.max()))
			#VFilt=self.filter_value(vmin,vmax,df[(df.property=='vmag')& (df.phase=='a')])
			VFilt=self.filter_violations(vmin,vmax,df[(df.property=='vmag')& (df.phase=='a')])

			print('Original distribution nodes:{},Filtered distribution nodes:{}'.format(list(set(df.dnodeid)),list(set(VFilt.dnodeid))))
			print('Original samples:{},Filtered samples:{}'.format(len(df),len(VFilt)))
			legend=[];thisDf_list=[]
			plt.figure(figsize=(10,10))
			for thisBusId in set(VFilt.busid):
				for thisScenario in set(VFilt.scenarioid):
					for thisTag in set(VFilt.tag):
						for thisDnodeId in set(VFilt.dnodeid):
							thisDf=VFilt[(VFilt.busid==thisBusId)&(VFilt.property=='vmag')&\
							(VFilt.scenarioid==thisScenario)&(VFilt.tag==thisTag)&(VFilt.dnodeid==thisDnodeId)]
							if not thisDf.empty:
								thisDf_list.append(thisDf)
								plt.scatter(thisDf.time,thisDf.value,s=10.0)								
								legend.append('{}-{}-a:{}:{}'.format(thisBusId,thisDnodeId,thisScenario,thisTag,thisTag))
			
			
			plt.scatter(time_values,[vmin]*len(time_values),s=10.0,marker=".")
			plt.scatter(time_values,[vmax]*len(time_values),s=10.0,marker=".")
			legend.append('Vmin--{}'.format(vmin))
			legend.append('Vmax--{}'.format(vmax))
			
			plt.ylabel('Voltage (p.u.)',weight = "bold", fontsize=10)
			plt.xlabel('Time (s)',weight = "bold", fontsize=10)
			plt.legend(legend)
			plt.title('Voltage Violations\nViolation:Vmag <={} and >={} pu'.format(vmin,vmax))
			plt.show()
			return thisDf_list
            
		except:
			PrintException()
#===================================================================================================
	def show_voltage_violations(self,vmin,vmax,df=None):
		try:
			if not isinstance(df,pd.DataFrame):
				df=self.get_df()

			VFilt=self.filter_value(vmin,vmax,df[df.property=='vmag'])

			legend=[]
			for thisBusId in set(VFilt.busid):
				for thisScenario in set(VFilt.scenarioid):
					for thisTag in set(VFilt.tag):
						thisDf=df[(df.busid==thisBusId)&(df.property=='vmag')&\
						(df.scenarioid==thisScenario)&(df.tag==thisTag)]
						if not thisDf.empty:
							plt.plot(thisDf.time,thisDf.value)
							legend.append('{}:{}:{}'.format(thisBusId,thisScenario,thisTag))
			plt.legend(legend)
			plt.title('Voltage Violations\nViolation:Vmag >={} and <={} pu'.format(vmin,vmax))
			plt.show()
		except:
			PrintException()
			

#===================================================================================================
	def show_voltage_recovery_der(self,vmin,vmax,maxRecoveryTime,df=None):
		try:
			if not isinstance(df,pd.DataFrame):
				df=self.get_df()
			
			time_values = self.get_time_values(df)
			VFilt=self.filter_value(vmin,vmax,df[df.property=='vmag'])

			legend=[]
			violation_nodes = []
			for thisBusId in set(VFilt.busid):
				for thisDnodeId in set(VFilt.dnodeid):
					for thisScenario in set(VFilt.scenarioid):
						for thisTag in set(VFilt.tag):
							thisDf=df[(df.busid==thisBusId)&(df.dnodeid==thisDnodeId)&(df.phase=='a')&(df.property=='vmag')&(df.scenarioid==thisScenario)&(df.tag==thisTag)]
							thisDf=thisDf.sort_values(by='time')
							#print(thisBusId,thisDnodeId,thisScenario,thisDf.shape)
							startFlag=False; startTime=0
							for thisTime,thisVal in zip(thisDf.time,thisDf.value):
								if (thisVal<=vmin or thisVal>=vmax) and not startFlag:
									startFlag=True
									startTime=thisTime
									#print('Timer started at {} s for node {} at {} V'.format(thisTime,thisDnodeId,thisVal))
								if thisVal>vmin and thisVal<vmax and startFlag:
									startFlag=False
									startTime=thisTime
									#print('Timer reset at {} s for node {} at {} V'.format(thisTime,thisDnodeId,thisVal))
								if (thisVal<=vmin or thisVal>=vmax) and startFlag:
									if thisTime-startTime>=maxRecoveryTime:
										#startFlag=False
										print('Timer breached at {:.2f} s after {:.2f} s for node {} at {:.2f} V'.format(thisTime,thisTime-startTime,thisDnodeId,thisVal))
										legend.append('{}:{}:{}:{}'.format(thisBusId,thisDnodeId,thisScenario,thisTag))
										violation_nodes.append(thisDnodeId)
										break
			thisDf_list = []
			print('{} nodes had recovery time > {} s:{}'.format(len(violation_nodes),maxRecoveryTime,violation_nodes))
			if legend:
				plt.figure(figsize=(10,10))
				for entry in legend:
					thisBusId=entry.split(':')[0]
					thisDnodeId=entry.split(':')[1]
					thisScenario=entry.split(':')[2]
					thisTag=entry.split(':')[3]
					
					thisDf=df[(df.busid==thisBusId)&(df.dnodeid==thisDnodeId)&(df.phase=='a')&(df.property=='vmag')&(df.scenarioid==thisScenario)&(df.tag==thisTag)]
					
					if not thisDf.empty:
						thisDf_list.append(thisDf)
						plt.plot(thisDf.time,thisDf.value)
				
				plt.scatter(time_values,[vmin]*len(time_values),s=10.0,marker=".")
				plt.scatter(time_values,[vmax]*len(time_values),s=10.0,marker=".")
				legend.append('Vmin--{}'.format(vmin))
				legend.append('Vmax--{}'.format(vmax))
				plt.ylabel('Voltage (p.u.)',weight = "bold", fontsize=10)
				plt.xlabel('Time (s)',weight = "bold", fontsize=10)
				plt.legend(legend)
				plt.title('Voltage Violations\nViolation:Vmag <={} or >={} pu for time>={}'.format(vmin,vmax,maxRecoveryTime))
				plt.show()
			return thisDf_list
		except:
			PrintException()

#===================================================================================================
	def show_voltage_recovery(self,vmin,vmax,maxRecoveryTime,df=None):
		try:
			if not isinstance(df,pd.DataFrame):
				df=self.get_df()

			VFilt=self.filter_value(vmin,vmax,df[df.property=='vmag'])

			legend=[]
			for thisBusId in set(VFilt.busid):
				for thisScenario in set(VFilt.scenarioid):
					for thisTag in set(VFilt.tag):
						thisDf=df[(df.busid==thisBusId)&(df.property=='vmag')&\
						(df.scenarioid==thisScenario)&(df.tag==thisTag)]
						thisDf=thisDf.sort_values(by='time')
						startFlag=False; startTime=0
						for thisTime,thisVal in zip(thisDf.time,thisDf.value):
							if thisVal>=vmin and thisVal<=vmax and not startFlag:
								startFlag=True
								startTime=thisTime
							elif thisVal>=vmin and thisVal<=vmax and startFlag and thisTime-startTime>=maxRecoveryTime:
								startFlag=False
								legend.append('{}:{}:{}'.format(thisBusId,thisScenario,thisTag))
								break

			if legend:
				for entry in legend:
					thisBusId=entry.split(':')[0]
					thisDf=df[(df.busid==thisBusId)&(df.property=='vmag')&\
					(df.scenarioid==thisScenario)&(df.tag==thisTag)]
					if not thisDf.empty:
						plt.plot(thisDf.time,thisDf.value)

				plt.legend(legend)
				plt.title('Voltage Violations\nViolation:Vmag >={} and <={} pu for time>={}'.format(vmin,vmax,maxRecoveryTime))
				plt.show()
		except:
			PrintException()

#===================================================================================================

	def get_voltage_stability_time_der(self,vmin,vmax,maxRecoveryTime,error_threshold,df=None):
		try:
			if not isinstance(df,pd.DataFrame):
				df=self.get_df()
				
			VFilt=self.filter_value(vmin,vmax,df[df.property=='vmag'])
			
			legend=[]
			
			for thisBusId in set(VFilt.busid):
				for thisDnodeId in set(VFilt.dnodeid):
					for thisScenario in set(VFilt.scenarioid):
						for thisTag in set(VFilt.tag):
							thisDf=df[(df.busid==thisBusId)&(df.dnodeid==thisDnodeId)&(df.phase=='a')&(df.property=='vmag')&(df.scenarioid==thisScenario)&(df.tag==thisTag)]
							thisDf=thisDf.sort_values(by='time')
							startFlag=False; startTime=0
							for thisTime,thisVal in zip(thisDf.time,thisDf.value):
								if thisVal>=vmin and thisVal<=vmax and not startFlag:
									startFlag=True
									startTime=thisTime
								elif thisVal>=vmin and thisVal<=vmax and startFlag and thisTime-startTime>=maxRecoveryTime:
									startFlag=False
									legend.append('{}:{}:{}:{}'.format(thisBusId,thisDnodeId,thisScenario,thisTag))
									break
			
			if legend:
				ST=pd.DataFrame(columns=['Label','T0','T1','Stability time','Stability State'])
				plt.figure(figsize=(10,10))
				for entry in legend:
					thisBusId=entry.split(':')[0]
					thisDnodeId=entry.split(':')[1]
					thisScenario=entry.split(':')[2]
					thisTag=entry.split(':')[3]
					
					thisDf=df[(df.busid==thisBusId)&(df.dnodeid==thisDnodeId)&(df.phase=='a')&(df.property=='vmag')&(df.scenarioid==thisScenario)&(df.tag==thisTag)]
					
					if not thisDf.empty:
						ST_temp = self.compute_stability_time(entry,thisDf,error_threshold,ST)
						ST = ST.append(ST_temp, ignore_index=True)
			
			print(ST)
			plt.grid(True)
			plt.show()
			return ST
			
		except:
			PrintException()
#===================================================================================================
	
	def get_voltage_stability_time(self,vmin,vmax,maxRecoveryTime,error_threshold,df=None):
		try:
			if not isinstance(df,pd.DataFrame):
				df=self.get_df()
				
			VFilt=self.filter_value(vmin,vmax,df[df.property=='vmag'])
			
			legend=[]
			for thisBusId in set(VFilt.busid):
				for thisScenario in set(VFilt.scenarioid):
					for thisTag in set(VFilt.tag):
						thisDf=df[(df.busid==thisBusId)&(df.property=='vmag')&\
						(df.scenarioid==thisScenario)&(df.tag==thisTag)]
						thisDf=thisDf.sort_values(by='time')
						startFlag=False; startTime=0
						for thisTime,thisVal in zip(thisDf.time,thisDf.value):
							if thisVal>=vmin and thisVal<=vmax and not startFlag:
								startFlag=True
								startTime=thisTime
							elif thisVal>=vmin and thisVal<=vmax and startFlag and thisTime-startTime>=maxRecoveryTime:
								startFlag=False
								legend.append('{}:{}:{}'.format(thisBusId,thisScenario,thisTag))
								break
			if legend:
				ST=pd.DataFrame(columns=['Label','T0','T1','Stability time','Stability State','Comment'])
				for entry in legend:
					thisBusId=entry.split(':')[0]
					thisDf=df[(df.busid==thisBusId)&(df.property=='vmag')&\
					(df.scenarioid==thisScenario)&(df.tag==thisTag)]
					if not thisDf.empty:
						ST_temp = self.compute_stability_time(entry,thisDf,error_threshold,0.95,1.05)
						ST = ST.append(ST_temp, ignore_index=True)
			print(ST)
			plt.grid(True)
			plt.show()
			return ST					
			
		except:
			PrintException()
#-------------------------------------------------------------------------------------------			
	def compute_stability_time(self,entry,thisDf,error_threshold,minValue,maxValue):
		try:
			plt.plot(thisDf.time,thisDf.value)
			V =np.array(thisDf.value)
			T = np.array(thisDf.time)
			dV = []
			for t in range(len(V)-1):
				dV.append(V[t+1]-V[t])
			plt.plot(T,V)
			plt.plot(T[0:len(T)-1],dV)
			t0 = 0
			t2 = 0
			exit_token = 0
			Stability_time = []
			T1 = -1
			for i in range(len(dV)):
				if abs(dV[i]) >= error_threshold*V[0] and t0 == 0 and exit_token == 0:
					t0 = i
					T0 = T[i]
				if t0 != 0 and max([abs(ele) for ele in dV[i:len(dV)]] ) <= error_threshold*V[0] and exit_token == 0:
					exit_token = 1
					T1 = T[i]
					t2 = i 
					Stability_time = T1 - T0
			if t0 == 0:
				Comment = 'System is always stable'
				Stability_State = 0
			elif T1 == -1:
				Comment = 'System does not Stabilize'
				Stability_State = 4
			elif (abs(V[t2+1] -V[t0-1]))<=0.01:
				Stability_State = 1
				Comment = "System voltage is stable and recovered to its original value"
			elif V[t2] >=minValue and V[t2] <=maxValue:
				#Comment = ("System voltage is recovered, stable and within" +  [%f , %f] volt" %(minValue, maxValue))
				Comment = "System voltage is recovered, stable and within [" + str(minValue) + "," + str(maxValue) + "] volt range"
				Stability_State = 2
			else:
				Comment = "System voltage is stable and outside [" + str(minValue) + "," + str(maxValue) + "] volt range"
				Stability_State = 3
			print(Comment)
			ST_temp = pd.DataFrame([[entry,T0,T1,Stability_time,Stability_State,Comment]],columns=['Label','T0','T1','Stability time','Stability State','Comment'])
			return ST_temp
		except:
			PrintException()
#===================================================================================================
	
	def compare_voltages(self,vmin,vmax,maxRecoveryTime,error_threshold,df=None):
		try:
			if not isinstance(df,pd.DataFrame):
				df=self.get_df()
				
			VFilt=self.filter_value(vmin,vmax,df[df.property=='vmag'])
			
			legend=[]
			for thisBusId in set(VFilt.busid):
				for thisScenario in set(VFilt.scenarioid):
					for thisTag in set(VFilt.tag):
						thisDf=df[(df.busid==thisBusId)&(df.property=='vmag')&\
						(df.scenarioid==thisScenario)&(df.tag==thisTag)]
						thisDf=thisDf.sort_values(by='time')
						startFlag=False; startTime=0
						for thisTime,thisVal in zip(thisDf.time,thisDf.value):
							if thisVal>=vmin and thisVal<=vmax and not startFlag:
								startFlag=True
								startTime=thisTime
							elif thisVal>=vmin and thisVal<=vmax and startFlag and thisTime-startTime>=maxRecoveryTime:
								startFlag=False
								legend.append('{}:{}:{}'.format(thisBusId,thisScenario,thisTag))
								break
			if legend:
				
				x = 0
				for entry in legend:
					if x == 0:
						thisBusId=entry.split(':')[0]
						thisDf1=df[(df.busid==thisBusId)&(df.property=='vmag')&\
						(df.scenarioid==thisScenario)&(df.tag==thisTag)]
						x = x+1
					elif x == 1:
						thisBusId=entry.split(':')[0]
						thisDf2=df[(df.busid==thisBusId)&(df.property=='vmag')&\
						(df.scenarioid==thisScenario)&(df.tag==thisTag)]
						break
				ST, Status = self.compare_signals(thisDf1,thisDf2,error_threshold)
				
			return ST					
			
			
			
		except:
			PrintException()			
#-------------------------------------------------------------------------------------------			
	def compare_signals(self,thisDf1,thisDf2,error_threshold):
		try:
			
			V1 =np.array(thisDf1.value)
			T1 = np.array(thisDf1.time)
			V2 =np.array(thisDf2.value)
			T2 = np.array(thisDf2.time)
			
			# Scale and Rotate vector... Delete next 5 lines after testing phase
			V2 = 0.9*self.shift_array(V2, -10)									
			thisDf2.value = V2
			
			fig, axs = plt.subplots(2)
			axs[0].plot(T1,V1)
			axs[0].plot(T2,V2)
			axs[0].set_title('Original Signals without Bias and Lag Corrections')
			axs[0].grid(True)
			
			status = 0
			
			# Check if signals are essentially the same
			MSE = (((V1-V2)/V1)**2).mean(axis=None)
			print('Original MSE = ' + str(MSE))
			if MSE <= error_threshold**2:
				print('Both Signals are essentially the same')
				status = 1
				lag = 0
				M1 = 0
				M2 = 0
			else:
			
			# If signals are not same and if there is a time shift, detect it and correct it
			
				lag = self.lag_finder(V1, V2)			# Lag detection
				V2 = self.shift_array(V2, -lag)			# Leg correction
				MSE = (((V1-V2)/V1)**2).mean(axis=None)	# Compute Mean Square Error after lag correction
				print('MSE after Lag Correction = ' + str(MSE))
				
				if MSE <= error_threshold**2:
					print('Both Signals are essentially the same after correcting the lag of ' + str(lag) +'.')
					status = 2
				
			# If signals are not same after bias corrections. Correct for measurement bias...
				elif lag ==0:
					V2 =np.array(thisDf2.value)
					M1 = np.mean(V1)
					M2 = np.mean(V2)
					V2 = V2 - (M2-M1)
					MSE = (((V1-V2)/V1)**2).mean(axis=None)	
					print('MSE after Bias Correction = ' + str(MSE))
					if MSE <= error_threshold**2 and status == 0:
						print('Both Signals are essentially the same after correcting the Bias of ' + str(M2-M1) + '.')
						status = 3
				else:
			# If signals are not same after bias and lag corrections. try both...
					V2 =np.array(thisDf2.value)
					lag = self.lag_finder(V1, V2)			# Lag detection
					V2 = self.shift_array(V2, -lag)			# Leg correction
					M1 = np.mean(V1)
					M2 = np.mean(V2)
					V2 = V2 - (M2-M1)
					MSE = (((V1-V2)/V1)**2).mean(axis=None)	
					print('MSE after Bias and Lag Correction = ' + str(MSE))
					if MSE <= error_threshold**2:
						print('Both Signals are essentially the same after correcting the lag of ' + str(lag)+' and the Bias of ' + str(M2-M1) + '.')
						status = 4
					else:
			# Both signals are not same
						print('Both Signals are not same')
						status = 5
					
			print('Status = ' + str(status))	
			axs[1].plot(T1,V1)
			axs[1].plot(T2,V2)
			axs[1].set_title('Signals After Correcting lag of ' + str(lag)+' and Bias of ' + str(M2-M1))
			axs[1].grid(True)
			plt.show()			
			
			
			V1 =np.array(thisDf1.value)
			T1 = np.array(thisDf1.time)
			V2 =np.array(thisDf2.value)
			T2 = np.array(thisDf2.time)
			
			P1_min = np.min(V1)
			P1_max = np.max(V1)
			P2_min = np.min(V2)
			P2_max = np.max(V2)
			
			dV1 = []
			dV2 = []
			for t in range(len(V1)-1):
				dV1.append(V1[t+1]-V1[t])
				dV2.append(V2[t+1]-V2[t])
			
			t01= 0
			exit_token1 = 0
			Stability_time1 = []
			T11 = -1
			for i in range(len(dV1)):
				if abs(dV1[i]) >= error_threshold*V1[0] and t01 == 0 and exit_token1 == 0:
					t01 = i
					T01 = T1[i]
				if t01 != 0 and max([abs(ele) for ele in dV1[i:len(dV1)]] ) <= error_threshold*V1[0] and exit_token1 == 0:
					exit_token1 = 1
					T11 = T1[i]
					Stability_time1 = T11 - T01
				
			t02= 0
			exit_token2 = 0
			Stability_time2 = []
			T12 = -1
			for i in range(len(dV2)):
				if abs(dV2[i]) >= error_threshold*V2[0] and t02 == 0 and exit_token2 == 0:
					t02 = i
					T02 = T2[i]
				if t02 != 0 and max([abs(ele) for ele in dV2[i:len(dV2)]] ) <= error_threshold*V2[0] and exit_token2 == 0:
					exit_token2 = 1
					T12 = T2[i]
					Stability_time2 = T12 - T02
			
			ST=pd.DataFrame(columns=['Label','T0','T1','Stability time','P_min','P_max'])
			ST_temp1=pd.DataFrame(columns=['Label','T0','T1','Stability time','P_min','P_max'])
			ST_temp2=pd.DataFrame(columns=['Label','T0','T1','Stability time','P_min','P_max'])
			ST_temp1 = pd.DataFrame([['Signal 1',T01,T11,Stability_time1,P1_min,P1_max]],columns=['Label','T0','T1','Stability time','P_min','P_max'])
			ST = ST.append(ST_temp1, ignore_index=True)
			ST_temp2 = pd.DataFrame([['Signal 2',T02,T12,Stability_time2,P2_min,P2_max]],columns=['Label','T0','T1','Stability time','P_min','P_max'])
			ST = ST.append(ST_temp2, ignore_index=True)
			
			print(ST)
			return ST, status
			
		except:
			PrintException()
	
#--------------------------------------------------------------	
	def lag_finder(self,y1, y2):
		try:
			n = len(y1)
			corr = []
			delay_arr = range(-(n-1)/2, (n-1)/2)
			for i in delay_arr:
				y_temp = np.roll(y1,i)
				corr.append(sum(y_temp*y2))
			
			delay = delay_arr[np.argmax(corr)]
			print('y2 is ' + str(delay) + ' behind y1')
			#plt.figure()
			#plt.plot(delay_arr, corr)
			#plt.title('Lag: ' + str(np.round(delay, 3)) + ' s')
			#plt.xlabel('Lag')
			#plt.ylabel('Correlation coeff')
			#plt.grid(True)
			#plt.show()
			return delay
		except:
			PrintException()
	
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
			PrintException()