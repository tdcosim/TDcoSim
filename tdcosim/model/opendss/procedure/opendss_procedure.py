from tdcosim.model.opendss.model.opendss_interface import OpenDSSInterface
from tdcosim.model.opendss.model.pvderaggregation.procedure.pvder_aggregated_procedure import PVDERAggregatedProcedure
from tdcosim.model.opendss.opendss_data import OpenDSSData


class OpenDSSProcedure(object):
	def __init__(self):
		try:
			self._opendssinterface = OpenDSSInterface()
			self._pvderAggProcedure = PVDERAggregatedProcedure()
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

			if OpenDSSData.config['myconfig']['solarFlag']:
				# Re-setup DER after reload the OpenDSS
				S0 = self._opendssinterface.getLoads()
				V0 = self._opendssinterface.getVoltage(vtype='actual')
				pvdermap = self._pvderAggProcedure.setup(S0, V0)
				self._opendssinterface.setupDER(pvdermap)			
				for n in range(200):# synchronize
					V = self._opendssinterface.getVoltage(vtype='actual')
					derP, derQ = self._pvderAggProcedure.run(V)
					self._opendssinterface.pvderInjection(derP, derQ)
					P,Q,Converged = self._opendssinterface.getS(pccName='Vsource.source')

			P, Q, convergedFlg = self._opendssinterface.initialize(Vpcc, targetS, tol)
		
			OpenDSSData.log(level=20,msg="completed initialize with P:{},Q:{},convergedFlg:{}".format(\
			P,Q,convergedFlg))
			return P, Q
		except:
			OpenDSSData.log()

#===================================================================================================
	def setVoltage(self, Vpu,Vang,pccName):
		try:
			self._opendssinterface.setVoltage(Vpu,Vang,pccName)
		except:
			OpenDSSData.log()

#===================================================================================================
	def getLoads(self, pccName):
		try:
			derP = {}
			derQ = {}
			if OpenDSSData.config['myconfig']['solarFlag']:
				V = self._opendssinterface.getVoltage(vtype='actual')
				derP, derQ = self._pvderAggProcedure.run(V)
				self._opendssinterface.pvderInjection(derP, derQ)
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


