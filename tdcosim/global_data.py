import json
import os
import logging
import pprint
import uuid
import pdb

from tdcosim.exceptionutil import ExceptionUtil


class GlobalData(ExceptionUtil):
#===================================================================================================
	def __init__(self):
		try:
			super(GlobalData,self).__init__()
			self.config={}
		except:
			raise

#===================================================================================================
	def set_config(self, inputfile):
		try:
			# check
			filepath = os.path.abspath(inputfile)
			assert os.path.exists(filepath),"config file {} does not exist".format(filepath)
			self.config = json.load(open(filepath))
			if not 'simID' in self.config['outputConfig'] or not self.config['outputConfig']['simID']:
				self.config['outputConfig']['simID']=uuid.uuid4().hex
			self.config['outputConfig']['outputDir']=os.path.join(os.path.abspath(\
			self.config['outputConfig']['outputDir']),self.config['outputConfig']['simID'])
			if not os.path.exists(self.config['outputConfig']['outputDir']):
				os.system('mkdir {}'.format(self.config['outputConfig']['outputDir']))
			if 'scenarioID' not in self.config['outputConfig'] or \
			not self.config['outputConfig']['scenarioID']:
				self.config['outputConfig']['scenarioID']=uuid.uuid4().hex

			# check encoding
			if 'openDSSConfig' in self.config:
				for entry in self.config['openDSSConfig']:
					if isinstance(self.config['openDSSConfig'][entry],unicode):
						self.config['openDSSConfig'][entry]=\
						self.config['openDSSConfig'][entry].encode('ascii')
				if 'manualFeederConfig' in self.config['openDSSConfig'] and \
				'nodes' in self.config['openDSSConfig']['manualFeederConfig']:
					for entry in self.config['openDSSConfig']['manualFeederConfig']['nodes']:
						if 'filePath' in entry:
							for item in entry['filePath']:
								if isinstance(item,unicode):
									item=item.encode('ascii')
			for entry in self.config['outputConfig']:
				if isinstance(self.config['outputConfig'][entry],unicode):
					self.config['outputConfig'][entry]=\
					self.config['outputConfig'][entry].encode('ascii')

			# setup logging
			if 'logging' in self.config and 'level' in self.config['logging']:
				logLevel=self.config['logging']['level']
			else:
				logLevel=logging.DEBUG

			basedir=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
			self.create_logger("GlobalData_logger",logFilePath=os.path.join(basedir,'logs',
			'globaldata.log'),logLevel=logLevel,mode='w')
		except:
			raise

#===================================================================================================
	def set_TDdata(self):
		try:
			self.data = {'TNet':{},'DNet':{},'TS': 0.0}
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
			if level==logging.ERROR or level==logging.CRITICAL:# will also raise
				self.exception_handler(msg)
			else:
				self.logger.log(level,msg)
		except:
			raise


GlobalData = GlobalData()


