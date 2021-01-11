from tdcosim.model.opendss.model.pvderaggregation.model.pvder_aggregated_model import PVDERAggregatedModel
from tdcosim.model.opendss.opendss_data import OpenDSSData
from tdcosim.global_data import GlobalData


class PVDERAggregatedProcedure(object):
#===================================================================================================
	def __init__(self):
		try:
			self._pvderAggModel = PVDERAggregatedModel()
		except:
			GlobalData.log()

#===================================================================================================
	def setup(self,S0,V0):
		try:
			pvdermap = self._pvderAggModel.setup(S0, V0)
			return pvdermap
		except:
			GlobalData.log()

#===================================================================================================
	def run(self,V):
		try:
			P, Q = self._pvderAggModel.run(V)
			return P, Q
		except:
			GlobalData.log()
