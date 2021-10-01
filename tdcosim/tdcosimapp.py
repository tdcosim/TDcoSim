import os
import sys
import time
import argparse
import json
import pdb
import inspect

import tdcosim
from tdcosim.global_data import GlobalData
from tdcosim.procedure.procedure import Procedure

baseDir=os.path.dirname(os.path.abspath(__file__))
installDir=os.path.dirname(inspect.getfile(tdcosim))


def run(args):
	try:
		startTime = time.time()
		args.config=os.path.abspath(args.config)
		assert os.path.exists(args.config),'{} does not exist'.format(args.config)

		# check if the config is valid
		check_config(args.config)

		GlobalData.set_config(args.config)
		GlobalData.set_TDdata()
		proc = Procedure()
		proc.simulate()
		print('Solution time:',time.time()-startTime)
	except:
		raise

def check_config(fpath):
	try:
		conf=json.load(open(fpath))

		# check if files exist
		items2check=[conf['psseConfig']['installLocation']]

		if not os.path.exists(conf['psseConfig']['dyrFilePath']) and \
		os.path.exists(os.path.join(installDir,conf['psseConfig']['dyrFilePath'])):
			conf['psseConfig']['dyrFilePath']=os.path.join(installDir,conf['psseConfig']['dyrFilePath'])

		if not os.path.exists(conf['psseConfig']['rawFilePath']) and \
		os.path.exists(os.path.join(installDir,conf['psseConfig']['rawFilePath'])):
			conf['psseConfig']['rawFilePath']=os.path.join(installDir,conf['psseConfig']['rawFilePath'])
		
		items2check.extend([conf['psseConfig']['dyrFilePath'],conf['psseConfig']['rawFilePath']])

		if conf['openDSSConfig']:
			if 'defaultFeederConfig' in conf['openDSSConfig'] and \
			'filePath' in conf['openDSSConfig']['defaultFeederConfig']:
				if not os.path.exists(conf['openDSSConfig']['defaultFeederConfig']['filePath'][0]) and \
				os.path.exists(os.path.join(installDir,conf['openDSSConfig']['defaultFeederConfig']['filePath'][0])):
					conf['openDSSConfig']['defaultFeederConfig']['filePath'][0]=\
					os.path.join(installDir,conf['openDSSConfig']['defaultFeederConfig']['filePath'][0])
				items2check.append(conf['openDSSConfig']['defaultFeederConfig']['filePath'][0])
			if 'manualFeederConfig' in conf['openDSSConfig'] and \
			'nodes' in conf['openDSSConfig']['manualFeederConfig']:
				for thisNode in conf['openDSSConfig']['manualFeederConfig']['nodes']:
					if 'filePath' in thisNode:
						if not os.path.exists(thisNode['filePath'][0]) and os.path.exists(os.path.join(installDir,thisNode['filePath'][0])):
							thisNode['filePath'][0]=os.path.join(installDir,thisNode['filePath'][0])
						items2check.append(thisNode['filePath'][0])

		for entry in items2check:
			assert os.path.exists(entry),'{} does not exist'.format(entry)

		# update
		json.dump(conf,open(fpath,'w'),indent=3)
	except:
		raise

def template(args):
	try:
		res=json.load(open(os.path.join(baseDir,'config','template.json')))
		args.templatePath=os.path.abspath(args.templatePath)
		
		if args.simType=='dynamic':
			res['simulationConfig'].pop('staticConfig')
			res['simulationConfig']['protocol']="loose_coupling"
			res['simulationConfig']['simType']="dynamic"
			res['openDSSConfig']['manualFeederConfig']['nodes'].pop(-1)
		elif args.simType=='static':
			res['simulationConfig'].pop('dynamicConfig')
			res['simulationConfig']['protocol']="tight_coupling"
			res['simulationConfig']['simType']="static"
			res['openDSSConfig'].pop('DEROdeSolver')
			res['openDSSConfig']['manualFeederConfig']['nodes'].pop(0)
		else:
			print('simType has to be either static or dynamic but {} was provided!!!!'.format(args.simType))
			raise

		json.dump(res,open(args.templatePath,'w'),indent=3)
	except:
		raise

def dashboard(args):
	try:
		appPath=os.path.join(baseDir,'dashboard','app.py')
		os.system('python {} {} "{}"'.format(appPath,args.outputPath,args.pssePath))
	except:
		raise

def configHelp(args):
	try:
		data=json.load(open(os.path.join(baseDir,'config','configHelp.json')))
		if args.configHelp=='all':
			for entry in data:
				print(data[entry]['help'])
		elif not '.' in args.configHelp and args.configHelp in data:
			print(data[args.configHelp]['help'])
		elif '.' in args.configHelp:
			res=args.configHelp.split('.')
			thisData=data[res.pop(0)]
			while res:
				thisData=thisData[res.pop(0)]
			print(thisData['help'])
	except:
		raise

def print_help():
	try:
		print('\n\nNo input arguments are provided. Typical usage is as follows,\n')
		print('To run a test case use,\npython tdcosimapp.py -t run -c config.json\n')
		print('To create template for QSTS,\npython tdcosimapp.py -t template --templatePath test.json --simType static\n')
		print('To create template for dynamic simulation,\npython tdcosimapp.py -t template --templatePath test.json --simType dynamic\n')
		print('To obtain help about configuration keywords,\npython tdcosimapp.py --configHelp outputConfig')
		print('python tdcosimapp.py --configHelp outputConfig.scenarioID')
	except:
		raise


if __name__ == "__main__":
	startTime = time.time()
	parser = argparse.ArgumentParser()
	parser.add_argument('-t','--type', required=False, type=str)	
	parser.add_argument('-c','--config', type=str, help='The configfile location')
	parser.add_argument('--configHelp', type=str, help='Help on configuration options',default='')
	parser.add_argument('--templatePath', type=str, help='location to store template config')	
	parser.add_argument('--simType', type=str,default='dynamic')	
	parser.add_argument('-o','--outputPath', type=str, help='Path to output pickle file')
	parser.add_argument('-p','--pssePath', type=str, help='psse location')

	if len(sys.argv)==1:
		print_help()
	else:
		args = parser.parse_args()
		if args.configHelp:
			configHelp(args)
		elif args.type=='run':
			run(args)
		elif args.type=='template':
			template(args)
		elif args.type=='dashboard':
			dashboard(args)