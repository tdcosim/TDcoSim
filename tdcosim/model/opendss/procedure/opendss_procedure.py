from tdcosim.model.opendss.model.opendss_interface import OpenDSSInterface
from tdcosim.model.opendss.model.pvderaggregation.procedure.pvder_aggregated_procedure import PVDERAggregatedProcedure
from tdcosim.model.opendss.opendss_data import OpenDSSData
import time

import six


class OpenDSSProcedure(object):
	def __init__(self):
		try:
			self._opendssinterface = OpenDSSInterface()
			self._pvderAggProcedure = PVDERAggregatedProcedure()
			self._pvNodes=None
		except:
			OpenDSSData.log()

#===================================================================================================
	def setup(self):
		try:
			self._opendssinterface.setup()
		except:
			OpenDSSData.log()

#===================================================================================================
	def initialize(self,targetS ,Vpcc ,tol):
		try:
			derP = {}
			derQ = {}
			n_pre_run_steps = 200

			if OpenDSSData.config['myconfig']['solarFlag']:
				# Re-setup DER after reload the OpenDSS
				S0 = self._opendssinterface.getLoads()
				V0 = self._opendssinterface.getVoltage(vtype='actual')
				V0pu = self._opendssinterface.getVoltage(vtype='pu')
				pvdermap = self._pvderAggProcedure.setup(S0, V0,V0pu=V0pu)
				self._opendssinterface.setupDER(pvdermap)

				derType=OpenDSSData.config['openDSSConfig']['DEROdeSolver']
				if derType.replace('_','').replace('-','').lower()!='fastder':
					tic = time.perf_counter()
					for n in range(n_pre_run_steps):# synchronize
						V = self._opendssinterface.getVoltage(vtype='actual')
						Vpu = self._opendssinterface.getVoltage(vtype='pu')
						derP, derQ = self._pvderAggProcedure.run(V,Vpu)
						self._opendssinterface.pvderInjection(derP, derQ)
						P,Q,Converged = self._opendssinterface.getS(pccName='Vsource.source')
					toc = time.perf_counter()
					OpenDSSData.log(level=10,msg="Completed {} steps pre-run at {:.3f} seconds in {:.3f} seconds".format(n_pre_run_steps,toc,toc - tic))
			
			P, Q, convergedFlg,scale = self._opendssinterface.initialize(Vpcc, targetS, tol)
			OpenDSSData.log(level=20,msg="Completed initialize for feeder after {} steps with P:{},Q:{},convergedFlg:{}".format(n_pre_run_steps,P,Q,convergedFlg))
			return P, Q,convergedFlg,scale 
		except:
			OpenDSSData.log()

#===================================================================================================
	def setVoltage(self, Vpu,Vang,pccName):
		try:
			self._opendssinterface.setVoltage(Vpu,Vang,pccName)
		except:
			OpenDSSData.log()

#===================================================================================================
	def getLoads(self, pccName, t, dt):
		try:
			if OpenDSSData.config['myconfig']['solarFlag']:
				P,Q,Converged = self._opendssinterface.getS(pccName=pccName) #### get updated solution
				V = self._opendssinterface.getVoltage(vtype='actual',busID=self._pvNodes)
				Vpu = self._opendssinterface.getVoltage(vtype='pu',busID=self._pvNodes)
				derP, derQ = self._pvderAggProcedure.run(V=V,Vpu=Vpu,t=t,dt=dt)
				if not self._pvNodes:
					self._pvNodes=[entry+'_tfr' for entry in derP.keys()]
				self._opendssinterface.pvderInjection(derP,derQ,busID=self._pvNodes)
			P,Q,Converged = self._opendssinterface.getS(pccName=pccName)
		
			return P,Q,Converged
		except:
			OpenDSSData.log()

#===================================================================================================
	def scaleLoad(self,scale):
		try:
			self._opendssinterface.scaleLoad(scale)
			return None
		except:
			OpenDSSData.log()

#===================================================================================================
	def monitor(self,msg):
		try:
			res=self._opendssinterface.monitor(msg)
			return res
		except:
			OpenDSSData.log()


