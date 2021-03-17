import numpy as np
import pdb
from tdcosim.procedure.default_procedure import DefaultProcedure
from tdcosim.model.psse.psse_model import PSSEModel
from tdcosim.model.opendss.opendss_model import OpenDSSModel
from tdcosim.global_data import GlobalData


class DefaultStaticProcedure(DefaultProcedure):
    def __init__(self):
        self._tnet_model = PSSEModel()
        self._dnet_model = OpenDSSModel()
    def setup(self):
        self._tnet_model.setup()
        self._dnet_model.setup()        
    def initialize(self):        
        targetS, Vpcc = self._tnet_model.staticInitialize()        
        power = self._dnet_model.initialize(targetS, Vpcc)        
        self._tnet_model.shunt(targetS, Vpcc, power)
    def run(self):        
        GlobalData.data['static'] = {}
        maxIter = 20
        tol=10**-4
        count = 0
        loadShape = GlobalData.config['simulationConfig']['staticConfig']['loadShape']
        GlobalData.data['monitorData']={}
        for scale in loadShape:
            GlobalData.data['static'][count] = {}
            f=lambda x:[x[entry] for entry in x]
            iteration=0
            scaleData={}
            Vpcc = self._tnet_model.getVoltage()
            Vcheck=np.random.random((len(Vpcc),2))
            for nodeID in Vpcc:
                scaleData[nodeID]=scale
            self._dnet_model.scaleLoad(scaleData)# now scale distribution feeder load

            while np.any(np.abs(Vcheck[:,0]-Vcheck[:,1])>tol) and iteration<maxIter:
                self._tnet_model.runPFLOW()# run power flow
                Vpcc = self._tnet_model.getVoltage()
                self._dnet_model.setVoltage(Vpcc)#set voltage based on previous guess
                S = self._dnet_model.getLoad()# get complex power injection
                self._tnet_model.setLoad(S)# set complex power injection as seen from T side
                Vcheck[:,0]=Vcheck[:,1]#iterate for tight coupling
                Vcheck[:,1]=np.array(f(Vpcc))
                iteration+=1

            # collect data and store
            msg={}
            msg['varName']={}
            for node in Vpcc:
                msg['varName'][node]=['voltage']
            GlobalData.data['monitorData'][count]=self._dnet_model.monitor(msg)

            GlobalData.data['static'][count]['V'] = Vpcc
            GlobalData.data['static'][count]['S'] = S
            GlobalData.data['static'][count]['Scale'] = scale
            count = count + 1
        
