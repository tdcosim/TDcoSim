import os
import sys

from default_procedure import DefaultProcedure
from default_static_procedure import DefaultStaticProcedure
from default_dynamic_procedure import DefaultDynamicProcedure
from tdcosim.global_data import GlobalData

class Procedure(DefaultProcedure):
	def __init__(self):
		if GlobalData.config['simulationConfig']['simType'].lower() == 'static':
			self._procedure = DefaultStaticProcedure()
		elif GlobalData.config['simulationConfig']['simType'].lower() == 'dynamic':
			self._procedure = DefaultDynamicProcedure()
		else:
			print ("Unsupported Simulation Type")

	def simulate(self):
		self._procedure.setup()	
		self._procedure.initialize()
		self._procedure.run()
		if 'cleanup' in GlobalData.config['psseConfig']:
			for entry in GlobalData.config['psseConfig']['cleanup']:
				if 'win' in sys.platform:
					os.system('del {}'.format(entry))
				if 'linux' in sys.platform:
					os.system('rm {}'.format(entry))
