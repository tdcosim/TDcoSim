import json
import uuid
import pdb
import os

from tdcosim.global_data import GlobalData


#===================================================================================================
#==============================================CONFIG===============================================
#===================================================================================================
class ConfigHelper(object):
	"""A class to help the user create config for cosimulation.
	Most methods are names add_* and remove_*. add _* adds a
	particular configuration while remove_* will undo the change.
	There is also a read, write, show and validate methods to
	read an existing config file, write the current self.data
	to a file, show the contents of self.data and validate the
	configuration in self.data.
	
	Typical usage,
	foo=ConfigHelper()
	foo.add_*()
	foo.validate()
	foo.write()"""
	def __init__(self):
		self.data={}
		return None

#===================================================================================================
	def add_psseconfig(self,rawFilePath,dyrFilePath, installLocation):
		try:
			psseConfig=self.data['psseConfig']={}
			psseConfig['rawFilePath']=rawFilePath
			psseConfig['dyrFilePath']=dyrFilePath
			psseConfig['installLocation']=installLocation
		except:
			GlobalData.log()

#===================================================================================================
	def remove_psseconfig(self):
		try:
			self.data.pop('psseConfig')
		except:
			GlobalData.log()

#===================================================================================================
	def add_cosimhome(self,cosimHome):
		try:
			self.data['cosimHome']=cosimHome
		except:
			GlobalData.log()

#===================================================================================================
	def remove_cosimhome(self):
		try:
			self.data.pop('cosimHome')
		except:
			GlobalData.log()

#===================================================================================================
	def add_defaultfeederconfig(self,filePath,solarFlag,solarPenetration):
		try:
			if 'openDSSConfig' not in self.data:
				self.data['openDSSConfig']={}
			defConf=self.data['openDSSConfig']['defaultFeederConfig']={}
			defConf['filePath']=filePath
			defConf['solarFlag']=solarFlag
			defConf['solarPenetration']=solarPenetration
		except:
			GlobalData.log()

#===================================================================================================
	def remove_defaultfeederconfig(self):
		try:
			self.data['openDSSConfig'].pop('defaultFeederConfig')
		except:
			GlobalData.log()

#===================================================================================================
	def add_manualfeederconfig(self,nodenumber,filePath,solarFlag,DERFilePath,initializeWithActual,
	DERSetting,DERModelType,PVPlacement,
	defaultDERParameters={"solarPenetration":0.02,"derId":"50","powerRating":50,
	"VrmsRating":177.0,"steadyStateInitialization":True,"pvderScale": 1}):
		"""Each input should be a list such that the entries in the list index should match.
		for ex:nodenumber=[1,2],filePath=['case13.dss','case123.dss'],solarFlag=[0,1],
		solarPenetration=[0,50] implies case13.dss is attached to transmission bus 1 and that there
		is no solar generation in the distribution system."""
		try:
			if 'openDSSConfig' not in self.data:
				self.data['openDSSConfig']={}
			if 'manualFeederConfig' not in self.data['openDSSConfig']:
				self.data['openDSSConfig']['manualFeederConfig']={}
				self.data['openDSSConfig']['manualFeederConfig']['nodes']=[]

			data=self.data['openDSSConfig']['manualFeederConfig']['nodes']
			for i in range(len(nodenumber)):
				thisNodeData={'DERParameters':{}}
				thisNodeData['nodenumber']=nodenumber[i]
				thisNodeData['filePath']=[filePath[i]]
				thisNodeData['solarFlag']=solarFlag[i]
				thisNodeData['DERFilePath']=DERFilePath[i]
				thisNodeData['initializeWithActual']=initializeWithActual[i]
				thisNodeData['DERSetting']=DERSetting[i]
				thisNodeData['DERModelType']=DERModelType[i]
				thisNodeData['DERParameters']['PVPlacement']=PVPlacement[i]
				thisNodeData['DERParameters']['default']=defaultDERParameters
				data.append(thisNodeData)
		except:
			GlobalData.log()

#===================================================================================================
	def remove_manualfeederconfig(self):
		try:
			self.data['openDSSConfig'].pop('manualFeederConfig')
		except:
			GlobalData.log()

