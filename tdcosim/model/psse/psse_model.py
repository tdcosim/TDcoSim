import sys
import os
import re
import pdb
import json
import copy
import uuid

import six
import numpy as np

from tdcosim.global_data import GlobalData
from tdcosim.model.psse.dera import Dera


class PSSEModel(Dera):
	def __init__(self):
		try:
			super(PSSEModel,self).__init__()
			if "installLocation" in GlobalData.config['psseConfig'] and \
			os.path.exists(os.path.join(GlobalData.config['psseConfig']['installLocation'],'psspy.pyc')):
				pssePath = GlobalData.config['psseConfig']['installLocation']
			sys.path.insert(0,pssePath)
			os.environ['PATH']+=';'+pssePath
			import psspy

			# psse
			self._psspy=psspy
			ierr=self._psspy.psseinit(0); assert ierr==0
			ierr=self._psspy.report_output(6,'',[]); assert ierr==0
			ierr=self._psspy.progress_output(6,'',[]); assert ierr==0
			outputFilePath=os.path.join(GlobalData.config['outputConfig']['outputDir'],'psse_progress_output.txt')
			ierr=self._psspy.progress_output(2,outputFilePath,0); assert ierr==0

			ierr=self._psspy.alert_output(6,'',[]); assert ierr==0
			ierr=self._psspy.prompt_output(6,'',[]); assert ierr==0

			self.faultmap = {}
			self.faultindex = 1
			baseDir=os.path.dirname(os.path.dirname(os.path.dirname(\
			os.path.dirname(os.path.abspath(__file__)))))
			self.__cmld_rating_default=json.load(open(os.path.join(baseDir,'config',\
			'composite_load_model_rating.json')))
			self.__dera_rating_default=json.load(open(os.path.join(baseDir,'config',\
			'dera_rating.json')))
			self.__model_state_var_ind=json.load(open(os.path.join(baseDir,'config',\
			'psse_machine_state_var_ind.json')))
			self.__model_state_var_ind['outputFilePath']=outputFilePath
		except:
			GlobalData.log()

#===================================================================================================
	def setup(self, adjustOpPoint=True):
		try:
			# psspy info
			self._monitorID={}
			self._monitorID['angle'] = 1
			self._monitorID['pelec'] = 2
			self._monitorID['qelec'] = 3
			self._monitorID['eterm'] = 4
			self._monitorID['efd'] = 5
			self._monitorID['pmech'] = 6
			self._monitorID['speed'] = 7
			self._monitorID['xadifd'] = 8
			self._monitorID['ecomp'] = 9
			self._monitorID['volt'] = 13
			self._monitorID['pload'] = 25
			self._monitorID['qload'] = 26
		
			# load psse case
			ierr = self._psspy.read(0,GlobalData.config['psseConfig']['rawFilePath'].encode("ascii",
			"ignore"))
			assert ierr==0,"Reading raw file failed with error {}".format(ierr)
			ierr, nLoads = self._psspy.alodbuscount()
			assert ierr==0,"load bus count failed with error {}".format(ierr)
			GlobalData.data['TNet']['LoadBusCount'] = nLoads
			# default. Will connect dist syst feeder to all load buses
			ierr, loadBusNumber = self._psspy.alodbusint(string='NUMBER')
			assert ierr==0,"load bus number failed with error {}".format(ierr)
			GlobalData.data['TNet']['LoadBusNumber'] = loadBusNumber[0]

			if adjustOpPoint:# need to adjust operation point
				# find total load
				GlobalData.data['TNet']['TotalRealPowerLoad'] = 0
				GlobalData.data['TNet']['BusRealPowerLoad'] = {}
			
				ierr,S = self._psspy.alodbuscplx(string='MVAACT')
				assert ierr==0,"Reading bus complex load failed with error {}".format(ierr)

				for entry,val in zip(GlobalData.data['TNet']['LoadBusNumber'],S[0]):
					GlobalData.data['TNet']['TotalRealPowerLoad'] += val.real
					GlobalData.data['TNet']['BusRealPowerLoad'][entry]=val.real
		except:
			GlobalData.log()

