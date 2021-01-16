import sys
import os
import re
import pdb
import json

import numpy as np

from tdcosim.global_data import GlobalData


class PSSEModel(object):
	def __init__(self):
		try:
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
			####ierr=self._psspy.progress_output(6,'',[]); assert ierr==0
			ierr=self._psspy.alert_output(6,'',[]); assert ierr==0
			ierr=self._psspy.prompt_output(6,'',[]); assert ierr==0

			self.faultmap = {}
			self.faultindex = 1
			baseDir=os.path.dirname(os.path.dirname(os.path.dirname(\
			os.path.dirname(os.path.abspath(__file__)))))
			self.__cmld_rating_default=json.load(open(os.path.join(baseDir,'config',\
			'composite_load_model_rating.json')))
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
	def convert_loads(self,conf=None,loadType='zip'):
		try:
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
				prefix=["'CLODBL'",1]
				tempCMLDDyrFile='tempCMLDDyrFile.dyr'
				f=open(tempCMLDDyrFile,'w')

				for thisBus in loadBusNumber:
					if thisBus not in GlobalData.data['DNet']['Nodes']:
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
				if self._psspy.psseversion()[1]>=35:
					prefix=["'USRLOD'",1,"'CMLDBLU2'",12,1,2,133,27,146,48,0,0]
				elif self._psspy.psseversion()[1]<35:
					prefix=["'USRLOD'",1,"'CMLDBLU1'",12,1,0,132,27,146,48]
					defaultVal=defaultVal[1:-1]

				tempCMLDDyrFile='tempCMLDDyrFile.dyr'
				f=open(tempCMLDDyrFile,'w')
				avoidBus=GlobalData.data['DNet']['Nodes'].keys()

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

			# convert all loads to given load type
			self.convert_loads(loadType=defaultLoadType)

			# update
			loadType=0
			for busID,val in zip(GlobalData.data['TNet']['LoadBusNumber'],S[0]):
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
			ierr=self._psspy.dist_bus_fault(faultBus, 1,0.0,faultImpedance)
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