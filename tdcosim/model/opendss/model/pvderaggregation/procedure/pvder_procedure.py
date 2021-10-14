from tdcosim.model.opendss.opendss_data import OpenDSSData
from tdcosim.model.opendss.model.pvderaggregation.model.pvder_model import PVDERModel
from tdcosim.global_data import GlobalData


class PVDERProcedure(object):
#===================================================================================================
	def __init__(self):
		try:
			self._pvderModel = PVDERModel()
		except:
			GlobalData.log()

#===================================================================================================
	def setup(self, nodeid, V0):
		try:
			self._pvderModel.setup(nodeid, V0)
		except:
			GlobalData.log()

#===================================================================================================
	def prerun(self, Va, Vb, Vc):
		try:
			self._pvderModel.prerun(Va, Vb, Vc)
		except:
			GlobalData.log()

#===================================================================================================
	def postrun(self, sol,t):
		try:
			S = self._pvderModel.postrun(sol,t)
			return S
		except:
			GlobalData.log()