#===================================================================================================
	def convert_loads(self,conf=None,loadType='zip',avoidBus=None,prefix=None):
		try:
			if not avoidBus:
				avoidBus=GlobalData.data['DNet']['Nodes'].keys()

			if loadType.lower()=='zip':
				GlobalData.logger.info('converting all loads at to ZIP load')
				if not conf:
					conf={'conl':{'all':1,'apiopt':1,'status':[0,0],'loadin':[.3,.4,.3,.4]}}
				assert 'conl' in conf
				ierr,_=self._psspy.conl(**conf['conl'])# initialize
				assert ierr==0,"psspy.conl failed with error {}".format(ierr)

				conf['conl'].update({'apiopt':2})
				ierr,_=self._psspy.conl(**conf['conl'])# convert
				assert ierr==0,"psspy.conl failed with error {}".format(ierr)

				conf['conl'].update({'apiopt':3})
				ierr,_=self._psspy.conl(**conf['conl'])# convert
				assert ierr==0,"psspy.conl failed with error {}".format(ierr)

			elif loadType.lower()=='complex_load' or loadType.lower()=='complexload':
				# get load info
				ierr,loadBusNumber=self._psspy.aloadint(-1,1,'NUMBER')
				assert ierr==0,'psspy.aloadint failed with error {}'.format(ierr)
				loadBusNumber=loadBusNumber[0]
				defaultVal=[.2,.2,.2,.2,.1,2,.04,.08]
			
				# write
				if not prefix:
					prefix=["'CLODBL'",1]
				tempCMLDDyrFile='tempCMLDDyrFile.dyr'
				f=open(tempCMLDDyrFile,'w')

				for thisBus in loadBusNumber:
					if thisBus not in avoidBus:
						GlobalData.logger.info('converting load at {} to complex load (CLODBL)'.format(thisBus))
						thisData=[thisBus]+prefix+defaultVal
						thisStr=''; thisLineLen=0
						for thisItem in thisData:
							thisStr+='{}'.format(thisItem)+','
							thisLineLen+=len('{}'.format(thisItem)+',')
							if thisLineLen>180:# break long lines so that PSSE can read without error
								thisStr+='\n'
								thisLineLen=0
						f.write(thisStr[0:-1]+' /\n')
				f.close()

				# load cmld file
				ierr=self._psspy.dyre_add(dyrefile=tempCMLDDyrFile.encode("ascii", "ignore"))
				assert ierr==0,"Adding dyr file failed with error {}".format(ierr)
				os.system('del {}'.format(tempCMLDDyrFile))

			elif loadType.lower()=='composite_load' or loadType.lower()=='compositeload' \
			or loadType.lower()=='cmld':
				# get load info
				ierr,loadBusNumber=self._psspy.aloadint(-1,1,'NUMBER')
				assert ierr==0,'psspy.aloadint failed with error {}'.format(ierr)
				loadBusNumber=loadBusNumber[0]
				default=self.__cmld_rating_default['default']
				if 'cmldParameters' in GlobalData.config['psseConfig'] and GlobalData.config['psseConfig']['cmldParameters']:
					cmldParameters=GlobalData.config['psseConfig']['cmldParameters']
					cmldParametersKeys=cmldParameters.keys()
					if six.PY3:
						cmldParametersKeys=list(cmldParametersKeys)
					for unknownParam in set(cmldParametersKeys).difference(default.keys()):
						cmldParameters.pop(unknownParam)
					default.update(cmldParameters)

				ind2name=self.__cmld_rating_default['ind2name']
				defaultVal=[default[ind2name[str(n)]] for n in range(len(default))]
				if not prefix and self._psspy.psseversion()[1]>=35:
					prefix=["'USRLOD'",'1',"'CMLDBLU2'",12,1,2,133,27,146,48,0,0]
				elif not prefix and self._psspy.psseversion()[1]<35:
					prefix=["'USRLOD'",'1',"'CMLDBLU1'",12,1,0,132,27,146,48]
				if self._psspy.psseversion()[1]<35:
					defaultVal=defaultVal[1:-1]

				tempCMLDDyrFile='tempCMLDDyrFile.dyr'
				f=open(tempCMLDDyrFile,'w')

				for thisBus in set(loadBusNumber).difference(avoidBus):
					thisData=[thisBus]+prefix+defaultVal
					thisStr=''; thisLineLen=0
					for thisItem in thisData:
						thisStr+='{}'.format(thisItem)+','
						thisLineLen+=len('{}'.format(thisItem)+',')
						if thisLineLen>180:# break long lines so that PSSE can read without error
							thisStr+='\n'
							thisLineLen=0
					f.write(thisStr[0:-1]+' /\n')
				f.close()

				# load cmld file
				ierr=self._psspy.dyre_add(dyrefile=tempCMLDDyrFile.encode("ascii", "ignore"))
				assert ierr==0,"Adding dyr file failed with error {}".format(ierr)
				os.system('del {}'.format(tempCMLDDyrFile))
		except:
			GlobalData.log()