#===================================================================================================
	def add_derparameters(self,nodenumber,solarPenetration,derId,powerRating=50.0,VrmsRating=177.0,
	steadyStateInitialization=True,pvderScale=1):
		"""Add DER parameters to a given nodenumber (nodeID/busID/busNumber)"""
		try:
			assert 'openDSSConfig' in self.data and \
			'manualFeederConfig' in self.data['openDSSConfig'] and \
			'nodes' in self.data['openDSSConfig']['manualFeederConfig'],"""
			Please use add_manualfeederconfig method to define nodes at which solar is present
			before running this method."""

			nodes=self.data['openDSSConfig']['manualFeederConfig']['nodes']
			targetnode={}
			for n in range(len(self.data['openDSSConfig']['manualFeederConfig']['nodes'])):
				if nodes[n]['nodenumber'] == nodenumber:
					targetnode = nodes[n]
					break;

			derprop=targetnode['DERParameters']={}#overwrite even if previous data exists
			default=derprop['default']={}

			default['solarPenetration'] = solarPenetration
			default['derId'] = derId
			default['powerRating'] = powerRating
			default['VrmsRating'] = VrmsRating
			default['steadyStateInitialization'] = steadyStateInitialization
			default['pvderScale'] = pvderScale

		except:
			GlobalData.log()

#===================================================================================================
	def remove_derparameters(self,nodenumber):
		"""Remove DER parameters of a given nodenumber (nodeID/busID/busNumber)"""
		try:
			if 'openDSSConfig' in self.data and \
			'manualFeederConfig' in self.data['openDSSConfig'] and \
			'nodes' in self.data['openDSSConfig']['manualFeederConfig']:

				nodes=self.data['openDSSConfig']['manualFeederConfig']['nodes']
				targetnode={}
				for n in range(len(self.data['openDSSConfig']['manualFeederConfig']['nodes'])):
					if nodes[n]['nodenumber'] == nodenumber:
						targetnode = nodes[n]
						break;

				assert 'DERParameters' in targetnode, """
				Can't find the DERParameters accoding to the given nodenumber"""

				targetnode.pop('DERParameters')
		except:
			GlobalData.log()

#===================================================================================================
	def add_LVRT(self,nodenumber,LVRTkey,V_threshold,t_threshold,mode):
		"""Each inputs of the LVRT except nodenumber should be a list such that the entries in 
		the list index should match.
		for ex:LVRTkey=["1","2"],V_threshold=[0.6,0.7],t_threshold=[1.0,1.0],
		mode=['mandatory_operation','mandatory_operation'] 
		implies LVRT 1 and 2 are attached to transmission bus [nodenumber] and that LVRTs
		will operate as mandatory operation with V and t threshholds"""
		try:
			assert 'openDSSConfig' in self.data and \
			'manualFeederConfig' in self.data['openDSSConfig'] and \
			'nodes' in self.data['openDSSConfig']['manualFeederConfig'],"""
			Please use add_manualfeederconfig method to define nodes at which solar is present
			before running this method."""

			nodes=self.data['openDSSConfig']['manualFeederConfig']['nodes']
			targetnode={}
			for n in range(len(self.data['openDSSConfig']['manualFeederConfig']['nodes'])):
				if nodes[n]['nodenumber'] == nodenumber:
					targetnode = nodes[n]
					break;

			assert 'DERParameters' in targetnode and \
			'default' in targetnode['DERParameters'], """
			Can't find the DERParameters accoding to the given nodenumber"""
			
			default=targetnode['DERParameters']['default']
			LVRT = default['LVRT'] = {} #overwrite even if previous data exists

			for i in range(len(LVRTkey)):
				LVRT[LVRTkey[i]] = {}
				LVRT[LVRTkey[i]]['V_threshold'] = V_threshold[i]
				LVRT[LVRTkey[i]]['t_threshold'] = t_threshold[i]
				LVRT[LVRTkey[i]]['mode'] = mode[i]

		except:
			GlobalData.log()

#===================================================================================================
	def remove_LVRT(self,nodenumber):
		"""Remove LVRT of a given nodenumber (nodeID/busID/busNumber)"""
		try:
			if 'openDSSConfig' in self.data and \
			'manualFeederConfig' in self.data['openDSSConfig'] and \
			'nodes' in self.data['openDSSConfig']['manualFeederConfig']:

				nodes=self.data['openDSSConfig']['manualFeederConfig']['nodes']
				targetnode={}
				for n in range(len(self.data['openDSSConfig']['manualFeederConfig']['nodes'])):
					if nodes[n]['nodenumber'] == nodenumber:
						targetnode = nodes[n]
						break;

				assert 'DERParameters' in targetnode and \
				'default' in targetnode['DERParameters'], """
				Can't find the DERParameters accoding to the given nodenumber"""

				targetnode['DERParameters']['default'].pop('LVRT')
		except:
			GlobalData.log()
