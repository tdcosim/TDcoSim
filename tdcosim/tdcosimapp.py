import os
import sys
import time
import argparse
import json
import pdb

import win32api
import click


baseDir=os.path.dirname(os.path.abspath(__file__))
if '~' in baseDir:
	baseDir=win32api.GetLongPathName(baseDir)
installDir=baseDir

userPreference=json.load(open(os.path.join(baseDir,'config','user_preference.json')))


@click.group()
def main():
	pass


@main.command()
@click.option("-c","--config", required=True, help="Path to config")
def run(config):
	# lazy import
	from tdcosim.global_data import GlobalData
	from tdcosim.procedure.procedure import Procedure

	startTime = time.time()
	# assert args.config, "config is not provided. You can specify this using -c --config"
	if not os.path.exists(os.path.abspath(config)) and os.path.exists(os.path.join(baseDir,config)):
		config=os.path.join(baseDir,config)
	assert os.path.exists(config),'{} does not exist'.format(config)

	# check if the config is valid
	check_config(config)

	GlobalData.set_config(config)
	GlobalData.set_TDdata()
	proc = Procedure()
	proc.simulate()
	print('Solution time:',time.time()-startTime)


def check_config(fpath):
	conf=json.load(open(fpath))
	userPreference=json.load(open(os.path.join(baseDir,'config','user_preference.json')))

	if 'installLocation' not in conf['psseConfig'] and 'psseConfig' in userPreference and 'installLocation' in userPreference['psseConfig']:
		conf['psseConfig']['installLocation']=userPreference['psseConfig']['installLocation']

	if 'installLocation' in conf['psseConfig'] and not conf['psseConfig']['installLocation'] and 'psseConfig' in userPreference and 'installLocation' in userPreference['psseConfig']:
		conf['psseConfig']['installLocation']=userPreference['psseConfig']['installLocation']

	assert conf['psseConfig']['installLocation'],"psseConfig->installLocation not provided in configuration"

	if 'outputDir' not in conf['outputConfig'] and 'outputConfig' in userPreference and 'outputDir' in userPreference['outputConfig']:
		conf['outputConfig']['outputDir']=userPreference['outputConfig']['outputDir']

	if conf['outputConfig']['outputDir']!=os.path.abspath(conf['outputConfig']['outputDir']) and \
	'outputConfig' in userPreference and 'outputDir' in userPreference['outputConfig']:
		conf['outputConfig']['outputDir']=os.path.join(userPreference['outputConfig']['outputDir'],conf['outputConfig']['outputDir'])
	elif conf['outputConfig']['outputDir']!=os.path.abspath(conf['outputConfig']['outputDir']):
		conf['outputConfig']['outputDir']=os.path.abspath(conf['outputConfig']['outputDir'])

	if not os.path.exists(conf['outputConfig']['outputDir']):
		os.system('mkdir "{}"'.format(conf['outputConfig']['outputDir']))
	conf['outputConfig']['outputDir']='{}'.format(win32api.GetLongPathName(conf['outputConfig']['outputDir']))

	# check if files exist
	items2check=[conf['psseConfig']['installLocation']]

	if not os.path.exists(conf['psseConfig']['dyrFilePath']) and \
	os.path.exists(os.path.join(installDir,conf['psseConfig']['dyrFilePath'])):
		conf['psseConfig']['dyrFilePath']=os.path.join(installDir,conf['psseConfig']['dyrFilePath'])

	if not os.path.exists(conf['psseConfig']['rawFilePath']) and \
	os.path.exists(os.path.join(installDir,conf['psseConfig']['rawFilePath'])):
		conf['psseConfig']['rawFilePath']=os.path.join(installDir,conf['psseConfig']['rawFilePath'])
	
	items2check.extend([conf['psseConfig']['dyrFilePath'],conf['psseConfig']['rawFilePath']])
	conf['psseConfig']['dyrFilePath']='{}'.format(win32api.GetLongPathName(conf['psseConfig']['dyrFilePath']))
	conf['psseConfig']['rawFilePath']='{}'.format(win32api.GetLongPathName(conf['psseConfig']['rawFilePath']))

	if conf['openDSSConfig']:
		if 'defaultFeederConfig' in conf['openDSSConfig'] and \
		'filePath' in conf['openDSSConfig']['defaultFeederConfig']:
			if not os.path.exists(conf['openDSSConfig']['defaultFeederConfig']['filePath'][0]) and \
			os.path.exists(os.path.join(installDir,conf['openDSSConfig']['defaultFeederConfig']['filePath'][0])):
				conf['openDSSConfig']['defaultFeederConfig']['filePath'][0]=\
				os.path.join(installDir,conf['openDSSConfig']['defaultFeederConfig']['filePath'][0])
			items2check.append(conf['openDSSConfig']['defaultFeederConfig']['filePath'][0])
			conf['openDSSConfig']['defaultFeederConfig']['filePath'][0]=\
			'{}'.format(win32api.GetLongPathName(conf['openDSSConfig']['defaultFeederConfig']['filePath'][0]))
		if 'defaultFeederConfig' in conf['openDSSConfig'] and \
		'DERFilePath' in conf['openDSSConfig']['defaultFeederConfig']:
			if not os.path.exists(conf['openDSSConfig']['defaultFeederConfig']['DERFilePath']) and \
			os.path.exists(os.path.join(installDir,conf['openDSSConfig']['defaultFeederConfig']['DERFilePath'])):
				conf['openDSSConfig']['defaultFeederConfig']['DERFilePath']=\
				os.path.join(installDir,conf['openDSSConfig']['defaultFeederConfig']['DERFilePath'])
			items2check.append(conf['openDSSConfig']['defaultFeederConfig']['DERFilePath'])
			conf['openDSSConfig']['defaultFeederConfig']['DERFilePath']=\
			'{}'.format(win32api.GetLongPathName(conf['openDSSConfig']['defaultFeederConfig']['DERFilePath']))
		if 'manualFeederConfig' in conf['openDSSConfig'] and \
		'nodes' in conf['openDSSConfig']['manualFeederConfig']:
			for thisNode in conf['openDSSConfig']['manualFeederConfig']['nodes']:
				if 'filePath' in thisNode:
					if not os.path.exists(thisNode['filePath'][0]) and os.path.exists(os.path.join(installDir,thisNode['filePath'][0])):
						thisNode['filePath'][0]=os.path.join(installDir,thisNode['filePath'][0])
					items2check.append(thisNode['filePath'][0])
					thisNode['filePath'][0]='{}'.format(win32api.GetLongPathName(thisNode['filePath'][0]))
				if 'DERFilePath' in thisNode:
					if not os.path.exists(thisNode['DERFilePath']) and os.path.exists(os.path.join(installDir,thisNode['DERFilePath'])):
						thisNode['DERFilePath']=os.path.join(installDir,thisNode['DERFilePath'])
					items2check.append(thisNode['DERFilePath'])
					thisNode['DERFilePath']='{}'.format(win32api.GetLongPathName(thisNode['DERFilePath']))

	for entry in items2check:
		assert os.path.exists(entry),'{} does not exist'.format(entry)
	# update
	json.dump(conf,open(fpath,'w'),indent=3)


