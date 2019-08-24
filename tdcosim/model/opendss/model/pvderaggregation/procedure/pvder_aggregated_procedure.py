from tdcosim.model.opendss.model.pvderaggregation.model.pvder_aggregated_model import PVDERAggregatedModel
from tdcosim.model.opendss.opendss_data import OpenDSSData
class PVDERAggregatedProcedure:
    def __init__(self):        
        self._pvderAggModel = PVDERAggregatedModel()        
    def setup(self, S0, V0):        
        pvdermap = self._pvderAggModel.setup(S0, V0)        
        return pvdermap
    def run(self, V):
        P, Q = self._pvderAggModel.run(V)
        return P, Q