#===================================================================================================
	def add_HVRT(self,nodenumber,HVRTkey,V_threshold,t_threshold,mode):
		"""Each inputs of the HVRT except nodenumber should be a list such that the entries in 
		the list index should match.
		for ex:HVRTkey=["1","2"],V_threshold=[0.6,0.7],t_threshold=[1.0,1.0],
		mode=['mandatory_operation','mandatory_operation'] 
		implies HVRT 1 and 2 are attached to transmission bus [nodenumber] and that HVRTs
		will operate as mandatory operation with V and t threshholds"""
		try:
			assert 'openDSSConfig' in self.data and \
			'manualFeederConfig' in self.data['openDSSConfig'] and \
			'nodes' in self.data['openDSSConfig']['manualFeederConfig'],"""
			Please use add_manualfeederconfig method to define nodes at which solar is present
			before running this method."""

			nodes=self.data['openDSSConfig']['manualFeederConfig']['nodes']
			targetnode={}
			for n in range(len(self.data['openDSSConfig']['manualFeederConfig']['nodes'])):
				if nodes[n]['nodenumber'] == nodenumber:
					targetnode = nodes[n]
					break;
			
			assert 'DERParameters' in targetnode and \
			'default' in targetnode['DERParameters'], """
			Can't find the DERParameters accoding to the given nodenumber"""
			
			default=targetnode['DERParameters']['default']
			HVRT = default['HVRT'] = {} #overwrite even if previous data exists
			
			for i in range(len(HVRTkey)):
				HVRT[HVRTkey[i]] = {}
				HVRT[HVRTkey[i]]['V_threshold'] = V_threshold[i]
				HVRT[HVRTkey[i]]['t_threshold'] = t_threshold[i]
				HVRT[HVRTkey[i]]['mode'] = mode[i]
		except:
			GlobalData.log()

#===================================================================================================
	def remove_HVRT(self,nodenumber):
		"""Remove HVRT of a given nodenumber (nodeID/busID/busNumber)"""
		try:
			if 'openDSSConfig' in self.data and \
			'manualFeederConfig' in self.data['openDSSConfig'] and \
			'nodes' in self.data['openDSSConfig']['manualFeederConfig']:

				nodes=self.data['openDSSConfig']['manualFeederConfig']['nodes']
				targetnode={}
				for n in range(len(self.data['openDSSConfig']['manualFeederConfig']['nodes'])):
					if nodes[n]['nodenumber'] == nodenumber:
						targetnode = nodes[n]
						break;
				assert 'DERParameters' in targetnode and \
				'default' in targetnode['DERParameters'], """
				Can't find the DERParameters accoding to the given nodenumber"""

				targetnode['DERParameters']['default'].pop('HVRT')
		except:
			GlobalData.log()
#===================================================================================================
	def add_PVPlacement(self,nodenumber,PVPlacementkey,derId,powerRating,pvderScale):
		"""Each inputs of the PVPlacement except nodenumber should be a list such that the entries in 
		the list index should match.
		for ex:PVPlacementkey=["25","13"],derId=[50,50],powerRating=[50,50],
		pvderScale=[1,1] 
		implies DER will attached to distribution node 25 and 13 in transmission bus [nodenumber] 
		and that the both DER will operate as DER setting as DERid 50, powerRating 50, and pvderScale 1"""
		try:
			assert 'openDSSConfig' in self.data and \
			'manualFeederConfig' in self.data['openDSSConfig'] and \
			'nodes' in self.data['openDSSConfig']['manualFeederConfig'],"""
			Please use add_manualfeederconfig method to define nodes at which solar is present
			before running this method."""

			nodes=self.data['openDSSConfig']['manualFeederConfig']['nodes']
			targetnode={}
			for n in range(len(self.data['openDSSConfig']['manualFeederConfig']['nodes'])):
				if nodes[n]['nodenumber'] == nodenumber:
					targetnode = nodes[n]
					break;

			assert 'DERParameters' in targetnode, """
			Can't find the DERParameters accoding to the given nodenumber"""
			
			DERParameters=targetnode['DERParameters']
			PVPlacement = DERParameters['PVPlacement'] = {} #overwrite even if previous data exists
			
			for i in range(len(PVPlacementkey)):
				PVPlacement[PVPlacementkey[i]] = {}
				PVPlacement[PVPlacementkey[i]]['derId'] = derId[i]
				PVPlacement[PVPlacementkey[i]]['powerRating'] = powerRating[i]
				PVPlacement[PVPlacementkey[i]]['pvderScale'] = pvderScale[i]

		except:
			GlobalData.log()

