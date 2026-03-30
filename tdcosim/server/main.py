import json
import uuid
from http import HTTPStatus
import subprocess
import shlex

import psutil
from flask import Flask,Response,request


procMap={}


#=======================================================================================================================
def run():
	data=request.json
	runUUID=uuid.uuid4().hex
	if data:
		config=data['config']
		ravensData=data['solution']
		config['costadmg_interface']={'distribution':{}}

		for busId in data['td_interface']:
			config['costadmg_interface']['distribution'][busId]=\
				{'set':ravens2tdcosim(ravensData,busId)}

		nDis=len(config['costadmg_interface']['distribution'][busId]['set'])
		config['simulationConfig']['staticConfig']['loadShape']=[1]*nDis

		fpath=f'/tmp/{runUUID}.json'
		config['outputConfig']['outputDir']='/tmp'
		config['outputConfig']['simID']=runUUID
		json.dump(config,open(fpath,'w'))
		directive=f'tdcosimcli run -c {fpath}'
	else:
		directive='tdcosimcli run -c config_case118_qsts_costadmg.json'
	proc=subprocess.Popen(shlex.split(directive),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
	procMap[runUUID]=proc.pid
	res=Response(status=HTTPStatus.OK)
	res.mimetype='application/json'
	res.response=json.dumps({"success":True,"uuid":runUUID})
	return res


#=======================================================================================================================
def get_ravens_switch_status_data(ravensData):
	inputData=ravensData['OptimalPowerFlow']['OperationsResult.Switches']
	data={e['ArSwitch.Switch'].replace('Switch::','').replace("'",''):e for e in inputData}

	res={}
	for loadId in data:
		for item in data[loadId]['AnalysisResultData.Curve']['AnalysisResultCurve.CurveDatas']:
			t=item['ArCurveData.xvalue']
			if t not in res:
				res[t]={'asset':[],'property':[],'value':[]}
			res[t]['asset'].append(f'Line.{loadId}')
			res[t]['property'].append('Enabled')
			res[t]['value'].append(not item['ArCurveData.DataValues']['AvSwitch.open'])

	return res


#=======================================================================================================================
def get_ravens_loadshed_data(ravensData):
	inputData=ravensData['OptimalPowerFlow']['OperationsResult.Statuses']
	data={e['ArStatus.ConductingEquipment'].replace('EnergyConsumer::','').replace("'",''):e for e in inputData \
		if 'EnergyConsumer' in e['ArStatus.ConductingEquipment']}

	res={}
	for loadId in data:
		for item in data[loadId]['AnalysisResultData.Curve']['AnalysisResultCurve.CurveDatas']:
			t=item['ArCurveData.xvalue']
			if t not in res:
				res[t]={'asset':[],'property':[],'value':[]}
			res[t]['asset'].append(f'Load.{loadId}')
			res[t]['property'].append('Enabled')
			res[t]['value'].append(item['ArCurveData.DataValues']['AvStatus.inService'])

	return res


#=======================================================================================================================
def ravens2tdcosim(ravensData,busId):
	res_switch=get_ravens_switch_status_data(ravensData)
	res_loadshed=get_ravens_loadshed_data(ravensData)

	res={}
	for t in res_switch:
		res[t]={'asset':[],'property':[],'value':[]}
		for entry in res[t]:
			res[t][entry].extend(res_switch[t][entry])
			res[t][entry].extend(res_loadshed[t][entry])

	t=list(res.keys())
	t.sort()
	reply=[{'time':timestep,'data':res[timestep]} for timestep in t]

	return reply


#=======================================================================================================================
def status():
	runUUID = request.args.get('uuid')
	if runUUID in procMap:
		procStatus='completed'
		procExists=psutil.pid_exists(procMap[runUUID])
		if procExists:
			p=psutil.Process(procMap[runUUID])
			if p.status()!='zombie':
				procStatus='running'
		res=Response(status=HTTPStatus.OK)
		res.mimetype='application/json'
		res.response=json.dumps({"success":True,"status":procStatus})
	else:
		res=Response(status=HTTPStatus.BAD_REQUEST)
		res.mimetype='application/json'
		res.response=json.dumps({"success":False,"error":f"UUID {runUUID} does not exist"})
	return res


#=======================================================================================================================
def results():
	runUUID = request.args.get('uuid')

	if runUUID in procMap:
		# first check status
		procStatus='completed'
		procExists=psutil.pid_exists(procMap[runUUID])
		if procExists:
			p=psutil.Process(procMap[runUUID])
			if p.status()!='zombie':
				procStatus='running'

		res=Response(status=HTTPStatus.OK)
		res.mimetype='application/json'
		if procStatus=='completed':
			fpath=f'/tmp/{runUUID}/costadmg_results_{runUUID}.csv'
			f=open(fpath)
			fileData=f.read().splitlines()
			f.close()
			data=[]
			for line in fileData[1::]:
				success=True if line.split(',')[-1].lower()=='true' else False
				data.append(success)
			res.response=json.dumps({"success":True,"status":procStatus,"data":data})
		else:
			res.response=json.dumps({"success":False,"status":procStatus,"data":{}})
	else:
		res=Response(status=HTTPStatus.BAD_REQUEST)
		res.mimetype='application/json'
		res.response=json.dumps({"success":False,"error":f"UUID {runUUID} does not exist"})
	return res


#=======================================================================================================================
if __name__ == '__main__':
	app = Flask(__name__)
	app.add_url_rule(rule='/run',methods=['POST','GET'],view_func=run)
	app.add_url_rule(rule='/status',methods=['POST','GET'],view_func=status)
	app.add_url_rule(rule='/results',methods=['POST','GET'],view_func=results)
	app.run(host='0.0.0.0',port=5000,debug=False,use_reloader=True,threaded=True)


