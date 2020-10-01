import unittest
import sys
import os

import tdcosim
from tdcosim.model.opendss.opendss_data import OpenDSSData
from tdcosim.model.opendss.model.pvderaggregation.model.pvder_model import PVDERModel
from pvder.DER_components_three_phase  import SolarPVDERThreePhase
from tdcosim.test import der_test_manual_config

dirlocation= os.path.dirname(tdcosim.__file__)
dirlocation = dirlocation[0:len(dirlocation)-8]
print('Home directory:{}'.format(dirlocation))

OpenDSSData.config['myconfig'] = der_test_manual_config.test_config

class TestPVDERModel(unittest.TestCase):
    
    def test_init(self):
        model = PVDERModel()
        self.assertIsInstance(model, PVDERModel)

    def test_setup(self):
        model = PVDERModel()
        model.setup('150r',{'a': (2370.2490676972598+7.948851747145637e-07j), 'c': (-1185.1245340341793+2052.695905722238j), 'b': (-1185.1245332166936-2052.695905884739j)})
        self.assertIsInstance(model.PV_model, SolarPVDERThreePhase)

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

