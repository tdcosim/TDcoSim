import os
import pdb
import time

import numpy as np
import oct2py

from tdcosim.global_data import GlobalData


class MatpowerModel:

	def __init__(self,octavePath=None):
		startTime=time.time()
		# check for config
		assert 'matpowerConfig' in GlobalData.config,'matpowerConfig is not provided'
		self.config=GlobalData.config['matpowerConfig']
		assert os.path.exists(self.config['filePath']),f"{self.config['filePath']} does not exist"

		self.oc = oct2py.Oct2Py()

		# add tdcosim matpower interface folder
		baseDir=os.path.dirname(os.path.abspath(__file__))
		self.oc.addpath(self.oc.genpath(baseDir))

		if 'matpowerInstallLocation' in self.config and self.config['matpowerInstallLocation']:
			self.oc.addpath(self.oc.genpath(self.config['matpowerInstallLocation']))

		if octavePath:
			for entry in octavePath:
				self.oc.addpath(self.oc.genpath(entry))

		self.oc.eval('init_mpc')
		self.casedata={}
		self.availableAlgorithms=['runpf','rundcpf','runopf','rundcopf']

		self.load_case(self.config['filePath'])
		self.run('runpf')

#=======================================================================================================================
	def setup(self):
		GlobalData.data['TNet']['LoadBusCount'] = self.casedata['pqbus'].shape[0]
		GlobalData.data['TNet']['LoadBusNumber'] = self.casedata['pqbus'].tolist()
		GlobalData.data['TNet']['TotalRealPowerLoad'] = self.casedata['pd'].sum()
		GlobalData.data['TNet']['BusRealPowerLoad'] = \
			{int(bus):float(pd) for bus,pd in zip(self.casedata['bus_id'],self.casedata['pd'])}

#=======================================================================================================================
	def staticInitialize(self):
		s,v={},{}
		self.casedata['interfacedBuses']=[]
		self.casedata['interfacedBusesInd']=[]
		for bus,pd,qd,vt in zip(self.casedata['bus_id'],self.casedata['pd'],self.casedata['qd'],self._get_voltage()):
			if bus in self.casedata['pqbus'] and bus in GlobalData.data['DNet']['Nodes']:
				bus=int(bus)
				s[bus]=[float(pd)*10**3,float(qd)*10**3]# convert to kw/kvar from mw/mvar
				v[bus]=float(vt)
				self.casedata['interfacedBuses'].append(bus)
				self.casedata['interfacedBusesInd'].append(self.casedata['busid2ind'][bus])
		self.casedata['interfacedBuses']=np.array(self.casedata['interfacedBuses'])
		self.casedata['interfacedBusesInd']=np.array(self.casedata['interfacedBusesInd'])
		return s,v

#=======================================================================================================================
	def getVoltage(self):
		"""Get PCC voltage from MATPOWER."""
		V=self._get_voltage(returnAsList=False)
		interfaceBusId=self.casedata['interfacedBuses']
		interfaceBusInd=self.casedata['interfacedBusesInd']

		# subset of loadbuses interfaced as dist syst
		Vpcc={int(busId):float(V[busInd]) for busId,busInd in zip(interfaceBusId,interfaceBusInd)}

		return Vpcc

#=======================================================================================================================
	def post_checker(self,vmin=0.9,vmax=1.1):
		success=True
		vm=self._get_voltage(returnAsList=False)
		violation=np.where((vm < vmin) | (vm > vmax))
		if violation[0].shape[0]>0:
			GlobalData.log(20,f'violation:{vm[violation[0]]}')
			success=False
		return success

#=======================================================================================================================
	def _get_voltage(self,returnAsList=True):
		startTime=time.time()
		vm=self.oc.get_mpc('bus','vm');
		vm=vm.flatten()
		if returnAsList:
			vm=vm.tolist()
		return vm

#=======================================================================================================================
	def setLoad(self,S):
		startTime=time.time()
		busInd,p,q=[],[],[]
		for entry in S:
			assert S[entry]['convergenceFlg'],f'T-D interface {entry} convergence failed'
			busInd.append(entry)
			p.append(S[entry]['P'])
			q.append(S[entry]['Q'])
		self._set_loads(busInd,p,q)

#=======================================================================================================================
	def runPFLOW(self):
		self.run('runpf')

#=======================================================================================================================
	def load_case(self,casename:str):
		startTime=time.time()
		res=self.oc.load_mpc(casename); assert res['success']
		self.casedata['bus_id']=self.oc.get_mpc('bus','bus_id')
		assert not isinstance(self.casedata['bus_id'],type(None))
		self.casedata['bus_id']=np.array(self.casedata['bus_id'].flatten(),dtype=np.int32)

		self.casedata['busid2ind']=\
			{id:ind for id,ind in zip(range(1,1+len(self.casedata['bus_id'])),self.casedata['bus_id'])}
		self.casedata['busind2id']={self.casedata['busid2ind'][e]:e for e in self.casedata['busid2ind']}

		self.casedata['pd']=self.oc.get_mpc('bus','pd').flatten()
		self.casedata['qd']=self.oc.get_mpc('bus','qd').flatten()
		busType=self.casedata['type']=self.oc.get_mpc('bus','type').flatten()
		self.casedata['pqbus']=self.casedata['bus_id'][busType==1]
		self.casedata['pvbus']=self.casedata['bus_id'][busType!=1]

		return True if self.casedata['busind2id'] else False

#=======================================================================================================================
	def _set_loads(self,busInd,p,q):
		startTime=time.time()
		res=self.oc.set_mpc('bus','pd',p,busInd);assert res['success']
		res=self.oc.set_mpc('bus','qd',q,busInd);assert res['success']

#=======================================================================================================================
	def run(self,alg):
		assert alg in self.availableAlgorithms
		startTime=time.time()
		res=self.oc.run_mpc(alg);assert res['success']
		return res

#=======================================================================================================================
	def finalize(self):
		self.oc.exit()

