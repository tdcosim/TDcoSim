import unittest
import sys
import os

import tdcosim
from tdcosim.global_data import GlobalData
from tdcosim.model.psse.psse_model import PSSEModel

dirlocation= os.path.dirname(tdcosim.__file__)
dirlocation = dirlocation[0:len(dirlocation)-8]
print('Home directory:{}'.format(dirlocation))

configlocation = os.path.join(dirlocation,'tests\\testconfig.json')
print('Config location:{}'.format(configlocation))
GlobalData.set_config(configlocation)
GlobalData.set_TDdata()

GlobalData.config["cosimHome"] = dirlocation + '\\tdcoim'
GlobalData.config["psseConfig"]["rawFilePath"] = dirlocation + '\\SampleData\\TNetworks\\118bus\\case118.raw'
GlobalData.config["psseConfig"]["dyrFilePath"] = dirlocation + '\\SampleData\\TNetworks\\118bus\\case118.dyr'
GlobalData.config["openDSSConfig"]["defaultFeederConfig"]["filePath"] = [dirlocation + '\\SampleData\\DNetworks\\123Bus\\case123ZIP.dss']
GlobalData.config["openDSSConfig"]["manualFeederConfig"]["nodes"][0]["filePath"] = [dirlocation + '\\SampleData\\DNetworks\\123Bus\\case123ZIP.dss']


class TestPSSEModel(unittest.TestCase):

    def test_init(self):
        model = PSSEModel()
        self.assertIsInstance(model, PSSEModel)

    def test_setup(self):
        model = PSSEModel()
        model.setup()
        self.assertNotEqual(GlobalData.data['TNet']['TotalRealPowerLoad'], 0)

    def test_staticInitalize(self):
        model = PSSEModel()
        model.setup()
        GlobalData.data['DNet']['Nodes'] = {
            11: {}
        }
        targetS, Vpcc = model.staticInitialize()        
        self.assertIsNotNone(Vpcc[11])
        self.assertIsNotNone(targetS[11])

    def test_dynamicInitalize(self):  
        GlobalData.data['dynamic'] = {}
        model = PSSEModel()
        model.setup()
        GlobalData.data['DNet']['Nodes'] = {
            11: {
                'solarPenetration':0.1
            }
        }        
        GlobalData.data['DNet']['ReductionPercent'] = 0.1
        targetS, Vpcc = model.dynamicInitialize()
        self.assertIsNotNone(Vpcc[11])
        self.assertIsNotNone(targetS[11])
    
    def test_getVoltage(self):
        model = PSSEModel()
        model.setup()
        GlobalData.data['DNet']['Nodes'] = {
            11: {}
        }
        targetS, Vpcc = model.staticInitialize()
        Vpcc2 = model.getVoltage()
        for node in Vpcc:
            self.assertEqual(Vpcc[node], Vpcc2[node])   

    def test_setLoad(self):
        model = PSSEModel()
        model.setup()
        GlobalData.data['DNet']['Nodes'] = {
            11: {}
        }
        S = {
            11: {
                'P': 0.0,
                'Q': 0.0
            }
        }
        targetS, Vpcc = model.staticInitialize()
        model.setLoad(S)
        model.runPFLOW()
        Vpcc2 = model.getVoltage()
        for node in Vpcc:
            self.assertNotEqual(Vpcc[node], Vpcc2[node])     
    
    def test_shunt(self):
        GlobalData.data['dynamic'] = {}
        model = PSSEModel()
        model.setup()
        GlobalData.data['DNet']['Nodes'] = {
            11: {
                'solarPenetration':0.1
            }
        }        
        GlobalData.data['DNet']['ReductionPercent'] = 0.1
        targetS, Vpcc = model.dynamicInitialize()
        power = {
            11: {
                'P': 10.0,
                'Q': 10.0
            }
        }
        model.shunt(targetS, Vpcc, power)
        model.runPFLOW()
        Vpcc2 = model.getVoltage()        
        for node in Vpcc:
            self.assertEqual(Vpcc[node], Vpcc2[node])     

if __name__ == '__main__':
    unittest.main()
