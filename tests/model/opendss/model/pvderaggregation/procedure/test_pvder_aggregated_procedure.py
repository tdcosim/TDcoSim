import unittest
import sys
import os

from tdcosim.model.opendss.opendss_data import OpenDSSData
from tdcosim.model.opendss.model.pvderaggregation.procedure.pvder_aggregated_procedure import PVDERAggregatedProcedure

from pvder.DER_components_three_phase  import SolarPV_DER_ThreePhase

dirlocation = os.path.abspath(sys.modules['__main__'].__file__)
dirlocation = dirlocation[0:len(dirlocation)-14]
OpenDSSData.config= {'myconfig':{'solarFlag':1,"solarPenetration":0.02,
                                 "filePath":[dirlocation+"\\SampleData\\DNetworks\\123Bus\\case123ZIP.dss"],
                                 'DERParameters':{'power_rating': 50,'voltage_rating':174,'SteadyState':True,
                                                  'V_LV1':0.70,'V_LV2':0.88,'t_LV1_limit':1.0,'t_LV2_limit':2.0,
                                                  'LVRT_INSTANTANEOUS_TRIP':False,'LVRT_MOMENTARY_CESSATION':False,
                                                  'pvderScale':1.0,'solarPenetrationUnit':'kw',
                                                  'avoidNodes': ['sourcebus','rg60'],'dt':1/120.0
                                                 }
                                }
                    }

V0 = {u'160r': {'a': (2237.390351547694-145.8565669057777j),
                'c': (-1057.619553242159+2015.8767511523129j),
                'b': (-1239.6905281551674-  1973.2639490407653j)},
      u'91': {'a': (2224.01488121963-165.40934059326244j),
              'c': (-1045.2656088579122+2023.2200394345857j),
              'b': (-1261.0671426797442-1947.5104779794774j)},
      u'135': {'a': (2265.2376124369284-97.71670507503666j),
               'c': (-1104.4294252268437+2012.442241107808j),
               'b': (-1218.429324410273-2003.9666831963164j)},
      u'25': {'a': (2260.621044619631-103.61439555673951j),
              'c': (-1099.5790100141614+2007.83819556158j),
              'b': (-1218.7432236968239-2005.8619118100912j)}
     }

S0 = {'Q': {u's53a': 21.416015625, u's73c': 21.416015625, u's106b': 21.416015625, u's90b': 21.416015625, u's86b': 0.0, u's111a': 0.0,                   u's63a': 21.416015625, u's104c': 21.416015625
           },
      'P': {u's53a': 40.0, u's73c': 40.0, u's106b': 40.0, u's90b': 40.0, u's86b': 20.0, u's111a': 20.0,u's63a': 40.0, u's104c': 40.0
           }
     }


V = {u'160r_tfr': {'a': (172.7027796828413+2.3069971144665763e-07j),
                   'c': (-86.35139000457411+149.5649944085661j),
                   'b': (-86.35138964574229-149.5649945931886j)},
     u'91_tfr':  {'a': (172.70277968284137+2.293657871797609e-07j),
                  'c': (-86.35139000345653+149.5649944092112j),
                  'b': (-86.35138964673416-149.56499459261593j)},
     u'135_tfr': {'a': (172.7031565838637-0.000189301313610517j),
                  'c': (-86.35140563897261+149.56535461412395j),
                  'b': (-86.3516093540961-149.56515658508175j),},
     u'25_tfr': {'a': (172.70318091085673-0.000192775612229237j),
                 'c': (-86.35140322712465+149.5653757629125j),
                 'b': (-86.35162096585621-149.56516733818685j)}
    }
  
nodeid = '150r'

class TestPVDERAggregatedProcedure(unittest.TestCase):
    
    def test_init(self):
        model = PVDERAggregatedProcedure()        
        self.assertIsInstance(model, PVDERAggregatedProcedure)
    
    def test_setup(self):
        model = PVDERAggregatedProcedure()
        
        pvdermap = model.setup(S0, V0)
        
        self.assertTrue(len(pvdermap) == len(model._pvderAggModel._pvders),msg = 'Number of PV-DER nodes should be equal to number of PV-DER instances')
        for node in pvdermap:
            self.assertTrue(pvdermap[node]['nSolar_at_this_node'] == 1,msg = 'Node should contain only one PV-DER instance')
       
        for model in model._pvderAggModel._pvders.values():
            self.assertIsInstance(model._pvderModel.PV_model,SolarPV_DER_ThreePhase,msg = 'Node should contain a 3 phase PV-DER instance')              
    def test_run(self):
        model = PVDERAggregatedProcedure()
            
        pvdermap = model.setup(S0, V0)
            
        P,Q = model.run(V)
        
        for node in pvdermap:
            print('DER aggregated power -- Active:{} kW,Reactive:{} kVAR'.format(P[node],Q[node]))
            self.assertIsInstance(P[node],float)
            self.assertIsInstance(Q[node],float)

if __name__ == '__main__':
    unittest.main()
