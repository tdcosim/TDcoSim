# -*- coding: utf-8 -*-
"""
Created on Thu May  7 16:21:41 2020

@author: splathottam
"""

import os
import tdcosim

dirlocation= os.path.dirname(tdcosim.__file__)
dirlocation = dirlocation[0:len(dirlocation)-8]

test_config = {
	"nodenumber": 11,
	"filePath": [os.path.join(dirlocation,"SampleData\\DNetworks\\123Bus\\case123ZIP.dss")],
	"solarFlag":1,
	"DERFilePath": os.path.join(dirlocation,"examples\\config_der.json"),
	"initializeWithActual":True,
	"DERSetting":"default",
	"DERModelType":"ThreePhaseUnbalanced",
	"DERParameters":{
	   "default":{
				  "solarPenetration":0.01,
				  "solarPenetrationUnit":'kw',
				  "derId":"50",
				  "powerRating":50,
				  "VrmsRating":177.0,
				  "steadyStateInitialization":True,
				  "pvderScale": 1,
				  "LVRT":{"0":{"V_threshold":0.5,"t_threshold":0.1,"mode":"momentary_cessation"},
						  "1":{"V_threshold":0.7,"t_threshold":1.0,"mode":"mandatory_operation"},
						  "2":{"V_threshold":0.88,"t_threshold":2.0,"mode":"mandatory_operation"}},
				  "HVRT":{"0":{"V_threshold":1.12,"t_threshold":0.016,"mode":"momentary_cessation"},
						  "1":{"V_threshold":1.06,"t_threshold":3.0,"mode":"momentary_cessation"}},
				  "output_restore_delay":0.4
						 },
	   "PVPlacement":{"50":{"derId":"250","powerRating":250,"pvderScale":1,"VrmsRating":230.0},
					  "25":{"derId":"50","powerRating":50,"pvderScale":1}
					 },
	   "avoidNodes": ['sourcebus','rg60'],
	   "dt":1/120.0
	}
}