from __future__ import division
from __future__ import print_function
import sys
import os
import psutil
import json
import pdb
import time

import six

from tdcosim.global_data import GlobalData
from tdcosim.procedure.default_procedure import DefaultProcedure
from tdcosim.model.psse.psse_model import PSSEModel
from tdcosim.model.opendss.opendss_model import OpenDSSModel
from tdcosim.report import generate_excel_report
from tdcosim.dashboard.indexer import Indexer

indHelper=Indexer()


class DefaultDynamicProcedure(DefaultProcedure):
#===================================================================================================
	def __init__(self):
		try:
			self._tnet_model = PSSEModel()
			self._dnet_model = OpenDSSModel()
		except:
			GlobalData.log()

#===================================================================================================
	def setup(self):
		try:
			self._tnet_model.setup()
			self._dnet_model.setup()
		except:
			GlobalData.log()

#===================================================================================================
	def initialize(self):
		try:
			GlobalData.data['dynamic'] = {}
			targetS, Vpcc = self._tnet_model.dynamicInitialize()
			power = self._dnet_model.initialize(targetS, Vpcc)
			self._tnet_model.shunt(targetS, Vpcc, power)
		except:
			GlobalData.log()

#===================================================================================================
	def run(self):
		try:
			GlobalData.data['monitorDataCsv']={}
			GlobalData.data['monitorData']={}
			GlobalData.data['TNet']['Dynamic'] = {}
			maxIter=1
			tol=10**-4
			if GlobalData.config['simulationConfig']['protocol'].lower() != 'loose_coupling':
				maxIter = GlobalData.config['simulationConfig']['protocol']['maxiteration']
			eventData=GlobalData.config['simulationConfig']['dynamicConfig']['events']
			events=eventData.keys()
			if six.PY3:
				events=list(events)
			events.sort()

			memory_threshold = GlobalData.config['simulationConfig']['memoryThreshold']
			t = 0.0
			dt= dt_default = 1/120.
			eps=1e-4
			stepCount=0
			stepThreshold=1e6
			lastWriteInd=0
			nPart=0
			simEnd=eventData[events[-1]]['time']
			updateBins=20
			eventFlag=False
			resetFlag=False

			# t0
			Vpcc = self._tnet_model.getVoltage()
			self._dnet_model.setVoltage(Vpcc)
			S = self._dnet_model.getLoad(t=t,dt=dt)
			
			msg={'varName':{},'info':{}}
			for node in Vpcc:
				msg['varName'][node]=['voltage_der','der']
				msg['info'][node]={'t':t}

			GlobalData.data['monitorData'][t]=self._dnet_model.monitor(msg)
			GlobalData.data['TNet']['Dynamic'][t] = {'V': Vpcc,'S': S}

			for event in events:
				while t<eventData[event]['time']:
					GlobalData.log(20,'started processing t:{}'.format(t))
					iteration=0
					mismatch=100.
					while mismatch>tol and iteration<maxIter:
						if t+dt-eps<eventData[event]['time']<t+dt+eps:
							eventFlag=True
							dt=dt_default-eps
						t+=dt
					
						iteration+=1
						GlobalData.log(20,'runDynamic t:{}'.format(t))
						self._tnet_model.runDynamic(t)
						GlobalData.log(20,'finished runDynamic t:{}'.format(t))
						print('Simulation Progress : ='+'='*int((updateBins-1)*(t/simEnd))+'>'+\
						' {}%({}s/{}s)'.format((t/simEnd)*100,t,simEnd),end='\r')
						GlobalData.log(level=10,msg="Sim time: " + str(t))
						GlobalData.log(20,'getVoltage t:{}'.format(t))
						Vpcc = self._tnet_model.getVoltage()
						GlobalData.log(20,'finished getVoltage t:{}'.format(t))


						# collect data and store
						monitor={'varName':{},'info':{}}
						for node in Vpcc:
							monitor['varName'][node]=['voltage_der','der']
							monitor['info'][node]={'t':t}

						GlobalData.log(20,'computeStep t:{}'.format(t))
						S,monData=self._dnet_model.computeStep(Vpu=Vpcc,t=t,dt=dt,monitor=monitor)
						GlobalData.log(20,'finished computeStep t:{}'.format(t))

						GlobalData.log(20,'setLoad t:{}'.format(t))
						self._tnet_model.setLoad(S)
						GlobalData.log(20,'finished setLoad t:{}'.format(t))
						GlobalData.data['TNet']['Dynamic'][t] = {'V': Vpcc,'S': S}

						# write to disk if running low on memory based on memory threshold
						if stepCount==0:
							currentMemUsage=psutil.Process().memory_full_info().uss*1e-6
							GlobalData.log(level=10,msg="Current Memory: " + str(currentMemUsage))
						elif stepCount==1:
							memUseRate=psutil.Process().memory_full_info().uss*1e-6-currentMemUsage
							if memUseRate==0:
								memUseRate=1
							stepThreshold=int(memory_threshold/memUseRate)
							GlobalData.log(level=10,msg="Step Threshhold: " + str(stepThreshold))
						elif stepCount>1 and stepCount%stepThreshold==0:####
							ffullpath = str(GlobalData.config["outputPath"]+\
							"\\report{}.xlsx".format(nPart))
							stype = str(GlobalData.config['simulationConfig']['simType'])
							generate_excel_report(GlobalData,fname=ffullpath,sim=stype)
							GlobalData.log(level=10,msg="generated report part" + str(nPart))
							GlobalData.data['monitorData']={}# empty data
							GlobalData.data['TNet']['Dynamic']={}# empty data
							nPart+=1; lastWriteInd=stepCount
						stepCount+=1

						#mismatch=Vprev-V ####TODO: Need to update mismatch
						####TODO: tight_coupling isn't implemented
						if GlobalData.config['simulationConfig']['protocol'].lower()==\
						'tight_coupling' and mismatch>tol:
							GlobalData.log(level=50,msg="Tight Couping is not implemented")

						# check for DSS convergence
						DSSconvergenceFlg = True
						for busID in GlobalData.data['TNet']['LoadBusNumber']:
							if busID in GlobalData.data['DNet']['Nodes']:
								if S[busID]['convergenceFlg'] is False:
									DSSconvergenceFlg = False
									break
						if DSSconvergenceFlg is False:
							GlobalData.log(msg='OpenDSS Convergence Failed')

						if resetFlag:
							dt=dt_default-2*eps
							resetFlag=False
						elif eventFlag:
							if eventData[event]['type']=='faultOn':
								self._tnet_model.faultOn(eventData[event]['faultBus'],
								eventData[event]['faultImpedance'])
							elif eventData[event]['type']=='faultOff':
								self._tnet_model.faultOff(eventData[event]['faultBus'])
							eventFlag=False
							dt=3*eps
							resetFlag=True
						else:
							dt=dt_default
					GlobalData.log(20,'finished processing t:{}'.format(t))

			# close
			print('')# for newline
			ack=self._dnet_model.close()
			GlobalData.log(level=20,msg=json.dumps(ack))
			ierr=self._tnet_model._psspy.pssehalt_2(); assert ierr==0

			# process output data
			indObj={'tnodeid':{},'dnodeid':{},'ineq':{},'dfLen':0,'property':{},'pointer':[]}
			f=open(os.path.join(GlobalData.config['outputConfig']['outputDir'],'df.csv'),'w')# empty file
			f.close()
			for node in Vpcc:
				dataStr=''
				thisFPath=os.path.join(GlobalData.config['outputConfig']['outputDir'],'{}_temp.csv'.format(node))
				f=open(thisFPath)
				data=f.read(); f.close()
				scenarioID=GlobalData.config['outputConfig']['scenarioID']
				data=data.replace('$1',scenarioID).replace('$3','{}'.format(node)).replace(\
				'$4','').replace('$5','').splitlines()
				for stride in range(len(data)):
					if float(data[stride].split(',')[1])>=dt_default-1e-6 and \
					float(data[stride].split(',')[1])<=dt_default+1e-6:
						break
				dataStrLen=len(dataStr.splitlines())
				for offset in range(stride):
					if offset==0:
						strideOffset=len(data[offset::stride])
					indHelper.get_index_from_string(indObj,data[offset],strideOffset,dataStrLen)
					dataStr+='\n'.join(data[offset::stride])+'\n'
					dataStrLen+=strideOffset

				os.system('del {}'.format(thisFPath))

				f=open(os.path.join(GlobalData.config['outputConfig']['outputDir'],'df.csv'),'a')
				f.write(dataStr)
				f.close()

			indObj['pointer']=[len(entry) for entry in dataStr.splitlines()]
			json.dump(indObj,open(os.path.join(GlobalData.config['outputConfig']['outputDir'],'index.json'),'w'))
		except:
			GlobalData.log()


