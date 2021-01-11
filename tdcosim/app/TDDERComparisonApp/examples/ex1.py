import os
import pdb

from tdcosim.confighelper import ConfigHelper
from tdcosim.report import generate_output
from tdcosim.global_data import GlobalData
from tdcosim.procedure.procedure import Procedure
from tdcosim.app.TDDERComparisonApp import PrintException


#=======================================================================================================================
if __name__=='__main__':
	try:
		ch=ConfigHelper()

		# create config using ConfigHelper
		thisAppHome=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
		cosimHome=os.path.dirname(os.path.dirname(thisAppHome))
		ch.add_cosimhome(cosimHome) # specifies tdcosim path

		# psse config
		psseDataDir=os.path.join(thisAppHome,'data','transmission')
		# rawFilePath=os.path.join(psseDataDir,'118bus','case118.raw')
		# dyrFilePath=os.path.join(psseDataDir,'118bus','case118.dyr')
		rawFilePath=os.path.join(psseDataDir,'68bus','case68.raw')
		dyrFilePath=os.path.join(psseDataDir,'68bus','case68.dyr')
		installLocation=''
		ch.add_psseconfig(rawFilePath=rawFilePath,dyrFilePath=dyrFilePath,installLocation=installLocation)

		# opendss config
		opendssDataDir=os.path.join(thisAppHome,'data','distribution')
		fc=feederConfig={}
		fc['nodenumber']=[59,60]# T-D interface bus

		# we define one config for bus 59 and use the same for 60
		fc['filePath']=[os.path.join(opendssDataDir,'123Bus','case123ZIP.dss')]*2
		fc['solarFlag']=[1]*2
		fc['DERFilePath']=[os.path.join(thisAppHome,'config','config_der.json')]*2
		fc['initializeWithActual']=[True]*2
		fc['DERSetting']=['PVPlacement']*2
		fc['DERModelType']=['ThreePhaseUnbalanced']*2

		# here 25 is the feeder nodeID where PV will be placed.
		# der_id is the configuration for a particular standard, for instance,
		# "50_2003" represents a 50 kva pvder that follows IEEE 1547 2003 standard
		fc['PVPlacement']=[{'25':{"derId":"50","powerRating":50,"pvderScale":1},
		'51':{"derId":"50","powerRating":50,"pvderScale":1}}]*2

		ch.add_manualfeederconfig(**fc)

		# add simulation config
		ch.add_simulationconfig(simType='dynamic')
		ch.add_fault(faultBus=10,faultImpedance=[0.0,-10000],faultOnTime=0.1,faultOffTime=0.267)
		ch.add_simend(0.4)

		# add output
		ch.add_outputconfig(outputDir=os.path.join(thisAppHome,'data','out'),
		outputFileName='report.xlsx',outputFileType='xlsx')

		# validate
		ch.validate()

		# write config
		fpath=os.path.join(thisAppHome,'config','config_ex_1.json')
		ch.write(fpath=fpath)

		# run
		GlobalData.set_config(fpath)
		GlobalData.set_TDdata()
		proc = Procedure()
		proc.simulate()

		# clean up
		os.system('del {}'.format(fpath))# delete config file
	except:
		PrintException()

