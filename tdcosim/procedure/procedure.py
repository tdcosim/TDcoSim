import os
import sys
import pdb

from tdcosim.global_data import GlobalData
from tdcosim.procedure.default_procedure import DefaultProcedure
from tdcosim.procedure.default_dynamic_procedure import DefaultDynamicProcedure
from tdcosim.procedure.default_static_procedure import DefaultStaticProcedure
from tdcosim.report import generate_output


class Procedure(DefaultProcedure):
#===================================================================================================
	def __init__(self):
		try:
			# empty opendss log file from previous run
			baseDir=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
			f=open(os.path.join(baseDir,'logs','opendssdata.log'),'w')
			f.close()
			if GlobalData.config['simulationConfig']['simType'].lower() == 'static':
				self._procedure = DefaultStaticProcedure()
			elif GlobalData.config['simulationConfig']['simType'].lower() == 'dynamic':
				self._procedure = DefaultDynamicProcedure()
			else:
				print ("Unsupported Simulation Type")
		except:
			GlobalData.log()

#===================================================================================================
	def simulate(self):
		try:
			self._procedure.setup()
			self._procedure.initialize()
			self._procedure.run()
			generate_output(GlobalData,excel=False)
		except:
			GlobalData.log()

			