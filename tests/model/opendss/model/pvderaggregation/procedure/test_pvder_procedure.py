import unittest
import sys
import os
import math

import tdcosim
from tdcosim.model.opendss.opendss_data import OpenDSSData
from tdcosim.model.opendss.model.pvderaggregation.procedure.pvder_procedure import PVDERProcedure
from tdcosim.test import der_test_manual_config

from pvder.DER_components_three_phase  import SolarPV_DER_ThreePhase

dirlocation= os.path.dirname(tdcosim.__file__)
dirlocation = dirlocation[0:len(dirlocation)-8]
print('Home directory:{}'.format(dirlocation))

OpenDSSData.config['myconfig'] = der_test_manual_config.test_config

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
		
	def test_prerun(self):
		model = PVDERProcedure()
			
		model.setup(nodeid)
		
		model.prerun(V['a'], V['b'],V['c'])			
		self.assertAlmostEqual(V['a'], (model._pvderModel.PV_model.gridVoltagePhaseA*model._pvderModel.PV_model.Vbase)/math.sqrt(2),msg = 'PCC - LV side voltages must be equal!')
		self.assertAlmostEqual(V['b'], (model._pvderModel.PV_model.gridVoltagePhaseB*model._pvderModel.PV_model.Vbase)/math.sqrt(2),msg = 'PCC - LV side voltages must be equal!')
		self.assertAlmostEqual(V['c'], (model._pvderModel.PV_model.gridVoltagePhaseC*model._pvderModel.PV_model.Vbase)/math.sqrt(2),msg = 'PCC - LV side voltages must be equal!')
		
		
		#S = model.postrun(V['a'], V['b'],V['c'])
		#print('DER apparent power:{} kVA'.format(S))
		
		#self.assertIsInstance(S,complex)
		#self.assertAlmostEqual(S.real, model._pvderModel.PV_model.S_PCC.real*model._pvderModel.PV_model.Sbase/1e3,msg = 'Active power must be equal!')
		#self.assertAlmostEqual(S.imag, model._pvderModel.PV_model.S_PCC.imag*model._pvderModel.PV_model.Sbase/1e3,msg = 'Reactive power must be equal!')

if __name__ == '__main__':
	unittest.main()