def template(args):
	assert args.templatePath, "templatePath is not provided. You can specify this using --templatePath"
	assert args.simType, "simType is not provided. You can specify this using --simType"
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
	elif args.simType=='dynamic_detailed_der':
		res=json.load(open(os.path.join(baseDir,'config','template_detailed_der.json')))
		args.templatePath=os.path.abspath(args.templatePath)
		res['simulationConfig'].pop('staticConfig')
		res['simulationConfig']['protocol']="loose_coupling"
		res['simulationConfig']['simType']="dynamic"
		res['openDSSConfig']['manualFeederConfig']['nodes'].pop(-1)
	else:
		print('simType has to be either static or dynamic but {} was provided!!!!'.format(args.simType))
		raise
	json.dump(res,open(args.templatePath,'w'),indent=3)


@main.command('dashboard')
@click.option("-o","--output_path", required=True, help="Path to output folder")
@click.option("-r","--reduced_memory", required=False, default=False, help="")
@click.option("-u","--use_dask", required=False, default=False, help="")
@click.option("-p","--psse_path", required=False, default=userPreference['psseConfig']['installLocation'], help="")
@click.option("--port_number", required=False, default=8050, help="port number for server")
@click.option("-n","--nfiles", required=False, default=2, help="")
def dashboard(output_path,reduced_memory,use_dask,psse_path,port_number,nfiles):
	if os.path.abspath(output_path)!=output_path and os.path.exists(os.path.abspath(output_path)):
		output_path=os.path.abspath(output_path)
	elif os.path.abspath(output_path)!=output_path and not os.path.exists(os.path.abspath(output_path)) and \
		'outputConfig' in userPreference and 'outputDir' in userPreference['outputConfig'] and \
		os.path.exists(os.path.join(userPreference['outputConfig']['outputDir'],output_path)):
		output_path=os.path.join(userPreference['outputConfig']['outputDir'],output_path)
	appPath=os.path.join(baseDir,'dashboard','app.py')
	os.system('python {} {} "{}" {} {} {} {}'.format(appPath,output_path,psse_path,reduced_memory,nfiles,use_dask,port_number))


