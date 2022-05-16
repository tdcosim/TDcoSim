import os
import json
import pdb
import inspect

import tdcosim
from tdcosim.model.opendss.opendss_server import OpenDSSServer
from tdcosim.model.opendss.opendss_data import OpenDSSData
from tdcosim.global_data import GlobalData


class OpenDSSModel(object):
#===================================================================================================
	def __init__(self):
		try:
			self._opendss_server = OpenDSSServer()
		except:
			OpenDSSData.log()

#===================================================================================================
	def setup(self,adjustOpPoint=True):
		try:
			# Either map based on manual feeder config, if false, then do auto feeder map
			DNet=GlobalData.data['DNet']
			DNet['Nodes'] = {}
			TNet=GlobalData.data['TNet']
			openDSSConfig=GlobalData.config['openDSSConfig']

			if 'defaultFeederConfig' in openDSSConfig:
				openDSSConfig['manualFeederConfig']={'nodes':[]}

				if 'excludenode' not in openDSSConfig['defaultFeederConfig']:
					openDSSConfig['defaultFeederConfig']['excludenode']=[]

				for thisNode in set(TNet['LoadBusNumber']).difference(\
				openDSSConfig['defaultFeederConfig']['excludenode']):
					thisEntry={'nodenumber':thisNode}
					for item in openDSSConfig['defaultFeederConfig']:
						thisEntry[item]=openDSSConfig['defaultFeederConfig'][item]
					openDSSConfig['manualFeederConfig']['nodes'].append(thisEntry)

			if 'manualFeederConfig' in openDSSConfig and \
			'nodes' in openDSSConfig['manualFeederConfig'] and \
			openDSSConfig['manualFeederConfig']['nodes']:
				totalSolarGen=0; reductionPercent=0

				for entry in openDSSConfig['manualFeederConfig']['nodes']:
					if 'solarFlag' not in entry:####
						entry['solarFlag']=0
					if 'solarPenetration' not in entry:####
						entry['solarPenetration']=0.0
					if 'interconnectionStandard' not in entry:
						entry['interconnectionStandard']={'ieee_2018_category_2':1.0}

					DNet['Nodes'][entry['nodenumber']]={}
					DNet['Nodes'][entry['nodenumber']]['filepath'] = entry['filePath'][0]
					if 'solarFlag' in entry and entry['solarFlag']==1:
						if 'DEROdeSolver' in openDSSConfig:
							entry['DEROdeSolver'] = openDSSConfig['DEROdeSolver']
						if 'DEROdeMethod' in openDSSConfig:
						 	entry['DEROdeMethod'] = openDSSConfig['DEROdeMethod']
						self.setDERParameter(entry, entry['nodenumber'])
						entry['DERParameters']['default']['solarFlag']=entry['solarFlag']
						entry['DERParameters']['default']['solarPenetration']=entry['solarPenetration']
					if adjustOpPoint:
						totalSolarGen+=TNet['BusRealPowerLoad'][entry['nodenumber']]*\
						entry['solarPenetration']
					if 'fractionAggregatedLoad' in entry:
						DNet['Nodes'][entry['nodenumber']]['fractionAggregatedLoad']=\
						entry['fractionAggregatedLoad']
				if adjustOpPoint:
					reductionPercent=totalSolarGen/TNet['TotalRealPowerLoad']
			else:
				reductionPercent=0

			DNet['ReductionPercent'] = reductionPercent

			for entry in DNet['Nodes'].keys():
				if 'logging' in GlobalData.config and \
				'saveSubprocessOutErr' in GlobalData.config['logging'] and \
				GlobalData.config['logging']['saveSubprocessOutErr']:
					baseDir=os.path.dirname(inspect.getfile(tdcosim))
					DNet['Nodes'][entry]['f_out']=open(os.path.join(baseDir,'logs',\
					'dss_out_{}.txt'.format(entry)),'w')
					DNet['Nodes'][entry]['f_err']=open(os.path.join(baseDir,'logs',\
					'dss_err_{}.txt'.format(entry)),'w')
				else:
					DNet['Nodes'][entry]['f_out']=DNet['Nodes'][entry]['f_err']=open(os.devnull,'w')
				self._opendss_server.connect_opendssclient(entry)
		except:
			OpenDSSData.log()

