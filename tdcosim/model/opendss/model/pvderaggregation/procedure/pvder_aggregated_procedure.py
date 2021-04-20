from tdcosim.model.opendss.model.pvderaggregation.model.pvder_aggregated_model import PVDERAggregatedModel
from tdcosim.model.opendss.opendss_data import OpenDSSData


class PVDERAggregatedProcedure(object):
#===================================================================================================
	def __init__(self):
		try:
			self._pvderAggModel = PVDERAggregatedModel()
		except:
			OpenDSSData.log()

#===================================================================================================
	def setup(self,S0,V0,V0pu):
		try:
			pvdermap = self._pvderAggModel.setup(S0, V0, V0pu)
			return pvdermap
		except:
			OpenDSSData.log()

#===================================================================================================
	def run(self,V,Vpu):
		try:
			P, Q = self._pvderAggModel.run(V,Vpu)
			return P, Q
		except:
			OpenDSSData.log()