#===================================================================================================
	def remove_HVRT(self,nodenumber):
		"""Remove HVRT of a given nodenumber (nodeID/busID/busNumber)"""
		try:
			if 'openDSSConfig' in self.data and \
			'manualFeederConfig' in self.data['openDSSConfig'] and \
			'nodes' in self.data['openDSSConfig']['manualFeederConfig']:

				nodes=self.data['openDSSConfig']['manualFeederConfig']['nodes']
				targetnode={}
				for n in range(len(self.data['openDSSConfig']['manualFeederConfig']['nodes'])):
					if nodes[n]['nodenumber'] == nodenumber:
						targetnode = nodes[n]
						break;

				assert 'DERParameters' in targetnode, """
				Can't find the DERParameters accoding to the given nodenumber"""

				targetnode['DERParameters'].pop('PVPlacement')
		except:
			GlobalData.log()
#===================================================================================================
	def add_simulationconfig(self,simType,protocol='loose_coupling',memoryThreshold=100.0):
		try:
			if 'simulationConfig' not in self.data:
				self.data['simulationConfig']={}
			simConf=self.data['simulationConfig']
			simConf['simType']=simType
			simConf['protocol']=protocol
			simConf['memoryThreshold']=memoryThreshold
		except:
			GlobalData.log()

#===================================================================================================
	def remove_simulationconfig(self):
		try:
			self.data.pop('simulationConfig')
		except:
			GlobalData.log()

#===================================================================================================
	def add_loadshape(self,loadShape):
		try:
			if 'simulationConfig' not in self.data:
				self.data['simulationConfig']={}
			self.data['simulationConfig']['staticConfig']={}
			self.data['simulationConfig']['staticConfig']['loadShape']=loadShape
		except:
			GlobalData.log()

#===================================================================================================
	def remove_loadshape(self):
		try:
			self.data['simulationConfig']['staticConfig'].pop('loadShape')
		except:
			GlobalData.log()

#===================================================================================================
	def add_fault(self,faultBus,faultImpedance,faultOnTime,faultOffTime):
		try:
			if 'simulationConfig' not in self.data:
				self.data['simulationConfig']={}

			if 'dynamicConfig' not in self.data['simulationConfig']:
				self.data['simulationConfig']['dynamicConfig']={}
				self.data['simulationConfig']['dynamicConfig']['events']={}

			events=self.data['simulationConfig']['dynamicConfig']['events']

			if events.keys():
				prevEvents=[]
				for entry in events.keys():
					prevEvents.append(int(entry))
			else:
				prevEvents=[0]
			nextEvent=max(prevEvents)+1

			events[str(nextEvent)]={}
			events[str(nextEvent)]['time'],events[str(nextEvent)]['faultBus'],\
			events[str(nextEvent)]['faultImpedance']=faultOnTime,faultBus,faultImpedance
			events[str(nextEvent)]['type']='faultOn'
			
			events[str(nextEvent+1)]={}
			events[str(nextEvent+1)]['time']=faultOffTime
			events[str(nextEvent+1)]['faultBus']=faultBus
			events[str(nextEvent+1)]['type']='faultOff'
		except:
			GlobalData.log()

#===================================================================================================
	def remove_fault(self,faultBus,faultOnTime,faultOffTime):
		try:
			events=self.data['simulationConfig']['dynamicConfig']['events']

			popID=[]
			for entry in events:
				if events[entry]['faultBus']==faultBus and events[entry]['type']=='faultOn' and \
				events[entry]['time']==faultOnTime:
					popID.append(entry)
				if events[entry]['faultBus']==faultBus and events[entry]['type']=='faultOff' and \
				events[entry]['time']==faultOffTime:
					popID.append(entry)

			for entry in popID:
				events.pop(entry)
		except:
			GlobalData.log()