#===================================================================================================
	def dynamicInitialize(self,adjustOpPoint=True):
		try:
			if 'defaultLoadType' in GlobalData.config['simulationConfig']:
				defaultLoadType=GlobalData.config['simulationConfig']['defaultLoadType']
			else:
				defaultLoadType='zip'
			if adjustOpPoint:
				S = self._adjustSystemOperatingPoint(defaultLoadType=defaultLoadType)
			else:
				ierr=self._psspy.dyre_new([1,1,1,1],self.config['psseConfig']['dyrFilePath'].encode("ascii",
				"ignore"))
				assert ierr==0,"psspy.dyre_new failed with error {}".format(ierr)
				self.convert_loads(loadType=defaultLoadType)

			# run power flow
			ierr=self._psspy.fnsl()
			assert ierr==0,"fnsl with error {}".format(ierr)
			Vpcc=self.getVoltage()

			ierr=self._psspy.cong(1); assert ierr==0
			GlobalData.data['dynamic']['channel'] = {}
			nMonVars=0
			ierr,nGenBus=self._psspy.agenbuscount(-1,1); assert ierr==0
			ierr,nBus=self._psspy.abuscount(-1,1); assert ierr==0
			ierr,nLoad=self._psspy.aloadcount(-1,1); assert ierr==0
			ierr,genBusNumber=self._psspy.agenbusint(-1,1,'NUMBER'); assert ierr==0
			genBusNumber=genBusNumber[0]
			ierr,busNumber=self._psspy.abusint(string='NUMBER'); assert ierr==0
			busNumber=busNumber[0]
			ierr,loadBusNumber=self._psspy.aloadint(-1,1,'NUMBER'); assert ierr==0
			loadBusNumber=loadBusNumber[0]
			for item in ['angle','speed','pelec','qelec','pmech']:
				ierr=self._psspy.chsb(sid=0,all=1,status=[-1,-1,-1,1,self._monitorID[item],0])
				assert ierr==0
				GlobalData.data['dynamic']['channel'][item]={}
				for channelID,node in zip(range(nMonVars+1,nMonVars+1+nGenBus),genBusNumber):# psse uses 1 ind
					GlobalData.data['dynamic']['channel'][item][channelID]=node
				nMonVars+=nGenBus

			ierr=self._psspy.chsb(sid=0,all=1,status=[-1,-1,-1,1,self._monitorID['volt'],0])
			assert ierr==0
			GlobalData.data['dynamic']['channel']['volt']={}
			for channelID,node in zip(range(nMonVars+1,nMonVars+1+nBus),busNumber):# psse uses 1 ind
				GlobalData.data['dynamic']['channel']['volt'][channelID]=node
			nMonVars+=nBus

			for item in ['pload','qload']:
				ierr=self._psspy.chsb(sid=0,all=1,status=[-1,-1,-1,1,self._monitorID[item],0])
				assert ierr==0
				GlobalData.data['dynamic']['channel'][item]={}
				for channelID,node in zip(range(nMonVars+1,nMonVars+1+nLoad),loadBusNumber):# psse uses 1 ind
					GlobalData.data['dynamic']['channel'][item][channelID]=node
				nMonVars+=nLoad

			# compute initial conditions
			outputConfig=GlobalData.config['outputConfig']
			if not 'outputDir' in outputConfig:
				outputConfig['outputDir']=os.getcwd()
			if '.' in outputConfig['outputfilename']:# remove file extension
				outputConfig['outputfilename']=outputConfig['outputfilename'].split('.')[0]

			if '.out' not in outputConfig['outputfilename']:
				outputConfig['outputfilename']+='.out'

			outfile=os.path.join(outputConfig['outputDir'],outputConfig['outputfilename'])
			if six.PY2 and isinstance(outfile,unicode):
				outfile=outfile.encode('ascii','ignore')
			GlobalData.logger.log(10,'outfile:{}'.format(outfile))

			ierr=self._psspy.strt(outfile=outfile)
			assert ierr==0,"psspy.strt failed with error {}".format(ierr)

			targetS={}
			for entry,val in zip(GlobalData.data['TNet']['LoadBusNumber'],S[0]):
				if entry in GlobalData.data['DNet']['Nodes']:
					targetS[entry]=[val.real*10**3,val.imag*10**3] # convert to kw/kvar from mw/mvar

			# update targetS, if "fractionAggregatedLoad" is set for T-D interface nodes
			openDSSConfig=GlobalData.config['openDSSConfig']
			if 'manualFeederConfig' in openDSSConfig:
				if 'nodes' in openDSSConfig['manualFeederConfig']:
					for entry in openDSSConfig['manualFeederConfig']['nodes']:
						if 'fractionAggregatedLoad' in entry:
							# if more than one load identifier is present, then feeder will
							# be interfaced by default to load identifier "1"
							ierr,val=self._psspy.loddt2(entry['nodenumber'],'1','TOTAL','ACT')
							assert ierr==0,"loddt2 failed with error {}".format(ierr)
							if six.PY2:
								thisAggregatedLoadType=entry['fractionAggregatedLoad'].keys()[0]
							elif six.PY3:
								thisAggregatedLoadType=list(entry['fractionAggregatedLoad'].keys())[0]
							targetS[entry['nodenumber']]=[val.real*10**3,val.imag*10**3]

			return targetS,Vpcc
		except:
			GlobalData.log()

