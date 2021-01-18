import sys
import os
import re
import pdb
import json

import numpy as np

from tdcosim.global_data import GlobalData
from tdcosim.model.psse.dera import Dera


class PSSEModel(Dera):
	def __init__(self):
		try:
			super(PSSEModel,self).__init__()
			pssePath="C:\\Program Files (x86)\\PTI\\PSSE33\\PSSBIN" # Default PSSEPY path is PSSE33
			if "installLocation" in GlobalData.config['psseConfig'] and \
			os.path.exists(GlobalData.config['psseConfig']['installLocation']+os.path.sep+'psspy.pyc'):
				pssePath = GlobalData.config['psseConfig']['installLocation']
			sys.path.append(pssePath)
			os.environ['PATH']+=';'+pssePath
			import psspy

			# psse
			self._psspy=psspy
			ierr=self._psspy.psseinit(0); assert ierr==0
			ierr=self._psspy.report_output(6,'',[]); assert ierr==0
			ierr=self._psspy.progress_output(6,'',[]); assert ierr==0
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
				ind2name=self.__cmld_rating_default['ind2name']
				defaultVal=[default[ind2name[str(n)]] for n in range(len(default))]
				if not prefix and self._psspy.psseversion()[1]>=35:
					prefix=["'USRLOD'",1,"'CMLDBLU2'",12,1,2,133,27,146,48,0,0]
				elif not prefix and self._psspy.psseversion()[1]<35:
					prefix=["'USRLOD'",1,"'CMLDBLU1'",12,1,0,132,27,146,48]
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
			if isinstance(outfile,unicode):
				outfile=outfile.encode('ascii','ignore')
			GlobalData.logger.log(10,'outfile:{}'.format(outfile))

			ierr=self._psspy.strt(outfile=outfile)
			assert ierr==0,"psspy.strt failed with error {}".format(ierr)

			targetS={}
			for entry,val in zip(GlobalData.data['TNet']['LoadBusNumber'],S[0]):
				if entry in GlobalData.data['DNet']['Nodes']:
					targetS[entry]=[val.real*10**3,val.imag*10**3] # convert to kw/kvar from mw/mvar

			# update targetS, if "fractionAggregatedLoad" is set for T-D interface nodes
			# "fractionAggregatedLoad":{"complexLoad":0.6}
			openDSSConfig=GlobalData.config['openDSSConfig']
			if 'manualFeederConfig' in openDSSConfig:
				if 'nodes' in openDSSConfig['manualFeederConfig']:
					for entry in openDSSConfig['manualFeederConfig']['nodes']:
						if 'fractionAggregatedLoad' in entry:
							# if more than one load identifier is present, then feeder will
							# be interfaced by default to load identifier "1"
							ierr,val=self._psspy.loddt2(entry['nodenumber'],'1','TOTAL','ACT')
							assert ierr==0,"loddt2 failed with error {}".format(ierr)
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

			tempDyrPath=dyrPath.split('.dyr')[0]+'_temp.dyr'
			tempDyrPath=os.path.abspath(tempDyrPath)
			if isinstance(tempDyrPath,unicode):
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

			if busIDToAddComplexLoad or busIDToAddCompositeLoad:
				ierr,S=self._psspy.aloadcplx(sid=-1, flag=4, string='MVAACT')
				assert ierr==0,"aloadcplx failed with error {}".format(ierr)
				S=S[0]
				ierr,loadBusID=self._psspy.aloadint(sid=-1, flag=4, string='NUMBER')
				assert ierr==0,"aloadcplx failed with error {}".format(ierr)
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

			# add der_a, if configured
			conf=None
			if 'dera' in GlobalData.config['simulationConfig']:
				conf=GlobalData.config['simulationConfig']['dera']
			if conf and self._psspy.psseversion()[1]>=35:
				self.add_dera_to_case(conf=conf)
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
			GlobalData.logger.debug('Input: targetS={}; Vpcc={}; power={};'.format(\
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
			if solarPercentage>0:# update conf to have all busIDs
				LogUtil.logger.info(\
				'Updating conf to use {} for all load buses as solarPercentage>0'.format(conf.keys()[0]))
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
				thisStandard=conf.keys()[0]
				conf={thisStandard:loadBusNumber}

			deraBuses=[]
			for thisStandard in conf:
				deraBuses.extend(conf[thisStandard])

			if not rating:
				rating=[self.__dera_rating_default['default']]*len(deraBuses)

			# generate dera params and write .dya file
			thisConf={}; busID=[]
			for entry in conf:
				thisConf.update(self.generate_config(conf[entry],entry))
				busID.extend(conf[entry])
			self.dera2dyr(thisConf,additionalDyrFilePath)

			# rating
			realarData=rating
			if rating and solarPercentage==0:
				assert isinstance(rating,list) and len(rating)==len(busID)
				for thisRating,thisRealarData in zip(rating,realarData):
					if isinstance(thisRating,dict):
						thisRealarData.update(thisRating)
			elif solarPercentage>0:
				realarData=[self.__dera_rating_default['default']]*len(loadBusNumber)
				for thisBus,thisS,thisRealarData in zip(loadBusNumber,S,realarData):
					thisRating={'pg':thisS.real*solarPercentage,'qg':0.0,
					'pt':thisS.real*solarPercentage,'pb':0.0,
					'qt':thisS.imag*solarPercentage,'qb':-thisS.imag*solarPercentage}
					thisRealarData.update(thisRating)

			ind2name=self.__dera_rating_default['ind2name']
			for thisBusID,thisRealarData in zip(busID,realarData):
				ierr=self._psspy.bus_data_2(thisBusID,[2,1,1,1])# convert to a gen bus
				assert ierr==0, 'error code {}'.format(ierr)
				ierr=self._psspy.plant_data(thisBusID)
				assert ierr==0, 'error code {}'.format(ierr)
				realar=[thisRealarData[ind2name[str(n)]] for n in range(len(thisRealarData))]
				ierr=self._psspy.machine_data_2(i=thisBusID,intgar=[1,1,0,0,0,1],realar=realar)
				assert ierr==0

			# add dera to base case
			ierr=self._psspy.dyre_add(dyrefile=additionalDyrFilePath); assert ierr==0

			# cleanup
			if cleanup:
				os.system('del {}'.format(additionalDyrFilePath))
		except:
			GlobalData.log()