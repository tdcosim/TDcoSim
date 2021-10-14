import os
import sys
import pdb
import inspect

import tdcosim
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
			baseDir=os.path.dirname(inspect.getfile(tdcosim))
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
			if GlobalData.config['simulationConfig']['simType']=='dynamic':
				generate_output(GlobalData,excel=False)
			elif GlobalData.config['simulationConfig']['simType']=='static':
				generate_output(GlobalData,excel=False,dataframe=True)
		except:
			GlobalData.log()

			