#===================================================================================================
	def _adjustSystemOperatingPoint(self,defaultLoadType='complex_load'):
		try:
			GlobalData.logger.debug('GlobalData.data["DNet"]={}'.format(GlobalData.data['DNet']))
			offset=3
			reductionPercent=GlobalData.data['DNet']['ReductionPercent']
			ind={}
			ind['GENCLS']=0
			ind['GENDCO']=4
			ind['GENROE']=4
			ind['GENROU']=4
			ind['GENSAE']=3
			ind['GENSAL']=3
			ind['GENTPJU1']=4
			ind['GENTRA']=1

			dyrPath=GlobalData.config['psseConfig']['dyrFilePath'].encode("ascii", "ignore")
			f=open(dyrPath)
			dyrData=f.read().splitlines()
			f.close()

			dyrDataStr=''; Zr={}; Zx={}
			for line in dyrData:
				line=line.lstrip().rstrip()
				if line[-1]==r'/':
					line=line[0:-1]
				if "," not in line:
					line=re.sub('\s{1,}',',',line)
				entry=line.split(',')
				for item in ind:
					if entry[1]=="'{}'".format(item):
						entry[offset+ind[item]]=\
						str(float(entry[offset+ind[item]])*(1-reductionPercent))
						break
				dyrDataStr+=','.join(entry+['\n'])

			dyrPath=dyrPath.decode() if isinstance(dyrPath,bytes) else dyrPath
			tempDyrPath=dyrPath.split('.dyr')[0]+'_temp.dyr'
			tempDyrPath=os.path.abspath(tempDyrPath)
			if six.PY2 and isinstance(tempDyrPath,unicode):
				tempDyrPath=tempDyrPath.encode('ascii','ignore')
			f=open(tempDyrPath,'w')
			f.write(dyrDataStr)
			f.close()
			
			# now read raw file to get Zr and Zx
			f=open(GlobalData.config['psseConfig']['rawFilePath'].encode("ascii", "ignore"))
			rawFileData=f.read().splitlines()
			f.close()
			
			readFlg=False
			for line in rawFileData:
				if "END OF GENERATOR DATA" in line:
					readFlg=False
				if readFlg:
					entry=line.split(',')
					Zr[int(entry[0])]=float(entry[9])
					Zx[int(entry[0])]=float(entry[10])
				if "BEGIN GENERATOR DATA" in line:
					readFlg=True

			# make changes in machine data through psse internal data structure
			m=macVarMap={}
			m['PGEN']=0
			m['QGEN']=1
			m['QMAX']=2
			m['QMIN']=3
			m['PMAX']=4
			m['PMIN']=5
			m['MBASE']=6

			# read dyr file
			ierr=self._psspy.dyre_new([1,1,1,1],tempDyrPath)
			assert ierr==0
			GlobalData.log(level=20,msg='read modified dyr file {}'.format(tempDyrPath))
			os.system('del {}'.format(tempDyrPath))

			# get machine data
			macVarData={}
			for entry in macVarMap:
				ierr,macVarData[entry]=self._psspy.amachreal(sid=-1, flag=1, string=entry)# get data
				assert ierr==0,"reading machine data failed with error {}".format(ierr)

			ierr,genBusNumber=self._psspy.agenbusint(-1,1,'NUMBER') # get gen bus number
			assert ierr==0
			genBusNumber=genBusNumber[0]

			# change machine data
			for n in range(len(genBusNumber)):# make changes at each gen
				macVarDataNew=[0.]*11+[1.]*6
				for entry in macVarData:# make changes for each variable
					# passing double precision data results in long values
					# and psspy.machine_chng_2 API fails to change data.
					# Hence, use 3 digit precision.
					macVarDataNew[macVarMap[entry]]=np.round(macVarData[entry][0][n]\
					*(1-reductionPercent),5)
				macVarDataNew[7]=np.round(Zr[genBusNumber[n]],5)
				macVarDataNew[8]=np.round(Zx[genBusNumber[n]],5)
				ierr=self._psspy.machine_chng_2(genBusNumber[n], realar=macVarDataNew)# change machine data
				assert ierr==0,"machine_chng_2 failed with error {}".format(ierr)

			# adjust load data
			ierr,S=self._psspy.alodbuscplx(string='MVAACT')
			assert ierr==0,"reading complex load failed with error {}".format(ierr)
			S=S[0]

			# convert all loads to given load type
			self.convert_loads(loadType=defaultLoadType)

			# add new loads, if configured
			ierr, systemBuses = self._psspy.abusint(sid=-1, flag=2, string='NUMBER')
			assert ierr==0,"abusint failed with error {}".format(ierr)
			systemBuses=systemBuses[0]

			busIDToAddComplexLoad={}; busIDToAddCompositeLoad={}
			if 'manualFeederConfig' in GlobalData.config['openDSSConfig'] and \
			'nodes' in GlobalData.config['openDSSConfig']['manualFeederConfig']:
				for entry in GlobalData.config['openDSSConfig']['manualFeederConfig']['nodes']:
					if 'fractionAggregatedLoad' in entry:
						for item in entry['fractionAggregatedLoad']:
							if item.lower()=='complexload' or item.lower()=='complex_load':
								busIDToAddComplexLoad[entry['nodenumber']]=\
								entry['fractionAggregatedLoad'][item]
							elif item.lower()=='compositeload' or \
							item.lower()=='composite_load' or item.lower()=='cmld':
								busIDToAddCompositeLoad[entry['nodenumber']]=\
								entry['fractionAggregatedLoad'][item]
			elif 'defaultFeederConfig' in GlobalData.config['openDSSConfig'] and \
			'fractionAggregatedLoad' in GlobalData.config['openDSSConfig']['defaultFeederConfig']:
				defaultFeederConfig=GlobalData.config['openDSSConfig']['defaultFeederConfig']
				fractionAggregatedLoad=defaultFeederConfig['fractionAggregatedLoad']
				for item in fractionAggregatedLoad:
					if item.lower()=='complexload' or item.lower()=='complex_load':
						# find all T-D interface buses
						for busID in GlobalData.data['DNet']['Nodes']:
							busIDToAddComplexLoad[busID]=fractionAggregatedLoad[item]
					elif item.lower()=='compositeload' or \
					item.lower()=='composite_load' or item.lower()=='cmld':
						# find all T-D interface buses
						for busID in GlobalData.data['DNet']['Nodes']:
							busIDToAddCompositeLoad[busID]=fractionAggregatedLoad[item]

			if busIDToAddComplexLoad or busIDToAddCompositeLoad:
				ierr,S=self._psspy.aloadcplx(sid=-1, flag=4, string='MVAACT')
				assert ierr==0,"aloadcplx failed with error {}".format(ierr)
				S=S[0]
				ierr,loadBusID=self._psspy.aloadint(sid=-1, flag=4, string='NUMBER')
				assert ierr==0,"aloadint failed with error {}".format(ierr)
				loadBusID=loadBusID[0]
				bus2SMapping={thisLoadBusID:thisS for thisLoadBusID,thisS in zip(loadBusID,S)}

			if busIDToAddComplexLoad:
				realar=[]
				for entry in busIDToAddComplexLoad:
					realar.append([bus2SMapping[entry].real*busIDToAddComplexLoad[entry],\
					bus2SMapping[entry].imag*busIDToAddComplexLoad[entry],0,0,0,0])
				loadID='2'# use load identifier as 2
				self.add_load_with_new_load_id(busID=busIDToAddComplexLoad.keys(),realar=realar,\
				loadID=[loadID]*len(busIDToAddComplexLoad.keys()))
				self.convert_loads(loadType='complex_load',\
				avoidBus=set(systemBuses).difference(busIDToAddComplexLoad.keys()),\
				prefix=["'CLODBL'",loadID])# use load identifier as 2

			if busIDToAddCompositeLoad:
				realar=[]
				for entry in busIDToAddCompositeLoad:
					realar.append([bus2SMapping[entry].real*busIDToAddCompositeLoad[entry],\
					bus2SMapping[entry].imag*busIDToAddCompositeLoad[entry],0,0,0,0])
				loadID='2'# use load identifier as 2
				self.add_load_with_new_load_id(busID=busIDToAddCompositeLoad.keys(),realar=realar,\
				loadID=[loadID]*len(busIDToAddCompositeLoad.keys()))

				if self._psspy.psseversion()[1]==35:
					prefix=["'USRLOD'",'2',"'CMLDBLU2'",12,1,2,133,27,146,48,0,0]
				elif self._psspy.psseversion()[1]<35:
					prefix=["'USRLOD'",'2',"'CMLDBLU1'",12,1,0,132,27,146,48]

				self.convert_loads(loadType='cmld',\
				avoidBus=set(systemBuses).difference(busIDToAddCompositeLoad.keys()),\
				prefix=prefix)# use load identifier as 2

			# add der_a, if configured
			conf=None
			if 'dera' in GlobalData.config['simulationConfig']:
				conf=GlobalData.config['simulationConfig']['dera']

			if conf and self._psspy.psseversion()[1]>=35:
				if 'solarPenetration' in GlobalData.config['simulationConfig']:
					solarPercentage=GlobalData.config['simulationConfig']['solarPenetration']
				else:
					solarPercentage=0.0
				self.add_dera_to_case(conf=conf,solarPercentage=solarPercentage,\
				additionalDyrFilePath='dera_{}.dya'.format(uuid.uuid4().hex))
			elif conf and self._psspy.psseversion()[1]<35:
				GlobalData.logger.warning(\
				"This version of psse ({}) does not support der_a".format(self._psspy.psseversion()))

			# update
			loadType=0
			for busID,val in zip(GlobalData.data['TNet']['LoadBusNumber'],S):
				if busID in GlobalData.data['DNet']['Nodes']:
					# constP,Q,IP,IQ,YP,YQ
					loadVal=[0]*6
					if 'solarPenetration' not in GlobalData.data['DNet']['Nodes'][busID]:
						GlobalData.data['DNet']['Nodes'][busID]['solarPenetration']=0.0
					reductionPercent=GlobalData.data['DNet']['Nodes'][busID]['solarPenetration']

					if 'fractionAggregatedLoad' in GlobalData.data['DNet']['Nodes'][busID]:
						fractionAggregatedLoadData=\
						GlobalData.data['DNet']['Nodes'][busID]['fractionAggregatedLoad']
						if six.PY2:
							thisAggregatedLoadType=fractionAggregatedLoadData.keys()[0]
						elif six.PY3:
							thisAggregatedLoadType=list(fractionAggregatedLoadData.keys())[0]
						# percentage of solar based on percentage of fractionFeederLoad
						fractionFeederLoad=1-fractionAggregatedLoadData[thisAggregatedLoadType]
						reductionPercent=reductionPercent*fractionFeederLoad
						# add fractionFeederLoad to reductionPercent
						reductionPercent+=fractionAggregatedLoadData[thisAggregatedLoadType]

					loadVal[loadType*2],loadVal[loadType*2+1]=\
					val.real*(1-reductionPercent),val.imag*(1-reductionPercent)
					ierr=self._psspy.load_chng_4(busID,'1',[1,1,1,1,1,0],loadVal)
					assert ierr==0,"load change failed with error {}".format(ierr)

			ierr,S=self._psspy.alodbuscplx(string='MVAACT')
			assert ierr==0,"reading complex load failed with error {}".format(ierr)

			return S
		except:
			GlobalData.log(msg='Failed to adjustSystemOperatingPoint from PSSEModel')

