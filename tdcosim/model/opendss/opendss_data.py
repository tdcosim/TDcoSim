import json
import os
import pprint
import logging
import pdb
import inspect

import tdcosim
from tdcosim.global_data import GlobalData
from tdcosim.exceptionutil import ExceptionUtil


class OpenDSSData(ExceptionUtil):
#===================================================================================================
	def __init__(self,logLevel=logging.DEBUG):
		try:
			super(OpenDSSData,self).__init__()
			self.config = {}
			self.data = {'TNet':{},'DNet':{},'TS': 0.0}

			# setup logging
			if 'logging' in GlobalData.config and 'level' in GlobalData.config['logging']:
				logLevel=GlobalData.config['logging']['level']
			else:
				logLevel=logging.DEBUG

			baseDir=os.path.dirname(inspect.getfile(tdcosim))
			self.create_logger("OpenDSSData_logger",logFilePath=os.path.join(baseDir,'logs',
			'opendssdata.log'),logLevel=logLevel,mode='a')
		except:
			raise

#===================================================================================================
	def set_config(self,filepath):
		try:
			filepath = os.path.abspath(inputfile)
			self.config = json.load(open(filepath))
		except:
			raise

#===================================================================================================
	def print_config(self):
		try:
			pprint.pprint(self.config)
		except:
			raise

#===================================================================================================
	def print_data(self):
		try:
			pprint.pprint(self.data)
		except:
			raise

#===================================================================================================
	def log(self,level=None,msg=None):
		try:
			if not level:
				level=logging.ERROR
			if level==logging.ERROR:
				self.exception_handler(msg)
			else:
				self.logger.log(level,msg)
		except:
			raise


OpenDSSData = OpenDSSData()


