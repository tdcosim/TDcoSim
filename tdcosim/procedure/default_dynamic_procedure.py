from default_procedure import DefaultProcedure
from tdcosim.model.psse.psse_model import PSSEModel
from tdcosim.model.opendss.opendss_model import OpenDSSModel
from tdcosim.global_data import GlobalData
class DefaultDynamicProcedure(DefaultProcedure):
    def __init__(self):
        self._tnet_model = PSSEModel()
        self._dnet_model = OpenDSSModel()

    def setup(self):
        self._tnet_model.setup()
        self._dnet_model.setup()        
    def initialize(self):
        GlobalData.data['dynamic'] = {}        
        targetS, Vpcc = self._tnet_model.dynamicInitialize()        
        power = self._dnet_model.initialize(targetS, Vpcc)        
        self._tnet_model.shunt(targetS, Vpcc, power)
    def run(self):
        
        GlobalData.data['monitorData']={}
        GlobalData.data['TNet']['Dynamic'] = {}    
        dt = 0.0083333
        maxIter=1
        tol=10**-4
        if GlobalData.config['simulationConfig']['protocol'].lower() != 'loose_coupling':
            maxIter = GlobalData.config['simulationConfig']['protocol']['maxiteration']
        eventData=GlobalData.config['simulationConfig']['dynamicConfig']['events']
        events=eventData.keys()
        events.sort()
        t = 0
        for event in events:
            while t<eventData[event]['time']:
                iteration=0
                mismatch=100.
                if t<=eventData[event]['time'] and t+dt>=eventData[event]['time']:
                    if eventData[event]['type']=='faultOn':
                        self._tnet_model.faultOn(eventData[event]['faultBus'],eventData[event]['faultImpedance'])
                    elif eventData[event]['type']=='faultOff':
                        self._tnet_model.faultOff()    
                while mismatch>tol and iteration<maxIter:
                    try:
                        self._tnet_model.runDynamic(t+dt)                    
                        t = t + dt
                        print ("Sim time: " + str(t))
                        Vpcc = self._tnet_model.getVoltage()
                        self._dnet_model.setVoltage(Vpcc)
                        S = self._dnet_model.getLoad()
                        self._tnet_model.setLoad(S)

                        # collect data and store
                        msg={}
                        msg['varName']={}
                        for node in Vpcc:
                            msg['varName'][node]=['voltage','der']
                        GlobalData.data['monitorData'][t]=self._dnet_model.monitor(msg)

                        GlobalData.data['TNet']['Dynamic'][t] = {
                                            'V': Vpcc,
                                            'S': S
                                        }
                        #mismatch=Vprev-V ##TODO: Need to update mismatch
                        #TODO: tight_coupling isn't implemented
                        if GlobalData.config['simulationConfig']['protocol'].lower()=='tight_coupling' and mismatch>tol:
                            print ("Tight Couping is not implemented")
                        iteration+=1
                    except Exception as e:
                        print ('failed to run dynamic simulation')
                        GlobalData.data['TNet']['Dynamic'][t] = {
                                            'V': Vpcc,
                                            'S': S
                                        }
                        DSSconvergenceFlg = True
                        for busID in GlobalData.data['TNet']['LoadBusNumber']:
                            if busID in GlobalData.data['DNet']['Nodes']:
                                if S[busID]['convergenceFlg'] is False:
                                    DSSconvergenceFlg = False
                                    break;
                        if DSSconvergenceFlg is False:
                            print ('OpenDSS Convergence Failed')