#===================================================================================================
	def add_load_with_new_load_id(self,busID,realar,loadID=None):
		try:
			if not isinstance(busID,list) and (isinstance(busID,int) or isinstance(busID,str)):
				busID=[busID]
			if not loadID:
				loadID=['2']*len(busID)

			assert len(busID)==len(realar)==len(loadID),"Input dimension mismatch"

			for thisBusID,thisRealar,thisLoadID in zip(busID,realar,loadID):
				ierr=self._psspy.load_data_4(thisBusID,thisLoadID,realar=thisRealar)
				assert ierr==0,"load_data_4 failed with error {}".format(ierr)
		except:
			GlobalData.log()

#===================================================================================================
	def staticInitialize(self):
		try:
			Vpcc=self.getVoltage()

			# scale feeder
			targetS={}
			ierr,S=self._psspy.alodbuscplx(string='MVAACT')
			assert ierr==0,"Reading load bus complex power failed with error {}".format(ierr)

			for entry,val in zip(GlobalData.data['TNet']['LoadBusNumber'],S[0]):
				if entry in GlobalData.data['DNet']['Nodes']:
					targetS[entry]=[val.real*10**3,val.imag*10**3]# convert to kw/kvar from mw/mvar

			return targetS, Vpcc
		except:
			GlobalData.log(msg='Failed to initialize from PSSEModel')

#===================================================================================================
	def getVoltage(self):
		try:
			"""Get PCC voltage from psse."""
			Vpcc={}
			# dist syst interfaced at all load buses
			if GlobalData.data['TNet']['LoadBusCount']==len(GlobalData.data['TNet']['LoadBusNumber']):
				ierr,loadBusVPU=self._psspy.alodbusreal(string='PU'); assert ierr==0
				loadBusVPU = loadBusVPU[0]
				for entry,val in zip(GlobalData.data['TNet']['LoadBusNumber'],loadBusVPU):# efficient
					if entry in GlobalData.data['DNet']['Nodes']:
						Vpcc[entry]=val
			else:# subset of loadbuses interfaced as dist syst
				for entry in GlobalData.data['TNet']['LoadBusNumber']:# not as efficient for large cases
					ierr,Vpcc[entry]=self._psspy.busdat(entry,'PU'); assert ierr==0
			return Vpcc
		except:
			GlobalData.log(msg='Failed to getVoltage from PSSEModel')

