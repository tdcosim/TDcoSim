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
		fpath=f'/tmp/{runUUID}.json'
		json.dump(data,open(fpath,'w'))
		directive=f'tdcosimcli run -c {fpath}'
	else:
		directive='tdcosimcli run -c config_case68_qsts.json'
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
		res=Response(status=HTTPStatus.OK)
		res.mimetype='application/json'
		res.response=json.dumps({"success":True,"data":{}})
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


