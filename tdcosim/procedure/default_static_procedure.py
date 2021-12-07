from __future__ import print_function
import json
import pdb

import numpy as np

from tdcosim.global_data import GlobalData
from tdcosim.procedure.default_procedure import DefaultProcedure
from tdcosim.model.psse.psse_model import PSSEModel
from tdcosim.model.opendss.opendss_model import OpenDSSModel


class DefaultStaticProcedure(DefaultProcedure):
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
			targetS, Vpcc = self._tnet_model.staticInitialize()
			GlobalData.log(20,'Attaching substaion to following buses: {}'.format(Vpcc.keys()))
			power = self._dnet_model.initialize(targetS, Vpcc)
		except:
			GlobalData.log()

#===================================================================================================
	def run(self):
		try:
			GlobalData.data['static'] = {}
			maxIter = 20
			tol=10**-4
			count = 0
			loadShape = GlobalData.config['simulationConfig']['staticConfig']['loadShape']
			GlobalData.data['monitorData']={}
			updateBins=20

			for scale in loadShape:
				GlobalData.log(20,'Running dispatch with loadshape {}'.format(scale))
				GlobalData.data['static'][count] = {}
				f=lambda x:[x[entry] for entry in x]
				iteration=0
				scaleData={}
				Vpcc = self._tnet_model.getVoltage()
				Vcheck=np.random.random((len(Vpcc),2))
				for nodeID in Vpcc:
					scaleData[nodeID]=scale
				self._dnet_model.scaleLoad(scaleData)# now scale distribution feeder load

				while np.any(np.abs(Vcheck[:,0]-Vcheck[:,1])>tol) and iteration<maxIter:
					self._tnet_model.runPFLOW()# run power flow
					Vpcc = self._tnet_model.getVoltage()
					self._dnet_model.setVoltage(Vpcc)#set voltage based on previous guess
					S = self._dnet_model.getLoad()# get complex power injection
					self._tnet_model.setLoad(S)# set complex power injection as seen from T side
					Vcheck[:,0]=Vcheck[:,1]#iterate for tight coupling
					Vcheck[:,1]=np.array(f(Vpcc))
					iteration+=1
				
				print('Simulation Progress : ='+'='*int((updateBins-1)*(count/len(loadShape)))+'>'+\
				' {}%({} dispatches/{} dispatches)'.format(((count+1)/len(loadShape))*100,count+1,len(loadShape)),end='\r')
				GlobalData.log(20,'Loadshape {} Converged in {} iterations with mismatch {}'.format(scale,iteration,max(abs(np.abs(Vcheck[:,0]-Vcheck[:,1])))))

				# collect data and store
				msg={}
				msg['varName']={}
				for node in Vpcc:
					msg['varName'][node]=['voltage']
				GlobalData.data['monitorData'][count]=self._dnet_model.monitor(msg)

				GlobalData.data['static'][count]['V'] = Vpcc
				GlobalData.data['static'][count]['S'] = S
				GlobalData.data['static'][count]['Scale'] = scale
				count+=1

			# close
			print('')# for newline
			ack=self._dnet_model.close()
			GlobalData.log(level=20,msg=json.dumps(ack))
			ierr=self._tnet_model._psspy.pssehalt_2(); assert ierr==0
		except:
			GlobalData.log()


