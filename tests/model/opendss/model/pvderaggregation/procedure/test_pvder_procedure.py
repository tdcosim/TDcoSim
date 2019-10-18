import unittest
import sys
import os

from tdcosim.model.opendss.opendss_data import OpenDSSData
from tdcosim.model.opendss.model.pvderaggregation.procedure.pvder_procedure import PVDERProcedure

from pvder.DER_components_three_phase  import SolarPV_DER_ThreePhase

dirlocation = os.path.abspath(sys.modules['__main__'].__file__)
dirlocation = dirlocation[0:len(dirlocation)-14]
OpenDSSData.config= {'myconfig':{'solarFlag':1,"solarPenetration":0.02,
                                 "filePath":[dirlocation+"\\SampleData\\DNetworks\\123Bus\\case123ZIP.dss"],
                                 'DERParameters':{'power_rating': 50,'voltage_rating':174,'SteadyState':True,
                                                  'V_LV0':0.5,'V_LV1':0.70,'V_LV2':0.88,
                                                  't_LV0_limit': 0.1, 't_LV1_limit':1.0,'t_LV2_limit':2.0,
                                                  'V_HV1':1.06,'V_HV2':1.12,
                                                  't_HV1_limit':3.0,'t_HV2_limit':0.016,
                                                 'VRT_INSTANTANEOUS_TRIP':False,'VRT_MOMENTARY_CESSATION':False,'OUTPUT_RESTORE_DELAY':0.5,
                                                  'pvderScale':1.0,'solarPenetrationUnit':'kw',
                                                  'avoidNodes': ['sourcebus','rg60'],'dt':1/120.0
                                                 }
                                }
                    }
V =  {'a': (172.7027796828413+2.3069971144665763e-07j), 'c': (-86.35139000457411+149.5649944085661j), 'b': (-86.35138964574229-149.5649945931886j)}

nodeid = '150r'

class TestPVDERProcedure(unittest.TestCase):
    
    def test_init(self):
        model = PVDERProcedure()
        self.assertIsInstance(model, PVDERProcedure)
    
    def test_setup(self):
        model = PVDERProcedure()    
        
        model.setup(nodeid)
        self.assertIsInstance(model._pvderModel.PV_model, SolarPV_DER_ThreePhase)
        self.assertTrue(str(os.getpid()) in model._pvderModel.PV_model.name and nodeid in model._pvderModel.PV_model.name,msg = 'DER name must contain PID and node ID')
        
    def test_run(self):
        model = PVDERProcedure()
            
        model.setup(nodeid)
            
        S = model.run(V['a'], V['b'],V['c'])
        print('DER apparent power:{} kVA'.format(S))
        
        self.assertIsInstance(S,complex)
        self.assertAlmostEqual(S.real, model._pvderModel.PV_model.S_PCC.real*model._pvderModel.PV_model.Sbase/1e3,msg = 'Active power must be equal!')
        self.assertAlmostEqual(S.imag, model._pvderModel.PV_model.S_PCC.imag*model._pvderModel.PV_model.Sbase/1e3,msg = 'Reactive power must be equal!')

if __name__ == '__main__':
    unittest.main()
