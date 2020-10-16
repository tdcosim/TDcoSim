import os
import copy
import json

import numpy as np

from utils import PrintException


class Dera(object):
	def __init__(self,templatePath=None):
		if not templatePath:
			templatePath=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+os.path.sep\
			+'config'+os.path.sep+'guideline.json'
		templates=self.load_config_template(templatePath)
		self.template=templates['table3.1']
		self.ind=templates['ind']

#=======================================================================================================================
	def load_config_template(self,fpath):
		try:
			conf=json.load(open(fpath))
			return conf
		except:
			PrintException()

#=======================================================================================================================
	def generate_config(self,busID,configType):
		try:
			conf={}
			if configType in self.template:
				for thisBusID in busID:
					flagArray=np.zeros(len(self.template[configType]['flags']),dtype=int)
					paramArray=np.zeros(len(self.template[configType]['included_parameters']))

					for flag in self.template[configType]['flags']:
						flagArray[self.ind['flag_properties'][flag]['index']]=\
						self.template[configType]['flags'][flag]['value']

					for param in self.ind['parameter_properties']:
						paramArray[self.ind['parameter_properties'][param]['index']]=\
						self.template[configType]['included_parameters'][param]['value']

					conf[thisBusID]={'flags':flagArray,'params':paramArray}

			return conf
		except:
			PrintException()

#=======================================================================================================================
	def dera2dyr(self,conf,dyrFilePath):
		"""Write dera data to dyrFilePath that can then be added using psspy.dyre_add method."""
		try:
			dyrStr=''
			for busID in conf:
				dyrStr+="{},'DERA1',1,".format(busID)
				for thisIdata in conf[busID]['flags']:
					dyrStr+='{},'.format(thisIdata)
				for thisRdata in conf[busID]['params']:
					dyrStr+='{},'.format(thisRdata)
				dyrStr+=' /\n'

			f=open(dyrFilePath,'w'); f.write(dyrStr); f.close()
		except:
			PrintException()



