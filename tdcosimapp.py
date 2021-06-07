import os
import time
import argparse
import json
import pdb

from tdcosim.global_data import GlobalData
from tdcosim.procedure.procedure import Procedure


baseDir=os.path.dirname(os.path.abspath(__file__))


def run(args):
	try:
		startTime = time.time()
		args.config=os.path.abspath(args.config)
		assert os.path.exists(args.config),'{} does not exist'.format(args.config)

		GlobalData.set_config(args.config)
		GlobalData.set_TDdata()
		proc = Procedure()
		proc.simulate()
		print('Solution time:',time.time()-startTime)
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


if __name__ == "__main__":
	#### sampleRun: python tdcosimapp.py -t template --templatePath test.json --simType dynamic
	#### python tdcosimapp.py -t template --templatePath test.json --simType static
	#### python ..\tdcosimapp.py -t run -c config_fast_der.json
	#### python tdcosimapp.py --configHelp outputConfig
	#### python tdcosimapp.py --configHelp outputConfig.scenarioID
	startTime = time.time()
	parser = argparse.ArgumentParser()
	parser.add_argument('-t','--type', required=False, type=str)	
	parser.add_argument('-c','--config', type=str, help='The configfile location')
	parser.add_argument('--configHelp', type=str, help='Help on configuration options',default='')
	parser.add_argument('--templatePath', type=str, help='location to store template config')	
	parser.add_argument('--simType', type=str,default='dynamic')	


	args = parser.parse_args()
	if args.configHelp:
		configHelp(args)
	elif args.type=='run':
		run(args)
	elif args.type=='template':
		template(args)