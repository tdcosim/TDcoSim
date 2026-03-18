import json
import uuid
from http import HTTPStatus
import subprocess
import shlex

import psutil
from flask import Flask,Response,request


procMap={}


def process_costadmg_interface_data(switchStatus):
	res={}
	for entry in switchStatus:
		switchId=entry['ArSwitch.Switch'].replace('switch::','Line.').replace("'","")
		for item in entry['AnalysisResultData.Curve']['AnalysisResultCurve.CurveDatas']:
			if not item['ArCurveData.xvalue'] in res:
				res[int(item['ArCurveData.xvalue'])]=[]
			res[int(item['ArCurveData.xvalue'])].append([switchId,'Enabled',item['ArCurveData.DataValues']['AvSwitch.open']])

	costadmgInterfaceData=[]
	for t in res:
		timestepData={'time':t,'data':{'asset':[],'property':[],'value':[]}}
		for item in res[t]:
			timestepData['data']['asset'].append(item[0])
			timestepData['data']['property'].append(item[1])
			timestepData['data']['value'].append(item[2])
		costadmgInterfaceData.append(timestepData)

	return costadmgInterfaceData


#=======================================================================================================================
def run():
	data=request.json
	runUUID=uuid.uuid4().hex
	if data:
		config=data['config']
		switchStatus=data['switch_status']
		config['costadmg_interface']={'distribution':{}}

		for busId in switchStatus:
			config['costadmg_interface']['distribution'][busId]=\
				{'set':process_costadmg_interface_data(switchStatus[busId])}

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