#===================================================================================================
	def add_simend(self,simEndTime):
		try:
			if 'simulationConfig' not in self.data:
				self.data['simulationConfig']={}
			if 'dynamicConfig' not in self.data['simulationConfig']:
				self.data['simulationConfig']['dynamicConfig']={}
			if 'events' not in self.data['simulationConfig']['dynamicConfig']:
				self.data['simulationConfig']['dynamicConfig']['events']={}

			events=self.data['simulationConfig']['dynamicConfig']['events']
			if events.keys():
				prevEvents=[]
				for entry in events.keys():
					prevEvents.append(int(entry))
			else:
				prevEvents=[0]
			nextEvent=max(prevEvents)+1
			
			events[nextEvent]={}
			events[nextEvent]['type']='simEnd'
			events[nextEvent]['time']=simEndTime
		except:
			GlobalData.log()

#===================================================================================================
	def remove_simend(self):
		try:
			assert 'events' in self.data['simulationConfig']['dynamicConfig'],"add events first"
			events=self.data['simulationConfig']['dynamicConfig']['events']

			for entry in events:
				if events[entry]['type']=='simEnd':
					events.pop(entry)
		except:
			GlobalData.log()

#===================================================================================================
	def add_outputconfig(self,outputDir,simID=None,outputFileName='report.xlsx',outputFileType='xlsx'):
		try:
			if not simID:
				simID=uuid.uuid4().hex
			if 'outputConfig' not in self.data:
				self.data['outputConfig']={}
			self.data['outputConfig']['outputDir']=outputDir
			self.data['outputConfig']['simID']=simID
			self.data['outputConfig']['outputfilename']=outputFileName
			self.data['outputConfig']['type']=outputFileType
		except:
			GlobalData.log()

#===================================================================================================
	def remove_outputconfig(self):
		try:
			self.data.pop('outputConfig')
		except:
			GlobalData.log()

#===================================================================================================
	def write(self,fpath):
		"""Will write the configuration data in self.data to the given filename."""
		try:
			if not os.path.exists(os.path.dirname(fpath)):
				os.system('mkdir {}'.format(os.path.dirname(fpath)))
			json.dump(self.data,open(fpath,'w'),indent=3)
		except:
			GlobalData.log()

#===================================================================================================
	def read(self,fpath):
		"""Will load the config data from an existing config file.
		Use this method to make modifications to an existing file.
		P.S. This will overwrite self.data."""
		try:
			self.data=json.load(open(fpath))
		except:
			GlobalData.log()

#===================================================================================================
	def show(self):
		"""Will print out the configuration data in self.data"""
		try:
			pprint(self.data)
		except:
			GlobalData.log()

#===================================================================================================
	def validate(self):
		"""Validates if the provided settings are valid.
		P.S. Validity in this context simply means that the provided options
		satisfy the minimum requirements. When the config options are validated
		by this method it does not mean that the cosimulation will run without
		errors. For instance, this method does not verify, if a given filepath
		exists.
		
		P.S. This method will not find the issues when used in optimized mode
		i.e. python -O foo.py or python -OO foo.py
		
		Sample call: self.validate() will return without error when config is correct."""
		try:
			#join is used for better formatting while using GlobalData.log()
			assert 'cosimHome' in self.data and self.data['cosimHome'],\
			''.join(['cosimHome missing.\n','Please use add_cosimhome'])

			assert 'psseConfig' in self.data,\
			''.join(['psseConfig key is missing.\n','Please add pssConfig'])

			assert 'installLocation' in self.data['psseConfig'] and \
			'rawFilePath' in self.data['psseConfig'] and \
			'dyrFilePath' in self.data['psseConfig'],\
			''.join(['psse properties are missing.\n','Please add pssConfig properties'])

			assert ('defaultFeederConfig' in self.data['openDSSConfig'] and \
			len(self.data['openDSSConfig']['defaultFeederConfig'])>0) or \
			len(self.data['openDSSConfig']['manualFeederConfig'])>0,\
			''.join(['Either default feeder config or manual feeder config should be set.\n',\
			'Use add_defaultfeederconfig or add_manualfeederconfig.'])

			assert 'simulationConfig' in self.data,\
			''.join(['simulation config missing.\n',\
			'Use add_simulationconfig method to add simulation config.'])

			assert 'simType' in self.data['simulationConfig'],\
			''.join(['Simulation type missing.\n',\
			'Use add_simulationconfig method to define simulation type.'])

			assert 'outputConfig' in self.data,\
			''.join(['output config not set.\n',\
			'Use add_outputconfig method to set it.'])
			
			return True
		except:
			GlobalData.log()
			return False


