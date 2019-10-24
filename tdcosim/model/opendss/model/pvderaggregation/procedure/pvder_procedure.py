from tdcosim.model.opendss.opendss_data import OpenDSSData
from tdcosim.model.opendss.model.pvderaggregation.model.pvder_model import PVDERModel
class PVDERProcedure:
    def __init__(self):        
        self._pvderModel = PVDERModel()        

    def setup(self, nodeid, V0):
        self._pvderModel.setup(nodeid, V0)        

    def prerun(self, Va, Vb, Vc):
        self._pvderModel.prerun(Va, Vb, Vc)
        return None

    def postrun(self, sol,t):
        S = self._pvderModel.postrun(sol,t)
        return S