#===================================================================================================
	def setLoad(self, S,loadType=0):
		"""set PCC Pinj,Qinj for psse.
		Input: S -- dictionary containing Pinj and Qinj.
		loadType -- 0- constant power, 1-constant current, 2-constant admittance."""
		try:
			for busID in GlobalData.data['TNet']['LoadBusNumber']:
				if busID in GlobalData.data['DNet']['Nodes']:
					# constP,Q,IP,IQ,YP,YQ
					loadVal=[0]*6
					loadVal[loadType*2],loadVal[loadType*2+1]=S[busID]['P'],S[busID]['Q']
					ierr=self._psspy.load_chng_4(busID,'1',[1,1,1,1,1,0],realar=loadVal)
					assert ierr==0,"load change failed with error {}".format(ierr)
		except:
			GlobalData.log()

#===================================================================================================
	def shunt(self, targetS, Vpcc, power):
		try:
			mismatchTolerance=0.1
			GlobalData.logger.info('Input: targetS={}; Vpcc={}; power={};'.format(\
			targetS, Vpcc, power))
			for node in power:
				if abs(power[node]['P']-targetS[node][0])>mismatchTolerance or abs(
				power[node]['Q']-targetS[node][1])>mismatchTolerance:# add shunt if needed
					Pshunt = targetS[node][0]*1e-3 - power[node]['P']
					Qshunt = targetS[node][1]*1e-3 - power[node]['Q']
					# The remaining power is incorporated as compensating shunt
					# The compensating shunt power
					# Pshunt + j*Qshunt = Vpcc^2*(YPshunt - YQshunt)
					# which gives the below two equations for shunt.
					# Note the negative sign for YQshunt is because we are
					# considering admittances
					YPshunt = Pshunt/(Vpcc[node]*Vpcc[node])
					YQshunt = -Qshunt/(Vpcc[node]*Vpcc[node])
					# Add the remaining as fixed compensating shunt
					ierr = self._psspy.shunt_data(node,'1 ',1,[YPshunt,YQshunt])
					assert ierr==0,"Adding shunt failed with error {}".format(ierr)
		except:
			GlobalData.log(msg='Failed to shunt from PSSEModel')

#===================================================================================================
	def runPFLOW(self):
		try:
			ierr=self._psspy.fnsl()
			assert ierr==0,"psspy.fnsl failed with error: {}".format(ierr)
		except:
			GlobalData.log()

#===================================================================================================
	def runDynamic(self, tpause):
		try:
			ierr=self._psspy.run(tpause=tpause)
			assert ierr==0,"psspy.run failed with error: {}".format(ierr)
		except:
			GlobalData.log()

#===================================================================================================
	def faultOn(self, faultBus, faultImpedance):
		try:
			ierr=self._psspy.dist_bus_fault(faultBus,1,0.0,faultImpedance)
			assert ierr==0
			self.faultmap[faultBus] = self.faultindex
			self.faultindex = self.faultindex + 1
		except:
			GlobalData.log()

#===================================================================================================
	def faultOff(self, faultBus):
		try:
			if faultBus in self.faultmap:
				ierr=self._psspy.dist_clear_fault(self.faultmap[faultBus])
				assert ierr==0
			else:
				GlobalData.log(level=30,
				msg="Failed Fault Off, Fault was not applied to the Bus Number: {}".format(faultBus))
		except:
			GlobalData.log()

