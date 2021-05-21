import os
import copy
import json
import pdb

import numpy as np

from tdcosim.global_data import GlobalData


class Dera(object):
	def __init__(self,templatePath=None):
		try:
			super(Dera,self).__init__()
			if not templatePath:
				baseDir=os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(\
				os.path.abspath(__file__)))))
			templatePath=os.path.join(baseDir,'config','guideline.json')
			templates=self.load_config_template(templatePath)
			self.template=templates['table3.1']
			self.ind=templates['ind']
		except:
			GlobalData.log()

#=======================================================================================================================
	def load_config_template(self,fpath):
		try:
			conf=json.load(open(fpath))
			return conf
		except:
			GlobalData.log()

#=======================================================================================================================
	def generate_config(self,busID,configType,userInput=None):
		try:
			conf={}
			if configType in self.template:
				for thisBusID in busID:
					thisTemplate=copy.deepcopy(self.template[configType])
					if userInput:
						if 'all' in userInput:
							if 'flags' in userInput['all']:
								for thisFlag in userInput['all']['flags']:
									thisTemplate['flags'][thisFlag]['value']=\
									userInput['all']['flags'][thisFlag]
							if 'params' in userInput['all']:
								for thisParam in userInput['all']['params']:
									thisTemplate['included_parameters'][thisParam]['value']=\
									userInput['all']['params'][thisParam]
						elif str(thisBusID) in userInput:
							if 'flags' in userInput[str(thisBusID)]:
								for thisFlag in userInput[str(thisBusID)]['flags']:
									thisTemplate['flags'][thisFlag]['value']=\
									userInput[str(thisBusID)]['flags'][thisFlag]
							if 'params' in userInput[str(thisBusID)]:
								for thisParam in userInput[str(thisBusID)]['params']:
									thisTemplate['included_parameters'][thisParam]['value']=\
									userInput[str(thisBusID)]['params'][thisParam]

					flagArray=np.zeros(len(thisTemplate['flags']),dtype=int)
					paramArray=np.zeros(len(thisTemplate['included_parameters']))

					for flag in thisTemplate['flags']:
						flagArray[self.ind['flag_properties'][flag]['index']]=\
						thisTemplate['flags'][flag]['value']

					for param in self.ind['parameter_properties']:
						paramArray[self.ind['parameter_properties'][param]['index']]=\
						thisTemplate['included_parameters'][param]['value']

					conf[thisBusID]={'flags':flagArray,'params':paramArray}

			return conf
		except:
			GlobalData.log()

#=======================================================================================================================
	def dera2dyr(self,conf,dyrFilePath,deraID=None,fileMode='w'):
		"""Write dera data to dyrFilePath that can then be added using psspy.dyre_add method."""
		try:
			dyrStr=''
			if not deraID:
				deraID=['1']*len(conf)
			for busID,thisDeraID in zip(conf,deraID):
				dyrStr+="{},'DERA1',{},".format(busID,thisDeraID)
				for thisIdata in conf[busID]['flags']:
					dyrStr+='{},'.format(thisIdata)
				for thisRdata in conf[busID]['params']:
					dyrStr+='{},'.format(thisRdata)
				dyrStr+=' /\n'

			f=open(dyrFilePath,fileMode); f.write(dyrStr); f.close()
		except:
			GlobalData.log()