def configHelp(args):
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


@main.command(name="describe")
@click.option("-j","--json_format", required=False, default=False, help="output in JSON format")
def describe(json_format):
	os.system('cls')
	if json_format:
		res={}
		res['Install Directory']=baseDir
		res['Examples Directory']=os.path.join(baseDir,'examples')
		res['Available Examples']=[entry for entry in os.listdir(os.path.join(baseDir,'examples'))]
		res['Available Test Systems']={}
		res['Available Test Systems']['Transmission Test Systems']=\
		[entry for entry in os.listdir(os.path.join(baseDir,'data','transmission')) if '~' not in entry]
		res['Available Test Systems']['Distribution Test Systems']=\
		[entry for entry in os.listdir(os.path.join(baseDir,'data','distribution')) if '~' not in entry]
		res['Log Directory']=os.path.join(baseDir,'logs')
		print(json.dumps(res,indent=5))
	else:
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


@main.command(name="test")
def test():
	pyExe=sys.executable.split('\\')[-1].replace('.exe','')
	res={}

	data=json.load(open(os.path.join(baseDir,'examples','config_case68_dynamics.json')))
	data['outputConfig']['outputDir']=os.path.join(baseDir,'output')
	json.dump(data,open(os.path.join(baseDir,'examples','config_case68_dynamics.json'),'w'),indent=3)
	tdcosimappPath=os.path.abspath(__file__)
	if '~' in tdcosimappPath:
		tdcosimappPath=win32api.GetLongPathName(tdcosimappPath)
	directive='{} "{}" run -c examples{}config_case68_dynamics.json'.format(pyExe,tdcosimappPath,os.path.sep)
	os.system(directive)
	mtime=time.time()-os.path.getmtime(\
	os.path.join(baseDir,'output','case68_dynamics_b19f4c5a2cbf4ab0a3c1d1ba30a31442','df_pickle.pkl'))
	if mtime<=60:
		res['config_case68_dynamics']=True

	data=json.load(open(os.path.join(baseDir,'examples','config_case68_qsts.json')))
	data['outputConfig']['outputDir']=os.path.join(baseDir,'output')
	json.dump(data,open(os.path.join(baseDir,'examples','config_case68_qsts.json'),'w'),indent=3)
	directive='{} "{}" run -c examples{}config_case68_qsts.json'.format(pyExe,tdcosimappPath,os.path.sep)
	os.system(directive)
	mtime=time.time()-os.path.getmtime(\
	os.path.join(baseDir,'output','case68_qsts_b19f4c5a2cbf4ab0a3c1d1ba30a31442','df_pickle.pkl'))
	if mtime<=60:
		res['config_case68_qsts']=True

	data=json.load(open(os.path.join(baseDir,'examples','config_case68_dynamics_detailed_der.json')))
	data['outputConfig']['outputDir']=os.path.join(baseDir,'output')
	json.dump(data,open(os.path.join(baseDir,'examples','config_case68_dynamics_detailed_der.json'),'w'),indent=3)
	directive='{} "{}" run -c examples{}config_case68_dynamics_detailed_der.json'.format(pyExe,tdcosimappPath,os.path.sep)
	os.system(directive)
	mtime=time.time()-os.path.getmtime(\
	os.path.join(baseDir,'output','case68_dynamics_detailed_der','df_pickle.pkl'))
	if mtime<=100:
		res['config_case68_dynamics_detailed_der']=True

	os.system('cls')
	for entry in res:
		print('Success flag for {}:{}'.format(entry,res[entry]))


@main.command(name="setconfig")
@click.option("-o","--output_root_dir", required=False, default=None, help="Root directory to store results")
@click.option("-p","--psse_path", required=False, default=None, help="psse location")
def setconfig(output_root_dir,psse_path):
	conf=json.load(open(os.path.join(baseDir,'config','user_preference.json')))
	if output_root_dir:
		conf['outputConfig']={'outputDir':output_root_dir}
	if psse_path:
		conf['psseConfig']={'installLocation':psse_path}
	json.dump(conf,open(os.path.join(baseDir,'config','user_preference.json'),'w'),indent=3)


@main.command(name="getconfig")
def getconfig():
	conf=json.load(open(os.path.join(baseDir,'config','user_preference.json')))
	print(json.dumps(conf,indent=3))


if __name__ == '__main__':
	main()