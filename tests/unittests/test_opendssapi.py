import os
import sys
import linecache
import unittest
import pickle
import json
import pdb

from tdcosim.model.opendss.opendss_data import OpenDSSData
from tdcosim.model.opendss.model.opendss_interface import OpenDSSInterface


baseDir=os.path.dirname(os.path.abspath(__file__))
try:
	dss=OpenDSSInterface()
	OpenDSSData.config=json.load(open(baseDir+'\\opendssdata_config.json'))
	expectedResult=pickle.load(open(baseDir+'\\expected_result.pkl'))['OpenDSSInterface']
except:
	raise


#===============================EXCEPTION===============================
def PrintException(debug=False):
	_, exc_obj, tb = sys.exc_info()
	f = tb.tb_frame
	lineno = tb.tb_lineno
	filename = f.f_code.co_filename
	linecache.checkcache(filename)
	line = linecache.getline(filename, lineno, f.f_globals)
	print("Exception in Line {}".format(lineno))
	print("Error in Code: {}".format(line.strip()))
	print("Error Reason: {}".format(exc_obj))
	raise
	if debug:
		return lineno,line,exc_obj


class TestOpenDSSAPI(unittest.TestCase):
#===================================================================================================
	def test_setup(self):
		"""Test OpenDSSInterface.setup"""
		try:
			dss.setup()
			thisER=expectedResult['setup']
			for entry in dss.S0:
				assert entry in thisER['S0']
				for item in dss.S0[entry]:
					assert item in thisER['S0'][entry]
					self.assertAlmostEqual(dss.S0[entry][item],thisER['S0'][entry][item],4)
		except:
			PrintException()

#===================================================================================================
	def test_getVoltage(self):
		"""Test OpenDSSInterface.getVoltage"""
		try:
			V=dss.getVoltage()
			thisER=expectedResult['getVoltage']
			for node in V:
				assert node in thisER['V']
				for phase in V[node]:
					assert phase in thisER['V'][node]
					self.assertAlmostEqual(V[node][phase],thisER['V'][node][phase],4)
		except:
			PrintException()

#===================================================================================================
	def test_getS(self):
		"""Test OpenDSSInterface.getS"""
		try:
			P,Q,convergedFlag=dss.getS()
			thisER=expectedResult['getS']
			self.assertAlmostEqual(P,thisER['P'],4)
			self.assertAlmostEqual(Q,thisER['Q'],4)
			self.assertAlmostEqual(convergedFlag,thisER['convergedFlag'],4)
		except:
			PrintException()

#===================================================================================================
	def test_scaleLoad(self):
		"""Test OpenDSSInterface.scaleLoad"""
		try:
			dss.scaleLoad(1.1)
			P,Q,convergedFlag=dss.getS()
			thisER=expectedResult['scaleLoad']
			self.assertAlmostEqual(P,thisER['P'],4)
			self.assertAlmostEqual(Q,thisER['Q'],4)
			self.assertAlmostEqual(convergedFlag,thisER['convergedFlag'],4)
		except:
			PrintException()

#===================================================================================================
	def test_initialize(self):
		"""Test OpenDSSInterface.initialize"""
		try:
			dss.initialize(Vpcc=1.0,targetS=[100*1e6*1e-3,35*1e6*1e-3],tol=1e-6)
			P,Q,convergedFlag=dss.getS()
			thisER=expectedResult['initialize']
			self.assertAlmostEqual(P,thisER['P'],4)
			self.assertAlmostEqual(Q,thisER['Q'],4)
			self.assertAlmostEqual(convergedFlag,thisER['convergedFlag'],4)
		except:
			PrintException()

#===================================================================================================
	def test_setVoltage(self):
		"""Test OpenDSSInterface.setVoltage"""
		try:
			dss.setVoltage(Vpu=1.04)
			P,Q,convergedFlag=dss.getS()
			thisER=expectedResult['setVoltage']
			self.assertAlmostEqual(P,thisER['P'],4)
			self.assertAlmostEqual(Q,thisER['Q'],4)
			self.assertAlmostEqual(convergedFlag,thisER['convergedFlag'],4)
		except:
			PrintException()


#===================================================================================================
if __name__=="__main__":
	try:
		suite=unittest.TestLoader().loadTestsFromTestCase(TestOpenDSSAPI)

		reqOrder=['test_setup','test_getVoltage','test_getS','test_scaleLoad','test_initialize',
		'test_setVoltage']
		ind=[entry.id().split('.')[-1] for entry in suite.__dict__['_tests']]
		reqOrderInd=[ind.index(entry) for entry in reqOrder]
		orderedTests=[suite.__dict__['_tests'][thisInd] for thisInd in reqOrderInd]
		suite.__dict__['_tests']=orderedTests

		unittest.TextTestRunner(verbosity=2).run(suite)
	except:
		PrintException()