#===================================================================================================
	def initialize(self, targetS, Vpcc):
		try:
			power = self._opendss_server.initialize(targetS, Vpcc)
			return power
		except:
			OpenDSSData.log()

#===================================================================================================
	def setVoltage(self, Vpcc):
		self._opendss_server.setVoltage(Vpcc)

#===================================================================================================
	def getLoad(self,pccName='Vsource.source',t=None,dt=1/120.):
		try:
			S = self._opendss_server.getLoad(pccName=pccName,t=t,dt=dt)
			return S
		except:
			OpenDSSData.log()

#===================================================================================================
	def scaleLoad(self,scale):
		try:
			self._opendss_server.scaleLoad(scale)
			return None
		except:
			OpenDSSData.log()

#===================================================================================================
	def monitor(self,msg):
		try:
			reply=self._opendss_server.monitor(msg)
			return reply
		except:
			OpenDSSData.log()

#===================================================================================================
	def computeStep(self,Vpu,monitor,pccName='Vsource.source',t=None,dt=1/120.):
		try:
			S,monData=self._opendss_server.computeStep(Vpu=Vpu,monitor=monitor,pccName=pccName,t=t,dt=dt)
			return S,monData
		except:
			OpenDSSData.log()

#===================================================================================================
	def is_float(self, n):
		try:
			float(n)# Type-casting the string to `float`.
						# If string is not a valid `float`, 
						# it'll raise `ValueError` exception
		except ValueError:
			return False
		return True

#===================================================================================================
	def setDERParameter(self, entry, nodenumber):
		try:
			baseDir=os.path.dirname(inspect.getfile(tdcosim))
			defaults=json.load(open(os.path.join(baseDir,'config','der_defaults.json')))
			DNet=GlobalData.data['DNet']
			
			for item in defaults:
				if item not in entry:
					entry[item]=defaults[item]

			for item in defaults['DERParameters']:
				if item not in entry['DERParameters']:
					entry['DERParameters'][item]=defaults['DERParameters'][item]

			for item in defaults['DERParameters']['default']:
				if item not in entry['DERParameters']['default']:
					entry['DERParameters']['default'][item]=defaults['DERParameters']['default'][item]

			if entry['DERSetting'] == 'PVPlacement' and 'PVPlacement' in entry['DERParameters']:
				for node in entry['DERParameters']['PVPlacement']:
					if 'VrmsRating' not in entry['DERParameters']['PVPlacement'][node]:
						entry['DERParameters']['PVPlacement'][node]['VrmsRating']=\
						entry['DERParameters']['default']['VrmsRating']

			DNet['Nodes'][nodenumber]['solarFlag']= bool(entry['solarFlag'])
			DNet['Nodes'][nodenumber]['solarPenetration']= entry['solarPenetration']

			for key in entry['DERParameters']:
				#PYTHON3: isinstance(entry['DERParameters'][key], str)
				if isinstance(entry['DERParameters'][key], str):
					if entry['DERParameters'][key].lower() == 'true':
						DNet['Nodes'][nodenumber][key] = True
					elif entry['DERParameters'][key].lower() == 'false':
						DNet['Nodes'][nodenumber][key] = False
					elif self.is_float(entry['DERParameters'][key]):
						DNet['Nodes'][nodenumber][key] = float(entry['DERParameters'][key])
					else:
						DNet['Nodes'][nodenumber][key] = entry['DERParameters'][key]
				else:
					DNet['Nodes'][nodenumber][key] = entry['DERParameters'][key]
		except:
			OpenDSSData.log()

#===================================================================================================
	def close(self):
		try:
			ack = self._opendss_server.close()
			return ack
		except:
			OpenDSSData.log()



