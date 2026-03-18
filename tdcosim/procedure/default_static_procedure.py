from __future__ import print_function
import os
import json
import platform
import pdb

import numpy as np
from tqdm import tqdm

from tdcosim.global_data import GlobalData
from tdcosim.procedure.default_procedure import DefaultProcedure
from tdcosim.model.opendss.opendss_model import OpenDSSModel
if platform.system().lower()=='windows':
	from tdcosim.model.psse.psse_model import PSSEModel as TModel
elif platform.system().lower()=='linux':
	from tdcosim.model.matpower.matpower_model import MatpowerModel as TModel

class DefaultStaticProcedure(DefaultProcedure):
#===================================================================================================
	def __init__(self):
		self._tnet_model = TModel()
		self._dnet_model = OpenDSSModel()

#===================================================================================================
	def setup(self):
		self._tnet_model.setup()
		self._dnet_model.setup()

#===================================================================================================
	def initialize(self):
		targetS, Vpcc = self._tnet_model.staticInitialize()
		GlobalData.log(20,'Attaching substaion to following buses: {}'.format(Vpcc.keys()))
		power = self._dnet_model.initialize(targetS, Vpcc)
		return power

#===================================================================================================
	def check_for_costadmg_interface(self):
		hasInterface=False
		if 'costadmg_interface' in GlobalData.config and GlobalData.config['costadmg_interface']:
			hasInterface=True
		# setup
		simId=GlobalData.config['outputConfig']['simID']
		fpath=os.path.join(GlobalData.config['outputConfig']['outputDir'],f'costadmg_results_{simId}.csv')
		f=open(fpath,'w')
		f.write('time,feasible\n')
		f.close()
		return hasInterface

#===================================================================================================
	def costadmg_interface_distribution_handler(self,index):
		distribution=GlobalData.config['costadmg_interface']['distribution']
		data={}
		for busId in distribution:
			if 'set' in distribution[busId]:
				data[int(busId)]=distribution[busId]['set'][index]['data']

		reply=self._dnet_model.setter(data)

		success=True
		for busId in distribution:
			if not reply[int(busId)]['success']:
				success=False
				break
		return success

#===================================================================================================
	def costadmg_interface_output(self,data,t):
		simId=GlobalData.config['outputConfig']['simID']
		fpath=os.path.join(GlobalData.config['outputConfig']['outputDir'],f'costadmg_results_{simId}.csv')
		GlobalData.log(level=20,msg=fpath)
		GlobalData.log(level=20,msg=f"dir::::{GlobalData.config['outputConfig']['outputDir']}")
		success=True
		for busId in data:
			if not data[busId]['convergenceFlg']:
				success=False
				break
		f=open(fpath,'a')
		f.write(f'{t},{success}\n')
		f.close()

#===================================================================================================
	def run(self):
		GlobalData.data['static'] = {}
		maxIter = 20
		tol=10**-4
		count = 0
		loadShape = GlobalData.config['simulationConfig']['staticConfig']['loadShape']
		GlobalData.data['monitorData']={}
		progressBar = tqdm(total=len(loadShape))

		hasCostadmgInterface=self.check_for_costadmg_interface()

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

				if hasCostadmgInterface:
					success=self.costadmg_interface_distribution_handler(count)
					assert success,'costadmg interface failed to set values'
				S = self._dnet_model.getLoad()# get complex power injection

				self._tnet_model.setLoad(S)# set complex power injection as seen from T side
				Vcheck[:,0]=Vcheck[:,1]#iterate for tight coupling
				Vcheck[:,1]=np.array(f(Vpcc))
				iteration+=1

			if hasCostadmgInterface:
				self.costadmg_interface_output(S,count)

			progressBar.update(1)
			GlobalData.log(20,'Loadshape {} Converged in {} iterations with mismatch {}'.format(\
				scale,iteration,max(abs(np.abs(Vcheck[:,0]-Vcheck[:,1])))))

			# collect data and store
			msg={'varName':{},'info':{}}
			for node in Vpcc:
				msg['varName'][node]=['voltage']
				msg['info'][node]={'t':count}

			GlobalData.data['monitorData'][count]=self._dnet_model.monitor(msg)

			GlobalData.data['static'][count]['V'] = Vpcc
			GlobalData.data['static'][count]['S'] = S
			GlobalData.data['static'][count]['Scale'] = scale
			count+=1

		# close
		progressBar.close()
		ack=self._dnet_model.close()
		GlobalData.log(level=20,msg=json.dumps(ack))
		if platform.system().lower()=='windows':
			ierr=self._tnet_model._psspy.pssehalt_2(); assert ierr==0
		else:
			self._tnet_model.finalize()


