import unittest
import sys
import os

from tdcosim.model.opendss.opendss_data import OpenDSSData
from tdcosim.model.opendss.model.pvderaggregation.model.pvder_model import PVDERModel
from pvder.DER_components_three_phase  import SolarPV_DER_ThreePhase

dirlocation = os.path.abspath(sys.modules['__main__'].__file__)
rootindex = dirlocation.index('tdcosim_pkg')
dirlocation = dirlocation[0:rootindex+11]

OpenDSSData.config['myconfig'] = {
    "nodenumber": 11,
    "filePath": [dirlocation+"\\SampleData\\DNetworks\\123Bus\\case123ZIP.dss"],
    "solarFlag":1,
    "solarPenetration":0.1,
    "DERParameters":{
        "power_rating": 50,
        "voltage_rating":174,
        "SteadyState": True,
        "V_LV1": 0.70,
        "V_LV2": 0.88,
        "t_LV1_limit": 10.0,  
        "t_LV2_limit": 20.0,
        "LVRT_INSTANTANEOUS_TRIP": False,
        "LVRT_MOMENTARY_CESSATION": False
    }
}


class TestPVDERModel(unittest.TestCase):
    
    def test_init(self):
        model = PVDERModel()
        self.assertIsInstance(model, PVDERModel)

    def test_setup(self):
        model = PVDERModel()
        model.setup('150r')
        self.assertIsInstance(model.PV_model, SolarPV_DER_ThreePhase)

    ## TODO: Update the run test
    # def test_run(self):
    #     model = PVDERModel()
    #     model.setup('150r')
    #     v = {'a': (2370.2490676972598+7.948851747145637e-07j), 'c': (-1185.1245340341793+2052.695905722238j), 'b': (-1185.1245332166936-2052.695905884739j)}
    #     S = model.run(v['a'], v['b'],v['c'])
    #     print(S)
    #     self.assertNotEqual(S, 0)

if __name__ == '__main__':
    unittest.main()

