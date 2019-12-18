import numpy as np
import sys
import os
pssePath="C:\Program Files (x86)\PTI\PSSE33\PSSBIN"
sys.path.append(pssePath)
os.environ['PATH']+=';'+pssePath
import psspy

from tdcosim.global_data import GlobalData

class PSSEModel:
	def __init__(self):
		# psse
		self._psspy=psspy
		psspy.psseinit(0)
		psspy.report_output(6,'',[])
		psspy.progress_output(6,'',[])
		psspy.alert_output(6,'',[])
		psspy.prompt_output(6,'',[])

		self.faultmap = {}
		self.faultindex = 1
		
		return None

	def setup(self, adjustOpPoint=True):
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
		ierr = self._psspy.read(0,GlobalData.config['psseConfig']['rawFilePath'])
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

	def dynamicInitialize(self, adjustOpPoint=True):
		if adjustOpPoint:
			S = self._adjustSystemOperatingPoint()
		else:
			self._psspy.dyre_new([1,1,1,1],self.config['psseConfig']['dyrFilePath'])
		self._psspy.cong(1)
		GlobalData.data['dynamic']['channel'] = {}
		nMonVars=0
		nGenBus=self._psspy.agenbuscount(-1,1)[1]
		nBus=self._psspy.abuscount(-1,1)[1]
		nLoad=self._psspy.aloadcount(-1,1)[1]
		genBusNumber=self._psspy.agenbusint(-1,1,'NUMBER')[1][0]
		busNumber=self._psspy.abusint(string='NUMBER')[1][0]
		loadBusNumber=self._psspy.aloadint(-1,1,'NUMBER')[1][0]
		for item in ['angle','speed','pelec','qelec','pmech']:
			self._psspy.chsb(sid=0,all=1,status=[-1,-1,-1,1,self._monitorID[item],0])
			GlobalData.data['dynamic']['channel'][item]={}
			for channelID,node in zip(range(nMonVars+1,nMonVars+1+nGenBus),genBusNumber):# psse uses 1 ind
				GlobalData.data['dynamic']['channel'][item][channelID]=node
			nMonVars+=nGenBus

		self._psspy.chsb(sid=0,all=1,status=[-1,-1,-1,1,self._monitorID['volt'],0])
		GlobalData.data['dynamic']['channel']['volt']={}
		for channelID,node in zip(range(nMonVars+1,nMonVars+1+nBus),busNumber):# psse uses 1 ind
			GlobalData.data['dynamic']['channel']['volt'][channelID]=node
		nMonVars+=nBus

		for item in ['pload','qload']:
			self._psspy.chsb(sid=0,all=1,status=[-1,-1,-1,1,self._monitorID[item],0])
			GlobalData.data['dynamic']['channel'][item]={}
			for channelID,node in zip(range(nMonVars+1,nMonVars+1+nLoad),loadBusNumber):# psse uses 1 ind
				GlobalData.data['dynamic']['channel'][item][channelID]=node
			nMonVars+=nLoad

		self._psspy.strt(outfile=r'result.out')# compute initial conditions

		Vpcc=self.getVoltage()
		targetS={}
		for entry,val in zip(GlobalData.data['TNet']['LoadBusNumber'],S[0]):
			if entry in GlobalData.data['DNet']['Nodes']:
				targetS[entry]=[val.real*10**3,val.imag*10**3] # convert to kw and kvar from mw and mvar
		return targetS,Vpcc

	def _adjustSystemOperatingPoint(self):
		loadType = 0
		try:			
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

			dyrPath=GlobalData.config['psseConfig']['dyrFilePath']
			f=open(dyrPath)
			dyrData=f.read().splitlines()
			f.close()

			dyrDataStr=''; Zr={}; Zx={}
			for line in dyrData:
				entry=line.split(',')
				for item in ind:
					if entry[1]=="'{}'".format(item):
						entry[offset+ind[item]]=\
						str(float(entry[offset+ind[item]])*(1-reductionPercent))
						break
				dyrDataStr+=','.join(entry+['\n'])

			tempDyrPath=dyrPath.split('.dyr')[0]+'_temp.dyr'
			f=open(tempDyrPath,'w')
			f.write(dyrDataStr)
			f.close()
			
			# now read raw file to get Zr and Zx
			f=open(GlobalData.config['psseConfig']['rawFilePath'])
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

			# modify config to point to the temp dyr file
			GlobalData.config['psseConfig']['dyrFilePath']=tempDyrPath

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
			self._psspy.dyre_new([1,1,1,1],GlobalData.config['psseConfig']['dyrFilePath'])

			# get machine data
			macVarData={}
			for entry in macVarMap:
				ierr,macVarData[entry]=self._psspy.amachreal(sid=-1, flag=1, string=entry)# get data
				assert ierr==0,"reading machine data failed with error {}".format(ierr)


			genBusNumber=self._psspy.agenbusint(-1,1,'NUMBER')[1][0] # get gen bus number

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
				self._psspy.machine_chng_2(i=genBusNumber[n], realar=macVarDataNew) # change machine data

			# adjust load data
			ierr,S=self._psspy.alodbuscplx(string='MVAACT')
			assert ierr==0,"reading complex load failed with error {}".format(ierr)

			for busID,val in zip(GlobalData.data['TNet']['LoadBusNumber'],S[0]):
				if busID in GlobalData.data['DNet']['Nodes']:
					# constP,Q,IP,IQ,YP,YQ
					loadVal=[0]*6
					reductionPercent=GlobalData.data['DNet']['Nodes'][busID]['solarPenetration']
					loadVal[loadType*2],loadVal[loadType*2+1]=\
					val.real*(1-reductionPercent),val.imag*(1-reductionPercent)
					ierr=psspy.load_chng_4(busID,'1',[1,1,1,1,1,0],loadVal)
					assert ierr==0,"load change failed with error {}".format(ierr)

			return S
		except:
			GlobalData.log('Failed to adjustSystemOperatingPoint from PSSEModel')

	def staticInitialize(self):
		try:
			Vpcc=self.getVoltage()
			

			# scale feeder
			targetS={}
			ierr,S=self._psspy.alodbuscplx(string='MVAACT')
			assert ierr==0,"Reading load bus complex power failed with error {}".format(ierr)

			for entry,val in zip(GlobalData.data['TNet']['LoadBusNumber'],S[0]):
				if entry in GlobalData.data['DNet']['Nodes']:
					targetS[entry]=[val.real*10**3,val.imag*10**3] # convert to kw and kvar from mw and mvar
			
			return targetS, Vpcc
		except Exception as e:
			GlobalData.log('Failed to initialize from PSSEModel')
			

	#===================GET VOLTAGE FROM PSSSE========================
	def getVoltage(self):
		try:
			"""Get PCC voltage from psse."""
			Vpcc={}
			if GlobalData.data['TNet']['LoadBusCount']==len(GlobalData.data['TNet']['LoadBusNumber']): # dist syst interfaced at all load buses
				loadBusVPU=self._psspy.alodbusreal(string='PU')
				loadBusVPU = loadBusVPU[1][0]
				for entry,val in zip(GlobalData.data['TNet']['LoadBusNumber'],loadBusVPU):# efficient
					if entry in GlobalData.data['DNet']['Nodes']:
						Vpcc[entry]=val
			else:# subset of loadbuses interfaced as dist syst
				for entry in GlobalData.data['TNet']['LoadBusNumber']: # not as efficient for large cases
					Vpcc[entry]=self._psspy.busdat(entry,'PU')[1]
			return Vpcc
		except Exception as e:
			GlobalData.log('Failed to getVoltage from PSSEModel')

	def setLoad(self, S,loadType=0):
		"""set PCC Pinj,Qinj for psse.
		Input: S -- dictionary containing Pinj and Qinj.
		loadType -- 0- constant power, 1-constant current, 2-constant admittance."""		
		for busID in GlobalData.data['TNet']['LoadBusNumber']:
			if busID in GlobalData.data['DNet']['Nodes']:
				# constP,Q,IP,IQ,YP,YQ
				loadVal=[0]*6
				loadVal[loadType*2],loadVal[loadType*2+1]=S[busID]['P'],S[busID]['Q']
				ierr=self._psspy.load_chng_4(busID,'1',[1,1,1,1,1,0],realar=loadVal)
				assert ierr==0,"load change failed with error {}".format(ierr)

	
	def shunt(self, targetS, Vpcc, power):
		try:
			mismatchTolerance=0.1
			for node in power:
				if abs(power[node]['P']-targetS[node][0])>mismatchTolerance or abs(power[node]['Q']-targetS[node][1])>mismatchTolerance:# add shunt if needed
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
		except Exception as e:
			GlobalData.log('Failed to shunt from PSSEModel')
	
	def runPFLOW(self):
		self._psspy.fnsl()
	def runDynamic(self, tpause):
		self._psspy.run(tpause=tpause)
	def faultOn(self, faultBus, faultImpedance):
		self._psspy.dist_bus_fault(faultBus, 1,0.0,faultImpedance)
		self.faultmap[faultBus] = self.faultindex
		self.faultindex = self.faultindex + 1
	def faultOff(self, faultBus):
		if faultBus in self.faultmap:
			self._psspy.dist_clear_fault(faultmap[faultBus])
		else
			print("Failed Fault Off, Fault was not applied to the Bus Number: ", faultBus)