#=======================================================================================================================
	def add_dera_to_case(self,conf,rating=None,additionalDyrFilePath='dera.dya',
	solarPercentage=0,cleanup=True):
		"""Given conf and additionalDyrFilePath, this method adds dera model as an additional
		dyr/dya file that can then be read using psspy.dyre_add method. conf should be of the form
		conf={'standard':[busID]} for example conf={'1547_2003':[1,2,3]} will add dera model which
		follows IEEE 1547 2003 standard at buses 1,2 and 3. Also adds plant data at the said buses
		and changes WMOD to 1."""
		try:
			if solarPercentage>0 and not conf:# update conf to have all busIDs
				if six.PY2:
					LogUtil.logger.info(\
					'Updating conf to use {} for all load buses as solarPercentage>0'.format(conf.keys()[0]))
				elif six.PY3:
					LogUtil.logger.info(\
					'Updating conf to use {} for all load buses as solarPercentage>0'.format(list(conf.keys())[0]))
				# get load info
				ierr,loadBusNumberAll=self._psspy.aloadint(-1,1,'NUMBER')
				assert ierr==0,'psspy.aloadint failed with error {}'.format(ierr)
				loadBusNumberAll=loadBusNumberAll[0]
				ierr,genBusNumber=self._psspy.agenbusint(-1,1,'NUMBER')
				assert ierr==0,'psspy.agenbusint failed with error {}'.format(ierr)
				genBusNumber=genBusNumber[0]
				ierr,SAll=self._psspy.alodbuscplx(string='MVAACT')
				assert ierr==0,"reading complex load failed with error {}".format(ierr)
				SAll=SAll[0]

				# only non-gen buses
				loadBusNumber=[];S=[]
				for thisBus,thisS in zip(loadBusNumberAll,SAll):
					if thisBus not in genBusNumber:
						loadBusNumber.append(thisBus)
						S.append(thisS)

				# update
				if six.PY2:
					thisStandard=conf.keys()[0]
				elif six.PY3:
					thisStandard=list(conf.keys())[0]
				conf={thisStandard:loadBusNumber}
			else:
				deraBuses=[]
				for thisStandard in conf:
					deraBuses.extend(conf[thisStandard])

				if not rating:
					rating=[self.__dera_rating_default['default']]*len(deraBuses)

				if six.PY2:
					thisStandard=conf.keys()[0]
				elif six.PY3:
					thisStandard=list(conf.keys())[0]
				loadBusNumber=conf[thisStandard]
				S=[]
				for thisBus in loadBusNumber:
					ierr,val=self._psspy.loddt2(thisBus,'1','TOTAL','ACT')
					S.append(val)

			# generate dera params and write .dya file
			userInput={}
			if 'der_a' in GlobalData.config['psseConfig'] and GlobalData.config['psseConfig']['der_a']:
				userInput=GlobalData.config['psseConfig']['der_a']
			
			interconnectionStandardOrg={}
			for thisBus in userInput:
				if 'interconnectionStandard' in userInput[thisBus]:
					interconnectionStandardOrg[int(thisBus)]=\
					userInput[thisBus].pop('interconnectionStandard')
			interconnectionStandard=copy.deepcopy(interconnectionStandardOrg)

			thisConf={}; busID=[]; sep='::::'
			for thisInterconnectionStandard in conf:
				thisConf.update(self.generate_config(conf[thisInterconnectionStandard],\
				thisInterconnectionStandard,userInput))
				for thisDeraBus in interconnectionStandard:
					if thisDeraBus in thisConf:
						thisConf['{}{}{}'.format(thisDeraBus,sep,thisInterconnectionStandard)]=\
						thisConf.pop(thisDeraBus)
				busID.extend(conf[thisInterconnectionStandard])
			
			for thisBus in interconnectionStandard:
				thisBus=int(thisBus)
				if thisBus in loadBusNumber:
					nInstance=len(interconnectionStandard[thisBus])
					thisBusS=S[loadBusNumber.index(thisBus)]
					loadBusNumber.extend([thisBus]*(nInstance-1))
					S.extend([thisBusS]*(nInstance-1))

			# rating
			realarData=rating
			idOffset=50; usedID={}
			if rating and solarPercentage==0:
				assert isinstance(rating,list) and len(rating)==len(busID)
				for thisRating,thisRealarData in zip(rating,realarData):
					if isinstance(thisRating,dict):
						thisRealarData.update(thisRating)
			elif solarPercentage>0:
				realarData=[]; interconnectionStandard2id={}
				for thisBus,thisS in zip(loadBusNumber,S):
					if interconnectionStandard and interconnectionStandard[thisBus]:
						thisInterconnectionStandard=interconnectionStandard[thisBus].keys()
						if six.PY3:
							thisInterconnectionStandard=list(thisInterconnectionStandard)
						thisInterconnectionStandard=thisInterconnectionStandard[0]
						thisS=thisS*interconnectionStandard[thisBus][thisInterconnectionStandard] # scale
						interconnectionStandard[thisBus].pop(thisInterconnectionStandard)
						if thisBus not in interconnectionStandard2id:
							interconnectionStandard2id[thisBus]={}
						if thisBus not in usedID:
							usedID[thisBus]=[]
						if usedID[thisBus]:
							thisID='{}'.format(usedID[thisBus][-1]+1)
							usedID[thisBus].append(usedID[thisBus][-1]+1)
						else:
							thisID='{}'.format(idOffset+1)
							usedID[thisBus].append(idOffset+1)
						interconnectionStandard2id[thisBus][thisInterconnectionStandard]=thisID
						thisBus='{}{}{}'.format(thisBus,sep,thisInterconnectionStandard)
					thisRating=copy.deepcopy(self.__dera_rating_default['default'])
					thisRating.update({'pg':thisS.real*solarPercentage,'qg':0.0,
					'pt':thisS.real*solarPercentage,'pb':0.0,
					'qt':abs(thisS.imag*solarPercentage),'qb':-abs(thisS.imag*solarPercentage)})
					realarData.append(thisRating)
					thisConf[thisBus]['params'][self.ind['parameter_properties']['PMAX']['index']]=\
					thisRating['pt']/thisRating['mbase']

			ind2name=self.__dera_rating_default['ind2name']
			if "deraModelTransformer" not in GlobalData.config['simulationConfig']:
				GlobalData.config['simulationConfig']['deraModelTransformer']=False

			interconnectionStandard=copy.deepcopy(interconnectionStandardOrg)
			tfrNew2OldBusIDMap={}
			if not GlobalData.config['simulationConfig']['deraModelTransformer']:# no tfr
				for thisBusID,thisRealarData in zip(busID,realarData):
					if thisBusID not in usedID:
						usedID[thisBusID]=[]
					if thisBusID in interconnectionStandard:
						thisInterconnectionStandard=interconnectionStandard[thisBusID].keys()
						if six.PY3:
							thisInterconnectionStandard=list(thisInterconnectionStandard)
						thisInterconnectionStandard=thisInterconnectionStandard[0]
						thisID=interconnectionStandard2id[thisBusID][thisInterconnectionStandard]
						interconnectionStandard[thisBusID].pop(thisInterconnectionStandard)
					else:
						thisID='1'
					ierr=self._psspy.bus_data_2(thisBusID,intgar1=2)
					assert ierr==0, 'bus_data_2 failed with error code {}'.format(ierr)
					ierr=self._psspy.plant_data(ibus=thisBusID)
					assert ierr==0, 'plant_data failed with error code {}'.format(ierr)
					realar=[thisRealarData[ind2name[str(n)]] for n in range(len(thisRealarData))]
					ierr=self._psspy.machine_data_2(thisBusID,id=thisID,intgar6=1,realar=realar)
					assert ierr==0,'machine_data_2 failed with error code {}'.format(ierr)
			else:# model transformer
				ierr, busNo = self._psspy.abusint(-1, 2, string='number')
				busNumberOffset=busNo[0][-1]
				if "deraTransformer" not in GlobalData.config['simulationConfig']:
					GlobalData.config['simulationConfig']["deraTransformer"]={}
				for thisBusID,thisRealarData in zip(busID,realarData):
					thisNewBusID=int(busNumberOffset+thisBusID)
					if thisNewBusID not in usedID:
						usedID[thisNewBusID]=[]
					if thisBusID in interconnectionStandard:
						thisInterconnectionStandard=interconnectionStandard[thisBusID].keys()
						if six.PY3:
							thisInterconnectionStandard=list(thisInterconnectionStandard)
						thisInterconnectionStandard=thisInterconnectionStandard[0]
						thisID=interconnectionStandard2id[thisBusID][thisInterconnectionStandard]
						interconnectionStandard[thisBusID].pop(thisInterconnectionStandard)
					else:
						thisID='1'
					if str(thisBusID) not in GlobalData.config['simulationConfig']["deraTransformer"]:
						GlobalData.config['simulationConfig']["deraTransformer"][thisNewBusID]={'r':0.02,'x':0.06}
					else:
						GlobalData.config['simulationConfig']["deraTransformer"][thisNewBusID]=\
						GlobalData.config['simulationConfig']["deraTransformer"].pop(str(thisBusID))
					ierr,toBusBaseKV=self._psspy.busdat(thisBusID,string='BASE'); assert ierr==0
					ierr=self._psspy.bus_data_2(thisNewBusID,intgar1=2,realar1=toBusBaseKV)# new bus
					assert ierr==0, 'bus_data_2 failed with error code {}'.format(ierr)
					thisR=GlobalData.config['simulationConfig']["deraTransformer"][thisNewBusID]['r']
					thisX=GlobalData.config['simulationConfig']["deraTransformer"][thisNewBusID]['x']
					ierr,rx=self._psspy.two_winding_data_4(thisNewBusID,thisBusID,realari1=thisR,realari2=thisX)# tfr
					assert ierr==0, 'two_winding_data_4 failed with error code {}'.format(ierr)
					
					ierr=self._psspy.plant_data(ibus=thisNewBusID)
					assert ierr==0, 'plant_data failed with error code {}'.format(ierr)

					realar=[thisRealarData[ind2name[str(n)]] for n in range(len(thisRealarData))]
					ierr=self._psspy.machine_data_2(thisNewBusID,id=thisID,intgar6=1,realar=realar)
					assert ierr==0,'machine_data_2 failed with error code {}'.format(ierr)

				thisConfKeys=thisConf.keys()
				if six.PY3:
					thisConfKeys=list(thisConfKeys)
				for thisConfKey in thisConfKeys:
					if str(thisBusID) in thisConfKey:
						updatedKey=thisConfKey.replace(str(thisBusID),str(thisNewBusID))
						thisConf[updatedKey]=thisConf.pop(thisConfKey)
						tfrNew2OldBusIDMap[updatedKey]=thisConfKey

			# add dera to base case
			thisConfKeys=thisConf.keys()
			if six.PY3:
				thisConfKeys=list(thisConfKeys)
			thisConfKeys.sort()
			for thisBus in thisConfKeys:
				if isinstance(thisBus,str) and sep in thisBus:
					thisBusOrgID,thisInterconnectionStandard=thisBus.split(sep)
					try:
						thisDeraID=interconnectionStandard2id[int(thisBusOrgID)][thisInterconnectionStandard]
					except KeyError:
						tfrBusID=int(tfrNew2OldBusIDMap[thisBus].split(sep)[0])
						thisDeraID=interconnectionStandard2id[tfrBusID][thisInterconnectionStandard]

					thisConf[thisBusOrgID]=thisConf.pop(thisBus)
					self.dera2dyr({thisBusOrgID:thisConf[thisBusOrgID]},additionalDyrFilePath,\
					deraID=[thisDeraID],fileMode='a')
					thisConf.pop(thisBusOrgID)
			self.dera2dyr(thisConf,additionalDyrFilePath,fileMode='a')

			psseConfig=GlobalData.config['psseConfig']
			if 'monitor' in psseConfig and 'dera1' in psseConfig['monitor']:
				outputFilePath=self.__model_state_var_ind['outputFilePath']
				res=self.parse_progress_output(outputFilePath)# next available index before adding dera
			ierr=self._psspy.dyre_add(dyrefile=additionalDyrFilePath); assert ierr==0
		
			if 'monitor' in psseConfig and 'dera1' in psseConfig['monitor']:
				ierr=self._psspy.report_output(6,'',[]); assert ierr==0
				os.system('del {}'.format(outputFilePath))
				for thisState in psseConfig['monitor']['dera1']:
					idOffset=self.__model_state_var_ind['dera1']['state']['name2ind'][thisState]
					modelOffset=len(self.__model_state_var_ind['dera1']['state']['name2ind'])
					for n in range(len(thisConfKeys)):
						ierr=self._psspy.state_channel([-1,res['nState']+(n*modelOffset)+idOffset],\
						'{} {}[]1'.format(thisState,thisConfKeys[n])); assert ierr==0

			# cleanup
			if cleanup:
				os.system('del {}'.format(additionalDyrFilePath))
		except:
			GlobalData.log()

#=======================================================================================================================
	def parse_progress_output(self,outputFilePath):
		try:
			res={}
			if os.path.exists(outputFilePath):
				f=open(outputFilePath); data=f.read(); f.close()
				res=re.findall('NEXT AVAILABLE ADDRESSES ARE:\n[\s\w]{1,}\n[\s]{0,}[\s\d]{1,}',data)
				if res:
					res=res[-1].split('\n')[2].strip().split()# use the latest value
				res={'nCon':int(res[0]),'nState':int(res[1]),'nVar':int(res[2]),'nIcon':int(res[3])}
			return res
		except:
			GlobalData.log()