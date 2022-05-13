import os
os.environ["PATH"] += os.getcwd()
import sys
import socket
import pdb
import json
import time

import six

from tdcosim.model.opendss.opendss_data import OpenDSSData
from tdcosim.model.opendss.procedure.opendss_procedure import OpenDSSProcedure

#===================================================================================================
def findConfig(nodeid):
	try:
		if isinstance(nodeid,str):
			nodeid=int(nodeid)
		if nodeid > 0 and 'manualFeederConfig' in OpenDSSData.config['openDSSConfig'] and \
		'nodes' in OpenDSSData.config['openDSSConfig']['manualFeederConfig']:
			for x in OpenDSSData.config['openDSSConfig']['manualFeederConfig']['nodes']:
				if x['nodenumber'] == int(nodeid):
					dssconfig = x
		elif 'defaultFeederConfig' in OpenDSSData.config['openDSSConfig']:
			dssconfig = OpenDSSData.config['openDSSConfig']['defaultFeederConfig']
		return dssconfig
	except:
		OpenDSSData.log()


#===================================================================================================
if __name__=="__main__":
	try:
		nodeid = "-1"
		if len(sys.argv)>1:
			nodeid = sys.argv[1]

		dssProcedure=OpenDSSProcedure()

		BUFFER_SIZE = 1024*1024*16
		c = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		c.connect(('127.0.0.1',11000))

		comm_end=0
		while comm_end==0:
			replyMsg = {}
			raw = c.recv(BUFFER_SIZE)
			if six.PY3:
				raw=raw.decode('ascii')
			
			msg=json.loads(raw)# expect the msg to be of json format
			OpenDSSData.logger.debug('recvmsg={}'.format(msg))

			if 'COMM_END' in msg:
				comm_end=1
				if six.PY2:
					c.send(json.dumps({"shutdown":1}))# reply back to handler
				elif six.PY3:
					c.send(json.dumps({"shutdown":1}).encode())# reply back to handler
				tempOutputF.close()
				c.shutdown(0)
				c.close() # close comm with server
				OpenDSSData.log(level=20,msg="Open DSS Client {} is ended".format(nodeid))
				break
			elif msg['method'].lower()=='setup':
				OpenDSSData.config = msg['config']
				OpenDSSData.config['myconfig'] = findConfig(nodeid)
				dssProcedure.setup()
				replyMsg = {'response': nodeid}
				tempOutputF=open(os.path.join(OpenDSSData.config['outputConfig']['outputDir'],\
				'{}_temp.csv'.format(nodeid)),'w')
			elif msg['method'].lower()=='initialize':
				replyMsg['P'],replyMsg['Q'],replyMsg['convergedFlag'],replyMsg['scale']=\
				dssProcedure.initialize(targetS=msg['targetS'],Vpcc=msg['Vpcc'],tol=msg['tol'])
			elif msg['method'].lower()=='setvoltage':
				dssProcedure.setVoltage(Vpu=msg['Vpu'],Vang=msg['Vang'],pccName=msg['pccName'])
				replyMsg = {"AckNode":nodeid}
			elif msg['method'].lower()=='getload':
				replyMsg['P'],replyMsg['Q'],replyMsg['convergenceFlg'],replyMsg['derX']=\
				dssProcedure.getLoads(pccName=msg['pccName'],t=msg['t'],dt=msg['dt'])
			elif msg['method'].lower()=='scaleload':
				dssProcedure.scaleLoad(scale=msg['scale'])
			elif msg['method'].lower()=='monitor':
				replyMsg=dssProcedure.monitor(msg['varName'],tempOutputF,msg['info']['t'])
			
			OpenDSSData.logger.debug('replyMsg={}'.format(msg))
			if six.PY2:
				c.send(json.dumps(replyMsg))# reply back to handler
			elif six.PY3:
				c.send(json.dumps(replyMsg).encode())# reply back to handler
			OpenDSSData.logger.debug('sent reply to server')
	except:
		OpenDSSData.log(40,"Error in OpenDSS Client {}".format(nodeid))

