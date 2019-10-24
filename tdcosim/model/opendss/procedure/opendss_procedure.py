from tdcosim.model.opendss.model.opendss_interface import OpenDSSInterface
from tdcosim.model.opendss.model.pvderaggregation.procedure.pvder_aggregated_procedure import PVDERAggregatedProcedure
from tdcosim.model.opendss.opendss_data import OpenDSSData
class OpenDSSProcedure:
    def __init__(self):        
        
        self._opendssinterface = OpenDSSInterface()        
        self._pvderAggProcedure = PVDERAggregatedProcedure()            
        

#===================================================================================================
    def setup(self):        
        self._opendssinterface.setup()        
        

#===================================================================================================
    def initialize(self,targetS ,Vpcc ,tol):
        
        derP = {}
        derQ = {}

        P, Q, convergedFlg = self._opendssinterface.initialize(Vpcc, targetS, tol)
        if OpenDSSData.config['myconfig']['solarFlag']:
            # Re-setup DER after reload the OpenDSS
            S0 = self._opendssinterface.getLoads()
            V0 = self._opendssinterface.getVoltage(vtype='actual')
            pvdermap = self._pvderAggProcedure.setup(S0, V0)
            self._opendssinterface.setupDER(pvdermap)            
            #for n in range(1):# 25 cycles to synchronize
            #    V = self._opendssinterface.getVoltage(vtype='actual')
            #    derP, derQ = self._pvderAggProcedure.run(V)
            #    self._opendssinterface.pvderInjection(derP, derQ)
        
        return P, Q

#===================================================================================================
    def setVoltage(self, Vpu,Vang,pccName):
        self._opendssinterface.setVoltage(Vpu,Vang,pccName)

#===================================================================================================
    def getLoads(self, pccName):
        
        derP = {}
        derQ = {}
        if OpenDSSData.config['myconfig']['solarFlag']:
            V = self._opendssinterface.getVoltage(vtype='actual')
            derP, derQ = self._pvderAggProcedure.run(V)
            self._opendssinterface.pvderInjection(derP, derQ)
        P,Q,Converged = self._opendssinterface.getS(pccName=pccName)
        
        return P,Q,Converged

#===================================================================================================
    def scaleLoad(self,scale):
        self._opendssinterface.scaleLoad(scale)
        return None

#===================================================================================================
    def monitor(self,msg):
        res=self._opendssinterface.monitor(msg)
        return res




