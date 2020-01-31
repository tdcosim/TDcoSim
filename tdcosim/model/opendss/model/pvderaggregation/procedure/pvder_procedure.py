from tdcosim.model.opendss.opendss_data import OpenDSSData
from tdcosim.model.opendss.model.pvderaggregation.model.pvder_model import PVDERModel
class PVDERProcedure:
    def __init__(self):        
        self._pvderModel = PVDERModel()        

    def setup(self, nodeid,plantid=None):
        self._pvderModel.setup(nodeid,plantid)        

    def prerun(self, Va, Vb, Vc):
        self._pvderModel.prerun(Va, Vb, Vc)
        return None

    def postrun(self, sol,t):
        S = self._pvderModel.postrun(sol,t)
        return S
