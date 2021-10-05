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
		assert args.config, "config should be set using -c option, got {}".format(args.config)
		if not os.path.exists(os.path.abspath(args.config)) and os.path.exists(os.path.join(baseDir,args.config)):
			args.config=os.path.join(baseDir,args.config)
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
		userPreference=json.load(open(os.path.join(baseDir,'config','user_preference.json')))

		if 'installLocation' not in conf['psseConfig'] and 'psseConfig' in userPreference and 'installLocation' in userPreference['psseConfig']:
			conf['psseConfig']['installLocation']=userPreference['psseConfig']['installLocation']
		
		assert conf['psseConfig']['installLocation'],"psseConfig->installLocation not provided in configuration"

		if 'outputDir' not in conf['outputConfig'] and 'outputConfig' in userPreference and 'outputDir' in userPreference['outputConfig']:
			conf['outputConfig']['outputDir']=userPreference['outputConfig']['outputDir']

		if conf['outputConfig']['outputDir']!=os.path.abspath(conf['outputConfig']['outputDir']) and \
		'outputConfig' in userPreference and 'outputDir' in userPreference['outputConfig']:
			conf['outputConfig']['outputDir']=os.path.join(userPreference['outputConfig']['outputDir'],conf['outputConfig']['outputDir'])

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
		assert args.templatePath, "templatePath not set"
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
		print('To run a test case use,\ntdcosim run -c config.json\n')
		print('To create template for QSTS,\ntdcosim template --templatePath test.json --simType static\n')
		print('To create template for dynamic simulation,\ntdcosim template --templatePath test.json --simType dynamic\n')
		print('To obtain help about configuration keywords,\ntdcosim --configHelp outputConfig')
		print('tdcosim --configHelp outputConfig.scenarioID')
	except:
		raise

def describe(args):
	try:
		os.system('cls')
		print('\nInstall Directory:\n'+'='*len("Install Directory:")+'\n{}\n'.format(baseDir))

		print('Examples Directory:\n'+'='*len("Examples Directory:")+'\n{}\n'.format(os.path.join(baseDir,'examples')))

		print('Available Examples:\n'+'-'*len("Available Examples:"))
		for entry in os.listdir(os.path.join(baseDir,'examples')):
			print('{}'.format(entry))

		print('\nAvailable Test Systems:\n'+'='*len("Available Test Systems:"))
		print('\nTransmission Test Systems:\n'+'-'*len("Transmission Test Systems:"))
		for entry in os.listdir(os.path.join(baseDir,'data','transmission')):
			if '~' not in entry:
				print('{}'.format(entry))
		print('\nDistribution Test Systems:\n'+'-'*len("Distribution Test Systems:"))
		for entry in os.listdir(os.path.join(baseDir,'data','distribution')):
			if '~' not in entry:
				print('{}'.format(entry))

		print('\nLog Directory:\n'+'='*len("Log Directory:")+'\n{}'.format(os.path.join(baseDir,'logs')))
	except:
		raise

def test(args):
	try:
		pyExe=sys.executable.split('\\')[-1].replace('.exe','')
		res={}

		data=json.load(open(os.path.join(baseDir,'examples','config_case68_dynamics.json')))
		data['outputConfig']['outputDir']=os.path.join(baseDir,'output')
		json.dump(data,open(os.path.join(baseDir,'examples','config_case68_dynamics.json'),'w'),indent=3)
		os.system('{} {} run -c examples{}config_case68_dynamics.json'.format(pyExe,os.path.abspath(__file__),os.path.sep))
		mtime=time.time()-os.path.getmtime(os.path.join(baseDir,'output','case68_dynamics_b19f4c5a2cbf4ab0a3c1d1ba30a31442','df_pickle.pkl'))
		if mtime<=60:
			res['config_case68_dynamics']=True
	
		data=json.load(open(os.path.join(baseDir,'examples','config_case68_qsts.json')))
		data['outputConfig']['outputDir']=os.path.join(baseDir,'output')
		json.dump(data,open(os.path.join(baseDir,'examples','config_case68_qsts.json'),'w'),indent=3)
		os.system('{} {} run -c examples{}config_case68_qsts.json'.format(pyExe,os.path.abspath(__file__),os.path.sep))
		mtime=time.time()-os.path.getmtime(os.path.join(baseDir,'output','case68_qsts_b19f4c5a2cbf4ab0a3c1d1ba30a31442','df_pickle.pkl'))
		if mtime<=60:
			res['config_case68_qsts']=True

		os.system('cls')
		for entry in res:
			print('Success flag for {}:{}'.format(entry,res[entry]))
	except:
		raise

def setconfig(args):
	try:
		conf=json.load(open(os.path.join(baseDir,'config','user_preference.json')))
		if args.outputRootDir:
			conf['outputConfig']={'outputDir':args.outputRootDir}
		if args.pssePath:
			conf['psseConfig']={'installLocation':args.pssePath}
		json.dump(conf,open(os.path.join(baseDir,'config','user_preference.json'),'w'),indent=3)
	except:
		raise

def getconfig(args):
	try:
		conf=json.load(open(os.path.join(baseDir,'config','user_preference.json')))
		print(json.dumps(conf,indent=3))
	except:
		raise

if __name__ == "__main__":
	startTime = time.time()
	parser = argparse.ArgumentParser()
	parser.add_argument('type', type=str)	
	parser.add_argument('-c','--config', type=str, help='The configfile location')
	parser.add_argument('--configHelp', type=str, help='Help on configuration options',default='')
	parser.add_argument('--templatePath', type=str, help='location to store template config')	
	parser.add_argument('--simType', type=str,default='dynamic')	
	parser.add_argument('-o','--outputPath', type=str, help='Path to output pickle file')
	parser.add_argument('--outputRootDir', type=str, help='Root directory to store results')
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
		elif args.type=='describe':
			describe(args)
		elif args.type=='test':
			test(args)
		elif args.type.lower()=='setconfig':
			setconfig(args)
		elif args.type.lower()=='getconfig':
			getconfig(args)